# wer-tester

Orodje za testiranje govor-v-besedilo (STT) ponudnikov za slovenščino v živo. Nadzorujemo oddajanje avdio segmentov (dolžina chunk-a, simulacija realnega časa ali pošiljanje z največjo hitrostjo) in sproti spremljamo vračanje JSON segmentov besedila. Vsi segmenti in dogodki se zapišejo v lokalne loge (JSONL/CSV), hkrati pa so vidni na prikazu (CLI/GUI). Ponudnik doda svojo implementacijo `Provider` ter se vključi preko `--provider module:Class`.

Tri komponente:
- Oddajnik: pošilja avdio v segmentih (real-time simulacija ali maksimalna hitrost), z nastavitvijo dolžine segmenta.
- Sprejemnik: prejema JSON segmente in jih zapisuje v log (časovne oznake, statusi), posreduje prikazu.
- Ekran: prikazuje prejeto besedilo (interim vklop/izklop), gumbi za izbiro datoteke in start/stop.

Ponudniki implementirajo vmesnik `Provider` (glej `wer_tester/provider.py`). Za primer je dodan `MockProvider` (lokalna simulacija).

## Namestitev

Potrebujete Python 3.9+.

1) Namestite paket v razvijalnem načinu:

```pwsh
pip install -e .
```

2) Zaženite CLI:

```pwsh
wer-tester --file pot/do/test.wav --chunk-ms 200 --mode realtime --interim on --log-dir .\logs
```

3) Zaženite GUI:

```
.\scripts\run-gui.ps1
```

## Parametri

- --file: pot do WAV datoteke (mono/stereo, 16-bit PCM priporočeno)
- --chunk-ms: dolžina avdio segmenta v milisekundah (npr. 200)
- --mode: `realtime` (simuliraj realni čas) ali `maxspeed` (pošlji takoj)
- --interim: `on`/`off` za prikaz vmesnih (interim) rezultatov
- --log-dir: mapa za jsonl/csv loge

## Dnevniški zapisi (log)

- `receiver.jsonl`: vsaka vrstica je JSON s polji: time_utc, type, segment_id, start_ms, end_ms, text, is_final, provider_meta, confidence
- `receiver.csv`: CSV z istimi ključnimi podatki
- `events.jsonl`: generični dogodki (povezava, napake, ...)

## Kako implementira ponudnik

Ponudnik implementira razred, ki razširi `Provider`:

- `connect()` / `disconnect()`
- `send_audio_chunk(bytes, start_ms, end_ms)` – pošlje koščke avdia v pravem vrstnem redu
- `set_interim(enabled: bool)` – opcijsko
- `events()` – asinhroni iterator ali callback za sprejem JSON segmentov oblike:
  ```json
  {
    "type": "transcript",
    "segment_id": 12,
    "start_ms": 4000,
    "end_ms": 4200,
    "text": "primer besedila",
    "is_final": false,
    "provider_meta": {"latency_ms": 120},
    "confidence": 0.95
  }
  ```

  Opomba: Polje `confidence` je opcijsko in predstavlja zaupanje v transkript (običajno med 0.0 in 1.0).

Glej `wer_tester/provider.py` za definicijo ABC in `wer_tester/mock_provider.py` za popolnoma delujoč primer.

## Generator vzorčnega WAV-a

Zelo kratko: ustvari WAV in zaženi test.

```pwsh
python tools/make_sample_wav.py --out .\sample.wav
wer-tester --file .\sample.wav --chunk-ms 200 --mode realtime --interim on
```

Alternativa (PowerShell bližnjice):

```pwsh
./scripts/run-mock-test.ps1 -Out .\sample.wav -ChunkMs 200 -Mode realtime -Interim on -LogDir .\logs
```

Opomba: 16 kHz, mono, 16-bit PCM WAV je priporočljiv za enostavne teste.

## PowerShell skripte (Windows)

V mapi `scripts/` so pripravljene bližnjice:

- Namestitev (editable):
  ```pwsh
  .\scripts\install.ps1
  ```
- Zagon GUI:
  ```pwsh
  .\scripts\run-gui.ps1
  ```
- Zagon CLI (argumenti se prepustijo naprej):
  ```pwsh
  .\scripts\run-cli.ps1 --file .\sample.wav --chunk-ms 200 --mode realtime --interim on --log-dir .\logs
  ```
- Ustvari vzorčni WAV:
  ```pwsh
  .\scripts\make-sample.ps1 -Out .\sample.wav -Seconds 2
  ```
- Celoten preizkus z MockProvider (ustvari WAV in zažene CLI):
  ```pwsh
  .\scripts\run-mock-test.ps1 -Out .\sample.wav -ChunkMs 200 -Mode realtime -Interim on -LogDir .\logs
  ```

## Licence

MIT

## Spremembe

- **2025-09-25**: Dodano polje `confidence` za zaupanje v transkripte. MockProvider generira naključne vrednosti zaupanja med 0.5 in 1.0.
