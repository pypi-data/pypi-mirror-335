
import re
import sys
import json
import queue
from pathlib import Path
from google.cloud import speech
import pyaudio
import google.oauth2.service_account
import logging
import time
from .shared import transcript_queue, STREAMING_LIMIT
# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv
load_dotenv()


    
# Audio recording parameters
STREAMING_LIMIT = 240000  # 4 minutes in milliseconds
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
SILENCE_TIMEOUT = 3  # Seconds to wait before forcing a final transcript

def get_current_time() -> int:
    """Return current time in milliseconds."""
    return int(round(time.time() * 1000))

class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding audio chunks with resuming capability."""
    def __init__(self, rate: int = RATE, chunk_size: int = CHUNK) -> None:
        self._rate = rate
        self.chunk_size = chunk_size
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self._audio_interface = None
        self._audio_stream = None
        self.open_stream()

    def open_stream(self):
        """Open or reopen the audio stream."""
        if self._audio_interface is None:
            self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        logger.debug(f"Microphone stream opened (restart #{self.restart_counter})")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()
        logger.debug("Microphone stream closed")

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream audio from microphone to API."""
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            self.audio_input.append(chunk)
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)
                except queue.Empty:
                    break
            yield b"".join(data)

def listen_print_loop(responses, stream):
    """Process server responses and enqueue transcripts with timestamps."""
    num_chars_printed = 0
    last_transcript_time = time.time()
    last_transcript = ""

    for response in responses:
        if get_current_time() - stream.start_time > STREAMING_LIMIT:
            logger.info("Streaming limit reached, restarting stream")
            stream.start_time = get_current_time()
            break

        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))
        current_timestamp = time.time()

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
            logger.debug(f"Interim transcript: {transcript}")
            transcript_queue.put({
                "type": "transcript",
                "text": transcript,
                "speech_final": False,
                "timestamp": current_timestamp
            })
            last_transcript = transcript
            last_transcript_time = current_timestamp
        else:
            print(transcript + overwrite_chars)
            logger.debug(f"Final transcript: {transcript}")
            transcript_queue.put({
                "type": "transcript",
                "text": transcript,
                "speech_final": True,
                "timestamp": current_timestamp
            })
            last_transcript = ""
            last_transcript_time = current_timestamp
            num_chars_printed = 0

            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                logger.info("Exit command detected, closing stream")
                stream.closed = True
                break

        # Force final transcript if silence exceeds timeout
        current_time = time.time()
        if last_transcript and (current_time - last_transcript_time) >= SILENCE_TIMEOUT:
            print(last_transcript + overwrite_chars)
            logger.debug(f"Forcing final transcript due to silence: {last_transcript}")
            transcript_queue.put({
                "type": "transcript",
                "text": last_transcript,
                "speech_final": True,
                "timestamp": current_time
            })
            last_transcript = ""
            num_chars_printed = 0

def main():
    """Perform endless streaming speech recognition."""


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

    language_code = "en-US"
    credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    client = speech.SpeechClient(credentials=credentials)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    logger.info("Starting endless streaming speech recognition")
    with ResumableMicrophoneStream() as stream:
        while not stream.closed:
            logger.info(f"New stream request (restart #{stream.restart_counter})")
            # Clear transcript_queue to prevent old transcripts from being processed
            while not transcript_queue.empty():
                transcript_queue.get()
                transcript_queue.task_done()
            stream.audio_input = []
            audio_generator = stream.generator()
            requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
            responses = client.streaming_recognize(streaming_config, requests)
            listen_print_loop(responses, stream)

            stream._audio_stream.stop_stream()
            stream._audio_stream.close()
            stream.audio_input = []  # Clear buffer
            stream.restart_counter += 1
            stream.start_time = get_current_time()
            stream.open_stream()  # Restart the stream
            logger.debug("Stream restarted, buffers and queue cleared")

    logger.info("Streaming ended")

if __name__ == "__main__":
    main()