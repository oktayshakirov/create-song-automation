# song-automation

Write your own lyrics, render them as finished songs on your own machine, for
free. Local ACE-Step 1.5 synthesis, a song file that keeps the words and the
settings together, and a linter that predicts a bad take before it costs you
80 seconds.

Built while making real tracks. Everything in `docs/` is a measurement or a
mistake that cost something, not advice.

Sibling projects: [audio-book-automation](https://github.com/oktayshakirov/audio-book-automation),
[video-edit-automation](https://github.com/oktayshakirov/video-edit-automation).

## What it does

- **Keeps the song in one file.** Style, tempo, key and lyrics live together in
  markdown, so a take is a diff rather than a memory.
- **Predicts bad renders.** The linter counts syllables per section, catches
  tempo written into the style prompt, flags undocumented tags and warns when
  the duration cannot fit the words. It caught a 6-to-14 syllable hook on the
  first real song here.
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

The client itself is standard library only. Models (~7.2GB) download on first
`engine start`. See `docs/engine.md`.

## Use

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

## The song file

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
| Model footprint | 7.2GB |
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

Your own songs go in `projects/`, which is git-ignored - lyrics are work
product, and this repo is public.
