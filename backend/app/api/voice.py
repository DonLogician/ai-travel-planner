from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from app.schemas.user import VoiceInput, VoiceResponse
from app.services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["Voice Recognition"])


@router.post("/recognize", response_model=VoiceResponse)
async def recognize_speech(voice_input: VoiceInput):
    """
    Recognize speech from audio input using iFlytek API.

    Accepts base64 encoded audio data and returns recognized text.
    """
    try:
        result = await voice_service.recognize_speech(voice_input)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recognizing speech: {str(e)}",
        )


@router.post("/upload", response_model=VoiceResponse)
async def upload_voice(file: UploadFile = File(...), language: str = Form("zh_cn")):
    """Upload an audio file, transcribe it using the voice service, and return the text."""
    try:
        audio_bytes = await file.read()
        return await voice_service.recognize_audio_file(audio_bytes, language)
    except Exception as e:  # pragma: no cover - minimal surface area
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio upload: {str(e)}",
        )
