import json
import os
from pathlib import Path
import pyaudio
import queue
import logging
from google.cloud import texttospeech
import google.oauth2.service_account
import itertools
import time, re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()



# Audio parameters (same as your working script)
RATE = 24000
CHUNK = 1024
CHUNK_SIZE = 100  # Number of words per chunk for streaming

# Global variables for callback mode
_audio_queue = queue.Queue(maxsize=100)  # Limit queue size to prevent memory issues
_audio_buffer = bytearray()  # Buffer for audio data processing
_current_stream = None
_pyaudio_instance = None

def get_current_stream():
    """Return the current audio stream for interruption."""
    global _current_stream
    return _current_stream

def stream_tts_callback():
    """Start a callback-based TTS stream."""
    global _current_stream, _pyaudio_instance, _audio_buffer

    def callback(in_data, frame_count, time_info, status):
        global _audio_buffer
        try:
            # Calculate bytes needed for this callback
            bytes_needed = frame_count * 2  # 2 bytes per sample (16-bit audio)
            
            # If we don't have enough data in the buffer and queue isn't empty, get more
            while len(_audio_buffer) < bytes_needed and not _audio_queue.empty():
                chunk = _audio_queue.get_nowait()
                if chunk is None:  # Signal to stop
                    if len(_audio_buffer) == 0:
                        return (b"", pyaudio.paComplete)
                    break
                _audio_buffer.extend(chunk)
                _audio_queue.task_done()
            
            # If we have data to process
            if len(_audio_buffer) > 0:
                # If we have enough data for this callback
                if len(_audio_buffer) >= bytes_needed:
                    # Extract exactly what we need
                    output_data = bytes(_audio_buffer[:bytes_needed])
                    # Update buffer with remaining data
                    _audio_buffer = _audio_buffer[bytes_needed:]
                    return (output_data, pyaudio.paContinue)
                else:
                    # Not enough data, use what we have and pad with silence
                    output_data = bytes(_audio_buffer)
                    # Add silence padding (important for smooth transitions)
                    pad_length = bytes_needed - len(output_data)
                    output_data += b"\0" * pad_length
                    # Clear the buffer since we used everything
                    _audio_buffer = bytearray()
                    return (output_data, pyaudio.paContinue)
            else:
                # No data at all, return silence
                return (b"\0" * bytes_needed, pyaudio.paContinue)
                
        except queue.Empty:
            # Queue is empty but we might still have data in buffer
            if len(_audio_buffer) > 0:
                output_data = bytes(_audio_buffer[:min(len(_audio_buffer), bytes_needed)])
                pad_length = bytes_needed - len(output_data)
                output_data += b"\0" * pad_length
                _audio_buffer = _audio_buffer[min(len(_audio_buffer), bytes_needed):]
                return (output_data, pyaudio.paContinue)
            return (b"\0" * bytes_needed, pyaudio.paContinue)
        except Exception as e:
            logger.error(f"TTS callback error: {e}")
            return (b"", pyaudio.paAbort)

    _pyaudio_instance = pyaudio.PyAudio()
    _current_stream = _pyaudio_instance.open(
        format=pyaudio.paInt16,  # Explicitly use 16-bit format
        channels=1,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK,
        stream_callback=callback
    )
    _current_stream.start_stream()
    logger.info("Callback TTS stream started")
    return _current_stream, _pyaudio_instance

def stream_tts(text):
    """Queue TTS audio data for playback using exact previous Google TTS config."""
    global _audio_queue, _audio_buffer
    
    # Clear any existing audio data for new speech
    with _audio_queue.mutex:
        _audio_queue.queue.clear()
    _audio_buffer = bytearray()
    
    try:
        logger.info("Initializing TTS client...")

        # Direct credentials dictionary
        service_account_info = {
            "type": "service_account",
            "project_id": "tts-v1-453314",
            "private_key_id": "3050d43d8193f8a1a92aaa8e507ced02bc8fcb94",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCuJAIObRJn7cdO\nzih6hPY1Rd4+XTzvoI37r0iMS+Q7YB9jPp+3v1pFM98VnkIx3Kwg9adPenxuiSc1\nfw1BtE3G2o1nm9SatHR36IPZgCUTRPhK6uH7FP1DZi8N4+b5T43qB0GRQzuVmfDq\n+pOkxckJEoXmowhoFMuVK8JOU3u6RHHTtluSQ1KYYz0JnbhKxweqjJ8vsdMoSATg\nbGu7oPFL4Rit7UiyD84CKfribCuZn+o0j8YiGFjzQwcMFKOvdw3mLwe7xyVTYTMT\nuZKkBhhEYctBS24xbMOK7S2e0rgdlPfY68M4SA8lMhreFVKGjl2xMkNolpIv5VyB\nUKbptCqpAgMBAAECggEAC/DwKykTkAjgF+lPIUeo0nJeEQy3tv7dfZrBcM1rcx7e\nSCHtNd5rRD+QVp0pkN2+9+ugc3TEv5esFqEFubGxe6dU9vvaklk5e1d4YxvEbxPV\nqt18bYk87Lg/FcbA+euYoampt1pS5alOue5A3ZWqeXLJt80KMIjshOghRNm4rEcU\nRBGlwYrIAAyZctQn5GPTUkaQINykVX0tAXSPMoPCSoQHO/90qfDLBjGZn4MYiWEa\nhFpIgWRknTQglkHJPZahg7zIq4eL2MM3W3UWPr7XkiXptH9ynfPb/++wKLWL+elc\nL9I75hyomTiYY6LQXKqxRnPyoBn7q++WYJ7JSdMX4QKBgQDb2qW1wSHVocygLqX/\n9o2OcGvKMPa/5mtAsPt4+UzTInE6WnlnvFVKlAnvl0UxsqVEVEqCJh1wzwchXYWU\njvkVkzivBcN14HDWO4Bp6SWPii8Z5bZoyX6i6ZZFk78QyNxYtbyXCcnlk48NWBen\nv2+NSGwSidMeJzQnLUoTdEfD7QKBgQDKxViMHW7fWeaetfaKKAkvDZacvx026OlF\nO1COGRap8By2ynhIyMHdJoqxVvXBeuFciUvwQ7RiTBEvfIW+15WaxE4pwQ2h/Nji\n5sfuENUCWQufj7I8z1noXFDc2wPkbZh85Cg9Iy6ZVzym+Tgc9wZSkM7JwtDo7jBW\nA6OTia5iLQKBgCyggliVfn+12yp8rZd6fZt3OHoPXFbxt72m7zTMLgsBh8hXiyNC\neHGuASJQK2x+Hcvz7Dfk8r7uVz0vlajlKKx3eN8WJWntCBqEc3mMKOKtIwh3t4In\nvHvnPGidKACJNSkQotpp00C1pikIQ6z6T/N2yvEsZt1NCeoV6F5wkQy1AoGBAKVh\nR9MfvmoUnPAdYTNVbAgggRLfHSjH1lpNAmqjM8TuvbyobmqOsu94m+4ACvj/DAe5\nQ2J3FgyGFg4w9bStiKtuKIINntzbqNmHeNFGkTUVA1HklW7bf2zwvlMjno0UhiZ2\nwAr9Quh2KlXVNlsJbvKwgLg2WMViX7IHzcZrqPsRAoGBAIgT+7GThBhGeWMODEnJ\nY5uIhV1OzdG9+Ot5nitBcAnZdcALRcAtuqzrpOYLlx7fLz/lI0Tjv7GLxBn+6OiG\nCsx4pyuz1BJB3NgzUIpBttWqgfsVao8cfTu+Tcby4/d7IJgi3+s3QnAVKpIDfEoM\njEVzcs3RjI9cTRv+EGtoXbSd\n-----END PRIVATE KEY-----\n",
            "client_email": "srswti-service@tts-v1-453314.iam.gserviceaccount.com",
            "client_id": "114243557074263753039",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/srswti-service%40tts-v1-453314.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
            }


        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        
        voice = texttospeech.VoiceSelectionParams(
            name="en-US-Chirp3-HD-Aoede",
            language_code="en-US"
        )
        
        streaming_config = texttospeech.StreamingSynthesizeConfig(
            voice=voice  # No audio_config, matching your working script
        )
        
        config_request = texttospeech.StreamingSynthesizeRequest(
            streaming_config=streaming_config
        )
        
        words = text.split()
        chunks = [' '.join(words[i:i + CHUNK_SIZE]) for i in range(0, len(words), CHUNK_SIZE)]
        
        def request_generator():
            for chunk in chunks:
                yield texttospeech.StreamingSynthesizeRequest(
                    input=texttospeech.StreamingSynthesisInput(text=chunk)
                )
        
        streaming_responses = client.streaming_synthesize(
            itertools.chain([config_request], request_generator())
        )
        
        logger.info("Queuing audio data for playback...")
        for response in streaming_responses:
            # Add small delay if queue is getting full to prevent memory issues
            while _audio_queue.qsize() > 90:
                time.sleep(0.05)
            _audio_queue.put(response.audio_content)
        
    except Exception as e:
        logger.error(f"Error in stream_tts: {e}")
        # Add more detailed error information
        import traceback
        logger.debug(f"Detailed error: {traceback.format_exc()}")
    finally:
        # Signal end of audio data
        _audio_queue.put(None)

def main():
    print("Welcome to the Text-to-Speech System!")
    print("Type your text and press Enter. Type 'exit' to quit.")
    stream, audio = stream_tts_callback()
    try:
        while True:
            text = input("\nEnter text to speak: ")
            if text.lower() == 'exit':
                print("Goodbye!")
                break
            if text.strip():
                print("Speaking...")
                stream_tts(text)
                # Wait for audio to finish playing
                while not _audio_queue.empty() or len(_audio_buffer) > 0:
                    time.sleep(0.1)
    finally:
        _audio_queue.put(None)
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    main()