from __future__ import annotations
from typing import Optional
import sys

from .models import TranscriptionSegment


class ConsoleDisplay:
    def __init__(self, interim: bool = True) -> None:
        self.interim = interim

    def on_segment(self, seg: TranscriptionSegment) -> None:
        if seg.type != 'transcript':
            return
        if not self.interim and not seg.is_final:
            return
        status = 'FINAL' if seg.is_final else 'INTERIM'
        text = seg.text or ''
        sys.stdout.write(f"[{status}] {seg.start_ms}-{seg.end_ms} ms: {text}\n")
        sys.stdout.flush()
