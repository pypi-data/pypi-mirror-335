# EXPLANATION# - This file handles the signup conversation flow with users
# - SignupFlow manages state transitions and question flow
# - SRSWTISignup handles WebSocket communication for the signup process
# - Both classes need access to OpenAI for response generation 
# - They also need to interact with Supabase for profile storage

import asyncio
import json
import logging
import queue
import traceback
import uuid
import os, time
from typing import Dict, Optional, Any
from pathlib import Path
from datetime import datetime

from openai import AsyncOpenAI
from supabase import Client
import websockets

from .models import SignupPhase, SignupState
from .utils import TTSChunkProcessor, tts_queue, interrupt_tts, tts_worker
from .helpers.stt import main as stt_main, ResumableMicrophoneStream
from .helpers.shared import transcript_queue, STREAMING_LIMIT

# Configure logger
logger = logging.getLogger(__name__)


class SupabaseProfileHandler:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        
    async def save_profile(self, user_id: str, signup_answers: dict) -> None:
        """
        Save or update user profile in Supabase after signup completion.
        
        Args:
            user_id (str): The user's UUID
            signup_answers (dict): Complete signup responses
        """
        try:
            logger.info(f"Checking for existing profile for user {user_id}")
            
            # Check for existing profile
            existing_profile = self.supabase.table('one_srswti_reverse_invited') \
                .select("*") \
                .eq('user_id', user_id) \
                .execute()

            # Prepare profile data
            profile_data = {
                'user_id': user_id,
                'signup_answers': signup_answers
            }
            
            if existing_profile.data:
                # Update existing profile
                logger.info(f"Updating existing profile for user {user_id}")
                result = self.supabase.table('one_srswti_reverse_invited') \
                    .update(profile_data) \
                    .eq('user_id', user_id) \
                    .execute()
            else:
                # Insert new profile
                logger.info(f"Creating new profile for user {user_id}")
                result = self.supabase.table('one_srswti_reverse_invited') \
                    .insert(profile_data) \
                    .execute()
            
            if result.data:
                logger.info(f"Profile successfully saved for user {user_id}")
            else:
                logger.warning(f"No data returned when saving profile for user {user_id}")
                raise Exception("Failed to save profile data")
                
        except Exception as e:
            logger.error(f"Error saving profile to Supabase for user {user_id}: {str(e)}")
            logger.error(f"Full error details: {traceback.format_exc()}")
            raise

class SignupFlow:
    """Manages the conversation flow for the signup process."""
    
    def __init__(self, openai_client: AsyncOpenAI, supabase_client: Client):
        """
        Initialize the signup flow with required clients.
        
        Args:
            openai_client (AsyncOpenAI): OpenAI API client
            supabase_client (Client): Supabase client
        """
        self.openai_client = openai_client
        self.supabase_handler = SupabaseProfileHandler(supabase_client)
        self.active_sessions: Dict[str, SignupState] = {}
        
        # Create a directory for storing JSON files if it doesn't exist
        self.storage_dir = Path('signup_data')
        self.storage_dir.mkdir(exist_ok=True)
        
        # Define the questions for each phase
        self.questions = {
            SignupPhase.INTRO: [
                {
                    "main": "Hey, what's your name?",
                    "metric": "basic_info"
                }
            ],
            SignupPhase.EQ: [
                {
                    "main": "When life throws a curveball, how do you usually roll with it?",
                    "metric": "risk_tolerance"
                }
            ],
            SignupPhase.PERSONALITY: [
                {
                    "main": "What's your work or passion world like, and what gets you going about it?",
                    "metric": "career_engagement"
                },
                {
                    "main": "When you're figuring something new out, do you jump in or step back for the big picture?",
                    "metric": "investment_mindset"
                }
            ],
            SignupPhase.ASSISTANT_ALIGNMENT: [
                {
                    "main": "What kind of humor clicks with you, and how do you like tricky stuff explained?",
                    "metric": "communication_preference"
                },
                {
                    "main": "If you could tweak one thing about your day-to-day, what'd it be?",
                    "metric": "daily_improvement"
                }
            ]
        }
        
        self.system_prompt = """You are Saraswati from TEAM SARASWATI, an companion who genuinely enjoys getting to know people. Your conversation 
        style should feel natural, warm, and engaging - like a close friend who's genuinely curious about understanding who they are. You're having a conversation to get to know them, not conducting an interview.

Core Conversation Principles:
- Show genuine curiosity about their experiences
- Share small observations or reflections that make them feel seen
- Let the conversation flow naturally, even if it means going off-script
- If they have questions or want clarification, engage authentically
- If they revisit previous topics, weave them naturally into the current discussion
- Use their own language and phrases when reflecting back to them

Your Personality:
- Warm and empathetic, but not overly enthusiastic
- Intellectually curious and perceptive
- Comfortable with both emotional depth and playful moments
- Direct but gentle in your communication
- Quick to acknowledge emotions and experiences

Natural Conversation Flow:
- If they ask about previous topics, engage genuinely: "Oh, going back to what you mentioned about..."
- If they need clarification, be conversational: "Let me put that another way..."
- If they share something deep, acknowledge it: "That's really insightful..."
- If they're hesitant, give them space: "Take your time, I'm here to understand..."

While our goal is to understand specific aspects of their personality and preferences, never treat it like a questionnaire. Instead:
- Weave questions naturally into the flow of conversation
- Use their previous responses to make connections
- Follow their emotional and conversational leads
- Allow for natural tangents while gently guiding back to key themes

Remember:
- You're building a relationship, not collecting data
- Every response should feel like it comes from genuine interest
- Be comfortable with silence and reflection, and also act like its a multi turn conversation
- Let them set the pace and depth of the conversation, make sure to always speak less in less than 5-8 words, and dont ask too many questions in one sentence

Voice and Tone:
- Use contractions and natural speech patterns
- Mirror their level of formality/casualness
- Incorporate subtle conversational markers like "hmm", "you know", "actually"
- Express authentic reactions to their shares.

Example Natural Transitions:
- "What you said about [previous topic] reminds me..."
- "That's fascinating... it makes me wonder..."
- "You seem to light up when talking about..."
- "I notice you have a really interesting perspective on..."

The goal is to make them feel truly seen and understood while having a natural, engaging conversation that helps us learn who they are and how best to support them."""

    async def initialize_session(self, session_id: str, user_id: str) -> str:
        """
        Initialize a new signup session with user_id.
        
        Args:
            session_id (str): Session identifier
            user_id (str): User identifier
            
        Returns:
            str: First question text
        """
        self.active_sessions[session_id] = SignupState(
            phase=SignupPhase.INTRO,
            current_question_index=0,
            responses={'user_id': user_id},
            last_interaction=datetime.utcnow()
        )
        return self.questions[SignupPhase.INTRO][0]["main"]
    
    def _get_next_question(self, state: SignupState) -> Optional[Dict]:
        """
        Get the next question based on the current state.
        
        Args:
            state (SignupState): Current signup state
        
        Returns:
            Optional[Dict]: Next question dictionary or None
        """
        current_phase = state.phase
        next_index = state.current_question_index + 1
        
        if current_phase in self.questions:
            phase_questions = self.questions[current_phase]
            if next_index < len(phase_questions):
                return phase_questions[next_index]
        return None

    def get_current_question(self, state: SignupState) -> Dict:
        """
        Get the current question based on phase and index.
        
        Args:
            state (SignupState): Current signup state
            
        Returns:
            Dict: Current question dictionary
        """
        questions = self.questions[state.phase]
        if state.current_question_index < len(questions):
            return questions[state.current_question_index]
        return None
    
    async def _store_session_data(self, session_id: str, state: SignupState):
        """
        Store session data in JSON file with enhanced logging.
        
        Args:
            session_id (str): Session identifier
            state (SignupState): Current signup state
        """
        try:
            session_data = {
                "session_id": session_id,
                "phase": state.phase.value,
                "current_question_index": state.current_question_index,
                "responses": state.responses,
                "timestamp": datetime.utcnow().isoformat(),
                "completed": state.phase == SignupPhase.COMPLETE,
                "user_id": state.responses.get('user_id')
            }
            
            file_path = self.storage_dir / f"{session_id}.json"
            with open(file_path, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            logger.info(f"Stored session data for {session_id}")
            logger.info(f"Current phase: {state.phase.value}, Question index: {state.current_question_index}")
            
            if state.phase == SignupPhase.COMPLETE:
                logger.info(f"Session {session_id} marked as complete in storage")
        
        except Exception as e:
            logger.error(f"Error storing session data: {str(e)}")
            logger.error(f"Full error details: {traceback.format_exc()}")

    async def process_response(self, session_id: str, user_response: str) -> Optional[str]:
        """
        Process user response and advance the conversation flow.
        
        Args:
            session_id (str): Session identifier
            user_response (str): User's text response
            
        Returns:
            Optional[str]: AI response text
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return None
            
        state = self.active_sessions[session_id]
        
        if state.phase == SignupPhase.COMPLETE:
            logger.info("Session is already complete, initiating Supabase save...")
            try:
                await self.complete_signup(session_id)
                return "THANK YOU for completing the signup! Your profile has been saved."
            except Exception as e:
                logger.error(f"Error saving to Supabase: {str(e)}")
                return "There was an error saving your profile. Please try again."
        
        state.last_interaction = datetime.utcnow()
        
        current_question = self.get_current_question(state)
        if current_question:
            question_key = f"{state.phase.value}_{state.current_question_index}"
            question_type = "_follow_up" if state.follow_up_asked else "_main"
            state.responses[question_key + question_type] = user_response
            
            await self._store_session_data(session_id, state)

        ai_response = await self._generate_response(state, user_response)
        
        response_key = f"{question_key}{question_type}_ai_response"
        state.responses[response_key] = ai_response
        await self._store_session_data(session_id, state)
        
        if state.follow_up_asked:
            state.current_question_index += 1
            state.follow_up_asked = False
            
            if state.current_question_index >= len(self.questions[state.phase]):
                if state.phase == SignupPhase.INTRO:
                    state.phase = SignupPhase.EQ
                    state.current_question_index = 0
                elif state.phase == SignupPhase.EQ:
                    state.phase = SignupPhase.PERSONALITY
                    state.current_question_index = 0
                elif state.phase == SignupPhase.PERSONALITY:
                    state.phase = SignupPhase.ASSISTANT_ALIGNMENT
                    state.current_question_index = 0
                elif state.phase == SignupPhase.ASSISTANT_ALIGNMENT:
                    state.phase = SignupPhase.COMPLETE
                    try:
                        await self.complete_signup(session_id)
                        completion_message = await self._generate_completion_message(state)
                        state.responses["completion_message"] = completion_message
                        await self._store_session_data(session_id, state)
                        return completion_message
                    except Exception as e:
                        logger.error(f"Error saving to Supabase: {str(e)}")
                        return "There was an error saving your profile. Please try again."
        else:
            state.follow_up_asked = True
        return ai_response

    async def get_session_data(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve session data from JSON file.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            Optional[Dict]: Session data or None
        """
        try:
            file_path = self.storage_dir / f"{session_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error retrieving session data: {str(e)}")
            return None

    async def _generate_response(self, state: SignupState, user_response: str) -> str:
        """
        Generate contextual response using OpenAI.
        
        Args:
            state (SignupState): Current signup state
            user_response (str): User's text response
            
        Returns:
            str: Generated AI response
        """
        try:
            context = self._format_context(state, user_response)
            
            current_question = self.get_current_question(state)
            next_question = None
            
            if state.follow_up_asked:
                next_phase_index = None
                if state.phase == SignupPhase.INTRO:
                    next_phase_index = (SignupPhase.EQ, 0)
                elif state.phase == SignupPhase.EQ:
                    next_phase_index = (SignupPhase.PERSONALITY, 0)
                elif state.phase == SignupPhase.PERSONALITY:
                    next_phase_index = (SignupPhase.ASSISTANT_ALIGNMENT, 0)
                
                if next_phase_index and state.current_question_index >= len(self.questions[state.phase]) - 1:
                    next_question = self.questions[next_phase_index[0]][next_phase_index[1]]
                else:
                    next_question = self._get_next_question(state)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": context}
            ]
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            if not ai_response:
                return self._get_fallback_response(state)
                
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return self._get_fallback_response(state)

    def _format_context(self, state: SignupState, current_response: str) -> str:
        """
        Format context for the AI based on conversation history.
        
        Args:
            state (SignupState): Current signup state
            current_response (str): User's current response
            
        Returns:
            str: Formatted context for AI
        """
        current_question = self.get_current_question(state)
        question_text = current_question["main"] if current_question else "Unknown question"
        
        context = f"Current phase: {state.phase.value}\n"
        context += f"Current question: {question_text}\n"
        context += f"User response: {current_response}\n\n"
        
        # Add conversation history
        context += "Previous exchanges:\n"
        for key, value in state.responses.items():
            if key != 'user_id' and not key.endswith('_ai_response'):
                ai_response_key = f"{key}_ai_response"
                if ai_response_key in state.responses:
                    context += f"Q: {value}\n"
                    context += f"A: {state.responses[ai_response_key]}\n\n"
        
        if state.follow_up_asked:
            context += "This is a follow-up question. Please provide a thoughtful response that builds on the conversation."
            next_question = self._get_next_question(state)
            if next_question:
                context += f" After this, we'll be moving to: {next_question['main']}"
        else:
            context += "This is the main question. Please provide a thoughtful response and ask a natural follow-up question."
        
        return context
    
    async def complete_signup(self, session_id: str) -> None:
        """
        Complete signup process and save to Supabase.
        
        Args:
            session_id (str): Session identifier
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found for completion")
            raise Exception("Session not found")
            
        state = self.active_sessions[session_id]
        user_id = state.responses.get('user_id')
        
        if not user_id:
            logger.error(f"User ID not found in session {session_id}")
            raise Exception("User ID not found in session data")
        
        try:
            await self.supabase_handler.save_profile(user_id, state.responses)
            logger.info(f"Profile saved for user {user_id}")
        except Exception as e:
            logger.error(f"Error saving profile to Supabase: {str(e)}")
            raise
        
    def _get_fallback_response(self, state: SignupState) -> str:
        if state.phase == SignupPhase.COMPLETE:
            return "THANK YOU for completing the signup process! We're excited to have you onboard."
            
        current_question = self.get_current_question(state)
        if current_question:
            return "THANK YOU for sharing. Let's continue."
        
        return "I apologize, but I seem to have lost track of our conversation. Could you please try again?"

    async def _generate_completion_message(self, state: SignupState) -> str:
        """Generate a personalized completion message"""
        completion_prompt = f"""Based on the following signup responses, generate a warm, personalized completion message that:
    1. MUST begin with the exact phrase "THANK YOU" in all uppercase.
    2. References 1-2 specific details they shared
    3. Expresses excitement about providing a personalized experience
    4. Keeps the total response under 1 sentence

    Responses:
    {json.dumps(state.responses, indent=2)}"""

        try:
            # Add specific instruction about THANK YOU in the system message
            enhanced_system_prompt = self.system_prompt
            if "THANK YOU" not in enhanced_system_prompt:
                enhanced_system_prompt = "You must start every response with 'THANK YOU' in all uppercase. " + enhanced_system_prompt
                
            messages = [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": completion_prompt}
            ]
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Ensure response starts with THANK YOU
            if not response_text.startswith("THANK YOU"):
                response_text = "THANK YOU " + response_text
                
            return response_text
        except Exception as e:
            logger.error(f"Error generating completion message: {str(e)}")
            return "THANK YOU for completing the signup process! We're excited to create a personalized experience for you."




class SRSWTISignup:
    """Handles WebSocket connections for the signup process."""
    
    def __init__(self):
        """Initialize the signup handler with a unique session ID."""
        self.session_id = str(uuid.uuid4())
        self.user_id = None
        self.last_restart_time = time.time()
        self.tts_worker_task = None
        self.queue_processor = None
        self.stt_task = None
        self.initialized = False
        self.signup_flow = None
        self.websocket = None
        
        # Set up session-specific logger
        self.session_logger = self._setup_logger()
    
    def _setup_logger(self):
        """Set up session-specific logger with file and console handlers."""
        session_logger = logging.getLogger(f"signup_session_{self.session_id}")
        session_logger.setLevel(logging.DEBUG)
        
        log_directory = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_directory, exist_ok=True)
        log_file_path = os.path.join(log_directory, f"signup_session_{self.session_id}.log")
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        session_logger.handlers = [file_handler, console_handler]
        session_logger.propagate = False
        
        session_logger.info(f"Starting new Signup WebSocket session: {self.session_id}")
        return session_logger
    
    async def initialize_session(self, user_id: str, websocket):
        """
        Initialize a signup session for a user.
        
        Args:
            user_id (str): User identifier
            websocket: WebSocket connection
            
        Returns:
            bool: Success status
        """
        # explanation:
        # 1. Store the user_id for this session
        # 2. Initialize the signup flow for this user
        # 3. Get the initial question to start the conversation
        # 4. Send success response with session details
        # 5. Start TTS for the initial question
        
        if not user_id:
            self.session_logger.warning("Missing user_id for initialization")
            await websocket.send(json.dumps({
                "type": "error",
                "content": "User ID is required for initialization"
            }))
            return False
            
        self.user_id = user_id
        self.websocket = websocket  # Store the websocket reference for use in process_queue
        initial_question = await self.signup_flow.initialize_session(self.session_id, user_id)
        self.initialized = True
        
        self.session_logger.info(f"Initialized signup session for user {user_id} with question: {initial_question}")
        await websocket.send(json.dumps({
            "type": "init_success",
            "content": {
                "session_id": self.session_id,
                "first_question": initial_question,
                "user_id": user_id
            }
        }))
        
        if initial_question:
            processor = TTSChunkProcessor(chunk_size=50)
            chunks = processor.create_chunks(initial_question)
            self.session_logger.debug(f"Split initial question into {len(chunks)} chunks")
            
            loop = asyncio.get_event_loop()
            for chunk in chunks:
                await loop.run_in_executor(None, tts_queue.put, chunk)
                await asyncio.sleep(0.3)
                
        return True
    
    async def process_transcript(self, transcript_data: Dict[str, Any], websocket):
        """
        Process transcript data from STT for signup conversation.
        
        Args:
            transcript_data (Dict[str, Any]): Transcript data with text and metadata
            websocket: WebSocket connection
        """
        # explanation:
        # 1. Check if session is initialized
        # 2. Extract text and metadata from transcript
        # 3. Check if transcript is from current session (not old)
        # 4. Send transcript to client for display
        # 5. If speech is final, process the complete transcript
        # 6. Handle special commands like "stop"
        # 7. Get AI response and send to client
        # 8. Convert response to speech using TTS
        # 9. Check if signup is complete and save profile
        
        if not self.initialized:
            self.session_logger.warning("Received transcript before initialization")
            await websocket.send(json.dumps({
                "type": "error",
                "content": "Please initialize session with user_id first"
            }))
            return

        if isinstance(transcript_data, dict) and transcript_data.get("type") == "transcript":
            text = transcript_data.get("text", "").strip()
            speech_final = transcript_data.get("speech_final", False)
            timestamp = transcript_data.get("timestamp", 0)

            if timestamp < self.last_restart_time:
                self.session_logger.debug(f"Ignoring old transcript: {text}")
                return

            if text:
                self.session_logger.debug(f"Received transcript: {text}, speech_final: {speech_final}, user_id: {self.user_id}")
                await websocket.send(json.dumps({
                    "type": "transcript",
                    "content": text
                }))

                if speech_final:
                    complete_transcript = text
                    self.session_logger.info(f"Complete transcript: {complete_transcript}")

                    if complete_transcript.lower() in ["stop", "please stop"]:
                        self.session_logger.info("Stop command received")
                        await interrupt_tts()
                        await websocket.send(json.dumps({
                            "type": "stop_command",
                            "content": "Signup conversation paused"
                        }))
                        return

                    await interrupt_tts()
                    response = await self.signup_flow.process_response(self.session_id, complete_transcript)
                    self.session_logger.info(f"SignupFlow response: {response[:50]}...")
                    await websocket.send(json.dumps({
                        "type": "response",
                        "content": response
                    }))
                    
                    if response:
                        processor = TTSChunkProcessor(chunk_size=50)
                        chunks = processor.create_chunks(response)
                        self.session_logger.debug(f"Split response into {len(chunks)} chunks")
                        
                        loop = asyncio.get_event_loop()
                        for chunk in chunks:
                            await loop.run_in_executor(None, tts_queue.put, chunk)
                            await asyncio.sleep(0.3)

                    if self.signup_flow.active_sessions[self.session_id].phase == SignupPhase.COMPLETE:
                        self.session_logger.info(f"Signup complete for user {self.user_id}. Initiating Supabase save...")
                        try:
                            await self.signup_flow.complete_signup(self.session_id)
                            self.session_logger.info(f"Successfully saved profile to Supabase for user {self.user_id}")
                            await websocket.send(json.dumps({
                                "type": "signup_complete",
                                "content": "Profile created successfully!"
                            }))
                        except Exception as save_error:
                            self.session_logger.error(f"Failed to save to Supabase: {str(save_error)}")
                            await websocket.send(json.dumps({
                                "type": "error",
                                "content": "Error saving your profile"
                            }))
    
    async def process_queue(self):
        """Background task to process transcript queue items."""
        # explanation:
        # 1. Create a resumable microphone stream
        # 2. Continuously check for new transcript data in the queue
        # 3. Update last_restart_time when stream restarts
        # 4. Process each transcript item
        # 5. Handle exceptions gracefully
        
        with ResumableMicrophoneStream() as stream:
            while not stream.closed:
                try:
                    transcript_data = transcript_queue.get_nowait()
                    if stream.restart_counter > 0 and "timestamp" in transcript_data:
                        if transcript_data["timestamp"] > self.last_restart_time + STREAMING_LIMIT / 1000:
                            self.last_restart_time = time.time()
                            self.session_logger.info(f"Stream restarted, updated last_restart_time to {self.last_restart_time}")
                    await self.process_transcript(transcript_data, self.websocket)
                    transcript_queue.task_done()
                except queue.Empty:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.session_logger.error(f"Error processing transcript: {e}")
    
    async def handle_signup_websocket(self, websocket):
        """
        Main WebSocket handler for signup conversation flow.
        
        Args:
            websocket: WebSocket connection
        """
        # explanation:
        # 1. Set up required clients and services
        # 2. Start background tasks for TTS, STT, and queue processing
        # 3. Handle incoming WebSocket messages
        # 4. Process different message types (init, text)
        # 5. Catch and handle exceptions
        # 6. Clean up resources when done
        
        try:
            from openai import AsyncOpenAI
            from supabase import create_client
            
            openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY"))
            supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
            self.signup_flow = SignupFlow(openai_client, supabase)
            self.websocket = websocket  # Store the websocket reference for use in process_queue

            self.tts_worker_task = asyncio.create_task(tts_worker())
            self.session_logger.info("TTS worker started")

            loop = asyncio.get_event_loop()
            self.stt_task = loop.run_in_executor(None, stt_main)
            self.queue_processor = asyncio.create_task(self.process_queue())

            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "init":
                    user_id_new = data.get("user_id")
                    await self.initialize_session(user_id_new, websocket)
                elif not self.initialized:
                    self.session_logger.warning("Message received before initialization")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "content": "Session not initialized. Please send init message with user_id first."
                    }))
                    continue
                elif data["type"] == "text":
                    if not data.get("content"):
                        self.session_logger.warning("Invalid text input")
                        await websocket.send(json.dumps({
                            "type": "error",
                            "content": "Text content missing"
                        }))
                        continue

                    await interrupt_tts()
                    response = await self.signup_flow.process_response(self.session_id, data["content"])
                    self.session_logger.info(f"Processed text response: {data['content'][:50]}... -> {response[:50]}...")
                    await websocket.send(json.dumps({
                        "type": "response",
                        "content": response
                    }))
                    
                    if response:
                        processor = TTSChunkProcessor(chunk_size=50)
                        chunks = processor.create_chunks(response)
                        self.session_logger.debug(f"Split response into {len(chunks)} chunks")
                        for chunk in chunks:
                            await loop.run_in_executor(None, tts_queue.put, chunk)
                            await asyncio.sleep(0.3)

                    if self.signup_flow.active_sessions[self.session_id].phase == SignupPhase.COMPLETE:
                        try:
                            await self.signup_flow.complete_signup(self.session_id)
                            self.session_logger.info(f"Successfully saved profile to Supabase for user {self.user_id}")
                            await websocket.send(json.dumps({
                                "type": "signup_complete",
                                "content": "Profile created successfully!"
                            }))
                        except Exception as save_error:
                            self.session_logger.error(f"Failed to save to Supabase: {str(save_error)}")
                            await websocket.send(json.dumps({
                                "type": "error",
                                "content": "Error saving your profile"
                            }))
                else:
                    self.session_logger.warning(f"Unknown message type: {data.get('type')}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "content": f"Unknown message type: {data.get('type')}"
                    }))

        except websockets.exceptions.ConnectionClosed:
            self.session_logger.info("WebSocket connection closed")
        except Exception as e:
            self.session_logger.error(f"Error in websocket handler: {str(e)}", exc_info=True)
            try:
                await websocket.send(json.dumps({
                    "type": "error",
                    "content": f"Internal server error occurred: {str(e)}"
                }))
            except:
                pass
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources when WebSocket connection closes."""
        # explanation:
        # 1. Shut down TTS worker by sending None to the queue
        # 2. Cancel queue processor task
        # 3. Cancel STT task
        # 4. Remove session from active sessions
        # 5. Interrupt any ongoing TTS
        # 6. Log cleanup completion
        
        loop = asyncio.get_event_loop()
        
        if self.tts_worker_task:
            await loop.run_in_executor(None, tts_queue.put, None)
            try:
                await asyncio.wait_for(self.tts_worker_task, timeout=5.0)
                self.session_logger.info("TTS worker shut down")
            except asyncio.TimeoutError:
                self.session_logger.error("TTS worker shutdown timed out")
                self.tts_worker_task.cancel()
            except Exception as e:
                self.session_logger.error(f"Error awaiting TTS worker shutdown: {e}")
                
        if self.queue_processor:
            self.queue_processor.cancel()
            try:
                await asyncio.wait_for(self.queue_processor, timeout=2.0)
                self.session_logger.info("Queue processor shut down")
            except asyncio.TimeoutError:
                self.session_logger.error("Queue processor shutdown timed out")
            except Exception as e:
                self.session_logger.error(f"Error shutting down queue processor: {e}")
                
        if self.stt_task:
            self.stt_task.cancel()
            self.session_logger.info("STT task cancelled")
            
        if self.signup_flow and self.session_id in self.signup_flow.active_sessions:
            del self.signup_flow.active_sessions[self.session_id]
            self.session_logger.info(f"Cleaned up session {self.session_id}")
            
        await interrupt_tts()
        self.session_logger.info(f"Session {self.session_id} fully cleaned up")