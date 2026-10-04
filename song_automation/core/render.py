"""Render a song, keep the file, and write down what produced it.

Every render emits a sidecar JSON next to the audio. A take you like is only
worth anything if you can make it again, and the engine picks a random seed
unless told otherwise - so the seed it actually used is recorded here.
"""

from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, List, Optional

from song_automation.core.client import Engine, EngineError, JobResult
from song_automation.core.song import Song

Reporter = Optional[Callable[[str], None]]


@dataclass
class Take:
    """One rendered audio file and the parameters behind it."""

    path: Path
    seed: int
    duration: float
    bpm: Optional[int]
    keyscale: str
    render_seconds: Optional[float]
    task: str
    title: str

    def describe(self) -> str:
        bits = [f"{self.duration:.0f}s"]
        if self.bpm:
            bits.append(f"{self.bpm} bpm")
        if self.keyscale:
            bits.append(self.keyscale)
        bits.append(f"seed {self.seed}")
        if self.render_seconds:
            bits.append(f"rendered in {self.render_seconds:.0f}s")
        return f"{self.path.name}  ({', '.join(bits)})"


def render_song(
    song: Song,
    out_dir: Path,
    engine: Optional[Engine] = None,
    takes: Optional[int] = None,
    report: Reporter = None,
) -> List[Take]:
    """Render a song one take at a time.

    Takes are sequential, not batched: ``batch_size`` renders variants in one
    job but holds them all in memory at once, which a 16GB machine does not
    have to spare.
    """
    engine = engine or Engine()
    count = takes if takes is not None else song.takes
    results: List[Take] = []

    for index in range(count):
        # Only the first take honours a pinned seed; the rest explore, so a
        # `takes: 4` run gives genuine variety rather than four identical files.
        if count == 1 or index == 0:
            seed = song.seed
        else:
            seed = random.randint(1, 2**31 - 1)

        payload = song.to_payload(seed=seed)
        _say(report, f"take {index + 1}/{count}: submitting")
        task_id = engine.submit(payload)
        result = engine.poll(task_id, on_progress=lambda s: _say(report, f"  {s}"))
        take = _keep(result, song, out_dir, index, count, "text2music", payload)
        _say(report, f"  {take.describe()}")
        results.append(take)

    return results


def render_cover(
    src_audio: Path,
    style: str,
    out_dir: Path,
    strength: float = 0.2,
    duration: Optional[float] = None,
    seed: Optional[int] = None,
    audio_format: str = "flac",
    engine: Optional[Engine] = None,
    report: Reporter = None,
) -> Take:
    """Re-record an existing track in a different style.

    ``strength`` is the engine's ``audio_cover_strength``: ~0.2 lets the new
    style dominate, higher values stay closer to the source.
    """
    src_audio = Path(src_audio).expanduser().resolve()
    if not src_audio.exists():
        raise EngineError(f"no source audio at {src_audio}")
    engine = engine or Engine()
    staged, temporary = _stage_for_engine(src_audio)
    payload = {
        "task_type": "cover",
        "src_audio_path": staged,
        "prompt": style,
        "audio_cover_strength": strength,
        "audio_format": audio_format,
        "inference_steps": 8,
        "batch_size": 1,
        "use_random_seed": seed is None,
    }
    if seed is not None:
        payload["seed"] = seed
    if duration is not None:
        payload["audio_duration"] = duration

    _say(report, f"cover of {src_audio.name} at strength {strength}")
    try:
        task_id = engine.submit(payload)
        result = engine.poll(task_id, on_progress=lambda s: _say(report, f"  {s}"))
    finally:
        if temporary:
            os.unlink(staged)
    title = f"{src_audio.stem}-cover"
    take = _keep(result, None, out_dir, 0, 1, "cover", payload, title=title)
    _say(report, f"  {take.describe()}")
    return take


def render_repaint(
    src_audio: Path,
    style: str,
    start: float,
    end: float,
    out_dir: Path,
    seed: Optional[int] = None,
    audio_format: str = "flac",
    engine: Optional[Engine] = None,
    report: Reporter = None,
) -> Take:
    """Regenerate one time range of a track, leaving the rest alone.

    This is the tool for a bad bridge or a garbled line - it is far cheaper
    than re-rolling the whole song and losing the parts that worked.
    """
    src_audio = Path(src_audio).expanduser().resolve()
    if not src_audio.exists():
        raise EngineError(f"no source audio at {src_audio}")
    if end != -1 and end <= start:
        raise EngineError(f"repaint end ({end}) must be after start ({start})")
    engine = engine or Engine()
    staged, temporary = _stage_for_engine(src_audio)
    payload = {
        "task_type": "repaint",
        "src_audio_path": staged,
        "prompt": style,
        "repainting_start": start,
        "repainting_end": end,
        # Without "explicit" the model decides its own region and the range
        # above is only a hint.
        "chunk_mask_mode": "explicit",
        "audio_format": audio_format,
        "inference_steps": 8,
        "batch_size": 1,
        "use_random_seed": seed is None,
    }
    if seed is not None:
        payload["seed"] = seed

    _say(report, f"repainting {src_audio.name} from {start}s to {end}s")
    try:
        task_id = engine.submit(payload)
        result = engine.poll(task_id, on_progress=lambda s: _say(report, f"  {s}"))
    finally:
        if temporary:
            os.unlink(staged)
    title = f"{src_audio.stem}-repaint-{start:.0f}-{end:.0f}"
    take = _keep(result, None, out_dir, 0, 1, "repaint", payload, title=title)
    _say(report, f"  {take.describe()}")
    return take


def _probe_duration(path: Path) -> float:
    """Read a file's real duration with ffprobe.

    Cover and repaint jobs report their metas as "N/A", so the engine is not a
    reliable source for how long the result actually is.
    """
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=20, check=True,
        )
        return round(float(out.stdout.strip()), 2)
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0.0


def _stage_for_engine(src: Path) -> tuple[str, bool]:
    """Return a path the engine will accept, and whether we created it.

    The server rejects absolute paths outright *unless* they resolve inside the
    system temp directory (see acestep/api/http/release_task_audio_paths.py).
    Anything else must be relative to the server's own working directory, which
    is not where the user's files live. So we copy the source into temp and
    hand over the realpath - the server realpaths before comparing, and on
    macOS /var is a symlink to /private/var, so a non-resolved path fails.
    """
    src = src.expanduser().resolve()
    temp_root = Path(os.path.realpath(tempfile.gettempdir()))
    if temp_root in src.parents:
        return str(src), False
    fd, staged = tempfile.mkstemp(prefix="song_src_", suffix=src.suffix)
    os.close(fd)
    shutil.copy2(src, staged)
    return os.path.realpath(staged), True


def _keep(
    result: JobResult,
    song: Optional[Song],
    out_dir: Path,
    index: int,
    count: int,
    task: str,
    payload: dict,
    title: Optional[str] = None,
) -> Take:
    """Copy the render out of the engine's temp dir and log its provenance.

    The engine writes into .cache/acestep/tmp/api_audio, which it is free to
    clear. Anything we want to keep has to be copied immediately.
    """
    src = Path(result.audio_path)
    if not src.exists():
        raise EngineError(
            f"engine reported success but {src} is missing - the temp dir may "
            "have been cleared mid-run"
        )

    out_dir = Path(out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = (song.slug if song else None) or (title or "take")
    if title and song:
        stem = title
    suffix = src.suffix or ".flac"
    name = f"{stem}{suffix}" if count == 1 else f"{stem}-take{index + 1}{suffix}"
    dst = out_dir / name
    shutil.copy2(src, dst)

    take = Take(
        path=dst,
        seed=result.seed,
        duration=result.duration or _probe_duration(dst),
        bpm=result.bpm,
        keyscale=result.keyscale,
        render_seconds=result.generation_seconds,
        task=task,
        title=(song.title if song else stem),
    )

    sidecar = dst.with_suffix(dst.suffix + ".json")
    record = {
        "take": {**asdict(take), "path": str(dst)},
        "rendered_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "request": payload,
        "engine_metas": result.raw.get("metas", {}),
        "dit_model": result.raw.get("dit_model"),
        "lm_model": result.raw.get("lm_model"),
    }
    if song:
        record["song"] = {
            "title": song.title,
            "style": song.style,
            "lyrics": song.lyrics,
            "source_file": str(song.path) if song.path else None,
        }
    sidecar.write_text(json.dumps(record, indent=2, default=str))
    return take


def _say(report: Reporter, message: str) -> None:
    if report:
        report(message)
