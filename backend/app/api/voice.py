from fastapi import APIRouter, Depends, HTTPException, status
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
            detail=f"Error recognizing speech: {str(e)}"
        )
