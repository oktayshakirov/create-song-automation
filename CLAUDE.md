# create-song-automation

Funny, catchy AI songs about trending topics. The workflow is the
`/create-song` skill (`.claude/skills/create-song/SKILL.md`), and the rules are
in `docs/`, starting at `docs/workflow.md`. Read them, rather than working
from memory.

- One folder per song in `projects/<slug>/`: `README.md` (brief, decisions,
  takes), `SOURCES.md` (a row per factual claim), `song.md` (lyric sheet).
- Run `python -m song_automation check <sheet>` after every lyric edit, and
  `python -m pytest tests` after every engine edit.
- **Lyrics are original.** Riff on a famous song's title or vibe, but never
  reuse its lines, melody or signature hook, and never put an artist's name in
  a style prompt. See `docs/originality.md`.
- **Jokes are true.** A factual punchline needs a `SOURCES.md` row with a
  status. Do not upgrade a status you did not check.
- **Suggest, do not pick.** Topic, angle and hook are the user's choice:
  offer options with a recommendation.
- Rendering is not built here. The user renders with ACE-Step 1.5 locally,
  through the sibling `song-automation` repo (see `docs/engines.md`). Do not
  build a renderer here unless asked.
- Record any lesson in the narrowest doc that covers it, and add a
  `CHANGELOG.md` entry for engine changes.
