# Come Back at Five

A funny trap song about hitting Claude's usage limit. It is the first song
in this repo, and the "Claude's Plan" riff that started the idea is a title
pattern for later, not this song's title.

**Status:** the user approved the lyrics on 2026-11-03, after one round of
changes. Rendered with ACE-Step 1.5 locally on 2026-11-03; take 1 in the
Takes table is the keeper. Next: settle the "twenty one percent" line (row 2
is secondhand), then the release checklist in `docs/originality.md`. Before
release, the facts marked snippet or memory in `SOURCES.md` still need
checking. The user delegated the angle and hook choice for the first draft.

## Handoff (2026-11-03, cloud session to local)

Where it stands:

- **Lyrics: approved.** `song.md` passes `check` with one warning kept on
  purpose: the spoken bridge line "The docs don't say you're absolutely
  right" runs long, which is fine for a spoken line. Do not rewrite the
  lyrics unless the user asks.
- **Branch:** `song/come-back-at-five`, draft PR
  oktayshakirov/create-song-automation#1. It is not merged into `main` yet.
- **Export:** regenerate it with
  `python -m song_automation export projects/usage-limit/song.md`. `out/` is
  git-ignored, so the cloud session's copy did not come across.
- **Render:** the user generates the audio on their own machine, in their
  usual way. The repo's `docs/engines.md` still says the engine is
  undecided, so ask which engine and settings they use, then record it there.
  If the engine has form limits, check them against `export.py`'s assumed
  1000-character style prompt and 5000-character lyrics.

Next:

1. Export, then generate takes the user's way. Expect garbled ad-libs and
   dropped spoken parts, and regenerate rather than accept them.
2. Log every kept take in **Takes** below: engine, model version, ID or file
   path, date, and what is good or bad. A take cannot be regenerated.
3. If a take goes wrong because of the lyrics or style prompt, fix
   `song.md`, re-run `check`, and record the lesson in `docs/engines.md` or
   `docs/trap.md`.
4. Before release, upgrade `SOURCES.md` rows 2 and 8 to 12. The cloud
   session's network blocked the source sites. Row 2 ("twenty one percent,
   then a hundred, one prompt") rests on a single report: confirm it or
   soften the line. Then work through the release checklist in
   `docs/originality.md`.

## Why this topic

Picked on 2026-11-02 from four trending Claude topics: usage limits, the
"stop bullying Claude" policy memes, the IPO numbers, and the "Claude is
down, I forgot how to code" outage memes. Usage limits won because the pain
is **universal among people who use Claude a lot**. Everyone who would share
the song has hit it, and it stayed in the news all year: a drain bug in
March, complaint megathreads through spring, and app-review spikes in
September. See `SOURCES.md`.

The other three topics are still usable as verse bars or ad-libs, because
they are the same audience's in-jokes.

## Audience

Heavy Claude and Claude Code users, developers who "vibe code", and AI
Twitter and Reddit. They already know the jargon (Max plan, Opus, context
window, "your limit resets at…"), so the lyrics can use it without
explaining.

## Decided

- **Genre:** trap, funny, played straight (see `docs/trap.md`).
- **Render:** ACE-Step 1.5 turbo, locally on the user's M2 Pro through the
  sibling `song-automation` repo (decided 2026-11-03). It is free, and takes
  are reproducible by seed.
- **Length:** about 90 seconds, per the user. That means one verse, three
  hooks and a spoken bridge, with no second verse.
- **Angle:** a flex song that falls apart. A vibe coder brags about the Max
  plan, gets limited mid-flex, and grieves. Picked because the fall is the
  joke, and it lets the beat stay menacing.
- **Hook and title:** "Limit reached, come back at five". It is 7
  syllables, rides the "ai" vowel, and ties in the five-hour window.
- **Final hook twist:** the weekly limit hits right after the reset. It is
  true (`SOURCES.md` row 9), and it is the biggest laugh, so it goes last.
- **Outro loops to the intro** ("one more prompt"), so the song works on
  repeat in short-form clips.
- **Review round 1 (user):** "Uber for cats" became "Tinder for horses" with
  a "(Fireship)" ad-lib, a nod to the programming YouTube channel. The user
  added a laptop couplet: the laptop overheats, then sleeps while unattended
  and interrupts the task. It sits before the usage-bar lines, so the rerun
  is what burns the limit. The verse is now 16 bars, about 95 seconds in
  all.
- **Generation:** the cloud session planned Suno by hand because its container
  had no GPU. Superseded on 2026-11-03: the user renders locally with
  ACE-Step (see Render).

## Open

- The user's review of the draft.
- The verse line "twenty one percent, then a hundred, one prompt" rests on a
  single snippet-level report (row 2). Confirm it, or soften it to a
  feeling.
- Rows 8 to 12 need upgrading before release.
- Alternative angles, if the draft does not land: a breakup song with the
  rate limiter, five stages of grief counting down to the reset, or Claude's
  side, apologising cheerfully for the fourth time today.

## Facts the jokes can use

Every row in `SOURCES.md` is currently **snippet** or **memory** status: seen
in search summaries, not read. **Read and upgrade a row before a lyric
depends on it.**

## Takes

Every take renders from `ace-step.md`, the ACE-Step translation of
`song.md`: the same lyric lines with ACE-Step tags and header. Set its
`seed:` and `duration:` to a row's values to reproduce that take.

| # | Engine + model | Seed, file | Date | Notes |
|---|---|---|---|---|
| 1 | ACE-Step 1.5, DiT `acestep-v15-turbo`, LM `acestep-5Hz-lm-0.6B`, 8 steps | seed 743206035, 145s, D minor, 140 bpm; `~/Desktop/songs/come-back-at-five-s743206035-145s.flac` (sha256 `287c6cd14f6e1d7c…`) | 2026-11-03 | **Kept.** Good: the vocal is clear; the laptop couplet and "you're absolutely right, of course, boss" land, and so do the spoken bridge, the Thursday twist and the outro loop. Bad, per a Whisper transcript (check by ear): drops "Woke up, terminal open, coffee hot" and "Ten agents running, I'm the boss of the bots", and runs "Compacting conversation" straight into "had the whole team proud", losing "now my genius is gone" and "Max plan flexing". |
