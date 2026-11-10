import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional
import websockets
from backend.config import GNANI_API_KEY, GNANI_STT_WS_URL, GNANI_LANGUAGE

logger = logging.getLogger("gnani_client")

class GnaniStreamingClient:
    """
    Manages bidirectional streaming with Gnani.ai's Prisma STT WebSocket API.
    Handles PCM audio ingestion, interim transcripts, and VAD-based turn finalization.
    """
    def __init__(self, api_key: Optional[str] = None, language: str = GNANI_LANGUAGE):
        self.api_key = api_key or GNANI_API_KEY
        self.ws_url = GNANI_STT_WS_URL
        self.language = language
        self.ws = None
        self.is_connected = False

    async def connect(self) -> bool:
        """Connects and authenticates to Gnani's WebSocket endpoint."""
        if not self.api_key:
            logger.warning("No Gnani API key configured. Gnani STT will run in simulation/passthrough mode.")
            return False

        headers = {
            "X-API-Key-ID": self.api_key,
            "X-Language-Code": self.language,
            "X-Audio-Encoding": "pcm16",
            "X-Sample-Rate": "16000"
        }
        try:
            self.ws = await websockets.connect(self.ws_url, extra_headers=headers)
            self.is_connected = True
            logger.info("Connected to Gnani STT WebSocket!")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gnani STT: {e}")
            self.is_connected = False
            return False

    async def stream_audio_chunk(self, pcm_bytes: bytes):
        """Sends binary PCM audio chunk to Gnani's server."""
        if self.ws and self.is_connected:
            try:
                await self.ws.send(pcm_bytes)
            except Exception as e:
                logger.error(f"Error streaming audio chunk to Gnani: {e}")

    async def receive_transcripts(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Listens for Gnani STT events: processing, interim transcripts, and final turns."""
        if not self.ws or not self.is_connected:
            return

        try:
            async for message in self.ws:
                if isinstance(message, str):
                    data = json.loads(message)
                    event_type = data.get("type", "transcript")
                    transcript_text = data.get("text", "")
                    is_final = data.get("is_final", False) or (event_type == "final")
                    
                    yield {
                        "type": event_type,
                        "text": transcript_text,
                        "is_final": is_final
                    }
        except Exception as e:
            logger.warning(f"Gnani transcript streaming closed: {e}")
        finally:
            self.is_connected = False

    async def close(self):
        """Closes the WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.is_connected = False
