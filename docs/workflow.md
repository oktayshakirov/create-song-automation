# The run

Every song, every step. Nothing here has been measured yet, because no song
has shipped from this repo. When the first one does, replace guesses with
what it taught, the way the sibling repos' docs are written.

## 1. Trend

Search what is trending about the subject this month, not from memory.
Prefer news coverage and the community itself (Reddit, X, Hacker News) over
SEO blogs. Offer three or four topics, each with:

- what happened, with a date and a link
- why it is funny, in one line
- a hook seed: the phrase the chorus could hang on

Recommend one. **The user picks.**

## 2. Brief

Create `projects/<slug>/` with `README.md` and `SOURCES.md`. The brief holds
the topic, the audience (who already finds this funny?), the angle, and the
open decisions. Every factual claim a joke might use gets a `SOURCES.md` row
**before** any lyric is written (see `sourcing.md`).

## 3. Angle and title

One sentence: who is singing, to whom, about what. A song about a usage limit
can be the user grieving, the user in denial, Claude apologising, or a
breakup song with the rate limiter. Each is a different song. Offer two or
three, recommend one, and let the user pick.

The title is usually the hook phrase.

## 4. Hook first

Write the hook before anything else (see `hooks.md`). Offer three different
hooks, not three versions of one. Run `flow` on them. The user picks, and
then the hook is frozen: verses are written to serve it.

## 5. Structure

Write the section skeleton and target lengths into `song.md` (see `trap.md`).
The hook is written once, and its later `[Hook]` tags stay empty.

## 6. Verses

Each verse is a run of jokes in an escalating order, with the strongest last
before the hook. Every factual line gets a `> SOURCES row N` note. Write the
ad-libs in as you go: in trap they carry half the comedy.

## 7. Check

```bash
python -m song_automation check projects/<slug>/song.md
python -m song_automation flow  projects/<slug>/song.md
```

Fix every error. Read every warning and keep it only on purpose. Then read
the whole thing out loud, in rhythm, over a metronome at the target tempo.
The checker cannot hear.

## 8. Export and render

```bash
python -m song_automation export projects/<slug>/song.md
```

Rendering is not built yet (see `engines.md`). Until it is, paste
`out/<slug>/suno.txt` into the engine by hand.

## 9. Takes

Generate several takes. For every take worth keeping, add a row to the
project's `Takes` table: the engine, its model version, the song ID or link,
the date, and what is good and bad about it. A take is not reproducible, so
the row is the only record.

## 10. Lessons

Anything learned goes in the narrowest doc that covers it. For example, an
engine quirk goes in `engines.md`, a hook that failed goes in `hooks.md`, and
a decision about this one song goes in its own `README.md`.
