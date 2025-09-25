from __future__ import annotations
import asyncio
import argparse
from pathlib import Path

from .sender import Sender
from .receiver import Receiver
from .display import ConsoleDisplay
from .utils import import_string
from .provider import Provider
from typing import cast, Type


async def run(file: str, chunk_ms: int, mode: str, interim: bool, log_dir: str, provider_path: str) -> None:
    ProviderCls = import_string(provider_path)
    if not callable(ProviderCls):
        raise RuntimeError(f"Provider '{provider_path}' ne kaže na razred (module:Class)")
    provider = cast(Provider, cast(Type[Provider], ProviderCls)())
    display = ConsoleDisplay(interim=interim)
    receiver = Receiver(log_dir=log_dir, on_display=display.on_segment)

    await provider.connect()
    await provider.set_interim(interim)
    await receiver.log_event("connected")

    async def events_task():
        async for evt in provider.events():
            await receiver.handle_event(evt)

    async def send_task():
        sender = Sender(provider, chunk_ms=chunk_ms, mode=mode)
        await sender.send_wav(file)
        await asyncio.sleep(0.1)
        await provider.disconnect()
        await receiver.log_event("disconnected")

    await asyncio.gather(events_task(), send_task())


def main():
    p = argparse.ArgumentParser(description="STT live test harness")
    p.add_argument('--file', required=True, help='Pot do WAV datoteke')
    p.add_argument('--chunk-ms', type=int, default=200, help='Dolžina segmenta v ms')
    p.add_argument('--mode', choices=['realtime','maxspeed'], default='realtime', help='Način pošiljanja')
    p.add_argument('--interim', choices=['on','off'], default='on', help='Vmesni rezultati')
    p.add_argument('--log-dir', default='logs', help='Mapa za log datoteke')
    p.add_argument('--provider', default='wer_tester.mock_provider:MockProvider', help='Pot do ponudnika (module:Class)')
    args = p.parse_args()

    file = str(Path(args.file))
    interim = args.interim.lower() == 'on'

    asyncio.run(run(file=file, chunk_ms=args.chunk_ms, mode=args.mode, interim=interim, log_dir=args.log_dir, provider_path=args.provider))


if __name__ == '__main__':
    main()
