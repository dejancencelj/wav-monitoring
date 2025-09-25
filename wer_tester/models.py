from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import json
import time


@dataclass
class TranscriptionSegment:
    type: str  # 'transcript' | 'event' | 'error'
    segment_id: Optional[int]
    start_ms: Optional[int]
    end_ms: Optional[int]
    text: Optional[str]
    is_final: Optional[bool] = None
    provider_meta: Optional[Dict[str, Any]] = None
    time_utc: float = 0.0
    confidence: Optional[float] = None

    def to_json(self) -> str:
        if not self.time_utc:
            self.time_utc = time.time()
        return json.dumps(asdict(self), ensure_ascii=False)
