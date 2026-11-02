# Originality and release

Not legal advice. These are the working rules, and the release section is a
list of things to check before releasing, not settled answers.

## Riffing on a famous song

The inspiration for the first song is a viral pattern: a famous track's title
bent into a joke about something else ("God's Plan" becoming "Claude's
Plan"). What the repo takes from that is the **idea**, a title pun and a
genre, and nothing else.

- **Do:** use a title pun, the genre, a similar tempo and mood, and the
  general idea of a parody.
- **Do not:** reuse lyric lines, the melody, the signature hook rhythm, or
  the distinctive beat. Even a parody that copies a melody needs the
  rights-holder's licence in most places.
- **Never put an artist's or song's name in a style prompt.** Describe the
  sound instead. Engines commonly refuse artist names, and it is the most
  direct way to get something too close.
- Put the reference song's well-known lines in the sheet's `Banned:` field.
  `check` then fails if one sneaks back in.

## Trademarks

"Claude" and "Anthropic" are trademarks. A comedy song about a product is a
normal thing to make. Even so:

- Do not use the logo, or anything that looks like official artwork, on the
  cover.
- Do not imply the song is official or endorsed.
- Keep jokes about the product's behaviour, not claims about the company that
  are not sourced (see `sourcing.md`).

## Before release

Decide these **before** generating the final takes, because some depend on
which plan the take was made under:

- **Engine terms.** Who owns a generation, and whether commercial use
  (streaming royalties, monetised video) is allowed, often depends on whether
  the account was on a paid plan at the time of generation. Check the
  engine's current terms and record the answer in `engines.md`.
- **Distributor rules for AI music.** Distributors and platforms have their
  own AI-content and disclosure policies, and they change. Check the chosen
  one's current rules.
- **Disclosure.** Label it as AI-generated wherever the platform asks.
