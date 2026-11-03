# create-song-automation

Turn a trending topic into a funny, catchy AI-generated song: research the
trend, pick an angle, write the hook first, check the lyric sheet, and export
it in the shape a music engine wants.

Sibling projects: [audio-book-automation](https://github.com/oktayshakirov/audio-book-automation),
[video-edit-automation](https://github.com/oktayshakirov/video-edit-automation).

## What it does

- **Keeps the hook from drifting.** Write `[Hook]` once; every later empty
  `[Hook]` repeats it on export. Choruses that differ by one word are the most
  common way an AI render loses the plot.
- **Lints before it costs a generation.** `check` catches a missing hook, a
  hook that only plays once, lines far longer than their neighbours (they get
  rushed), digits the engine will guess at, em dashes and curly quotes, and any
  phrase you have banned, such as a line from the song you are riffing on.
- **Keeps jokes true.** Every factual joke traces to a row in the project's
  `SOURCES.md`. A funny song about a real product that gets the facts wrong is
  just a wrong song.

Rendering is **not built here**. Songs are rendered with ACE-Step 1.5 locally,
through a sibling repo: see [`docs/engines.md`](docs/engines.md).

## Install

Nothing beyond Python 3.11+ for the engine. Tests need pytest:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests
```

## Use

```bash
python -m song_automation check  projects/usage-limit/song.md
python -m song_automation flow   projects/usage-limit/song.md
python -m song_automation export projects/usage-limit/song.md
```

`flow` prints syllables per line, section by section, in play order. Use it
the way the audiobook repo uses `plan`: before every render, because the flow
is the part you will get wrong.

`export` refuses to run while `check` has errors, and writes `out/<song>/suno.txt`.

In Claude Code, `/create-song` runs the whole workflow.

## Lyric sheet format

```
# Usage Limit
Working notes for humans. Never exported.
Style: funny trap, half-time 140 bpm, booming 808s, deadpan male rap vocal
Exclude: choir, acoustic guitar
Banned: a phrase we must never echo; another one
---
[Intro]
(yeah) (uh huh)

[Hook]
First hook line
> a note for humans: this joke is SOURCES row 2

[Verse 1]
...

[Beat drop]

[Hook]
```

Above the `---`: the `# Title`, free notes, and `Key: value` fields. Below it,
`[Tag]` opens a section. An empty section that repeats an earlier name is a
repeat; an empty section with a new name (`[Beat drop]`) is a production
direction. Parentheses are ad-libs. `>` lines are notes.

## Layout

```
song_automation/core/  sheet parser, syllable counter, checker, exporter
projects/<song>/
  README.md            the brief: topic, angle, decisions, takes
  SOURCES.md           a row per factual claim a joke rests on
  song.md              the lyric sheet
docs/                  the rules, once
.claude/skills/        /create-song
tests/                 fast checks, never touch the network
```

Rendered audio is git-ignored: it is large. **Unlike the siblings, it is not
regenerable**: a generation cannot be reproduced from its inputs. So every
take worth keeping gets a row in its project's `Takes` table with the engine's
song ID or link, and the audio file is kept somewhere backed up.

## Docs

| | |
|---|---|
| [`docs/workflow.md`](docs/workflow.md) | The run, every step. **Read this first.** |
| [`docs/hooks.md`](docs/hooks.md) | Writing a hook that is funny and still catchy |
| [`docs/trap.md`](docs/trap.md) | Genre conventions: tempo, structure, flow, ad-libs |
| [`docs/sourcing.md`](docs/sourcing.md) | Jokes about real things have to be true |
| [`docs/originality.md`](docs/originality.md) | Riffing on a famous song without copying it, and release rules |
| [`docs/engines.md`](docs/engines.md) | The render engine (ACE-Step, local), its form limits, Suno for reference |
