---
name: create-song
description: Make songs end to end in create-song-automation - research a trending topic, suggest topics, write a brief with sourced facts, write the hook first and then the verses, check the lyric sheet, then render it locally with ACE-Step 1.5, fix takes in place, build the music video and the release kit. Use when the user runs /create-song, asks for a song, parody, rap or trap track, a beat or an instrumental, lyrics or a hook, wants lyrics turned into music, wants an existing track re-recorded in another style or one section of it fixed, asks about song prompting, structure tags or render settings, or wants to continue a song in projects/. For tinnitus sound albums use create-zen; for narration use audio-book; for videos use video-crypto / video-tinnitus / video-drone.
---

# Create a song

**One song per run, hook first.** The hook is the song: everything else is
written to serve it, after it is frozen.

**Repo:** `~/Coding/create-song-automation` (public). Run Python from the repo root:
`python -m song_automation <check|flow|export> projects/<slug>/song.md` for the
lyric sheet, and `plan`/`render`/`cover`/`repaint` on `projects/<slug>.md` for
the ACE-Step render file (see **Rendering** below).

## Read these first, every run

| Step | Read |
| --- | --- |
| **The run, every step** | **`docs/workflow.md`** |
| Writing the hook | `docs/hooks.md` |
| Genre, structure, flow | `docs/trap.md` (or the genre's own doc, if one exists) |
| Facts in jokes | `docs/sourcing.md` |
| Riffing on a famous song, release | `docs/originality.md` |
| Rendering: sheet to render file | `docs/engines.md` |
| A `style:` line | `docs/prompting.md` |
| Render tags, sections, syllable counts | `docs/lyrics.md` |
| Stems, duets, covers, fixing a take in place | `docs/tasks.md` |
| The engine, disk and time | `docs/engine.md` |

Do not work from memory of these. They change as songs teach things.

## The run

`workflow.md` is the procedure. What follows is only how to run it with the
user.

1. **Continuing or new?** If `$ARGUMENTS` or the conversation names a song,
   or `projects/` has a song whose README says it is in progress, read that
   project's `README.md`, `SOURCES.md` and `song.md` and pick up at its
   **Status** line. Otherwise start at step 1 of the workflow.
2. **Suggest, do not pick.** The topic, angle, title and hook are the user's.
   Offer three or four options with a recommendation, and wait.
3. **Research live.** Trends come from a web search this month, not memory.
   Every fact goes in `SOURCES.md` with an honest status before a lyric uses
   it.
4. **Hook first.** Offer three genuinely different hooks, each run through
   `flow`. Once the user picks one, write it into `song.md` once and freeze it.
5. **Verses after.** Escalate the jokes, tag factual lines with
   `> SOURCES row N`, and write the ad-libs in.
6. **Check until clean.** `check` with zero errors. Read each warning back to
   the user if you keep it.
7. **Export** when the user is happy with the lyrics. Do not build or run a
   renderer here unless the user asks. The engine is ACE-Step, local
   (see `docs/engines.md` and **Rendering** below).
8. **Render** here: translate the export into `projects/<slug>.md`, `plan`,
   then render (see **Rendering** below). Transcribe every take, keep every take until the user names the final,
   and fix faults in place rather than re-rolling. Log each kept take in the
   Takes table with seed, file, sha256 and what is good or bad.
9. **Music video**, once the master is approved: karaoke video in
   `~/Coding/video-edit-automation/projects/song/<slug>/` - copy
   `timing.py`, `video.py` and `art.py` from the newest song there
   (`gta-flu`), and read `docs/video/projects/song.md` there. Ask the look
   questions only if this song differs (no watermark, whole song at 9:16,
   plain SF Pro karaoke, speaker tags on dialogue, real subject images via
   cutouts are the standing answers).
   **Nothing on screen for less than a second.** Every sticker, label,
   stamp, emoji, card or bubble must hold `MIN_HOLD` (1.0s) before its
   scene or line changes: a punchline prop is pulled earlier (`at()`), an
   ad-lib that cannot hold, or that the next line sings, is not shown
   (`shows()`). Run `video.py long --audit` and `short --audit` before every
   full render and read what it hid; re-time anything that matters.
10. **Release kit** in the project's `RELEASE.md` (copy `usage-limit`'s):
    the distributor fields (DistroKid; title only, no "(AI)" or brand
    names), the 3000x3000 cover (title as its only text, no emoji, no logo),
    YouTube long and Short titles and descriptions with the sung lyrics, and
    a TikTok caption with no hashtags. The user preferred the Short's
    joke-first title style for the long one too, with the song's name after
    a `|` so video and track meet in search.
11. **Update the project README.** Update the Status line, the decisions made
    with a one-line reason each, and anything still open.
12. **Commit** the project folder, with lessons in the narrowest doc.

## Hard rules

- **Original lyrics and melody.** A title pun on a famous song is fine.
  Copying its lines, melody or signature hook is not. Put its known lines in
  `Banned:`. Never name an artist in the style prompt.
- **Jokes are true.** Exaggerate feelings, not facts. No invented quotes, and
  no unsourced claims about a company's motives.
- **No logos or official-looking art** for a song about a real product.

# Rendering

The render file is `projects/<slug>.md` (git-ignored: unreleased lyrics);
`examples/night-shift.md` is the committed reference. Renders go to
`~/Desktop/songs/`.

## Commands

```bash
cd ~/Coding/create-song-automation
python -m song_automation engine start          # ~7.2GB on first run
python -m song_automation engine status         # up? weights resident? which tasks?
python -m song_automation new "Night Shift"
python -m song_automation plan   projects/night-shift.md
python -m song_automation render projects/night-shift.md -o ~/Desktop/songs
python -m song_automation cover   <audio> --style "..." --strength 0.2   # --song FILE re-sings it
python -m song_automation repaint <audio> --from 18 --to 26 --song FILE   # --mode conservative|balanced|aggressive
python -m song_automation engine stop           # frees ~8GB
```

Run `plan` before every render. It is instant, rendering is ~2x the track
length, and the lyrics are the part that goes wrong.

Stop the engine when the session is done. It holds about 8GB on a 16GB machine.

## What the model will not do

Say these plainly when asked, rather than attempting them and shipping
something that quietly missed:

- **No stems, no per-instrument generation, no "build around my loop."** Those
  are `lego`/`extract`/`complete`, which are base-model only. The installed
  turbo model refuses them up front. Switching costs another ~4.5GB and
  several minutes a render.
- **No consistent second singer.** There is no speaker ID. A duet means
  rendering sections separately and splicing, or repainting one section's
  vocal. `[call and response]` and "male and female duet" only nudge it.
- **No placing a hit on a bar.** Rhythm is described, not sequenced. There is
  no MIDI and no step grid.
- **`guidance_scale` does nothing** on turbo. The caption text is the only
  adherence lever there is.

## The things that cost the most time

**The `style:` line carries the result.** Eight clauses across genre,
instruments, timbre and vocal character is the working length. "a sad song"
gets you nothing. There is no guidance dial on turbo to compensate for a thin
caption.

**Syllables decide whether a hook lands.** The model maps syllables onto beats.
Lines in one section should sit within about two of each other. The linter
caught a hook swinging 6 to 14 on the first real song here; evening it to 9
across the board was the whole fix.

**A seed you did not pin is a take you cannot get back.** The engine defaults
`use_random_seed` to true. The pipeline forces it off and records the real
seed in a sidecar, but only if you remember to read it back into the file.

**Tempo belongs in `bpm:`, never in the style line.** Written into the caption
it fights the parameter. The linter flags it.

**Duration too short is the most common ruined take.** Below roughly two
seconds a lyric line the vocal rushes and garbles. When unsure, go longer.

**Cover and repaint report no metadata.** They return `"N/A"` for duration,
bpm and key. The pipeline reads duration back with ffprobe; do not quote the
engine's numbers for those tasks.

## What the first full song taught (Come Back at Five, 2026-11)

**Transcribe every take before calling it good.** A 16-line verse lost two
to four lines in every render. `mlx-whisper` (large-v3-turbo) is installed in
this repo's `.venv`; a pass shows dropped, doubled and garbled lines in a
minute. Demucs (vocal separation) lives in
`~/.local/share/song-automation/sepvenv`. **Never keep tools or work files
in the session scratchpad** - it is wiped between days and took a build
script with it.

**Keep every take until the user names the final.** Their favourite was the
first take, after a later render had been logged as the keeper and the first
had gone to the Trash.

**Change one input and you have a new song.** Same seed at 115s, 130s and
145s gave three songs in three keys. Pin `key:` once a take is liked, then
fix it in place rather than re-rendering.

**Fixing in place, by size of fault** (recipes in `docs/tasks.md`):

| Fault | Fix |
|---|---|
| a present line sung badly | `repaint` that range with `--song` |
| a whole line missing | insert whole bars of silence, repaint ~14s around them with only that range's lines, splice back just the new line |
| a few words missing | render the line alone as a short text2music take (same style, bpm, key), demucs its vocal, lay the words into the gap, +4 dB over a level match |
| an ad-lib to replace | splice from a clean stretch, or synthesise a short effect |

Short repaints (under ~10s) of specific words fail: balanced over silence
mumbles, aggressive gives a bare beat. Splice at instrumental moments, never
inside inserted silence, and scan each splice point's level for a hole.

**After the song:** the music video is built in `~/Coding/video-edit-automation`
(`projects/song/<slug>/`, `docs/video/projects/song.md`), and the release copy
and cover in the project's `RELEASE.md` here.
In the video, nothing pops on screen for less than a second: copy the newest
song's `video.py` (it carries the `MIN_HOLD` guard) and run its `--audit`
before every full render.

## Auditioning with the user

Render **two** takes bracketing the likely answer and send both, rather than
one guess per round trip. Each render is 60-90 seconds and a round trip is
longer than that.

Say the seed with every file. Feedback like "the second one, but darker" is
only actionable if the second one can be reproduced.

Use `takes: N` in the song file for variations - the first honours the pinned
seed and the rest explore.

## Never

- **Render before showing the lyrics.** The words are the cheap part to change.
- **Skip `plan`.** It costs nothing and it is the only thing standing between
  a typo and ninety seconds.
- **Claim a capability from `docs/tasks.md`'s "not available" list.** Say what
  the model cannot do; do not approximate it and present the result as the
  thing asked for.
- **Cover a recording the user does not own** and treat it as publishable. The
  MIT licence covers the model, not the source song. Say so once, then let it
  be their call.
- **Commit a render file (`projects/<slug>.md`).** It is git-ignored on
  purpose: the repo is public and recruiter-facing, and unreleased lyrics are
  work product. A song's folder (`projects/<slug>/`) is committed once the
  user is releasing it.
- Add AI attribution to a commit.
