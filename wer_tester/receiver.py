from __future__ import annotations
import asyncio
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import csv

from .models import TranscriptionSegment


class Receiver:
    def __init__(self, log_dir: str, on_display: Optional[Callable[[TranscriptionSegment], None]] = None) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.on_display = on_display
        self._jsonl_path = self.log_dir / 'receiver.jsonl'
        self._csv_path = self.log_dir / 'receiver.csv'
        self._events_path = self.log_dir / 'events.jsonl'
        self._csv_inited = False
        self._lock = asyncio.Lock()

    async def handle_event(self, evt: Dict[str, Any]) -> None:
        seg = TranscriptionSegment(
            type=evt.get('type', 'event'),
            segment_id=evt.get('segment_id'),
            start_ms=evt.get('start_ms'),
            end_ms=evt.get('end_ms'),
            text=evt.get('text'),
            is_final=evt.get('is_final'),
            provider_meta=evt.get('provider_meta'),
            time_utc=evt.get('time_utc') or 0.0,
            confidence=evt.get('confidence'),
        )
        async with self._lock:
            # JSONL
            with self._jsonl_path.open('a', encoding='utf-8') as f:
                f.write(seg.to_json() + "\n")
            # CSV
            fieldnames = ["time_utc","type","segment_id","start_ms","end_ms","text","is_final"]
            with self._csv_path.open('a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not self._csv_inited or self._csv_path.stat().st_size == 0:
                    writer.writeheader()
                    self._csv_inited = True
                writer.writerow({
                    "time_utc": seg.time_utc,
                    "type": seg.type,
                    "segment_id": seg.segment_id,
                    "start_ms": seg.start_ms,
                    "end_ms": seg.end_ms,
                    "text": seg.text,
                    "is_final": seg.is_final,
                })
        if self.on_display:
            self.on_display(seg)

    async def log_event(self, message: str, kind: str = "info", **meta):
        evt = TranscriptionSegment(
            type="event",
            segment_id=None,
            start_ms=None,
            end_ms=None,
            text=f"{kind}: {message}",
            is_final=None,
            provider_meta=meta or None,
        )
        async with self._lock:
            with self._events_path.open('a', encoding='utf-8') as f:
                f.write(evt.to_json() + "\n")
