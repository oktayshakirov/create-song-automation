---
name: create-song
description: Make a funny, catchy AI song about a trending topic - research what is trending, suggest topics, write a brief with sourced facts, pick an angle, write the hook first, then the verses, check the lyric sheet and export it for a music engine. Use when the user runs /create-song, asks for a song, parody, rap or trap track, lyrics or a hook, or wants to continue a song in projects/. Rendering audio is not built yet.
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
   renderer unless the user asks: the engine is undecided.
8. **Update the project README.** Update the Status line, the decisions made
   with a one-line reason each, and anything still open.
9. **Commit** the project folder, with lessons in the narrowest doc.

## Hard rules

- **Original lyrics and melody.** A title pun on a famous song is fine.
  Copying its lines, melody or signature hook is not. Put its known lines in
  `Banned:`. Never name an artist in the style prompt.
- **Jokes are true.** Exaggerate feelings, not facts. No invented quotes, and
  no unsourced claims about a company's motives.
- **No logos or official-looking art** for a song about a real product.
