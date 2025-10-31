"""Placeholder client for interacting with the iFlytek speech recognition service."""

from __future__ import annotations

from typing import Optional


class IFlytekSpeechClient:
    """Lightweight placeholder for the official iFlytek SDK integration."""

    def __init__(
        self, app_id: Optional[str], api_key: Optional[str], api_secret: Optional[str]
    ) -> None:
        self._app_id = app_id
        self._api_key = api_key
        self._api_secret = api_secret

    @property
    def is_configured(self) -> bool:
        """Return True when required credentials are present."""
        return all([self._app_id, self._api_key, self._api_secret])

    async def transcribe(self, audio_bytes: bytes, language: str = "zh_cn") -> str:
        """Call the cloud API to transcribe audio.

        This is a placeholder that mimics the interface of the real SDK. In an actual
        implementation the method would:
          1. Create the authorised WebSocket/HTTP request payload.
          2. Stream `audio_bytes` to iFlytek.
          3. Parse the incremental responses and produce the final transcript.

        For now we simply raise to indicate that the behaviour is mocked elsewhere.
        """
        raise NotImplementedError("iFlytek SDK integration is not implemented yet")
