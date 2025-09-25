from __future__ import annotations
import asyncio
import time
from typing import AsyncIterator, Dict, Any, Optional
import random

from .provider import Provider


class MockProvider(Provider):
    """Preprost lokalni ponudnik, ki simulira STT s fiksno latenco in delnimi rezultati."""

    def __init__(self, latency_ms: int = 200, final_every_n: int = 5) -> None:
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._connected = False
        self._interim = True
        self._latency_ms = latency_ms
        self._final_every_n = final_every_n
        self._sent_chunks = 0

    async def connect(self) -> None:
        await asyncio.sleep(0)
        self._connected = True

    async def disconnect(self) -> None:
        self._connected = False
        # allow queue to drain
        await asyncio.sleep(0)

    async def set_interim(self, enabled: bool) -> None:
        self._interim = enabled

    async def send_audio_chunk(self, data: bytes, start_ms: int, end_ms: int) -> None:
        assert self._connected, "MockProvider ni povezan"
        self._sent_chunks += 1
        await asyncio.sleep(self._latency_ms / 1000.0)
        # Generiraj 'transcript'
        words = ["primer", "besedila", "za", "test", "slovenščine", "v", "živo"]
        text = " ".join(random.sample(words, k=min(3, len(words))))
        is_final = (self._sent_chunks % self._final_every_n == 0)
        if not self._interim:
            is_final = True
        evt = {
            "type": "transcript",
            "segment_id": self._sent_chunks,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "text": text,
            "is_final": is_final,
            "provider_meta": {"latency_ms": self._latency_ms},
            "time_utc": time.time(),
        }
        await self._queue.put(evt)

    async def _events_generator(self) -> AsyncIterator[Dict[str, Any]]:
        while self._connected or not self._queue.empty():
            try:
                evt = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                if not self._connected:
                    break
                continue
            yield evt

    def events(self) -> AsyncIterator[Dict[str, Any]]:
        return self._events_generator()
