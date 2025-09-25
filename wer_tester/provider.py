from __future__ import annotations
import abc
from typing import AsyncIterator, Dict, Any, Optional, Callable


class Provider(abc.ABC):
    """
    Abstraktni vmesnik, ki ga implementira ponudnik STT.
    Pretok:
      1) connect()
      2) set_interim(True/False) – opcijsko
      3) send_audio_chunk(bytes, start_ms, end_ms) večkrat
      4) iteracija po events() za prejete segmente
      5) disconnect()
    """

    on_event: Optional[Callable[[Dict[str, Any]], None]] = None

    @abc.abstractmethod
    async def connect(self) -> None:
        ...

    @abc.abstractmethod
    async def disconnect(self) -> None:
        ...

    @abc.abstractmethod
    async def set_interim(self, enabled: bool) -> None:
        ...

    @abc.abstractmethod
    async def send_audio_chunk(self, data: bytes, start_ms: int, end_ms: int) -> None:
        ...

    @abc.abstractmethod
    def events(self) -> AsyncIterator[Dict[str, Any]]:
        """Asinhroni iterator dogodkov/segmentov JSON iz strežnika."""
        ...
