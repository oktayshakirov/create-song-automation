# What the model can and cannot do

The installed `acestep-v15-turbo` reports its own capabilities:

```
$ python -m song_automation engine status
tasks:   text2music, repaint, cover, cover-nofsq
```

That list is the ground truth. Three further task types exist in the codebase
and are **base model only** - attempting them against turbo raises before a
request is sent.

## Available now

### text2music

Lyrics plus a style prompt in, song out. The normal path.

```bash
python -m song_automation render projects/night-shift.md -o ~/Desktop/songs
```

### cover - the same song in another genre

Feed existing audio plus a new style. `--strength` is the engine's
`audio_cover_strength`: low lets the new style dominate, high stays near the
original.

```bash
python -m song_automation cover ~/Desktop/songs/night-shift.flac \
  --style "acoustic folk, fingerpicked guitar, warm room, intimate male vocal" \
  --strength 0.2
```

| Strength | Effect |
|---|---|
| 0.2 | style transfer - keeps the shape, changes the genre |
| 0.5 | a recognisable arrangement of the original |
| 0.8-1.0 | close to the source; use for cleanup, not reinterpretation |

`--song` sends a song file's lyrics (and its style, unless `--style` is
given), so a cover can re-sing a take with changed lyrics. It does not add
room: a cover of "Come Back at Five" take 1 at 0.9, with the 16-line verse
split into two `[Verse]` blocks, kept the beat and length but still dropped
the missing couplet, lost the spoken bridge and garbled more words than the
source. Each cover's filename carries its strength and seed.

**On copyright:** the MIT licence covers the model, not the music you feed it.
Covering your own tracks is fine. Covering a commercial recording produces a
derivative work of something you do not own, which is a problem the moment you
publish it.

### repaint - fix one section

Regenerate a time range and leave the rest intact. Far cheaper than re-rolling
a whole song and losing the parts that worked.

```bash
python -m song_automation repaint ~/Desktop/songs/night-shift.flac \
  --from 18 --to 26 \
  --style "sparse breakdown, just 808 and reverb tail"
```

We always send `chunk_mask_mode="explicit"`. Without it the range is a hint and
the model picks its own region.

**Pass `--song` for any range with a vocal in it.** It sends the song file's
lyrics (and its style, unless `--style` overrides it). The engine treats
`lyrics` as an input for repaint too, and without it there are no words to
sing.

**A repaint cannot put back a line the take dropped.** It keeps the source's
length, so a section that was crammed stays crammed. Given the whole song's
lyrics it also does not know which lines belong in the range: on "Come Back
at Five" two repaints of a 28-second verse re-sang hook lines inside it and
garbled the missing couplet. Repaint fixes a bad performance of lines that
are there. A re-render at a longer `duration:` is a different song (see
Reproducibility), so for a missing line in a take you want to keep, make room
and splice:

1. Insert a whole number of bars of silence at a gap between two lines
   (`60 / bpm * 4 * bars` seconds; 4 bars at 140 bpm is 6.857s). Whole bars
   keep the beat grid on both sides of the insert.
2. Repaint a **wide** range around it, about 14 seconds, with `--song`
   pointed at a file holding only the lines that belong in that range.
3. Transcribe with word timestamps, and splice back only the stretch where
   the new lines are sung. Both files share one timeline, so cut both at the
   same instrumental moments with 50ms crossfades
   (`ffmpeg ... acrossfade=d=0.05`), and the rest stays the source take.
   Never cut inside the inserted bars: the source is silent there, and on
   "Come Back at Five" a splice 0.46s inside them left 0.4s of digital
   silence under the whole mix, which the user heard as two parts glued
   together. Check each splice point with a level scan in 50ms steps:
   any -180 dB frame is a hole. The repaint comes back sample-aligned with
   its source, but a few ms short at the end, so pad it before mixing.

What failed on "Come Back at Five" (2026-11-05), all on a 7-second range over
the inserted bars: balanced mode over silence sang mumble ("ah, ah, ah");
`--mode aggressive` gave a bare beat with no vocal; filling the bars with a
copy of the previous four bars of rap and repainting them gave mumble again.
A short range will not take specific lines. The wide repaint sang the
missing couplet clearly on one seed of three, but also dropped or doubled
the lines around it, which is why only the couplet is spliced back.

**A few missing words: generate the phrase and lay its vocal in** (2026-11-07).
"about to fly" was never sung on "Come Back at Five", and four repaints of
the verse (38.4-48.9s, the line's own lyrics) came back as mumble. What
worked in ten minutes: a 14-second text2music take of just that line,
repeated, with the song's style, `bpm:` and `key:` pinned; Whisper to find
the take that sings the words (1 of 4); demucs for its vocal; that phrase
laid into the master's gap, timed off the previous word's onset so it lands
on the beat, level-matched to the song's vocal on the same line and then
**+4 dB** - at a plain match Whisper could not hear it over the beat
without a prompt.

`--mode` sets the engine's `repaint_mode`: conservative, balanced (the
default) or aggressive.

Each repaint's filename carries its seed, so several attempts at one range
sit side by side.

**Find the range by transcribing, not by guessing.** A local Whisper pass
(`mlx-whisper`, `whisper-large-v3-turbo`) gives per-line timestamps and shows
which lines a take dropped or garbled. It caught a 16-line rap verse sung in
28 seconds with three lines missing and one sung twice.

## Not available without the base model

| Task | What it would do |
|---|---|
| `lego` | Generate one named track (vocals, drums, bass, guitar, keyboard, percussion, strings, synth, fx, brass, woodwinds) over a backing track |
| `extract` | Stem separation from a finished mix |
| `complete` | Arrange a partial idea into a full track |

This is the honest answer to "can I give it my own drum loop and have it build
around that" - yes, but only on the base model.

The cost of switching: another ~4.5GB download, and the base model wants 32-100
inference steps against turbo's 8, so renders go from ~80s to several minutes.
Check `df -h /System/Volumes/Data` first.

## Things the model will not do at all

- **Place a specific hit on a specific bar.** There is no step grid and no MIDI
  export. Rhythm is described, not sequenced.
- **Hold a consistent singer across sections.** There is no speaker ID or
  per-section voice assignment. `[call and response]`, `[harmonies]` and a
  caption saying "male and female duet" will nudge it, but vocal identity
  drifts. For a real duet, render the sections separately and splice them, or
  `repaint` one section's vocal.
- **Follow `guidance_scale`.** It is a no-op on turbo. Prompt adherence comes
  from the caption text alone.

## Reproducibility

The engine defaults `use_random_seed` to **true**, which silently discards any
seed you pass. We force it false whenever a seed is present, and every render
writes a `.json` sidecar recording the seed the engine actually used.

Workflow: render without a seed, listen, and if you like it paste the reported
seed into the song file to lock it.

```
To lock this take, add to projects/night-shift.md:
  seed: 4242
```

**A seed is only reproducible with everything else fixed.** Changing
`duration:` with the same seed gives a different song, not a stretched one:
seed 743206035 came out in B minor at 115s, G# minor at 130s and D minor at
145s, with different lines dropped each time. So a good take cannot be
lengthened to fit missing lines. Bracket the duration and pick a new take.

`takes: 4` renders four variations - the first honours a pinned seed, the rest
explore. Takes are sequential rather than batched, because `batch_size` holds
every variant in memory at once and this machine has no room for that.

## Output format

FLAC by default: 24-bit, 48kHz, around 1.4 Mbps. The engine's own default is
128kbps mp3, which is not a master. Override per song with `format:`
(`flac`, `wav`, `wav32`, `mp3`, `opus`, `aac`).

Renders land in the engine's temp directory, which it is free to clear, so
every take is copied out immediately.

## Source audio has to be staged

The engine rejects absolute paths outright unless they resolve inside the
system temp directory, and relative paths are interpreted against the server's
own working directory rather than yours:

```
HTTP 400: {"detail":"absolute audio file paths are not allowed"}
```

`cover` and `repaint` therefore copy the source into temp and pass the
realpath. It must be the *realpath* - on macOS `/var` is a symlink to
`/private/var`, and the server resolves before comparing, so an unresolved
path is refused. The staged copy is deleted after the job.

## Cover and repaint report no metadata

Both return `"N/A"` for duration, bpm and key instead of numbers, so the
duration of those renders is read back from the file with `ffprobe` rather
than believed from the engine.
