# Writing the style prompt

The `style:` line is the single biggest lever on the result. The engine's own
songwriting guide calls the caption "the most important factor affecting
generated music", and on the turbo model that is literally true, because
`guidance_scale` - the dial that would otherwise control how strictly the model
follows the prompt - **does nothing on turbo**. The text is the only adherence
lever there is.

## Dimensions worth naming

Combine several. One word from each line is a good target.

| Dimension | Examples |
|---|---|
| Genre | pop, rock, jazz, hip-hop, R&B, folk, lo-fi, synthwave, drill, house |
| Emotion | melancholic, uplifting, energetic, dreamy, dark, nostalgic, intimate |
| Instruments | acoustic guitar, rhodes piano, 808 sub bass, synth pads, strings |
| Timbre | warm, bright, crisp, muddy, airy, punchy, lush, raw, polished |
| Era | 80s synth-pop, 90s grunge, 2010s EDM, vintage soul, modern trap |
| Production | lo-fi, hi-fi, live recording, studio-polished, bedroom pop |
| Vocal | male vocal, female vocal, breathy, raspy, falsetto, choir |
| Rhythm | slow tempo, mid-tempo, driving, laid-back, groovy, half-time |

The trap prompt that worked here:

```
dark trap, hard 808 sub bass with glides, triplet hi-hat rolls,
sparse minor piano, crisp layered snare, heavy reverb,
male rap vocal, confident flow
```

Eight clauses, five dimensions. "sad song" gets you nothing like this.

## Rules

1. **Specific beats vague.** "sad piano ballad with breathy female vocal" is a
   different instruction from "a sad song".
2. **Never put BPM, key or tempo in the style.** Use `bpm:`, `key:`, `time:`.
   Tempo words in the caption fight the parameter. The linter flags this.
3. **Do not stack contradictions.** "classical strings" plus "hardcore metal"
   degrades the output rather than blending. If you want a genre shift, write
   it as a progression: "starts with soft strings, turns to metal at the
   halfway point".
4. **Repetition is emphasis.** Mentioning an element twice pushes it forward in
   the mix.
5. **Detail trades away surprise.** A short caption gives the model room; a
   long one pins it down. Neither is better - decide which you want.
6. **512 characters is the cap.** Past that the model truncates.

## Keeping style and lyrics consistent

The model is bad at resolving conflicts between the two inputs. Before
rendering, check:

- instruments in `style:` match any `[guitar solo]`-type tags in the lyrics
- the emotion in `style:` matches the energy tags
- the vocal description in `style:` matches the vocal tags

A caption saying "intimate acoustic" against lyrics tagged `[explosive]` will
produce something that commits to neither.

## Metadata: when to set it, when to leave it

Leave it blank and the LM infers it, usually sensibly - it chose G minor
unprompted on the first test here.

| Set it when | Field |
|---|---|
| You have a tempo in mind | `bpm` (30-300; slow 60-80, mid 90-120, fast 130-180) |
| You want a specific colour | `key` (C, G, D, Am, Em are the most stable) |
| It is a waltz or a shuffle | `time` (`3/4`, `6/8`) |
| It has to match other material | `bpm` + `duration` |

## Duration

Rough arithmetic, from the engine's guide:

- intro/outro: 5-10s each
- instrumental section: 5-15s
- 2 verses + 2 choruses: 120-150s minimum
- the same plus a bridge: 180-240s
- full song with intro and outro: 210-270s

Slower BPM needs *more* duration for the same lyrics. When unsure, go longer -
a song that is too short rushes the vocal, which is the most common way a take
is ruined. The linter warns below ~2s per lyric line.
