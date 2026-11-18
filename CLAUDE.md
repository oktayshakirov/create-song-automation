# create-song-automation

Funny, catchy AI songs about trending topics, rendered locally with ACE-Step
1.5, and sound-therapy albums for tinnitushelp.me. The workflows are the
`/create-song` and `/create-zen` skills (`.claude/skills/`), and the rules are
in `docs/`, starting at `docs/workflow.md` for songs and `docs/zen.md` for
albums. Read them, rather than working from memory.

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
- Rendering lives here (`render`, `cover`, `repaint`; `docs/engine.md`). The
  render file `projects/<slug>.md` is git-ignored: unreleased lyrics. The
  `.venv` holds mlx-whisper and the zen tools' numpy/scipy/soundfile/Pillow.
- **Never add AI attribution to a commit.** The repo is public and
  recruiter-facing.
- Record any lesson in the narrowest doc that covers it, and add a
  `CHANGELOG.md` entry for engine changes.
