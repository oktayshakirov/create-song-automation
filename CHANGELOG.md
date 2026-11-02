# Changelog

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
