from __future__ import annotations
import wave
import math
import struct
from pathlib import Path
import argparse


def make_tone_wav(path: str, duration_s: float = 3.0, freq_hz: float = 440.0, sr: int = 16000, amp: float = 0.5):
    nframes = int(sr * duration_s)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sr)
        for i in range(nframes):
            t = i / sr
            sample = amp * math.sin(2 * math.pi * freq_hz * t)
            val = int(max(-1.0, min(1.0, sample)) * 32767)
            wf.writeframes(struct.pack('<h', val))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='sample.wav')
    p.add_argument('--seconds', type=float, default=3.0)
    args = p.parse_args()
    make_tone_wav(args.out, duration_s=args.seconds)
    print(f"Zapisano: {args.out}")


if __name__ == '__main__':
    main()
