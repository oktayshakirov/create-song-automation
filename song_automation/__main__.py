"""CLI for song-automation.

Lyric sheets (a released song's `projects/<slug>/song.md`):

    python -m song_automation check  projects/<song>/song.md
    python -m song_automation flow   projects/<song>/song.md
    python -m song_automation export projects/<song>/song.md [-o DIR]

Rendering with the local ACE-Step engine (`projects/<slug>.md` render files):

    python -m song_automation engine status
    python -m song_automation new "Night Drive"
    python -m song_automation plan   projects/night-drive.md
    python -m song_automation render projects/night-drive.md -o ~/Desktop/songs
    python -m song_automation cover  track.flac --style "acoustic folk"
    python -m song_automation repaint track.flac --from 18 --to 26 --style "..."
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from song_automation.core import engine as engine_mod
from song_automation.core.client import Engine, EngineError
from song_automation.core.render import render_cover, render_repaint, render_song
from song_automation.core.song import SongError, lint, parse_song
from song_automation.core import check, export, sheet, syllables

DEFAULT_OUT = Path.home() / "Desktop/songs"
TEMPLATE = """# {title}
style: 
bpm: 
key: 
time: 4/4
language: en
duration: 
seed: 
---
[intro]

[verse]

[chorus]

[outro]
"""


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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="song_automation", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    for name, fn, hlp in (("check", "_check", "lint a lyric sheet"),
                          ("flow", "_flow", "syllables per line, in play order"),
                          ("export", "_export", "export a lyric sheet for a music engine")):
        p = sub.add_parser(name, help=hlp)
        p.add_argument("sheet")
        if name == "export":
            p.add_argument("-o", "--out", default=None)
            p.add_argument("--force", action="store_true")

    p_engine = sub.add_parser("engine", help="start/stop/inspect the local engine")
    p_engine.add_argument("action", choices=["start", "stop", "status", "log", "ready"])
    p_engine.add_argument("-n", "--lines", type=int, default=20)

    p_new = sub.add_parser("new", help="scaffold a song file")
    p_new.add_argument("title")
    p_new.add_argument("-d", "--dir", default="projects")

    p_plan = sub.add_parser("plan", help="validate and lint a song without rendering")
    p_plan.add_argument("song")

    p_render = sub.add_parser("render", help="render a song to audio")
    p_render.add_argument("song")
    p_render.add_argument("-o", "--out", default=str(DEFAULT_OUT))
    p_render.add_argument("--takes", type=int)
    p_render.add_argument("--force", action="store_true",
                          help="render even if the linter has warnings")

    p_cover = sub.add_parser("cover", help="re-record existing audio in a new style")
    p_cover.add_argument("src")
    p_cover.add_argument("--song", help="song file whose lyrics (and style, "
                         "unless --style is given) the cover is sung from")
    p_cover.add_argument("--style")
    p_cover.add_argument("--strength", type=float, default=0.2)
    p_cover.add_argument("--duration", type=float)
    p_cover.add_argument("--seed", type=int)
    p_cover.add_argument("-o", "--out", default=str(DEFAULT_OUT))

    p_repaint = sub.add_parser("repaint", help="regenerate one time range of a track")
    p_repaint.add_argument("src")
    p_repaint.add_argument("--song", help="song file whose lyrics (and style, "
                           "unless --style is given) the range is sung from")
    p_repaint.add_argument("--style")
    p_repaint.add_argument("--from", dest="start", type=float, required=True)
    p_repaint.add_argument("--to", dest="end", type=float, required=True)
    p_repaint.add_argument("--mode", choices=("conservative", "balanced", "aggressive"),
                           help="how much of the source the range keeps "
                           "(engine default: balanced)")
    p_repaint.add_argument("--seed", type=int)
    p_repaint.add_argument("-o", "--out", default=str(DEFAULT_OUT))

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except sheet.SheetError as exc:
        print(f"{args.sheet}: {exc}", file=sys.stderr)
        return 2
    except (EngineError, SongError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


def _dispatch(args) -> int:
    if args.command in ("check", "flow", "export"):
        return {"check": _check, "flow": _flow, "export": _export}[args.command](args)
    if args.command == "engine":
        return _engine(args)
    if args.command == "new":
        return _new(args)
    if args.command == "plan":
        return _plan(args)
    if args.command == "render":
        return _render(args)
    if args.command == "cover":
        song = parse_song(args.song) if args.song else None
        style = args.style or (song.style if song else None)
        if not style:
            print("error: cover needs --style, or --song to take it from",
                  file=sys.stderr)
            return 1
        take = render_cover(Path(args.src), style, Path(args.out),
                            strength=args.strength, duration=args.duration,
                            seed=args.seed, report=print,
                            lyrics=song.lyrics if song else None)
        print(f"\n{take.path}")
        return 0
    if args.command == "repaint":
        song = parse_song(args.song) if args.song else None
        style = args.style or (song.style if song else None)
        if not style:
            print("error: repaint needs --style, or --song to take it from",
                  file=sys.stderr)
            return 1
        take = render_repaint(Path(args.src), style, args.start, args.end,
                              Path(args.out), seed=args.seed, report=print,
                              lyrics=song.lyrics if song else None,
                              mode=args.mode)
        print(f"\n{take.path}")
        return 0
    return 1


def _engine(args) -> int:
    if args.action == "start":
        print(engine_mod.start())
    elif args.action == "ready":
        engine_mod.ensure_ready()
        print("weights resident")
    elif args.action == "stop":
        print(engine_mod.stop())
    elif args.action == "log":
        print(engine_mod.tail_log(args.lines))
    else:
        state = engine_mod.status()
        if not state["up"]:
            print("engine: down")
            return 1
        print(f"engine:  up ({'weights resident' if state['ready'] else 'weights not loaded'})")
        print(f"dit:     {state['dit']}")
        print(f"lm:      {state['lm']}")
        print(f"tasks:   {', '.join(state['tasks']) or 'unknown'}")
    return 0


def _new(args) -> int:
    out_dir = Path(args.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = "".join(c if c.isalnum() else "-" for c in args.title.lower()).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    path = out_dir / f"{slug}.md"
    if path.exists():
        print(f"error: {path} already exists", file=sys.stderr)
        return 1
    path.write_text(TEMPLATE.format(title=args.title))
    print(f"wrote {path}\nFill in 'style:' first - see docs/prompting.md.")
    return 0


def _plan(args) -> int:
    song = parse_song(args.song)
    warnings = lint(song)
    print(f"title:     {song.title}")
    print(f"style:     {song.style}")
    print(f"bpm:       {song.bpm if song.bpm is not None else '(engine decides)'}")
    print(f"key:       {song.key or '(engine decides)'}")
    print(f"time:      {song.time_signature or '(engine decides)'}")
    print(f"language:  {song.language}")
    print(f"duration:  {song.duration if song.duration is not None else '(engine decides)'}")
    print(f"seed:      {song.seed if song.seed is not None else '(random - not reproducible)'}")
    print(f"steps:     {song.steps}")
    print(f"format:    {song.audio_format}")
    print(f"takes:     {song.takes}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\nno warnings")
    return 0


def _render(args) -> int:
    song = parse_song(args.song)
    warnings = lint(song)
    if warnings:
        print(f"{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")
        if not args.force:
            print("\nFix these or pass --force. Rendering costs ~80s per take.")
            return 1
        print()

    engine_mod.ensure_ready()
    takes = render_song(song, Path(args.out), engine=Engine(),
                        takes=args.takes, report=print)
    print()
    for take in takes:
        print(take.path)
    if len(takes) == 1 and song.seed is None:
        print(f"\nTo lock this take, add to {args.song}:\n  seed: {takes[0].seed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
