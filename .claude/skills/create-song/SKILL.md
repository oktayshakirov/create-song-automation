---
name: create-song
description: Make a funny, catchy AI song about a trending topic - research what is trending, suggest topics, write a brief with sourced facts, pick an angle, write the hook first, then the verses, check the lyric sheet and export it for a music engine (rendered locally with ACE-Step in the sibling song-automation repo). Use when the user runs /create-song, asks for a song, parody, rap or trap track, lyrics or a hook, or wants to continue a song in projects/.
---

# Create a song

**One song per run, hook first.** The hook is the song: everything else is
written to serve it, after it is frozen.

**Repo:** this one. Run Python from the repo root:
`python -m song_automation <check|flow|export> projects/<slug>/song.md`.

## Read these first, every run

| Step | Read |
| --- | --- |
| **The run, every step** | **`docs/workflow.md`** |
| Writing the hook | `docs/hooks.md` |
| Genre, structure, flow | `docs/trap.md` (or the genre's own doc, if one exists) |
| Facts in jokes | `docs/sourcing.md` |
| Riffing on a famous song, release | `docs/originality.md` |
| Rendering | `docs/engines.md` |

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
   renderer here unless the user asks. The engine is ACE-Step,
   driven from the sibling repo (see `docs/engines.md`).
8. **Render** in the sibling repo with its `/create-song` skill (song-automation):
   transcribe every take, keep every take until the user names the final,
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
