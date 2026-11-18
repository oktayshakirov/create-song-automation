"""Render, master and measure a sound-therapy album from a spec file.

    .venv/bin/python -m zen.album zen/albums/colors_of_calm.py --preview
    .venv/bin/python -m zen.album zen/albums/colors_of_calm.py --final

A spec is a small Python file with TITLE, SLUG and TRACKS, a list of
`Track(n, title, bed, seed)` (see `zen/albums/colors_of_calm.py`). Output goes
to `~/Desktop/<SLUG>/previews` (2-minute MP3s, the audition) or `/final`
(10-minute 44.1 kHz 16-bit WAVs, the DistroKid upload), each with a
`measurements.json`.

Mastering, measured on the first album (docs/zen.md):
- every track at TARGET_LUFS (-18, the existing catalogue sits at -17.7),
- unless that puts the sample peak past PEAK_CEILING (-1.5 dBFS): then the
  track stops short of the target rather than being limited.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import soundfile as sf

from zen.noise import SR, Bed, band_energy, render

TARGET_LUFS = -18.0
PEAK_CEILING_DB = -1.5


@dataclass(frozen=True)
class Track:
    n: int
    title: str
    bed: Bed
    seed: int


def load_spec(path: Path):
    spec = importlib.util.spec_from_file_location("zen_spec", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def loudness(path: Path) -> tuple[float, float]:
    """(integrated LUFS, true peak dBTP) via ffmpeg's ebur128."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return (float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]),
            float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1]))


def master(x: np.ndarray, out: Path, mp3: bool) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = out.with_suffix(".raw.wav")
    sf.write(str(raw), x, SR, subtype="FLOAT")
    i, _ = loudness(raw)
    gain = min(10 ** ((TARGET_LUFS - i) / 20),
               10 ** (PEAK_CEILING_DB / 20) / float(np.max(np.abs(x))))
    sf.write(str(raw), x * gain, SR, subtype="FLOAT")
    codec = (["-ar", "44100", "-c:a", "libmp3lame", "-b:a", "320k"] if mp3 else
             ["-af", "aresample=44100:dither_method=triangular", "-c:a", "pcm_s16le"])
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(raw), *codec, str(out)], check=True)
    raw.unlink()
    i2, tp = loudness(out)
    return {"file": out.name, "lufs": round(i2, 1), "true_peak": round(tp, 1),
            **band_energy(x[int(min(30, len(x) / SR / 4) * SR):])}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preview", action="store_true", help="2-minute MP3s")
    mode.add_argument("--final", action="store_true", help="full-length WAVs")
    ap.add_argument("--minutes", type=float, default=10.0, help="final length")
    ap.add_argument("--variant", action="append", default=[], metavar="N:FIELD=VALUE",
                    help="preview an extra version of track N with one Bed field "
                         "changed, e.g. 2:drift_db=1.5 (repeatable)")
    a = ap.parse_args()

    spec = load_spec(a.spec)
    root = Path(f"~/Desktop/{spec.SLUG}").expanduser() / ("previews" if a.preview else "final")
    dur = 120.0 if a.preview else a.minutes * 60
    ext = "mp3" if a.preview else "wav"
    rows = [master(render(dur, t.bed, t.seed), root / f"{t.n:02d} {t.title}.{ext}", a.preview)
            for t in spec.TRACKS]

    for v in a.variant if a.preview else []:
        n, kv = v.split(":", 1)
        field, value = kv.split("=", 1)
        t = next(t for t in spec.TRACKS if t.n == int(n))
        cur = getattr(t.bed, field)
        bed = replace(t.bed, **{field: type(cur)(value) if cur is not None else float(value)})
        rows.append(master(render(dur, bed, t.seed),
                           root / f"{t.n:02d} {t.title} ({field} {value}).mp3", True))

    print(json.dumps(rows, indent=1))
    (root / "measurements.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
