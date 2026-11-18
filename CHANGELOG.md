# Changelog

## 0.2.0

2026-11-18: one repo for songs and zen albums.

- Merged the local-only `song-automation` repo in, with its history: the
  ACE-Step client (`engine`, `new`, `plan`, `render`, `cover`, `repaint`),
  its docs (`engine`, `prompting`, `lyrics`, `tasks`) and tests. One CLI now
  covers the lyric sheet and the render file. Render files
  (`projects/<slug>.md`) stay git-ignored.
- `/create-song` is one skill: write, check, render, fix, video, release.
- `/create-zen` and `zen/`: sound-therapy albums for tinnitushelp.me.
  `zen.noise` (white, pink, brown, green and grey beds, notch, tilt, slow
  drift, band energy), `zen.album` (previews, -18 LUFS masters under a
  -1.5 dBFS peak ceiling, measurements), `zen.cover` (the tinnitushelp.me
  bar, matched to an existing cover, and the 1200x800 site image),
  `zen.catalogue`. First album spec: `zen/albums/colors_of_calm.py`.
  Rules and backlog in `docs/zen.md`.

## 0.1.0

Repo scaffolded on 2026-11-02, before the first song.

- Lyric sheet format: fields above `---`, `[Section]` tags below. Empty
  repeats copy the first occurrence, so the hook is written once and cannot
  drift. Ad-libs go in parentheses, and notes start with `>`.
- `check`: a missing hook, a hook heard once, an empty first section, lines
  far longer than their section's median, long hook lines, digits, em dashes
  and curly quotes, `Banned:` phrases, and style and lyric length.
- `flow`: syllables per line in play order. A heuristic counter, plus
  overrides for the words that matter.
- `export`: a Suno-style title, style, exclude and tagged lyrics, written to
  `out/<song>/suno.txt`. The form limits are assumed, not yet verified.
- `/create-song` skill, plus the workflow, hooks, trap, sourcing, originality
  and engines docs.
- First project, `projects/usage-limit/`: the topic is picked and the facts
  are gathered at snippet status.
