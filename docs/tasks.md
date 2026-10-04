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
