"""Turn a lyric sheet into what a generator's form wants.

Only the Suno-style layout exists so far: a title, a style prompt, an exclude
prompt and a tagged lyric block. Most lyric-to-song engines (ACE-Step, YuE)
take the same `[Section]` tags, so this is the common shape, not a Suno
dependency. Rendering is not built yet: see docs/engines.md.
"""
from __future__ import annotations

from pathlib import Path

from .sheet import Sheet

# Form limits as of Suno v4.5. NOT yet checked in this repo: confirm on the
# first real generation, then delete this comment and record it in
# docs/engines.md.
STYLE_LIMIT = 1000
LYRICS_LIMIT = 5000


def lyrics(sheet: Sheet) -> str:
    blocks = []
    for s in sheet.expanded():
        blocks.append("\n".join([f"[{s.name}]", *s.lines]))
    return "\n\n".join(blocks)


def suno(sheet: Sheet) -> str:
    body = lyrics(sheet)
    style = sheet.field("style")
    exclude = sheet.field("exclude")
    parts = [
        f"TITLE\n{sheet.title}",
        f"STYLE ({len(style)}/{STYLE_LIMIT})\n{style}",
    ]
    if exclude:
        parts.append(f"EXCLUDE\n{exclude}")
    parts.append(f"LYRICS ({len(body)}/{LYRICS_LIMIT})\n{body}")
    return "\n\n".join(parts) + "\n"


def write(sheet: Sheet, out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    p = out / "suno.txt"
    p.write_text(suno(sheet), encoding="utf-8")
    return p
