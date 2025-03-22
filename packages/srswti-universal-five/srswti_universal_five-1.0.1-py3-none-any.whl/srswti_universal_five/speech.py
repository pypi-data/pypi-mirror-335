# EXPLANATION# - This file contains the SRSWTISpeech class that handles the main WebSocket interface
# - It processes transcripts from speech-to-text, manages LLM interactions, and generates responses
# - It integrates with LLM, TTS, and search functionality
# - It needs to handle real-time communication, session management, and cleanup

import asyncio
import json
import logging
import uuid
import queue
import time, os
from typing import Optional, Dict, Any

import websockets

from .llm import LLM
from .utils import (
    is_search_query, 
    is_deep_search_query, 
    TTSChunkProcessor, 
    tts_queue, 
    interrupt_tts, 
    generate_quick_filler, 
    process_with_llm
)
from .helpers.redis_server import redis_manager
from .helpers.chat_history_manager import OptimizedChatHistoryManager
from .helpers.quick_one import SRSWTIQuickOne
from .helpers.stt import main as stt_main, ResumableMicrophoneStream
from .helpers.shared import transcript_queue, STREAMING_LIMIT
from .helpers.response_gen_v2 import ResponseGenerator
from .helpers.node_manager import NodeManager

# Configure logger
logger = logging.getLogger(__name__)

class SRSWTISpeech:
    """Handles WebSocket connections for speech processing, LLM interaction, and response generation."""
    
    def __init__(self):
        """Initialize the speech handler with a unique session ID."""
        self.session_id = str(uuid.uuid4())
        self.user_id = None
        self.canvas_id = None
        self.mode = None
        self.last_restart_time = time.time()
        self.model_name = None
        self.llm = None
        self.tts_worker_task = None
        self.queue_processor = None
        self.stt_task = None
        self.initialized = False
        self.quick_search = SRSWTIQuickOne()
        
        # Set up session-specific logger
        self.session_logger = self._setup_logger()

    async def process_input(self, transcription: str, websocket):
        """
        Process user input with node or conversation logic.

        Args:
            transcription (str): User input text from STT
            websocket: WebSocket connection
        """
        try:
            import re
            response_generator = ResponseGenerator()
            node_manager = NodeManager()
            transcription_lower = transcription.lower()

            selected_nodes = await node_manager.get_selected_nodes(self.canvas_id, self.user_id)
            node_pattern = r'(?:node|parent|group)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine)(?:\s*(?:point|dot)\s*\d+)*'
            has_node_reference = bool(re.search(node_pattern, transcription_lower))
            is_node_processing = selected_nodes or has_node_reference

            if is_node_processing:
                response = await response_generator.generate_response(
                    user_input=transcription,
                    canvas_id=self.canvas_id,
                    user_id=self.user_id,
                    mode="extreme"
                )
                await self.llm.chat_manager.manage_chat_history(self.canvas_id, self.user_id, {"role": "user", "content": transcription})
                await self.llm.chat_manager.manage_chat_history(self.canvas_id, self.user_id, {"role": "assistant", "content": response.get('content', {}).get('detailed', '')})
                response["is_node_processing"] = True
                return response
            else:
                response = await self.llm.text_to_text(transcription, self.canvas_id, self.user_id)
                return {
                    "mode": "extreme",
                    "content": {"detailed": response, "speech": response},
                    "nodes": [],
                    "search_required": False,
                    "search_reasoning": "Direct conversation mode",
                    "flow_path": "direct"
                }
        except Exception as e:
            self.session_logger.error(f"Error in process_input: {str(e)}")
            return {
                "mode": "extreme",
                "content": {"detailed": f"Error: {str(e)}", "speech": "I encountered an error."},
                "nodes": [],
                "search_required": False,
                "search_reasoning": f"Error occurred: {str(e)}",
                "flow_path": "error",
                "is_node_processing": False
            }
            
    def _setup_logger(self):
        """Set up session-specific logger with file and console handlers."""
        import os
        
        session_logger = logging.getLogger(f"srswti_test_{self.session_id}")
        session_logger.setLevel(logging.DEBUG)
        
        log_directory = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_directory, exist_ok=True)
        log_file_path = os.path.join(log_directory, f"srswti_test_{self.session_id}.log")
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        
        session_logger.handlers = [file_handler, console_handler]
        session_logger.propagate = False
        
        session_logger.info(f"Starting new WebSocket session: {self.session_id}")
        return session_logger
    
    async def tts_worker(self):
        """Background worker to handle TTS tasks with callback playback."""
        global tts_stream, _pyaudio_instance
        loop = asyncio.get_event_loop()
        
        # Start the callback stream once
        from .helpers.tts import stream_tts_callback, stream_tts, get_current_stream, _audio_queue
        tts_stream, _pyaudio_instance = stream_tts_callback()
        
        try:
            while True:
                text = await loop.run_in_executor(None, tts_queue.get)
                if text is None:  # Poison pill to stop the worker
                    logger.debug("Received None in tts_queue, stopping worker")
                    break
                    
                logger.debug(f"Processing TTS for text: {text}")
                await interrupt_tts()  # Clear any ongoing playback
                await loop.run_in_executor(None, stream_tts, text)  # Queue audio data
                logger.info("TTS audio queued for playback")
                tts_queue.task_done()
                
        except Exception as e:
            logger.error(f"Error in TTS worker: {e}")
            if not tts_queue.empty():
                tts_queue.task_done()
        finally:
            from .helpers.tts import _audio_queue
            await loop.run_in_executor(None, _audio_queue.put, None)  # Signal stream to stop
            tts_stream.stop_stream()
            tts_stream.close()
            _pyaudio_instance.terminate()
    
    async def initialize_session(self, user_id: str, canvas_id: str, mode: str, model_name: str):
        """
        Initialize a new session with user details and preferences.
        
        Args:
            user_id (str): User identifier
            canvas_id (str): Canvas identifier
            mode (str): Processing mode (normal/extreme)
            model_name (str): LLM model to use (gemini/mini-flash)
        
        Returns:
            bool: Success status
        """
        try:
            # Validate input parameters
            if not all([user_id, canvas_id, mode, model_name]):
                self.session_logger.warning("Missing required initialization parameters")
                return False
                
            if mode not in ["normal", "extreme"]:
                self.session_logger.warning(f"Invalid mode: {mode}")
                return False
                
            if model_name not in ["gemini", "mini-flash"]:
                self.session_logger.warning(f"Invalid model name: {model_name}")
                return False
            
            # Update instance variables
            self.user_id = user_id
            self.canvas_id = canvas_id
            self.mode = mode
            
            # Initialize or update LLM if needed
            if self.llm and model_name != self.model_name:
                await self.llm.cleanup()
                self.llm = None
                
            if not self.llm:
                self.model_name = model_name
                self.llm = LLM(model_name=model_name)
                await self.llm.initialize()
            
            self.initialized = True
            self.session_logger.info(f"Session initialized: user_id={user_id}, canvas_id={canvas_id}, mode={mode}, model={model_name}")
            return True
            
        except Exception as e:
            self.session_logger.error(f"Error initializing session: {str(e)}")
            return False
    
    async def process_transcript(self, transcript_data: Dict[str, Any], websocket):
        """
        Process transcript data from STT and generate responses.
        
        Args:
            transcript_data (Dict[str, Any]): Transcript data with text and metadata
            websocket: WebSocket connection
        """
        if not self.initialized:
            self.session_logger.warning("Received transcript before initialization")
            await websocket.send(json.dumps({
                "type": "error",
                "content": "Please initialize session with user_id, canvas_id, mode, and model_name first"
            }))
            return

        if isinstance(transcript_data, dict) and transcript_data.get("type") == "transcript":
            text = transcript_data.get("text", "").strip()
            speech_final = transcript_data.get("speech_final", False)
            timestamp = transcript_data.get("timestamp", 0)
            
            # Skip old transcripts
            if timestamp < self.last_restart_time:
                self.session_logger.debug(f"Ignoring old transcript: {text}")
                return
            
            if text:
                self.session_logger.debug(f"Received transcript: {text}, speech_final: {speech_final}")
                await websocket.send(json.dumps({
                    "type": "transcript",
                    "content": text
                }))
                
                if speech_final:
                    complete_transcript = text
                    transcript_lower = complete_transcript.lower()
                    self.session_logger.info(f"Complete transcript: {complete_transcript}")
                    
                    # Handle stop command
                    if transcript_lower in ["stop", "please stop"]:
                        self.session_logger.info("Stop command received")
                        await websocket.send(json.dumps({
                            "type": "stop_command",
                            "content": "Conversation paused"
                        }))
                        return
                    
                    # Flag to track if main TTS has started
                    main_tts_started = False
                    
                    # Handle filler generation
                    loop = asyncio.get_event_loop()
                    async def handle_filler():
                        nonlocal main_tts_started
                        try:
                            filler = await generate_quick_filler(complete_transcript)
                            if not main_tts_started:
                                await loop.run_in_executor(None, tts_queue.put, filler)
                                self.session_logger.debug(f"Queued filler TTS: {filler}")
                            else:
                                self.session_logger.debug(f"Discarded filler '{filler}' - main TTS started")
                        except Exception as e:
                            self.session_logger.error(f"Error in filler generation: {str(e)}")
                    
                    filler_task = asyncio.create_task(handle_filler())
                    await interrupt_tts()
                    
                    # Process based on mode
                    if self.mode == "normal":
                        response = await self.llm.text_to_text(complete_transcript, self.canvas_id, self.user_id)
                        self.session_logger.info(f"Normal mode response: {response[:50]}...")
                        await websocket.send(json.dumps({
                            "type": "llm_response",
                            "content": response
                        }))
                        
                        if response:
                            main_tts_started = True
                            processor = TTSChunkProcessor(chunk_size=150)
                            chunks = processor.create_chunks(response)
                            self.session_logger.debug(f"Split response into {len(chunks)} chunks")
                            
                            for chunk in chunks:
                                await loop.run_in_executor(None, tts_queue.put, chunk)
                                await asyncio.sleep(0.1)  # Reduced delay for faster playback
                    else:
                        # Check if this is a search query
                        is_search = is_search_query(complete_transcript) or is_deep_search_query(complete_transcript)
                        
                        if is_search:
                            max_results = 20 if is_deep_search_query(complete_transcript) else 5
                            self.quick_search = SRSWTIQuickOne(max_results=max_results)
                            
                            await websocket.send(json.dumps({
                                "type": "processing_status",
                                "content": "STARTED QUICKONE SEARCH"
                            }))
                            
                            search_response = await self.quick_search(complete_transcript)
                            self.session_logger.info(f"Search response: {search_response[:50]}...")
                            
                            # Update chat history
                            await self.llm.chat_manager.manage_chat_history(self.canvas_id, self.user_id, {"role": "user", "content": complete_transcript})
                            await self.llm.chat_manager.manage_chat_history(self.canvas_id, self.user_id, {"role": "assistant", "content": search_response})
                            
                            await websocket.send(json.dumps({
                                "type": "llm_response",
                                "content": search_response
                            }))
                            
                            if search_response:
                                main_tts_started = True
                                processor = TTSChunkProcessor(chunk_size=50)
                                chunks = processor.create_chunks(search_response)
                                self.session_logger.debug(f"Split search response into {len(chunks)} chunks")
                                
                                for chunk in chunks:
                                    await loop.run_in_executor(None, tts_queue.put, chunk)
                                    await asyncio.sleep(0.1)
                        else:
                            # Process with regular LLM
                            response = await self.llm.text_to_text(complete_transcript, self.canvas_id, self.user_id)
                            self.session_logger.info(f"Extreme mode response: {response[:50]}...")
                            
                            await websocket.send(json.dumps({
                                "type": "llm_response",
                                "content": response
                            }))
                            
                            if response:
                                main_tts_started = True
                                processor = TTSChunkProcessor(chunk_size=50)
                                chunks = processor.create_chunks(response)
                                self.session_logger.debug(f"Split response into {len(chunks)} chunks")
                                
                                for chunk in chunks:
                                    await loop.run_in_executor(None, tts_queue.put, chunk)
                                    await asyncio.sleep(0.1)
    
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
                    await self.process_transcript(transcript_data, None)  # Will need to pass actual websocket in real implementation
                    transcript_queue.task_done()
                except queue.Empty:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.session_logger.error(f"Error processing transcript: {e}")
    
    async def handle_reverse_websocket(self, websocket):
        """
        Main WebSocket handler for speech/text interactions.
        
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
        # Initialize state variables

        self.user_id = None
        self.canvas_id = None
        self.mode = None
        self.last_restart_time = time.time()
        self.model_name = None
        self.llm = None
        self.tts_worker_task = None
        self.queue_processor = None
        self.stt_task = None
        self.initialized = False
        
        try:
            self.tts_worker_task = asyncio.create_task(self.tts_worker())
            self.session_logger.info("TTS worker started")
            
            loop = asyncio.get_event_loop()
            self.stt_task = loop.run_in_executor(None, stt_main)
            
            # Modified to pass the websocket to process_transcript
            async def process_queue_with_websocket():
                with ResumableMicrophoneStream() as stream:
                    while not stream.closed:
                        try:
                            transcript_data = transcript_queue.get_nowait()
                            if stream.restart_counter > 0 and "timestamp" in transcript_data:
                                if transcript_data["timestamp"] > self.last_restart_time + STREAMING_LIMIT / 1000:
                                    self.last_restart_time = time.time()
                                    self.session_logger.info(f"Stream restarted, updated last_restart_time to {self.last_restart_time}")
                            await self.process_transcript(transcript_data, websocket)
                            transcript_queue.task_done()
                        except queue.Empty:
                            await asyncio.sleep(0.1)
                        except Exception as e:
                            self.session_logger.error(f"Error processing transcript: {e}")
            
            self.queue_processor = asyncio.create_task(process_queue_with_websocket())
            
            async for message in websocket:
                data = json.loads(message)
                if not self.initialized and data["type"] != "init":
                    self.session_logger.warning("Message received before initialization")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "content": "Session not initialized. Please send init message with user_id, canvas_id, mode, and model_name first."
                    }))
                    continue

                if data["type"] == "init":
                    # Handle initialization message
                    user_id_new = data.get("user_id")
                    canvas_id_new = data.get("canvas_id")
                    mode_new = data.get("mode")
                    model_name_new = data.get("model_name")
                    
                    # Validate all required parameters are present and valid
                    if not all([user_id_new, canvas_id_new, mode_new, model_name_new]) or \
                       mode_new not in ["normal", "extreme"] or \
                       model_name_new not in ["gemini", "mini-flash"]:
                        self.session_logger.warning("Invalid init parameters")
                        await websocket.send(json.dumps({
                            "type": "error",
                            "content": "Invalid or missing initialization parameters. Required: user_id, canvas_id, mode (normal/extreme), model_name (gemini/mini-flash)"
                        }))
                        continue
                    
                    # Update instance variables with new values
                    self.user_id = user_id_new
                    self.canvas_id = canvas_id_new
                    self.mode = mode_new
                    
                    # Reinitialize LLM if model changed
                    if self.llm and model_name_new != self.model_name:
                        await self.llm.cleanup()
                        self.llm = None
                    
                    if not self.llm:
                        self.model_name = model_name_new
                        self.llm = LLM(model_name=self.model_name)
                        await self.llm.initialize()
                    
                    self.initialized = True
                    self.session_logger.info(f"Session initialized: user_id={self.user_id}, canvas_id={self.canvas_id}, mode={self.mode}, model={self.model_name}")
                    
                    # Send success response
                    await websocket.send(json.dumps({
                        "type": "init_success",
                        "content": "Session initialized successfully",
                        "model": self.model_name,
                        "user_id": self.user_id,
                        "canvas_id": self.canvas_id
                    }))
                
                elif data["type"] == "text":
                    # Validate text content
                    if not data.get("content"):
                        self.session_logger.warning("Invalid text input")
                        await websocket.send(json.dumps({
                            "type": "error",
                            "content": "Text content missing"
                        }))
                        continue
                    
                    # Process based on mode
                    if self.mode == "normal":
                        # Normal mode processing
                        response = await self.llm.text_to_text(data["content"], self.canvas_id, self.user_id)
                        self.session_logger.info(f"Text input response (normal): {response[:50]}...")
                        
                        await websocket.send(json.dumps({
                            "type": "llm_response",
                            "content": response
                        }))
                        
                        # Process TTS if response exists
                        if response:
                            processor = TTSChunkProcessor(chunk_size=50)
                            chunks = processor.create_chunks(response)
                            self.session_logger.debug(f"Split text response into {len(chunks)} chunks")
                            
                            for chunk in chunks:
                                await loop.run_in_executor(None, tts_queue.put, chunk)
                                await asyncio.sleep(0.1)
                    else:
                        # Extreme mode processing
                        is_search = is_search_query(data["content"]) or is_deep_search_query(data["content"])
                        
                        if is_search:
                            # Handle search queries
                            max_results = 20 if is_deep_search_query(data["content"]) else 5
                            quick_search = SRSWTIQuickOne(max_results=max_results)
                            
                            await websocket.send(json.dumps({
                                "type": "processing_status",
                                "content": "STARTED QUICKONE SEARCH"
                            }))
                            
                            search_response = await quick_search(data["content"])
                            self.session_logger.info(f"Text input search response: {search_response[:50]}...")
                            
                            # Update chat history
                            await self.llm.chat_manager.manage_chat_history(self.canvas_id, self.user_id, {"role": "user", "content": data["content"]})
                            await self.llm.chat_manager.manage_chat_history(self.canvas_id, self.user_id, {"role": "assistant", "content": search_response})
                            
                            await websocket.send(json.dumps({
                                "type": "llm_response",
                                "content": search_response
                            }))
                            
                            # Process TTS if response exists
                            if search_response:
                                processor = TTSChunkProcessor(chunk_size=50)
                                chunks = processor.create_chunks(search_response)
                                self.session_logger.debug(f"Split text response into {len(chunks)} chunks")
                                
                                for chunk in chunks:
                                    await loop.run_in_executor(None, tts_queue.put, chunk)
                                    await asyncio.sleep(0.1)
                        else:
                            # Handle regular LLM processing
                            response = await self.llm.text_to_text(data["content"], self.canvas_id, self.user_id)
                            self.session_logger.info(f"Text input response (extreme): {response[:50]}...")
                            
                            await websocket.send(json.dumps({
                                "type": "llm_response",
                                "content": response
                            }))
                            
                            # Process TTS if response exists
                            if response:
                                processor = TTSChunkProcessor(chunk_size=50)
                                chunks = processor.create_chunks(response)
                                self.session_logger.debug(f"Split response into {len(chunks)} chunks")
                                
                                for chunk in chunks:
                                    await loop.run_in_executor(None, tts_queue.put, chunk)
                                    await asyncio.sleep(0.1)
                
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
        # Clean up TTS worker
        if self.tts_worker_task:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, tts_queue.put, None)
            try:
                await asyncio.wait_for(self.tts_worker_task, timeout=5.0)
                self.session_logger.info("TTS worker shut down")
            except asyncio.TimeoutError:
                self.session_logger.error("TTS worker shutdown timed out")
                self.tts_worker_task.cancel()
            except Exception as e:
                self.session_logger.error(f"Error awaiting TTS worker shutdown: {e}")
        
        # Clean up queue processor
        if self.queue_processor:
            self.queue_processor.cancel()
            try:
                await asyncio.wait_for(self.queue_processor, timeout=2.0)
                self.session_logger.info("Queue processor shut down")
            except asyncio.TimeoutError:
                self.session_logger.error("Queue processor shutdown timed out")
            except Exception as e:
                self.session_logger.error(f"Error shutting down queue processor: {e}")
        
        # Clean up STT task
        if self.stt_task:
            self.stt_task.cancel()
            self.session_logger.info("STT task cancelled")
        
        # Clean up LLM
        if self.llm:
            await self.llm.cleanup()
        
        # Interrupt TTS
        await interrupt_tts()
        self.session_logger.info(f"Session {self.session_id} fully cleaned up")