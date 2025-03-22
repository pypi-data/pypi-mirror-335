import json
import os
from pathlib import Path
import logging
import uuid
import google.oauth2.service_account
from google.cloud import texttospeech
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load credentials
CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"
with open(CREDENTIALS_PATH) as f:
    CREDENTIALS = json.load(f)["google_cloud"]

# Audio parameters
RATE = 24000

# Create output directory if it doesn't exist
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Voice model mapping
VOICE_MODELS = {
    # Chirp3-HD as galaxies
    "SRSWTI-ANDROMEDA": "en-US-Chirp3-HD-Aoede",
    "SRSWTI-MILKYWAY": "en-US-Chirp3-HD-Charon",
    "SRSWTI-TRIANGULUM": "en-US-Chirp3-HD-Fenrir",
    "SRSWTI-SOMBRERO": "en-US-Chirp3-HD-Kore",
    "SRSWTI-WHIRLPOOL": "en-US-Chirp3-HD-Leda",
    "SRSWTI-PINWHEEL": "en-US-Chirp3-HD-Orus",
    "SRSWTI-CARTWHEEL": "en-US-Chirp3-HD-Puck",
    "SRSWTI-CIGAR": "en-US-Chirp3-HD-Zephyr",
    
    # CasualK as sun
    "SRSWTI-SUN": "en-US-Casual-K",
    
    # ChirpHD as planets
    "SRSWTI-MERCURY": "en-US-Chirp-HD-D",
    "SRSWTI-VENUS": "en-US-Chirp-HD-F",
    "SRSWTI-EARTH": "en-US-Chirp-HD-O",
    
    # Neural2 as moons
    "SRSWTI-MOON1": "en-US-Neural2-A",
    "SRSWTI-MOON2": "en-US-Neural2-C",
    "SRSWTI-MOON3": "en-US-Neural2-D"
}

# Create FastAPI app
app = FastAPI(title="Text-to-Speech API")

# Mount the output directory as a static files directory
app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")

class TTSRequest(BaseModel):
    text: str
    voice_model: str = "SRSWTI-ANDROMEDA"  # Default to Andromeda (Chirp3-HD-Aoede)
    language_code: str = "en-US"
    return_audio: bool = False  # Whether to return the audio file directly

class TTSBatchRequest(BaseModel):
    texts: List[str]
    voice_model: str = "SRSWTI-ANDROMEDA"
    language_code: str = "en-US"

class TTSResponse(BaseModel):
    filename: str
    download_url: str
    voice_model: str
    text: str

async def generate_tts(text: str, voice_model: str, language_code: str) -> tuple:
    """Generate TTS audio and return the filename and file path."""
    try:
        logger.info(f"Generating TTS for text: {text[:50]}...")
        
        # Map the SRSWTI voice model to Google's voice model
        google_voice_model = VOICE_MODELS.get(voice_model)
        if not google_voice_model:
            logger.warning(f"Unknown voice model: {voice_model}, using default")
            google_voice_model = "en-US-Chirp3-HD-Aoede"
        
        # Set up credentials
        credentials = google.oauth2.service_account.Credentials.from_service_account_info(
            CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Initialize client
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        
        # Set up voice parameters
        voice = texttospeech.VoiceSelectionParams(
            name=google_voice_model,
            language_code=language_code
        )
        
        # Set up audio config
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE
        )
        
        # Create synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Generate audio
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.wav"
        file_path = OUTPUT_DIR / filename
        
        # Write audio to file
        with open(file_path, "wb") as out:
            out.write(response.audio_content)
        
        logger.info(f"Audio saved to {file_path}")
        return filename, str(file_path)
    
    except Exception as e:
        logger.error(f"Error generating TTS: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating TTS: {str(e)}")

@app.post("/tts")
async def tts_endpoint(request: TTSRequest, req: Request):
    """Generate a single TTS audio file from text."""
    filename, file_path = await generate_tts(request.text, request.voice_model, request.language_code)
    
    # If return_audio is True, return the audio file directly
    if request.return_audio:
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="audio/wav"
        )
    
    # Otherwise, return the response with download URL
    base_url = str(req.base_url)
    download_url = f"{base_url}audio/{filename}"
    
    return TTSResponse(
        filename=filename,
        download_url=download_url,
        voice_model=request.voice_model,
        text=request.text[:100] + "..." if len(request.text) > 100 else request.text
    )

@app.post("/tts/batch", response_model=List[TTSResponse])
async def tts_batch_endpoint(request: TTSBatchRequest, req: Request):
    """Generate multiple TTS audio files from a list of texts."""
    results = []
    base_url = str(req.base_url)
    
    for text in request.texts:
        filename, _ = await generate_tts(text, request.voice_model, request.language_code)
        download_url = f"{base_url}audio/{filename}"
        
        results.append(
            TTSResponse(
                filename=filename,
                download_url=download_url,
                voice_model=request.voice_model,
                text=text[:100] + "..." if len(text) > 100 else text
            )
        )
    return results

@app.get("/tts/download/{filename}")
async def download_audio(filename: str):
    """Download a generated audio file."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type="audio/wav")

@app.get("/tts/voices")
async def list_voices():
    """List all available voice models."""
    return VOICE_MODELS

@app.get("/tts/direct", response_class=FileResponse)
async def tts_direct(text: str, voice_model: str = "SRSWTI-ANDROMEDA", language_code: str = "en-US"):
    """Generate TTS and return the audio file directly."""
    filename, file_path = await generate_tts(text, voice_model, language_code)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/wav"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8889)
