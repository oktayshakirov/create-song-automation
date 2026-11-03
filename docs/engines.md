# Engines

**Decided 2026-11-03: ACE-Step 1.5, local.** The user renders on their own
machine with the sibling repo `~/Coding/song-automation` (local only, no
remote), which drives a local ACE-Step server. This repo still does not render. It writes
the sheet, and `export` produces the Suno-shaped text that the ACE-Step song
file is translated from (see below).

## The user's setup

| | |
|---|---|
| Engine | ACE-Step 1.5, MIT licence, local |
| Machine | MacBook Pro, M2 Pro, 16GB (the server uses ~11.8GB) |
| Models | DiT `acestep-v15-turbo`, LM `acestep-5Hz-lm-0.6B` |
| Steps | 8 (turbo is tuned for 8) |
| Output | FLAC, written to `~/Desktop/songs/` with a JSON sidecar per take |
| Render time | about 2x the track length, plus ~8s of LM time |
| Driver | `python -m song_automation render <file> -o ~/Desktop/songs` from the sibling repo |

The song file goes in the sibling repo's `projects/<slug>.md`, which is
git-ignored there. Rendering details, the engine lifecycle and the prompting
rules are in that repo's `docs/`. They are not repeated here.

**Takes are reproducible by seed.** Unlike Suno, the same song file, seed and
model give the same take, and the sidecar records the seed. Log the seed, not
only the file path, in the project's Takes table. The audio still is not in
git, so keep kept takes backed up.

## Form limits: ACE-Step against `export.py`

`export.py` and `check` assume Suno's limits. ACE-Step's are different, and
some fields do not exist:

| | `export.py` (Suno) | ACE-Step 1.5 |
|---|---|---|
| Style prompt | 1000 chars | **512 chars**, truncated past that |
| Lyrics | 5000 chars | **4096 chars** |
| Exclude prompt | yes | **none**: no negative prompt. Say what you want instead |
| Tempo | in the style prompt | **`bpm:` field only**. Tempo in the caption fights the parameter |
| Key | in the style prompt | `key:` field |
| Length | the engine decides | `duration:` in seconds; aim for 2s or more per lyric line |
| Section tags | free text | only documented tags. An unknown tag such as `[Beat drop]` may be sung aloud |
| Prompt adherence | style plus model | style text only. `guidance_scale` does nothing on turbo |

So `check` passing does not mean the sheet fits ACE-Step. When translating
the export into an ACE-Step song file:

- Move the tempo out of `Style:` into `bpm:`, and the key into `key:`.
- Turn `Exclude:` into positive words in the style (say "minor key" rather
  than excluding "happy major key"), or drop it.
- Map tags to documented ones: `[Beat drop]` becomes `[Drop]`, and
  `[Hook (final)]` becomes `[Hook]`. Spoken sections can carry
  `[Bridge - spoken word]`.
- Set `duration:` from the line count, and leave `seed:` blank for the first
  take, then pin it.

## Suno, for reference

Not used for this repo's songs so far. If a song moves to Suno: it has no
official public API, a take cannot be regenerated, and who owns a generation
depends on the plan at the time it was made. `export.py`'s 1000 and 5000
limits were believed correct for v4.5 and were never checked.

## Terms

ACE-Step's MIT licence covers the model and code. It says nothing about
whether the output can be copyrighted or distributed, and distributors have
their own AI-music rules. See the release checklist in `originality.md`.
