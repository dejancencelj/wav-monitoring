from __future__ import annotations
import asyncio
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from .mock_provider import MockProvider
from .sender import Sender
from .receiver import Receiver


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("wer-tester GUI")

        self.file_var = tk.StringVar()
        self.chunk_var = tk.IntVar(value=200)
        self.mode_var = tk.StringVar(value='realtime')
        self.interim_var = tk.BooleanVar(value=True)
        self.logdir_var = tk.StringVar(value='logs')

        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky='nsew')

        # File chooser
        ttk.Label(frm, text="WAV datoteka").grid(row=0, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.file_var, width=50).grid(row=0, column=1, sticky='we')
        ttk.Button(frm, text="Izberi...", command=self.choose_file).grid(row=0, column=2)

        # Params
        ttk.Label(frm, text="Chunk (ms)").grid(row=1, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.chunk_var, width=8).grid(row=1, column=1, sticky='w')

        ttk.Label(frm, text="Način").grid(row=2, column=0, sticky='w')
        ttk.Combobox(frm, textvariable=self.mode_var, values=['realtime','maxspeed'], width=10).grid(row=2, column=1, sticky='w')

        ttk.Checkbutton(frm, text="Interim", variable=self.interim_var).grid(row=3, column=1, sticky='w')

        ttk.Label(frm, text="Log mapa").grid(row=4, column=0, sticky='w')
        ttk.Entry(frm, textvariable=self.logdir_var, width=30).grid(row=4, column=1, sticky='we')

        # Buttons
        ttk.Button(frm, text="Zaženi", command=self.start).grid(row=5, column=0)
        ttk.Button(frm, text="Ustavi", command=self.stop).grid(row=5, column=1)

        # Text display
        self.txt = tk.Text(frm, width=80, height=20)
        self.txt.grid(row=6, column=0, columnspan=3, sticky='nsew', pady=(10,0))

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._stop_evt = threading.Event()

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV", "*.wav"), ("All", "*.*")])
        if path:
            self.file_var.set(path)

    def _append_text(self, line: str):
        self.txt.insert('end', line + "\n")
        self.txt.see('end')

    def start(self):
        file = self.file_var.get()
        if not file:
            self._append_text("Izberite WAV datoteko.")
            return
        chunk_ms = int(self.chunk_var.get())
        mode = self.mode_var.get()
        interim = bool(self.interim_var.get())
        log_dir = self.logdir_var.get()

        self._stop_evt.clear()

        def run_asyncio():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._run_flow(file, chunk_ms, mode, interim, log_dir))

        self._thread = threading.Thread(target=run_asyncio, daemon=True)
        self._thread.start()
        self._append_text("Zagon...")

    def stop(self):
        self._stop_evt.set()
        self._append_text("Ustavljanje...")

    async def _run_flow(self, file: str, chunk_ms: int, mode: str, interim: bool, log_dir: str):
        provider = MockProvider()
        def _dispatch(seg):
            # Schedule GUI update on main thread
            self.root.after(0, self._on_seg, seg)
        receiver = Receiver(log_dir=log_dir, on_display=_dispatch)

        await provider.connect()
        await provider.set_interim(interim)

        async def events_task():
            async for evt in provider.events():
                await receiver.handle_event(evt)
                if self._stop_evt.is_set():
                    break

        async def send_task():
            sender = Sender(provider, chunk_ms=chunk_ms, mode=mode)
            await sender.send_wav(file)
            await asyncio.sleep(0.1)
            await provider.disconnect()

        await asyncio.gather(events_task(), send_task())

    def _on_seg(self, seg):
        if seg.type != 'transcript':
            return
        if not self.interim_var.get() and not seg.is_final:
            return
        status = 'FINAL' if seg.is_final else 'INTERIM'
        text = seg.text or ''
        self._append_text(f"[{status}] {seg.start_ms}-{seg.end_ms} ms: {text}")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
