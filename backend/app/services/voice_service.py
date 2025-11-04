import base64
import io
import os
import shutil
import subprocess
import tempfile
import wave
from typing import Optional

import audioop

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
        return await self._transcribe_audio(audio_bytes, voice_input.language)

    async def recognize_audio_file(
        self, audio_bytes: bytes, language: str = "zh_cn"
    ) -> VoiceResponse:
        """Helper to handle raw audio bytes coming from file uploads."""
        return await self._transcribe_audio(audio_bytes, language)

    async def _transcribe_audio(
        self, audio_bytes: bytes, language: str = "zh_cn"
    ) -> VoiceResponse:
        if not audio_bytes:
            raise ValueError("Audio payload is empty.")

        if not self._client.is_configured:
            raise RuntimeError("iFlytek credentials are not configured.")

        pcm_bytes = self._ensure_pcm16(audio_bytes)
        try:
            recognized_text = await self._client.transcribe(pcm_bytes, language)
        except Exception as exc:
            raise RuntimeError(f"iFlytek transcription failed: {exc}") from exc

        return VoiceResponse(text=recognized_text, confidence=0.9)

    def _ensure_pcm16(self, audio_bytes: bytes) -> bytes:
        if self._looks_like_wav(audio_bytes):
            return self._extract_pcm_from_wav(audio_bytes)

        converted = self._convert_with_ffmpeg(audio_bytes)
        if converted is not None:
            return self._extract_pcm_from_wav(converted)

        raise ValueError(
            "Unsupported audio format. Please upload WAV/PCM audio or install FFmpeg for automatic conversion."
        )

    def _looks_like_wav(self, audio_bytes: bytes) -> bool:
        return (
            len(audio_bytes) > 12
            and audio_bytes[:4] == b"RIFF"
            and audio_bytes[8:12] == b"WAVE"
        )

    def _extract_pcm_from_wav(self, wav_bytes: bytes) -> bytes:
        with wave.open(io.BytesIO(wav_bytes)) as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())

        if sample_width != 2:
            frames = audioop.lin2lin(frames, sample_width, 2)
            sample_width = 2

        if channels != 1:
            frames = audioop.tomono(frames, sample_width, 0.5, 0.5)
            channels = 1

        if frame_rate != 16000:
            frames, _ = audioop.ratecv(
                frames, sample_width, channels, frame_rate, 16000, None
            )

        return frames

    def _convert_with_ffmpeg(self, audio_bytes: bytes) -> Optional[bytes]:
        ffmpeg_path = self._ffmpeg_path()
        if not ffmpeg_path:
            print("FFmpeg executable not found; cannot convert audio format.")
            return None

        with tempfile.NamedTemporaryFile(suffix=".input", delete=False) as src:
            src.write(audio_bytes)
            src_path = src.name

        dst_path = src_path + ".wav"

        try:
            print(f"Running FFmpeg on {src_path} to produce 16k PCM wav: {dst_path}")
            subprocess.run(
                [
                    ffmpeg_path,
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    src_path,
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    dst_path,
                ],
                check=True,
            )
            with open(dst_path, "rb") as converted:
                print("FFmpeg conversion succeeded, returning WAV bytes.")
                return converted.read()
        except FileNotFoundError:
            print("FFmpeg executable not found at runtime.")
            return None
        except subprocess.CalledProcessError as exc:
            print(f"FFmpeg conversion failed: {exc}")
            return None
        finally:
            try:
                os.remove(src_path)
            except OSError:
                pass
            try:
                os.remove(dst_path)
            except OSError:
                pass

    def _ffmpeg_path(self) -> Optional[str]:
        return shutil.which("ffmpeg")


voice_service = VoiceService()
