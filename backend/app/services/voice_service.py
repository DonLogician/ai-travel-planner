import base64

from app.schemas.user import VoiceInput, VoiceResponse
from app.core.config import settings
from app.services.iflytek_client import IFlytekSpeechClient


class VoiceService:
    """Service for voice recognition using iFlytek API."""

    def __init__(self):
        self.app_id = settings.IFLYTEK_APP_ID
        self.api_key = settings.IFLYTEK_API_KEY
        self.api_secret = settings.IFLYTEK_API_SECRET
        self._client = IFlytekSpeechClient(self.app_id, self.api_key, self.api_secret)

    async def recognize_speech(self, voice_input: VoiceInput) -> VoiceResponse:
        """
        Recognize speech from audio data using iFlytek API.

        Args:
            voice_input: Voice input with base64 encoded audio

        Returns:
            Recognized text and confidence score
        """
        audio_bytes = base64.b64decode(voice_input.audio_data)

        if self._client.is_configured:
            try:
                recognized_text = await self._client.transcribe(
                    audio_bytes, voice_input.language
                )
                return VoiceResponse(text=recognized_text, confidence=0.9)
            except NotImplementedError:
                # Placeholder until the official SDK is wired in
                pass
            except Exception as exc:  # pragma: no cover - external dependency
                print(f"Error in speech recognition: {exc}")

        # Return mock response when SDK is not available or integration fails
        return VoiceResponse(
            text="我想去北京旅游三天，预算 5000 元，喜欢美食。", confidence=0.6
        )

    async def recognize_audio_file(
        self, audio_bytes: bytes, language: str = "zh_cn"
    ) -> VoiceResponse:
        """Helper to handle raw audio bytes coming from file uploads."""
        encoded = base64.b64encode(audio_bytes).decode("utf-8")
        voice_input = VoiceInput(audio_data=encoded, language=language)
        return await self.recognize_speech(voice_input)


voice_service = VoiceService()
