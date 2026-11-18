# create-song-automation

Turn a trending topic into a funny, catchy AI-generated song: research the
trend, pick an angle, write the hook first, check the lyric sheet, then render
it on your own machine with ACE-Step 1.5, for free, with every take
reproducible by seed. The same repo builds sound-therapy albums for
[tinnitushelp.me](https://www.tinnitushelp.me/zen) (see [Zen albums](#zen-albums)).

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

- **Predicts bad renders.** `plan` counts syllables per section, catches
  tempo written into the style prompt, flags undocumented tags and warns when
  the duration cannot fit the words.
- **Makes takes reproducible.** The engine defaults to a random seed and
  silently discards the one you pass. This forces it off and records the seed
  it actually used in a sidecar next to every render.
- **Writes masters, not previews.** 24-bit/48kHz FLAC. The engine's own default
  is 128kbps mp3.

## Install

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone --depth 1 https://github.com/ace-step/ACE-Step-1.5.git \
  ~/.local/share/ace-step/ACE-Step-1.5
cd ~/.local/share/ace-step/ACE-Step-1.5 && uv sync
```

The client itself is standard library only. Models (~10.8GB) download on first
`engine start`. One of them, the 1.7B LM, is never loaded but must not be
deleted - `docs/engine.md` explains why that costs more than it saves.

The client itself needs nothing beyond Python 3.11+. Tests need pytest:

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

Rendering, with the engine running locally:


```bash
python -m song_automation engine start
python -m song_automation new "Night Shift"
python -m song_automation plan   projects/night-shift.md
python -m song_automation render projects/night-shift.md -o ~/Desktop/songs
python -m song_automation engine stop
```

`plan` is a dry run: it resolves every parameter and lists every warning
without synthesising. Use it before each render, because rendering is slow and
the lyrics are the part you will get wrong.

Reworking existing audio:

```bash
python -m song_automation cover   track.flac --style "acoustic folk" --strength 0.2
python -m song_automation repaint track.flac --from 18 --to 26 --style "sparse breakdown"
```

In Claude Code, `/create-song` runs the whole workflow, and `/create-zen`
builds a sound album.

## Zen albums

Sound-therapy albums for [tinnitushelp.me/zen](https://www.tinnitushelp.me/zen),
released through DistroKid. Beds are generated, not recorded, so every
track's spectrum is a measured fact the album page can print.

```bash
.venv/bin/python -m zen.catalogue --store                         # what is on /zen
.venv/bin/python -m zen.album zen/albums/colors_of_calm.py --preview   # 2-min MP3s
.venv/bin/python -m zen.album zen/albums/colors_of_calm.py --final     # 10-min WAVs
.venv/bin/python -m zen.cover zen/albums/colors_of_calm.py             # cover + site image
```

Masters land at -18 LUFS under a -1.5 dBFS peak ceiling, 44.1 kHz 16-bit.
The rules, the catalogue and the backlog are in [`docs/zen.md`](docs/zen.md);
`/create-zen` runs the whole thing.

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
song_automation/core/  sheet parser, syllable counter, checker, exporter,
                       ACE-Step client, engine lifecycle, renderer
zen/                   sound-album generator, cover bar, site image
projects/<slug>.md     render file (git-ignored)
projects/<song>/
  README.md            the brief: topic, angle, decisions, takes
  SOURCES.md           a row per factual claim a joke rests on
  song.md              the lyric sheet
docs/                  the rules, once
.claude/skills/        /create-song, /create-zen
tests/                 fast checks, never touch the network
```

Rendered audio is git-ignored: it is large. A take is reproducible from its
song file, seed and model, but log every kept take in its project's `Takes`
table anyway (seed, file, sha256) and keep the audio backed up.

## Docs

| | |
|---|---|
| [`docs/workflow.md`](docs/workflow.md) | The run, every step. **Read this first.** |
| [`docs/hooks.md`](docs/hooks.md) | Writing a hook that is funny and still catchy |
| [`docs/trap.md`](docs/trap.md) | Genre conventions: tempo, structure, flow, ad-libs |
| [`docs/sourcing.md`](docs/sourcing.md) | Jokes about real things have to be true |
| [`docs/originality.md`](docs/originality.md) | Riffing on a famous song without copying it, and release rules |
| [`docs/engines.md`](docs/engines.md) | From lyric sheet to render file: ACE-Step's form limits, Suno for reference |
| [`docs/prompting.md`](docs/prompting.md) | Writing the `style:` line |
| [`docs/lyrics.md`](docs/lyrics.md) | Render tags, sections, syllable counts |
| [`docs/tasks.md`](docs/tasks.md) | Cover, repaint, fixing a take in place, what the model cannot do |
| [`docs/engine.md`](docs/engine.md) | Running the engine, disk and time |
| [`docs/zen.md`](docs/zen.md) | Sound-therapy albums: catalogue, generation, mastering, covers, release |

## The render file

```markdown
# Night Shift
style: dark trap, hard 808 sub bass with glides, triplet hi-hat rolls, sparse minor piano, male rap vocal
bpm: 140
key: F minor
time: 4/4
language: en
duration: 40
seed: 4242
---
[intro]

[verse]
Clock hit twelve and the city went quiet
Everybody sleeping, I was wide awake

[hook]
I don't talk about it, I just move
Put it on the table, watch me prove
```

`style:` is required and matters most. Everything else is optional - leave a
field out and the model infers it.

## Read this before you fight the model

| Before you | Read |
|---|---|
| write a style prompt | `docs/prompting.md` |
| write a word of lyrics | `docs/lyrics.md` |
| expect stems or per-instrument control | `docs/tasks.md` |
| try to make a duet | `docs/tasks.md` |
| cover someone else's song | `docs/tasks.md` |
| debug the engine or budget disk | `docs/engine.md` |

## Measured on an M2 Pro / 16GB

| | |
|---|---|
| 40s vocal track, 8 steps | 71s |
| 45s vocal track, 8 steps | 83s |
| Model footprint | 10.8GB on disk (7.2GB loaded) |
| Output | 24-bit/48kHz FLAC, ~1.4 Mbps |

Roughly 2x realtime. Published "under 10 seconds" figures are RTX 3090
numbers; "5-10 minutes" figures are M2 Air numbers.

## Licence

This tooling is MIT. ACE-Step 1.5 is MIT, which means songs you generate are
yours commercially, with no subscription. That is not true of Suno or
ElevenLabs, where commercial rights are tied to an active plan - and it does
not extend to covering recordings you do not own.

## Example

`examples/night-shift.md` is a complete song file that renders clean:

```bash
python -m song_automation plan   examples/night-shift.md
python -m song_automation render examples/night-shift.md -o ~/Desktop/songs
```

Render files go in `projects/<slug>.md`, which is git-ignored: unreleased
lyrics are work product, and this repo is public.
