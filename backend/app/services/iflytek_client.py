"""Async client for iFlytek Intelligent Speech recognition WebAPI (IAT)."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import queue
import ssl
import threading
import time
from datetime import datetime
from time import mktime
from typing import List, Optional, Tuple
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websocket


STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2


class IFlytekSpeechClient:
    """WebSocket client for iFlytek's real-time speech recognition service."""

    _HOST = "iat-api.xfyun.cn"
    _PATH = "/v2/iat"
    _DEFAULT_ENDPOINT = f"wss://{_HOST}{_PATH}"

    def __init__(
        self,
        app_id: Optional[str],
        api_key: Optional[str],
        api_secret: Optional[str],
        endpoint: Optional[str] = None,
    ) -> None:
        self._app_id = app_id
        self._api_key = api_key
        self._api_secret = api_secret
        self._endpoint = endpoint or self._DEFAULT_ENDPOINT

    @property
    def is_configured(self) -> bool:
        """Return True when required credentials are present."""
        return bool(self._app_id and self._api_key and self._api_secret)

    async def transcribe(self, audio_bytes: bytes, language: str = "zh_cn") -> str:
        """Send audio to iFlytek through WebSocket and return recognised text."""

        if not self.is_configured:
            raise RuntimeError("iFlytek credentials are not configured.")

        if not audio_bytes:
            raise ValueError("Audio payload is empty.")

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._transcribe_sync, audio_bytes, language
        )

    # ------------------------------------------------------------------
    # Internal helpers (synchronous, executed in background thread)
    # ------------------------------------------------------------------
    def _transcribe_sync(self, audio_bytes: bytes, language: str) -> str:
        ws_url, ws_headers = self._create_ws_request()
        result_queue: "queue.Queue[str]" = queue.Queue()
        error_queue: "queue.Queue[str]" = queue.Queue()
        latest_text: str = ""
        segments: list[str] = []

        business_params = self._build_iat_business(language)

        def on_message(ws, message):  # pragma: no cover - network callback
            nonlocal latest_text, segments
            data = json.loads(message)
            code = data.get("code")
            if code not in (None, 0):
                error_queue.put_nowait(
                    f"iFlytek returned error code={code}, message={data.get('message')}"
                )
                ws.close()
                return

            payload = data.get("data", {})
            result = payload.get("result")
            if result:
                text = self._decode_ws_result(result)
                if text:
                    pgs_mode = result.get("pgs")
                    if pgs_mode == "rpl":
                        rg = result.get("rg") or [0, 0]
                        start = max(0, int(rg[0])) if len(rg) > 0 else 0
                        end = max(start, int(rg[1])) if len(rg) > 1 else start
                        start = min(start, len(segments))
                        end = min(end, len(segments))
                        del segments[start:end]
                        segments.insert(start, text)
                    else:
                        segments.append(text)
                    latest_text = "".join(segments)

            if payload.get("status") == 2:
                result_queue.put_nowait(latest_text)
                ws.close()

        def on_error(ws, error):  # pragma: no cover - network callback
            error_queue.put_nowait(str(error))

        def on_close(ws, close_status_code, close_msg):  # pragma: no cover
            if not result_queue.qsize() and not error_queue.qsize():
                error_queue.put_nowait(
                    f"WebSocket closed unexpectedly: code={close_status_code}, message={close_msg}"
                )

        def on_open(ws):  # pragma: no cover - network callback
            def run():
                frame_size = 1280
                interval = 0.04
                status = STATUS_FIRST_FRAME
                offset = 0
                total_len = len(audio_bytes)

                while True:
                    end = min(total_len, offset + frame_size)
                    chunk = audio_bytes[offset:end]
                    offset = end

                    audio_b64 = base64.b64encode(chunk).decode("utf-8") if chunk else ""

                    if not chunk:
                        status = STATUS_LAST_FRAME

                    if status == STATUS_FIRST_FRAME:
                        frame = {
                            "common": {"app_id": self._app_id},
                            "business": business_params,
                            "data": {
                                "status": 0,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": audio_b64,
                            },
                        }
                        ws.send(json.dumps(frame))
                        status = STATUS_CONTINUE_FRAME
                    elif status == STATUS_CONTINUE_FRAME:
                        frame = {
                            "data": {
                                "status": 1,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": audio_b64,
                            }
                        }
                        ws.send(json.dumps(frame))
                    elif status == STATUS_LAST_FRAME:
                        frame = {
                            "data": {
                                "status": 2,
                                "format": "audio/L16;rate=16000",
                                "encoding": "raw",
                                "audio": audio_b64,
                            }
                        }
                        ws.send(json.dumps(frame))
                        break

                    if status != STATUS_LAST_FRAME:
                        time.sleep(interval)

            worker = threading.Thread(target=run, daemon=True)
            worker.start()

        ws = websocket.WebSocketApp(
            ws_url,
            header=ws_headers,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.on_open = on_open

        websocket.enableTrace(False)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        if not error_queue.empty():
            raise RuntimeError(error_queue.get())

        if not result_queue.empty():
            return result_queue.get().strip()

        raise RuntimeError("iFlytek returned no transcription result.")

    # ------------------------------------------------------------------
    # Supporting utilities
    # ------------------------------------------------------------------
    def _create_ws_request(self) -> Tuple[str, List[str]]:
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = (
            f"host: {self._HOST}\n" f"date: {date}\n" f"GET {self._PATH} HTTP/1.1"
        )

        signature_sha = hmac.new(
            (self._api_secret or "").encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_sha).decode("utf-8")

        authorization = (
            f'api_key="{self._api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature}"'
        )
        authorization_b64 = base64.b64encode(authorization.encode("utf-8")).decode(
            "utf-8"
        )

        query = urlencode(
            {
                "authorization": authorization_b64,
                "date": date,
                "host": self._HOST,
            }
        )

        url = f"{self._endpoint}?{query}"
        headers = [
            f"Host: {self._HOST}",
            f"Date: {date}",
            f"Authorization: {authorization}",
        ]
        return url, headers

    def _build_iat_business(self, language: str) -> dict:
        return {
            "language": language or "zh_cn",
            "domain": "iat",
            "accent": "mandarin",
            "dwa": "wpgs",
        }

    def _decode_ws_result(self, result_payload: dict) -> str:
        if not result_payload:
            return ""

        # Some responses encode the result as base64 text, others expose the token
        # structure directly. We attempt both to stay resilient.
        if isinstance(result_payload, dict):
            encoded = result_payload.get("text")
            if isinstance(encoded, str) and encoded:
                try:
                    decoded = base64.b64decode(encoded).decode("utf-8")
                    data = json.loads(decoded)
                except Exception:
                    data = None
                if data:
                    return self._extract_words(data)

            return self._extract_words(result_payload)

        if isinstance(result_payload, str):
            try:
                decoded = base64.b64decode(result_payload).decode("utf-8")
                data = json.loads(decoded)
            except Exception:
                return result_payload
            return self._extract_words(data)

        return ""

    def _extract_words(self, data: dict) -> str:
        if not isinstance(data, dict):
            return ""

        words: list[str] = []
        for ws_block in data.get("ws", []):
            if not isinstance(ws_block, dict):
                continue
            for item in ws_block.get("cw", []):
                if not isinstance(item, dict):
                    continue
                word = item.get("w")
                if word:
                    words.append(word)
        return "".join(words)
