"""song-automation CLI.

    python -m song_automation check  projects/<song>/song.md
    python -m song_automation flow   projects/<song>/song.md
    python -m song_automation export projects/<song>/song.md [-o DIR]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import check, export, sheet, syllables


def _check(a) -> int:
    s = sheet.parse(a.sheet)
    found = check.run(s)
    for f in found:
        print(f)
    errors = sum(1 for f in found if f.level == "error")
    warns = len(found) - errors
    print(f"\n{s.title}: {errors} error(s), {warns} warning(s)"
          if found else f"{s.title}: clean")
    return 1 if errors else 0


def _flow(a) -> int:
    """Syllables per line, section by section, in play order."""
    s = sheet.parse(a.sheet)
    total = 0
    for sec in s.expanded():
        rep = "  (repeat)" if sec.repeat_of else ""
        print(f"[{sec.name}]{rep}")
        for l in sec.lines:
            n = syllables.line(sheet.ADLIB.sub("", l))
            total += n
            print(f"  {n:3}  {l}")
        print()
    print(f"{total} sung syllables")
    return 0


def _export(a) -> int:
    s = sheet.parse(a.sheet)
    if any(f.level == "error" for f in check.run(s)) and not a.force:
        print("check has errors; fix them or pass --force", file=sys.stderr)
        return 1
    out = Path(a.out) if a.out else Path("out") / Path(a.sheet).parent.name
    p = export.write(s, out)
    print(export.suno(s))
    print(f"-> {p}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="song_automation")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check"); c.set_defaults(fn=_check)
    c.add_argument("sheet")

    f = sub.add_parser("flow"); f.set_defaults(fn=_flow)
    f.add_argument("sheet")

    e = sub.add_parser("export"); e.set_defaults(fn=_export)
    e.add_argument("sheet")
    e.add_argument("-o", "--out", default=None)
    e.add_argument("--force", action="store_true")

    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except sheet.SheetError as err:
        print(f"{a.sheet}: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
