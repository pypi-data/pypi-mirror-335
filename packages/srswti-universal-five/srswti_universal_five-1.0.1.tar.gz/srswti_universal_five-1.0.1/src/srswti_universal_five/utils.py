# EXPLANATION# - This file contains utility functions and classes used across multiple components.
# - TTSChunkProcessor is a key class for speech-related functions
# - Functions like is_search_query help with routing user inputs
# - Global TTS state is managed here to be accessible from multiple modules

import asyncio
import queue
import logging
import re
import random
from typing import List, Optional
import os
from google import genai as google_genai
from google.genai import types

# Global TTS state
active_tts = False
tts_queue = queue.Queue()
current_tts_task = None
tts_stream = None

# Set up logging
logger = logging.getLogger(__name__)

# Define search trigger words
SEARCH_TRIGGER_WORDS = [
    "quick one",
    "quickone",
    "quick one search",
    "quick one lookup",
    "quick one find",
    "quick one check",
    "quick one info",
    "latest",
    "google",
    "internet search",
    "search"
]

DEEP_SEARCH_TRIGGER_WORDS = [
    "deep quick one",
    "deep quickone",
    "deep quick one search",
    "deep quick one lookup",
    "deep quick one find",
    "deep quick one check",
    "deep quick one info"
]

class TTSChunkProcessor:
    """Processes text into smaller chunks suitable for Text-to-Speech (TTS) processing."""
    
    def __init__(self, chunk_size: int = 150):
        """
        Initialize the TTS chunk processor.
        
        Args:
            chunk_size (int): Maximum size of each text chunk (in approximate tokens)
        """
        self.chunk_size = chunk_size
        
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.
        
        Args:
            text (str): Input text to split
            
        Returns:
            List[str]: List of sentences
        """
        # Split on period followed by space or newline, exclamation mark, or question mark
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(self, text: str) -> List[str]:
        """
        Create chunks from text, respecting sentence boundaries.
        
        Args:
            text (str): Input text to chunk
            
        Returns:
            List[str]: List of text chunks
        """
        sentences = self.split_into_sentences(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            # Rough approximation of tokens (words + punctuation)
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # If adding this sentence would exceed chunk size, save current chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add the last chunk if there's anything left
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

def is_search_query(transcript: str, trigger_words: List[str] = None) -> bool:
    """
    Check if the transcript contains any search trigger words.
    
    Args:
        transcript (str): Full transcript text
        trigger_words (List[str], optional): List of words that trigger a search. 
                                            Defaults to SEARCH_TRIGGER_WORDS.
    
    Returns:
        bool: Boolean indicating if the query should trigger a search
    """
    if trigger_words is None:
        trigger_words = SEARCH_TRIGGER_WORDS
    
    # Convert transcript to lowercase for case-insensitive matching
    transcript_lower = transcript.lower()
    
    # Check if any trigger word is in the transcript
    return any(trigger.lower() in transcript_lower for trigger in trigger_words)

def is_deep_search_query(transcript: str) -> bool:
    """
    Check if the transcript contains any deep search trigger words.
    
    Args:
        transcript (str): Full transcript text
    
    Returns:
        bool: Boolean indicating if the query should trigger a deep search
    """
    transcript_lower = transcript.lower()
    return any(trigger.lower() in transcript_lower for trigger in DEEP_SEARCH_TRIGGER_WORDS)

async def process_tts_chunks(tts_connection, text: str, websocket) -> bool:
    """
    Process text chunks for TTS and send to websocket.
    
    Args:
        tts_connection: The TTS connection object
        text (str): Text to process
        websocket: WebSocket connection to send audio data
        
    Returns:
        bool: True if processing was successful
    """
    try:
        processor = TTSChunkProcessor()
        chunks = processor.create_chunks(text)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)}: {chunk[:50]}...")
            
            try:
                await tts_connection.send_text(chunk)
                await tts_connection.flush()
                
                # Add small pause between chunks for natural speech rhythm
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error in process_tts_chunks: {str(e)}")
        return False

async def tts_worker():
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

async def interrupt_tts():
    """Interrupt current TTS playback."""
    global tts_stream
    logger.debug("Attempting to interrupt TTS")
    
    from .helpers.tts import get_current_stream, _audio_queue
    current_stream = get_current_stream()
    if current_stream and current_stream.is_active():
        try:
            # Don't close the stream; just clear queues and let callback continue with silence
            logger.debug("TTS audio stream interrupted")
        except Exception as e:
            logger.error(f"Error interrupting TTS stream: {e}")
    
    # Clear both queues
    while not tts_queue.empty():
        try:
            tts_queue.get_nowait()
            tts_queue.task_done()
        except queue.Empty:
            break
    while not _audio_queue.empty():
        try:
            _audio_queue.get_nowait()
            _audio_queue.task_done()
        except queue.Empty:
            break
    logger.debug("TTS and audio queues cleared")

async def generate_quick_filler(transcript: str) -> str:
    """Generate a 5-8 word filler that sounds natural while waiting for a full response."""
    logger.info(f"Generating conversational filler for transcript: {transcript[:50]}...")
    try:
        client = google_genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        if not os.environ.get("GEMINI_API_KEY"):
            logger.error("GEMINI_API_KEY not found")
            return "Hmm, let me think about that..."

        contents = [
            types.Content(
                role="user", 
                parts=[types.Part.from_text(text=f"The user just said: '{transcript}'. Generate a natural filler response.")]
            )
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature=0.9,
            top_p=0.95,
            top_k=40,
            max_output_tokens=30,  
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="""You are generating natural-sounding filler phrases that a human friend would say while thinking about their response.

                Create a 5-8 word conversational filler that:
                1. Acknowledges what the user just said
                2. Sounds completely natural and human
                3. Buys time while the full response is being prepared
                4. Matches the emotional tone of what was said
                5. Includes natural speech patterns like "umm", "hmm", "Uhh....", "you know", etc.
                
                Examples of good fillers:
                - "Oh wow, that's really interesting actually..."
                - "Hmm, let me think about that..."
                - "You know, that reminds me of..."
                - "Oh gosh, I totally get what you're saying..."
                - "Well, that's a good question actually..."
                - "I see what you mean, and like..."
                - "That's actually a really good point..."
                - "Oh! I was just thinking about that..."
                - "Yeah, I've been wondering about that too..."
                - "Hmm, that's a fascinating perspective actually..."
                - "Uhh.... I'm not sure how to explain..."
                - "Y'know, I was just thinking..."
                
                Keep it conversational, warm, and authentic - exactly like a human friend would respond while gathering their thoughts.
                IMPORTANT: ONLY return the filler phrase itself, nothing else.""")
            ]
        )

        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.0-flash-lite",
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text
            logger.debug(f"Filler chunk: {chunk.text}")

        # Clean up and limit the response
        response_text = response_text.strip()
        words = response_text.split()
        if len(words) > 8:
            response_text = " ".join(words[:8]) + "..."

        logger.info(f"Conversational filler generated: {response_text}")
        return response_text

    except Exception as e:
        logger.error(f"Error in generate_quick_filler: {str(e)}")
        return "Hmm, let me think about that..."



async def process_with_llm(llm, text, canvas_id, user_id):
    """
    Process text with the LLM class.
    
    Args:
        llm: LLM instance
        text (str): Text to process
        canvas_id (str): Canvas ID
        user_id (str): User ID
        
    Returns:
        str: Generated response
    """
    try:
        logger.debug(f"Generating response for input: {text}")
        # Use the existing text_to_text method instead of generate_response
        response = await llm.text_to_text(text, canvas_id, user_id)
        logger.info(f"Generated response: {response}")
        # Extract speech content if available, otherwise use the full response
        if isinstance(response, dict):
            return response.get("content", {}).get("speech", str(response))
        return str(response)
    except Exception as e:
        logger.error(f"Error in process_with_llm: {e}")
        return f"I apologize, but I encountered an error: {str(e)}" 