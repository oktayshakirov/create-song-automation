---
name: create-song
description: Write lyrics and render them as finished songs locally with the ACE-Step pipeline in song-automation. Use when the user runs /create-song, asks for a song, a track, a beat or an instrumental, wants lyrics written or turned into music, wants a song in a particular genre, wants an existing track re-recorded in another style or one section of it fixed, or asks about song prompting, structure tags or render settings. For narration use audio-book; for videos use video-crypto / video-tinnitus / video-drone.
---

# Create song

Write lyrics, render them as songs on this machine, for free. Local ACE-Step
1.5, lossless output, every take reproducible by seed.

## Read first

The pipeline and every measurement live in `~/Coding/song-automation`.
**Do not re-derive any of this; read it.**

| Before you | Read |
|---|---|
| write a `style:` line | `docs/prompting.md` |
| write a word of lyrics | `docs/lyrics.md` |
| pick tags, sections or syllable counts | `docs/lyrics.md` |
| promise stems, a duet or per-instrument control | `docs/tasks.md` |
| cover or remix existing audio | `docs/tasks.md` |
| debug the engine, or budget disk and time | `docs/engine.md` |

A song lives in `projects/<slug>.md`, which is **git-ignored** - the repo is
public and lyrics are work product. `examples/night-shift.md` is the committed
reference. Renders go to `~/Desktop/songs/`.

## Ask first

**Whose lyrics, and do they already exist?** Writing a song is an afternoon;
rendering one is ninety seconds. Do not start drafting because the user said
"make me a song" when what they wanted was a re-render of one they have.

**What genre, specifically?** "Trap" is a start, not a brief. Get two or three
reference points before writing the `style:` line, because that line is the
single biggest lever on the result and rewriting it means re-rendering.

## The order of work

Each step has a gate. Do not pass one to save time.

1. **Brief.** Genre, mood, tempo feel, vocal character, and roughly how long.
   Settle this in chat before touching a file.
2. **Lyrics.** Draft and **show them before rendering.** They are the cheapest
   thing to change and the most expensive thing to get wrong. A register
   problem found on the page costs a rewrite; found in the render it costs
   every take since.
3. **`plan`.** Always. It is instant and it predicts the bad take.
4. **Render one take, no seed.** Listen before committing to a direction.
5. **Lock the seed.** Paste the reported seed into the song file. Now the take
   is repeatable and the next change is isolated to the thing you changed.
6. **Iterate narrowly.** One bad section is a `repaint`, not a re-roll - see
   `docs/tasks.md`. Re-rolling throws away the parts that worked.

## Commands

```bash
cd ~/Coding/song-automation
python -m song_automation engine start          # ~7.2GB on first run
python -m song_automation engine status         # up? weights resident? which tasks?
python -m song_automation new "Night Shift"
python -m song_automation plan   projects/night-shift.md
python -m song_automation render projects/night-shift.md -o ~/Desktop/songs
python -m song_automation cover   <audio> --style "..." --strength 0.2
python -m song_automation repaint <audio> --from 18 --to 26 --style "..."
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
- **Commit anything from `projects/`.** It is git-ignored on purpose. The repo
  is public and recruiter-facing; lyrics are work product.
- Add AI attribution to a commit.
