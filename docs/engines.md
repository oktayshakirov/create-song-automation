# Engines

**Rendering is not built, and the engine is undecided.** The user deferred
it: lyrics first, render later. This page lists the options and what each
would need, so that decision can be made with the song in hand.

## Options

| | Suno | ACE-Step (local) |
|---|---|---|
| Cost | credits; paid plan needed for commercial use (check current terms) | free, open source |
| Trap rap vocals | strongest of the options at time of writing | usable for drafts; behind on rap |
| Runs where | suno.com, by hand | a GPU machine or Apple Silicon |
| Automation | no official public API: manual paste | scriptable end to end |
| Input | title, style prompt, exclude prompt, tagged lyrics | style tags plus tagged lyrics |

The export format, with `[Section]` tags and ad-libs in parentheses, works
for both, so the lyric sheet does not depend on the choice.

## Suno form limits

`export.py` assumes a 1000-character style prompt and 5000-character lyrics,
which were believed correct for Suno v4.5. **Not yet checked in this repo.**
Confirm on the first real generation, then record the model version and the
real limits here.

## When rendering is built

- Keep audio out of git (it is already ignored), but record every kept take
  in its project's `Takes` table, because a take cannot be regenerated.
- Record the engine's model version with each take. The same prompt on a
  new model version is a different song.
