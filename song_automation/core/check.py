"""Lint a lyric sheet before it costs a generation.

Errors are things that will make the render wrong. Warnings are things a
human should look at and may keep on purpose.
"""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass

from . import export, syllables
from .sheet import HOOK_KINDS, LYRIC_KINDS, Sheet

# A hook line past this is hard to sing back after one listen.
HOOK_MAX_SYLLABLES = 14

# A line this much longer than its section's median gets rushed.
FLOW_RATIO = 1.5
FLOW_MIN_EXCESS = 4

BAD_CHARS = {
    "—": "em dash", "–": "en dash", "--": "double hyphen",
    "“": "curly quote", "”": "curly quote",
    "‘": "curly apostrophe", "’": "curly apostrophe",
}


@dataclass
class Finding:
    level: str      # "error" | "warn"
    where: str
    message: str

    def __str__(self) -> str:
        mark = "x" if self.level == "error" else "!"
        return f"  {mark} {self.where:<14} {self.message}"


def run(sheet: Sheet) -> list[Finding]:
    f: list[Finding] = []
    err = lambda w, m: f.append(Finding("error", w, m))
    warn = lambda w, m: f.append(Finding("warn", w, m))

    # Fields
    style = sheet.field("style")
    if not style:
        err("Style", "missing: the engine needs a genre/sound prompt")
    elif len(style) > export.STYLE_LIMIT:
        warn("Style", f"{len(style)} chars, over the {export.STYLE_LIMIT} "
                      "limit; the engine will cut it")

    # Structure
    played = sheet.expanded()
    hooks = [s for s in played if s.kind in HOOK_KINDS]
    if not hooks:
        err("structure", "no [Hook] or [Chorus]")
    elif len(hooks) < 2:
        warn("structure", "the hook plays once; a hook heard once is a verse")

    reported = set()
    for s in played:
        if not s.lines and s.kind in LYRIC_KINDS \
                and s.name.lower() not in reported:
            reported.add(s.name.lower())
            err(s.name, f"line {s.line_no}: empty, and no earlier "
                        f"[{s.name}] to repeat")

    # Lines
    for s in sheet.sections:
        for l in s.lines:
            for bad, name in BAD_CHARS.items():
                if bad in l:
                    err(s.name, f"{name} in {l!r}")
            if re.search(r"\d", l):
                warn(s.name, f"digits in {l!r}: write numbers as words, "
                             "engines guess at how to say digits")
            for phrase in sheet.banned:
                if phrase.lower() in l.lower():
                    err(s.name, f"banned phrase {phrase!r} in {l!r}")

        counts = [syllables.line(l) for l in s.sung]
        if s.kind in HOOK_KINDS:
            for l, c in zip(s.sung, counts):
                if c > HOOK_MAX_SYLLABLES:
                    warn(s.name, f"{c} syllables, long for a hook: {l!r}")
        if len(counts) >= 3:
            med = statistics.median(counts)
            for l, c in zip(s.sung, counts):
                if c >= med * FLOW_RATIO and c - med >= FLOW_MIN_EXCESS:
                    warn(s.name, f"{c} syl against a {med:g} median, will "
                                 f"be rushed: {l!r}")

    lyrics = export.lyrics(sheet)
    if len(lyrics) > export.LYRICS_LIMIT:
        warn("length", f"{len(lyrics)} chars of lyrics, over the "
                       f"{export.LYRICS_LIMIT} limit")
    return f
