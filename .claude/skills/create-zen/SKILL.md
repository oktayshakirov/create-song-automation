---
name: create-zen
description: Make a new sound-therapy album for tinnitushelp.me /zen - review the existing albums, offer what is missing and what could be added, pick the album with the user, generate and master the tracks (noise colours, notched noise, chimes), audition 2-minute previews, render the DistroKid WAVs, write a ChatGPT cover prompt, add the tinnitushelp.me promo bar and the site image, and once DistroKid approves, add the /zen page. Use when the user runs /create-zen, asks for a new zen album, sound album, noise album, white/pink/brown noise tracks, notched tracks or sound therapy for DistroKid, asks what albums are missing from /zen, or wants an album's cover or /zen page done. For session videos use video-tinnitus; for songs use create-song.
---

# Create a zen album

**One album per run, picked together.** The user chooses the album, the
track list and every audition; offer options with a recommendation and wait.

**Repo:** `~/Coding/create-song-automation`. Run from the repo root with
`.venv/bin/python -m zen.<tool>`. The rules, catalogue, backlog and every
measurement are in **`docs/zen.md`: read it first, every run.** Do not work
from memory of it.

## The run

1. **Catalogue.** `python -m zen.catalogue --store`. Say what is on /zen
   and anything made here but not yet live (an album waiting on DistroKid
   approval gets its site page first, see step 9).
2. **Offer, do not pick.** From `docs/zen.md`'s backlog plus what the
   catalogue shows is missing, offer three or four albums, each with what it
   is, what it needs built and why now, and a recommendation. Formats too
   (standard 10-minute album, playlist cut, session single). Wait for the
   pick.
3. **Track list.** Six or so tracks, names in the catalogue's style (two
   evocative words, no dashes), ordered so the album plays as an arc.
   Settle it in chat before writing a spec.
4. **Build what is missing.** If the album needs something `zen/noise.py`
   cannot make yet (the chime synth, for example), build it in `zen/` first,
   with a docstring saying what it is for and what it measured.
5. **Spec.** `zen/albums/<slug>.py`, copied from `colors_of_calm.py`:
   `TITLE`, `SLUG`, `SITE_SLUG`, `TRACKS`. Noise beds default to
   `drift_db=1.5` (the user's pick, 2026-11-18).
6. **Audition.** `python -m zen.album <spec> --preview`, plus
   `--variant N:field=value` for any open choice, so both ends are in hand.
   Send the MP3s (`SendUserFile`, attach) with a table of each track's band
   energy and LUFS, and say plainly what each one does and does not cover.
   Re-render until the user is happy, then delete the previews.
7. **Final.** `python -m zen.album <spec> --final`. Check every WAV is
   44.1 kHz 16-bit stereo and 10:00, LUFS within about 0.6 dB of each other,
   no sample peak above -1.5 dBFS. Put the measured table in the spec's
   docstring.
8. **Cover.** Write the ChatGPT prompt (two directions, plus the 3:2
   extension follow-up; `docs/zen.md`, "The cover"). When the user has saved
   `square` and `landscape` into `~/Desktop/<SLUG>/cover/`, run
   `python -m zen.cover <spec>` and **look at both outputs** next to an old
   cover before handing them over. The site image lands in
   `tinnitus-blog/public/images/` uncommitted.
9. **Release, then the page.** The user uploads to DistroKid. When they
   bring the store links, write `content/zen/<SITE_SLUG>.mdx` per
   `docs/zen.md`, "The site page", build it, show it, and commit and push
   in tinnitus-blog only on their word (a push there deploys production).
   Add the tracks to the video repo's `tinnitus-sounds.md`.
10. **Leave the skill better.** Mark the backlog row done, add new ideas
    that came up, and record every lesson as a dated line in the narrowest
    section of `docs/zen.md`. Commit the spec and doc changes here.

## Hard rules

- **No relief promises, no invented facts.** Health audience. Describe
  what a track measured, never what it will do for someone.
- **No long dashes and no curly quotes** in any title, description or page.
- **No ear close-ups and no text on the cover picture.** The bar is the only
  text.
- **Never upload to DistroKid or push the site** for the user.
- **Never commit audio.** WAVs and MP3s are git-ignored; finals live in
  `~/Desktop/<SLUG>/final/`.
- **No AI attribution in any commit.** Both repos are public.
