# The engine

ACE-Step 1.5, MIT licensed, running locally. Everything here was measured on
the machine it runs on, not taken from the project's README.

## Hardware reality

MacBook Pro, Apple M2 Pro, 16GB unified memory.

The server fingerprints the machine on boot and self-tunes. On this one it
reports:

```
macOS MPS detected (11.8 GB unified memory, tier=tier4).
Applying Apple Silicon optimizations: no compile, no quantization,
mlx backend, no CPU offload.
```

11.8GB is what it will actually use, not the nominal 16.

### Measured render times

| Track | Steps | Render | Ratio |
|---|---|---|---|
| 40s vocal, text2music | 8 | 71s | 1.8x realtime |
| 45s vocal, text2music | 8 | 83s | 1.8x realtime |
| 15s instrumental | 8 | ~45s | 3x realtime |

Published benchmarks quoting "under 10 seconds a song" are RTX 3090 numbers.
Blog posts quoting 5-10 minutes are M2 **Air** numbers. Neither applies: budget
roughly **2x the track length**, plus about 8s of LM time per job.

## Model choice

| Slot | Chosen | Why |
|---|---|---|
| DiT | `acestep-v15-turbo` (4.5GB) | The XL variants do not fit in 11.8GB |
| LM | `acestep-5Hz-lm-0.6B` (1.3GB) | 1.7B downloads by default and is unused; delete it |

Plus `Qwen3-Embedding-0.6B` (1.1GB) and the VAE (322MB). **7.2GB total**, under
`<engine>/checkpoints/`.

Note the first init downloads `acestep-5Hz-lm-1.7B` (3.5GB) whether you asked
for it or not. Deleting it afterwards is safe; the server runs on the 0.6B it
was told to load.

## Setup

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone --depth 1 https://github.com/ace-step/ACE-Step-1.5.git \
  ~/.local/share/ace-step/ACE-Step-1.5
cd ~/.local/share/ace-step/ACE-Step-1.5 && uv sync
```

Then `python -m song_automation engine start`. First start downloads the
weights, which took about 5 minutes here.

Override the location with `ACESTEP_HOME`.

## Why we do not use the vendored launch scripts

`start_api_server_macos.sh` and its siblings are unusable unattended:

- they use bash 4 parameter expansion (`${update_choice^^}`) and macOS ships
  bash 3.2
- they block on an interactive "update now?" prompt

`core/engine.py` launches the server process directly instead, with the three
environment variables that matter:

```
ACESTEP_LM_BACKEND=mlx              # native Apple Silicon path
TOKENIZERS_PARALLELISM=false        # silences a warning storm
PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
```

The last one is not optional. Without it a render dies partway with
`MPS backend out of memory` on a 16GB machine.

## Why HTTP and not the Python API

`acestep.inference.generate_music` is the richer interface, but it needs
in-process `dit_handler` and `llm_handler` objects - roughly 8GB of weights
loaded per invocation. A warm server pays that once and renders in 71s; the
in-process route would pay it every time.

The one thing the Python API appeared to offer exclusively - lossless output -
turned out to be available over HTTP too, via the `audio_format` request field.
It merely *defaults* to 128kbps mp3.

## Server lifecycle

```bash
python -m song_automation engine start    # boot it (downloads on first run)
python -m song_automation engine ready    # block until weights are resident
python -m song_automation engine status   # what is loaded, which tasks it does
python -m song_automation engine log -n 40
python -m song_automation engine stop     # frees ~8GB
```

`status` reporting "up" is not the same as ready: the server listens before the
DiT is resident, and the first request against a cold server blocks for minutes.
`render` calls `ensure_ready()` for you.

## Disk

The install is ~8.5GB (7.2GB weights + 1.2GB venv), plus a 1.2GB `uv` cache
that is safe to delete afterwards.

Check free space with `df -h /System/Volumes/Data`. On macOS `df -h /` reports
the sealed read-only system snapshot and will claim tens of gigabytes that do
not exist.
