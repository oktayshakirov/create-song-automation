"""The lyric sheet: one markdown file per song.

    # Usage Limit
    Style: funny trap, half-time 140 bpm, booming 808s, deadpan male rap
    Exclude: autotune choir, acoustic guitar
    Banned: some phrase we must never echo
    ---
    [Intro]
    (yeah) (yeah)

    [Hook]
    First hook line
    > a note for humans, never exported

    [Verse 1]
    ...

    [Hook]

Everything above the `---` is for humans except `Key: value` lines, which are
fields. Below it, a `[Tag]` line opens a section. A section left empty under a
name that already appeared repeats that section's lyrics on export, so the
hook is written once and can never drift between choruses. An empty section
with a new name is a production direction (`[Beat drop]`, `[Instrumental]`)
and is exported as a bare tag.

Lines in parentheses are ad-libs. Lines starting with `>` are notes.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

TAG = re.compile(r"^\[([^\]]+)\]\s*$")
FIELD = re.compile(r"^([A-Za-z][A-Za-z ]{0,30}):\s*(.*)$")
ADLIB = re.compile(r"\([^)]*\)")

# Section kinds that must carry words the first time they appear.
LYRIC_KINDS = {"hook", "chorus", "pre-hook", "pre-chorus", "post-hook",
               "verse", "bridge", "refrain"}
HOOK_KINDS = {"hook", "chorus"}


@dataclass
class Section:
    name: str
    lines: list[str] = field(default_factory=list)
    line_no: int = 0          # where the tag sits in the file, for messages
    repeat_of: str | None = None

    @property
    def kind(self) -> str:
        """`Verse 2` -> `verse`, `Hook (final)` -> `hook`."""
        base = re.sub(r"\(.*?\)", "", self.name)
        return re.sub(r"\s*\d+\s*$", "", base).strip().lower()

    @property
    def sung(self) -> list[str]:
        """Lyric lines with ad-libs removed, dropping ad-lib-only lines."""
        out = []
        for line in self.lines:
            core = ADLIB.sub("", line).strip()
            if core:
                out.append(core)
        return out


@dataclass
class Sheet:
    title: str
    fields: dict[str, str]
    sections: list[Section]
    notes: list[str]
    path: Path | None = None

    def field(self, key: str, default: str = "") -> str:
        return self.fields.get(key.lower(), default)

    @property
    def banned(self) -> list[str]:
        raw = self.field("banned")
        return [p.strip() for p in raw.split(";") if p.strip()]

    def expanded(self) -> list[Section]:
        """Sections in play order, with empty repeats filled in."""
        seen: dict[str, list[str]] = {}
        out = []
        for s in self.sections:
            key = s.name.lower()
            if s.lines:
                seen.setdefault(key, s.lines)
                out.append(s)
            elif key in seen:
                out.append(Section(s.name, list(seen[key]), s.line_no,
                                   repeat_of=s.name))
            else:
                out.append(s)
        return out


class SheetError(ValueError):
    pass


def parse_text(text: str, path: Path | None = None) -> Sheet:
    lines = text.splitlines()
    if "---" not in (l.strip() for l in lines):
        raise SheetError("no `---` line: put the fields above it and the "
                         "lyrics below it")
    split = next(i for i, l in enumerate(lines) if l.strip() == "---")
    head, body = lines[:split], lines[split + 1:]

    title, fields = "", {}
    for l in head:
        if l.startswith("# ") and not title:
            title = l[2:].strip()
        elif m := FIELD.match(l.strip()):
            fields[m.group(1).strip().lower()] = m.group(2).strip()
    if not title:
        raise SheetError("no `# Title` line above the `---`")

    sections: list[Section] = []
    notes: list[str] = []
    for n, raw in enumerate(body, start=split + 2):
        l = raw.strip()
        if not l:
            continue
        if l.startswith(">"):
            notes.append(l[1:].strip())
            continue
        if m := TAG.match(l):
            sections.append(Section(m.group(1).strip(), line_no=n))
            continue
        if not sections:
            raise SheetError(f"line {n}: lyric before any [Section] tag")
        sections[-1].lines.append(l)
    return Sheet(title, fields, sections, notes, path)


def parse(path: str | Path) -> Sheet:
    p = Path(path)
    return parse_text(p.read_text(encoding="utf-8"), p)
