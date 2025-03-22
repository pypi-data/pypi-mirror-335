# EXPLANATION# - This file contains the SRSWTIHome class for handling home page WebSocket interactions
# - HomeLLM is used for route suggestions and conversational responses in JSON format
# - TTS functionality is also integrated for speech output
# - Session management and transcript processing are handled like other WebSocket interfaces

import asyncio
import json
import logging
import uuid
import os
import random
import time
from typing import Dict, Any, Optional, List
import queue
from .llm import HomeLLM
from .utils import TTSChunkProcessor, tts_queue, interrupt_tts, tts_worker
from .models import SRSWTIResponse
from .helpers.stt import main as stt_main, ResumableMicrophoneStream
from .helpers.shared import transcript_queue, STREAMING_LIMIT

# Configure logger
logger = logging.getLogger(__name__)

class SRSWTIHome:
    """Handles WebSocket connections for home page interactions with route suggestions."""
    
    def __init__(self):
        """Initialize the home handler with a unique session ID."""
        self.session_id = str(uuid.uuid4())
        self.home_llm = HomeLLM()
        self.transcript_pieces = []
        self.stt_task = None
        self.tts_worker_task = None
        self.queue_processor = None
        self.last_restart_time = time.time()
        self.response_ready = asyncio.Event()
        self.websocket = None  # Initialize websocket attribute
        
        # Set up session-specific logger
        self.session_logger = self._setup_logger()
    
    def _setup_logger(self):
        """Set up session-specific logger with file and console handlers."""
        session_logger = logging.getLogger(f"home_session_{self.session_id}")
        session_logger.setLevel(logging.DEBUG)
        
        log_directory = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_directory, exist_ok=True)
        log_file_path = os.path.join(log_directory, f"home_session_{self.session_id}.log")
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        session_logger.handlers = [file_handler, console_handler]
        session_logger.propagate = False
        
        session_logger.info(f"Starting new Home WebSocket session: {self.session_id}")
        return session_logger
    
    async def process_transcript(self):
        """Background task to process speech transcript queue."""
        with ResumableMicrophoneStream() as stream:
            while not stream.closed:
                try:
                    transcript_data = transcript_queue.get_nowait()
                    if stream.restart_counter > 0 and "timestamp" in transcript_data:
                        if transcript_data["timestamp"] > self.last_restart_time + STREAMING_LIMIT / 1000:
                            self.last_restart_time = time.time()
                            self.session_logger.info(f"Stream restarted, updated last_restart_time to {self.last_restart_time}")

                    if isinstance(transcript_data, dict) and transcript_data.get("type") == "transcript":
                        text = transcript_data.get("text", "").strip()
                        speech_final = transcript_data.get("speech_final", False)
                        timestamp = transcript_data.get("timestamp", 0)

                        if timestamp < self.last_restart_time:
                            self.session_logger.debug(f"Ignoring old transcript: {text}")
                            continue

                        if text:
                            self.session_logger.info(f"Transcribed text: {text}, speech_final: {speech_final}")
                            await self.websocket.send(json.dumps({
                                "type": "transcript",
                                "content": text,
                                "speech_final": speech_final
                            }))

                            self.transcript_pieces.append({'text': text, 'start': timestamp})

                            if speech_final:
                                complete_transcript = text
                                self.session_logger.info(f"Complete transcript: {complete_transcript}")

                                if complete_transcript.strip().upper() == "STOP":
                                    self.session_logger.info(f"STOP command received in home session {self.session_id}")
                                    await interrupt_tts()
                                    await self.websocket.send(json.dumps({
                                        "type": "stop_command",
                                        "content": "Conversation paused"
                                    }))
                                    self.transcript_pieces.clear()
                                    return

                                await interrupt_tts()
                                filler_texts = ["uh", "uhhh", "hmmmm", "ummm", "ohh...", "wow!", "okay!!!", "hmm..."]
                                num_fillers = random.randint(1, 2)
                                selected_fillers = random.sample(filler_texts, num_fillers)
                                loop = asyncio.get_event_loop()
                                for filler in selected_fillers:
                                    await loop.run_in_executor(None, tts_queue.put, filler)
                                    self.session_logger.info(f"Queued filler TTS: {filler}")
                                    await asyncio.sleep(0.3)
                                    if self.response_ready.is_set():
                                        break

                                response_json = None
                                async def process_response():
                                    nonlocal response_json
                                    response_json = await self.home_llm.home_text_to_text(complete_transcript)
                                    self.response_ready.set()
                                    self.session_logger.info(f"HomeLLM response JSON: {response_json}")
                                    try:
                                        response_data = json.loads(response_json)
                                        tts_text = response_data.get("response", "")
                                        await self.websocket.send(json.dumps({
                                            "type": "home_response",
                                            "content": response_json
                                        }))
                                        if tts_text:
                                            await loop.run_in_executor(None, tts_queue.put, tts_text)
                                            self.session_logger.info(f"Queued TTS for response: {tts_text[:50]}...")
                                    except json.JSONDecodeError as je:
                                        self.session_logger.error(f"Invalid JSON from home_text_to_text: {response_json}", exc_info=True)
                                        await self.websocket.send(json.dumps({
                                            "type": "error",
                                            "content": f"Invalid response format: {str(je)}"
                                        }))

                                asyncio.create_task(process_response())
                                self.transcript_pieces.clear()
                except queue.Empty:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.session_logger.error(f"Error processing transcript: {str(e)}", exc_info=True)
    
    async def process_text_input(self, user_input: str, websocket):
        """
        Process text input directly from WebSocket message.
        
        Args:
            user_input (str): User input text
            websocket: WebSocket connection
        """
        self.session_logger.info(f"Processing user text input: {user_input}")
        await interrupt_tts()
        filler_texts = ["uh", "uhhh", "hmmmm", "ummm", "ohh...", "wow!", "okay!!!", "hmm..."]
        num_fillers = random.randint(1, 2)
        selected_fillers = random.sample(filler_texts, num_fillers)
        loop = asyncio.get_event_loop()
        for filler in selected_fillers:
            await loop.run_in_executor(None, tts_queue.put, filler)
            self.session_logger.info(f"Queued filler TTS: {filler}")
            await asyncio.sleep(0.3)
            if self.response_ready.is_set():
                break

        response_json = None
        
        async def process_response():
            nonlocal response_json
            response_json = await self.home_llm.home_text_to_text(user_input)
            self.response_ready.set()
            self.session_logger.info(f"HomeLLM response JSON: {response_json}")
            try:
                response_data = json.loads(response_json)
                tts_text = response_data.get("response", "")
                await websocket.send(json.dumps({
                    "type": "home_response",
                    "content": response_json
                }))
                if tts_text:
                    await loop.run_in_executor(None, tts_queue.put, tts_text)
                    self.session_logger.info(f"Queued TTS for response: {tts_text[:50]}...")
            except json.JSONDecodeError as je:
                self.session_logger.error(f"Invalid JSON from home_text_to_text: {response_json}", exc_info=True)
                await websocket.send(json.dumps({
                    "type": "error",
                    "content": f"Invalid response format: {str(je)}"
                }))

        asyncio.create_task(process_response())
    
    async def send_greeting(self, websocket):
        """
        Send initial greeting response to WebSocket.
        
        Args:
            websocket: WebSocket connection
        """
        initial_response = SRSWTIResponse(
            response="Hi, I'm Saraswati! What's up?",
            suggested_route=None,
            confidence=0.0
        ).to_json()
        
        await websocket.send(json.dumps({
            "type": "home_response",
            "content": initial_response
        }))
        
        self.session_logger.info(f"Sent initial greeting: {initial_response}")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, tts_queue.put, "Hi, I'm Saraswati! What's up?")
    
    async def handle_home_websocket(self, websocket):
        """
        Main WebSocket handler for home page interactions.
        
        Args:
            websocket: WebSocket connection
        """
        try:
            # Store websocket in instance
            self.websocket = websocket
            
            # Send initial greeting
            await self.send_greeting(websocket)
            
            # Start background tasks
            loop = asyncio.get_event_loop()
            self.stt_task = loop.run_in_executor(None, stt_main)
            self.session_logger.info("STT task started")

            self.tts_worker_task = asyncio.create_task(tts_worker())
            self.session_logger.info("TTS worker started")

            self.queue_processor = asyncio.create_task(self.process_transcript())
            
            # Process WebSocket messages
            async for message in websocket:
                data = json.loads(message)
                message_type = data.get("type")
                self.session_logger.debug(f"Received message: {message}")

                if message_type == "text":
                    user_input = data.get("content")
                    if not user_input:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "content": "Text input is required"
                        }))
                        continue
                    self.response_ready.clear()
                    await self.process_text_input(user_input, websocket)

                elif message_type == "init":
                    self.session_logger.info("Received init message (no user_id or canvas_id updates needed for home)")
                    await websocket.send(json.dumps({
                        "type": "init_success",
                        "content": "Home session initialized successfully"
                    }))
                    await loop.run_in_executor(None, tts_queue.put, "Hi, I'm Saraswati! What's up?")

                else:
                    self.session_logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "content": f"Unknown message type: {message_type}"
                    }))
                    
        except Exception as e:
            self.session_logger.error(f"Error in home websocket handler: {str(e)}", exc_info=True)
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
        self.session_logger.info("Cleaning up resources...")
        
        # Cancel queue processor task
        if self.queue_processor and not self.queue_processor.done():
            self.queue_processor.cancel()
            try:
                await self.queue_processor
            except asyncio.CancelledError:
                self.session_logger.info("Queue processor task cancelled")
        
        # Interrupt TTS
        await interrupt_tts()
        
        # Clean up TTS worker
        if self.tts_worker_task and not self.tts_worker_task.done():
            # Put a poison pill in the queue
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, tts_queue.put, None)
            try:
                await self.tts_worker_task
            except Exception as e:
                self.session_logger.error(f"Error waiting for TTS worker to finish: {str(e)}")
        
        # Cancel STT task
        if self.stt_task and not self.stt_task.done():
            self.stt_task.cancel()
            try:
                await self.stt_task
            except (asyncio.CancelledError, Exception) as e:
                self.session_logger.info(f"STT task cancelled: {str(e)}")
        
        self.session_logger.info(f"Session {self.session_id} cleanup completed") 