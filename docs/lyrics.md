# Lyrics and the song file

## The file format

One markdown file per song: header for the knobs, body for the words.

```markdown
# Night Shift
style: dark trap, hard 808 sub bass with glides, triplet hi-hat rolls, ...
bpm: 140
key: F minor
time: 4/4
language: en
duration: 40
seed: 4242
---
[intro]

[verse]
Clock hit twelve and the city went quiet
...
```

Header keys: `style` (required), `bpm`, `key`, `time`, `language`, `duration`,
`seed`, `steps`, `instrumental`, `format`, `takes`. An unknown key is an error
rather than a silent no-op, because the engine ignores what it does not
recognise and you would not find out until the render sounded wrong.

## Lyrics are a script, not just words

Anything in `[brackets]` is a directive to the model, not sung. Use them to
shape how the track unfolds.

**Structure:** `[Intro]` `[Verse]` `[Pre-Chorus]` `[Chorus]` `[Bridge]`
`[Outro]` `[Hook]` `[Refrain]` `[Post-Chorus]`

**Dynamics:** `[Build]` `[Drop]` `[Breakdown]`

**Instrumental:** `[Instrumental]` `[Guitar Solo]` `[Piano Interlude]`

**Endings:** `[Fade Out]` `[Silence]`

**Vocal delivery:** `[raspy vocal]` `[whispered]` `[falsetto]`
`[powerful belting]` `[spoken word]` `[harmonies]` `[call and response]`
`[ad-lib]`

**Energy:** `[high energy]` `[low energy]` `[building energy]` `[explosive]`
`[melancholic]` `[euphoric]` `[dreamy]` `[aggressive]` `[anthemic]`

Combine with a hyphen, but keep it short: `[Chorus - anthemic]` works,
`[Chorus - anthemic - stacked harmonies - epic - powerful]` does not. Long
style descriptions belong in `style:`.

A tag the linter does not recognise gets a warning, because an unrecognised
bracket may simply be sung aloud.

## Syllables matter more than you would expect

The model aligns syllables to beats. Lines in the same section should sit
within about two syllables of each other; 6-10 per line is the working range.

The linter counts them and warns when a section is lopsided. It caught this on
the first real song here:

```
[hook] line lengths vary a lot (6-14 syllables)
```

Evening those four lines out to 9 syllables each is the difference between a
hook that lands and one that crams.

## Other devices

- **UPPERCASE** reads as intensity: `WE ARE THE CHAMPIONS` vs `walking home`
- **(Parentheses)** become background vocals: `We rise together (together)`
- **Stretched vowels** (`aliiive`) sometimes work; the effect is unstable
- **Blank lines** between sections. Clear separation helps the model

## Avoiding AI-flavoured lyrics

From the engine's own guide, red flags:

| Flag | What it looks like |
|---|---|
| Adjective stacking | "neon skies, electric hearts, endless dreams" |
| Rhyme chaos | forced rhymes that break the sense of the line |
| Blurred boundaries | a thought running across a structure tag |
| No breathing room | lines too long to sing in one breath |
| Mixed metaphors | water, then fire, then flight - nothing to hold onto |

One core metaphor per song, explored from several angles, beats five metaphors
touched once each.

## Writing in a language other than English

Fifty are supported. Set `language:` - and spell the words properly, with
umlauts and accents intact. The model phonemises from spelling, so ASCII
transliterations like `wuerd` for `würd` or `gaeb` for `gäb` invite a
mispronunciation.

The syllable linter is language-aware but only roughly:

- It counts vowel groups, which works in English and is workable in German
  and the Romance languages, landing within a syllable or two.
- The silent terminal `-e` rule applies to English and French only. German
  `Kette` and `Name` are two syllables each, and treating them as one
  undercounts every line ending in a schwa.
- For non-Latin scripts (`ja`, `zh`, `ko`, `ar`, `he`, `hi`, `ru`, `th` and
  the rest) the count means nothing, so the check is skipped and says so.
  Judge those line lengths by ear.

Since the lint only ever compares lines inside one section against each other,
a consistent bias is harmless. An inconsistent one is not, which is why the
rules above are per-language rather than global.

## Languages

Fifty, plus `unknown`. Set `language:`, though it is usually detected from the
lyrics themselves.

```
ar az bg bn ca cs da de el en es fa fi fr he hi hr ht hu id is it ja ko la
lt ms ne nl no pa pl pt ro ru sa sk sr sv sw ta te th tl tr uk ur vi yue zh
```
