from __future__ import annotations
import asyncio
import wave
import contextlib
from typing import Optional

from .provider import Provider


class Sender:
    def __init__(self, provider: Provider, chunk_ms: int, mode: str = "realtime") -> None:
        assert mode in ("realtime", "maxspeed")
        self.provider = provider
        self.chunk_ms = max(10, int(chunk_ms))
        self.mode = mode

    async def send_wav(self, wav_path: str) -> None:
        with contextlib.closing(wave.open(wav_path, 'rb')) as wf:
            sample_rate = wf.getframerate()
            sampwidth = wf.getsampwidth()
            nchannels = wf.getnchannels()
            bytes_per_frame = sampwidth * nchannels
            chunk_frames = int(sample_rate * (self.chunk_ms / 1000.0))
            if chunk_frames <= 0:
                chunk_frames = 1

            frame_pos = 0
            start_ms = 0

            while True:
                frames = wf.readframes(chunk_frames)
                if not frames:
                    break
                end_ms = int((frame_pos + len(frames)//bytes_per_frame) * 1000 / sample_rate)
                await self.provider.send_audio_chunk(frames, start_ms, end_ms)

                # advance
                frame_pos += len(frames) // bytes_per_frame
                start_ms = end_ms

                if self.mode == "realtime":
                    await asyncio.sleep(self.chunk_ms / 1000.0)
                else:
                    await asyncio.sleep(0)
