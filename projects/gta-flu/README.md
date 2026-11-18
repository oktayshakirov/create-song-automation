# GTA Flu

A funny trap song about calling in sick for GTA VI's launch day. The second
song in this repo, built the same way as Come Back at Five (`usage-limit/`).

**Status:** lyrics approved 2026-11-17 with no changes. Rendered the same day.
Master approved by ear (user, 2026-11-17: "its good, lets use this one"): take 4
with real coughs and sneezes, vocal-matched reverb and phone-line calls (4s in
Takes). The Short uses a cut without the middle hook (S). Next: the music video
(long on 4s, Short on S) and thumbnails, then the release kit.
**Update 2026-11-18:** videos approved by the user ("perfect") after two review
rounds; the user publishes YouTube by hand from `RELEASE.md`. Videos in `~/Desktop/songs/video/`, art in `~/Desktop/songs/art/`.
`check` passes with two warnings kept on purpose (long spoken lines in the
intro and bridge, the same call as Come Back at Five's bridge).

## Decided (user, 2026-11-17)

- **Angle and hook:** GTA flu, "Can't come in, I got the GTA flu".
- **Genre:** A, Come Back at Five's comedy trap played straight, plus an 80s
  Miami synth lead for Vice City. Keeps the two songs a series.
- **Length:** about 2:10 (130s), both verses kept.
- **Speed:** everything as fast as possible, to land in launch week.
- **Title:** "GTA Flu". The user wants GTA in the title, everywhere,
  including the DistroKid title (DistroKid may query a brand name in a
  title; it is the user's call).
- **Names:** Lucia, Florida Man, Silksong, Vice City stay in.
- **No extra jokes** from the user this time.

## Why this topic

The user asked for GTA VI on 2026-11-17. The game launches Thursday
2026-11-19, so the trend peaks this week: preorders are the biggest ever
reported, pre-load strained UK broadband, and "we got X before GTA 6",
"GTA flu" and PS5-grooming memes are everywhere (see `SOURCES.md`). A song
that lands in launch week rides that; one that lands in December is late.

## Audience

Everyone who has waited since 2013: gamers in their twenties who were kids
when GTA V came out, and the meme crowd on TikTok, Reels and Shorts. They
know Lucia, Leonida, Vice City, the delays and the memes without explanation.

## Angles offered (2026-11-17)

1. **GTA flu (recommended, drafted).** Calling in sick for launch day. Hook:
   "Can't come in, I got the GTA flu". One metaphor (the wait as illness)
   holds every joke, it is a real trend this week, and the final twist (the
   boss has it too) lands like the weekly-limit twist did.
2. **Thirteen years.** The aging joke: twelve when GTA V came out, a back
   that cracks now. Hook seed: "Thirteen years, I got old for this (old)".
   Used as Verse 1 of the draft instead.
3. **Before GTA 6.** A list song: "We got everything before GTA Six". Funny
   once, but a list hook explains rather than repeats, and the meme is
   retiring this week. Used as a line in Verse 1.

## Draft decisions

- **Structure:** Come Back at Five's: spoken intro (phone call to the boss),
  hook, verse, hook, spoken midnight-countdown bridge, final hook with a
  twist, outro looping to the intro. The 16-line verse is split into two
  8-line `[Verse]` blocks to test the idea in `docs/engines.md`.
- **Callbacks to the first song:** the bridge's "better graphics than
  outside" and the outro's "(here we go again)".

## Open

- Upgrade SOURCES rows 8, 11 (Lucia, Florida Man) and 12 before release.

## Takes

| # | Engine + model | Seed, file | Date | Notes |
|---|---|---|---|---|
| 1 | ACE-Step 1.5, DiT `acestep-v15-turbo`, LM `acestep-5Hz-lm-0.6B`, 8 steps | seed 3890300975, 130s, E minor (LM's pick), 140 bpm; `~/Desktop/songs/gta-flu-take1.flac` (sha256 `893eacd96aa708eb…`) | 2026-11-17 | **In the Trash since 2026-11-17 (user: delete what we don't need).** Whisper: first hook sings only its first 4 lines (both takes do). Verses rushed into one run-on flow; drops the "fall became May / polish" couplet and "Thursday the nineteenth"; verse 2 lines 2-3 garbled. Hook 2 compressed. Final hook complete enough, twist sung. |
| 2 | same | seed 314139510, 130s, E minor, 140 bpm; `~/Desktop/songs/gta-flu-take2.flac` (sha256 `e8fba7f4b0f57478…`) | 2026-11-17 | **In the Trash since 2026-11-17 (user: delete what we don't need).** Whisper: first hook 4 lines only. Verse 1 clear line by line but drops "GTA Five dropped" opening words and the polish couplet; verse 2 mostly clear, "broadband heart attack" lost. Hook 2 scrambled. Bridge and final hook clear, twist sung. |
| 3 | same | seed 851536291, 150s, E minor, 140 bpm; `~/Desktop/songs/gta-flu-150-take1.flac` (sha256 `1a34c3e59e6890cc…`), song file was `gta-flu-150.md`, now merged into `gta-flu.md` | 2026-11-17 | **In the Trash since 2026-11-17 (user: delete what we don't need).** Whisper: first hook scrambled (no "two-twelve gig fever", hook line repeated). Verse 1 drops both the polish and the towel/dust couplets. Verse 2 complete. Hook 2 good. Final hook drops "Whole office got the GTA flu". |
| 4 | same | seed 1757101606, 150s, F# minor, 140 bpm; `~/Desktop/songs/gta-flu-150-take2.flac` (sha256 `296885c1758746ea…`), song file `projects/gta-flu.md` (seed pinned there) | 2026-11-17 | **Most complete; the user's favourite, source of the final.** Kept: the SFX edit is built from it. Whisper: the only take with the whole 8-line first hook. Verse 1 has the polish and towel couplets but merges/garbles its first three lines ("twenty-five / back is old", "aliens / Silksong"). Verse 2 drops "Just a code… wallet in shock" and "Thursday the nineteenth". Hook 2 complete. Final hook: "two-twelve" sung twice, "Whole office" line garbled. |
| **4s** | take 4 + real SFX | `~/Desktop/songs/gta-flu-take4-sfx.flac` (sha256 `7e1c249470f2ee5e…`); recipe in its `.flac.json` and `~/.local/share/song-automation/gta_flu_sfx.py` | 2026-11-17 | **Current master, approved by ear (user, 2026-11-17: "very good").** The user asked for real coughs and sneezes instead of sung ones. 12 sung "cough cough" / "achoo" ad-libs taken out (take 4's htdemucs vocal stem subtracted in each slot, 20 ms fades) and Mixkit clips laid in (free SFX licence; files and source in `~/.local/share/song-automation/sfx/mixkit/`). Sneezes (2212, 2213) at the removed vocal's level +1 dB: the user liked them. Coughs (2221, 2222, 2224) round 2: the user found them "a bit silent and plain" and distant, so they are processed for body and presence (70 Hz high-pass, +4 dB at 180 Hz, +4 dB at 3.2 and 6 kHz, 5:1 compression) and laid in at +5 dB, each capped so the song peaks at -0.3 dBFS (round 2's first build normalised the whole song down; fixed). Round 3 (user: coughs "too loud" at +5, and reverb on both once the beat drops "to match the lyrics and sound funnier"): coughs at +2.5 dB; every clip after the drop (13.6s) gets a synthetic stereo reverb (RT60 2.2s, 25 ms pre-delay, darkening tail, 200 Hz low cut, wet as loud as dry). The intro cough stays dry: it is a phone call. A first try at RT60 1.6s and wet -5 dB left the tail 25 dB under the beat within 0.25s, too quiet to hear. Round 4 (user: SFX "too loud", reverb "too much", "make it match the lyrics", and make the calls "sound like it's on the phone"): the reverb is matched to the sung vocal, whose line ends fall 20 dB in 0.25-0.5s (RT60 0.9s, wet -14 dB); coughs at 0 dB, sneezes at -1 dB, and no clip may be more than 1 dB louder over its slot than the sung ad-lib it replaced. The intro call (0-13.5s, its cough included) and the a cappella outro ("Boss? here we go again", 144.95s on) have the voice swapped for a telephone version (8 kHz codec round trip, 300-3400 Hz, 1.5 kHz bump, light drive) with -60 dB line hiss, a synthesised pickup click before each call, a hang-up clunk on the drop and three call-ended beeps at 147.7s that loop back to the intro. Whisper reads both calls cleanly. Every sample outside the 12 slots, their reverb tails and the two calls is take 4. Dropped lines left as sung (verse 1 opening merged, two verse 2 lines missing, "Whole office" mumbled). |
| **S** | short cut of 4s, for the Short | `~/Desktop/songs/gta-flu-short.flac` (sha256 `0e023707e22af069…`), 129.4s; recipe in its `.flac.json` and `~/.local/share/song-automation/gta_flu_short.py` | 2026-11-17 | **The Short's audio** (user: keep the opening and ending hooks, drop the middle one). Hook 2 cut: 82.78s joined to 103.35s, exactly 48 beats (12 bars) apart, the offset where the instrumental on both sides matches best; "Can't come" before the join taken out with the vocal stem; 15 ms crossfade. Re-transcribed: "…Florida Man" (cough) runs straight into the bridge's "refresh". |
