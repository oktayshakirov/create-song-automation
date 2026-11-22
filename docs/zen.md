# Zen albums

Sound-therapy albums for [tinnitushelp.me/zen](https://www.tinnitushelp.me/zen),
released through DistroKid to Spotify, Apple Music, YouTube Music, Amazon
Music and Deezer, then given a page on the site. The `/create-zen` skill runs
this. Everything below is a measurement or a decision, dated.

## Who it is for

People with tinnitus, many of them anxious, some with hyperacusis (sound
sensitivity). So:

- **Never promise relief, cure or healing**, in a track title, the store
  description or the page. "Sounds people use to mask tinnitus" is the
  register. The site's own rules forbid inventing a study or a statistic.
- **Measure before describing.** A track's description is its `band_energy`,
  not a mood word. Two older albums were sold "for masking" and measured as
  comfort beds with almost nothing above 1 kHz.
- **High, bright accents irritate some listeners.** Keep them sparse and
  quiet, and point to a plain album on the same page.
- **No long dashes (em or en) and no curly quotes** anywhere: titles,
  descriptions, the page. Plain `-`.

## The catalogue (as of 2026-11-18)

`python -m zen.catalogue --store` prints the live state. Store titles differ
from page names, so search a platform for the store title.

| page | store title | what it is |
|---|---|---|
| `/zen/notched-sounds` | Pitch Perfection | notched noise, 5 to 9 kHz in 1 kHz steps |
| `/zen/white-noise` | Infinite Horizons | white-noise textures (Tranquil Zenith carries ~53 pings/min near 5 kHz) |
| `/zen/nature-sounds` | Earth's Lullaby | waterfall, river, rain, crickets |
| `/zen/water-sounds` | Aqua Rhapsody | streams, waves, lagoon, brook |
| `/zen/bird-sounds` | Feathered Tunes | birdsong |
| `/zen/cat-purr-sounds` | Purrfect Calm | cat purrs |
| `/zen/fire-sounds` | Fireside Comfort | fireplace (one track with a music box) |
| `/zen/morning-sounds` | Morning Unfolding | coffee, shower, hair dryer, laundry |
| `/zen/evening-sounds` | Background Blur | lo-fi, fan, fire with rain, brown noise with pads |
| `/zen/quiet-universe` | Quiet Universe | space ambience |
| `/zen/jungle-stillness` | Jungle Stillness | jungle ambience |
| `/zen/noise-colors` | Colors of Calm | white, pink, grey, green, brown, sleep brown, all drifting (live 2026-11-21) |
| `/zen/breathing-chimes` (planned) | Breath and Bell | six breathing patterns marked by chimes over pink (1-4) and brown (5-6); finals and cover done 2026-11-22, waiting on DistroKid |

**The source files of the older albums are gone from disk.** Recorded sounds
cannot be re-cut; anything new is generated (`zen/noise.py`) or comes from a
file the user supplies.

## The backlog

Offer from here, then add anything the conversation turns up. Mark a row
done when its album ships.

| idea | what | needs | status |
|---|---|---|---|
| Noise colours | pink, brown, green, grey, soft white, sleep brown | nothing | **done: Colors of Calm, 2026-11** |
| Breathing with chimes | noise bed, soft high chime on each inhale, lower one on each exhale, silence on holds. 5-5, 6-6, 4-4-4, 4-4-4-4, 4-8, 4-7-8 | `zen/chime.py` (built 2026-11-22) | **done: Breath and Bell, built 2026-11-22**, page after DistroKid |
| Breathing, volume 2 | the two patterns left out: 6-6-6-6 and the physiological sigh (as short repeated sets with rests), maybe over white or green | nothing (`zen/chime.py`) | open |
| Starlight accents | white or pink noise with sparse, quiet high melodic accents (music box, glass, celesta) at irregular 20-60 s gaps, so nothing sounds looped. Closest to the user's "white noise with little high-pitched melodies" | `zen.chime.strike` plus a random scheduler (and a few more pitches) | open, now cheap: the synth exists |
| Notched, volume 2 | notches at 3, 4, 10, 11 and 12 kHz, plus a notched pink at 6 kHz. Covers 3 to 12 kHz with volume 1 | nothing (`Bed(notch_hz=)`) | open. Same careful framing as volume 1 |
| Focus blocks | 25 min pink or brown, a soft chime at the end, 5 min break tracks between | the chime synth | open |
| Sleep edition | 1-hour versions of the darkest beds, no accents, long fade | check store limits on track length first | open. YouTube may be the better home for 8-10 hours |

Never re-release old audio as a compilation or "best of": duplicate audio is
treated as spam by Spotify and DistroKid.

## Formats

- **Standard album:** 5 to 7 tracks of about 10 minutes. Every album so far.
- **Playlist cut:** the same beds at 3 to 4 minutes. Reportedly Spotify pays
  no royalties on noise tracks under 2 minutes and none on any track below
  1,000 streams a year. Verify both against Spotify's current rules before
  choosing this.
- **Session single:** a one-hour video session's audio released as a single
  in the week the video goes up, cross-linked.

## Generating

`zen/noise.py` makes the beds: `Bed(colour, tilt_hz, notch_hz, drift_db)`,
colours white, pink, brown, green and grey. A spec in `zen/albums/<slug>.py`
lists the tracks (`TITLE`, `SLUG`, `SITE_SLUG`, `TRACKS`); copy
`colors_of_calm.py`. Seeds are per track, so a take is reproducible.

Measured on Colors of Calm (percent of energy per band):

| bed | <200 | 200-1k | 1k-4k | 4k-8k | >8k | reads as |
|---|---|---|---|---|---|---|
| white, tilt 12 kHz | 2 | 7 | 25 | 32 | 35 | bright, covers high tinnitus |
| pink | 42 | 20 | 17 | 9 | 13 | balanced |
| grey | 16 | 7 | 8 | 13 | 56 | brighter than the name suggests |
| green | 17 | 56 | 26 | 0.5 | 0 | warm mid, nothing high |
| brown | 87 | 10 | 2 | 0.3 | 0.3 | comfort, not masking |
| brown, tilt 500 Hz | 93 | 8 | 0 | 0 | 0 | sleep |

**Drift:** the user picked a slow random level wander of +-1.5 dB over 30-90
s over a steady bed (2026-11-18). It shows as LRA 1.4-1.8 LU against 0.3 on
an old steady track. Default every new noise album to `drift_db=1.5` unless
the user says otherwise.

## Chimes

`zen/chime.py` (built for Breath and Bell, 2026-11-22): `strike(hz, ring)`
is an additive struck-bar chime (partials 1, 2, 2.76, 5.40, the upper ones
decaying faster, 12 ms raised-cosine attack, 5 kHz lowpass);
`Chimes(Breath(in, hold, out, rest))` schedules it, a high strike (A5, 880
Hz) where each inhale starts and a lower one (D5, 587 Hz) where each exhale
starts, holds silent. A spec adds it as `Track(..., chimes=Chimes(...))`;
`--variant N:field=value` reaches chime fields too (`1:level_db=12`).

- **Level: +6 dB** strike peak over the bed's RMS, the user's pick over 0
  and +12 (2026-11-22). At +6 the chimes add only 1 to 6 points in
  200 Hz-1 kHz and nothing measurable above 4 kHz: sparse strikes barely
  move a 30 s band average, so a chime album is described by its bed.
- **Timing is exact**, only strike loudness varies (+-0.75 dB): it is a
  guide to breathe to. 5 s of bed first, then whole breaths only, the last
  strike ringing out before the fade, so a 10-minute track holds fewer
  breaths than 600 / period (4-7-8: 30, box: 36).
- **Brown beds leave more peak headroom used**: chimes over brown peaked at
  -2.0 dBFS against -5 over pink, since brown's RMS sits closer to its
  peak after the 25 Hz highpass. Still under the -1.5 ceiling; a louder
  chime over brown may hit it and stop short of -18 LUFS.

## Mastering

`zen.album` does all of this; these are the reasons.

- **-18 LUFS integrated**, matching the catalogue (Cloudscape Serenity
  measured -17.7). Streaming normalises anyway; this keeps an album even
  back to back.
- **Sample peak ceiling -1.5 dBFS.** A track that cannot reach -18 under it
  stops short rather than being limited.
- **Brown is highpassed at 25 Hz.** At 12 Hz both brown tracks peaked at
  +1.6 dBTP at -18 LUFS: LUFS barely counts sub-bass, but it eats headroom.
  At 25 Hz they reach -18 with peaks around -2 dB. Nobody hears below 25 Hz
  on headphones.
- **3 s equal-power fades** at both ends.
- **Final: 44.1 kHz 16-bit WAV**, triangular dither, 10:00 exactly, about
  106 MB a track. Previews: 2-minute 320k MP3.

## Auditioning

Render 2-minute previews of every track and send them with the measured
numbers. For an open choice, render **both** ends (`--variant N:field=value`)
in the same round; the user answers "this one" precisely when both are in
hand. Delete the previews once the choice is made.

## The cover

**Existing covers:** a full-bleed picture (a bird, a cat, fire, a jungle, an
astronaut, a marble swirl, clouds), mostly photographic, **no title or text on
the picture**, and the promo bar on top.

**The user generates the image in ChatGPT.** Write them a prompt that:

- names the album and what it holds, and describes one picture that carries
  the concept (Colors of Calm: dusk hills, one colour per layer, bright at the
  horizon to dark in front);
- asks for a **square 1:1** image, photographic, calm, soft light, no harsh
  contrast and no neon;
- keeps the important detail in the **middle 60%** of the height and the
  **top 8% plain**, because the bar covers it;
- says **no text, letters, numbers, logos, watermarks, people, faces or
  ears** (no ear close-ups is a standing rule on this brand);
- offers two directions (one abstract, one photographic) so they can pick;
- adds a follow-up for the same chat: "Extend this exact image into a 3:2
  landscape version. Keep the scene, colours, lighting and style identical,
  and only add more of the same scene on the left and right. No text."

They save both as `~/Desktop/<SLUG>/cover/square` and `.../landscape` (any
image format; ChatGPT gives 1254x1254 and 1536x1024). Check the folder
first: on Breath and Bell (2026-11-22) only the square came back, saved as
`cover`. Rename it; with no landscape, `zen.cover` centre-crops the square
to 3:2, which works when the subject sits mid-height as the prompt asks. `python -m zen.cover
<spec>` then writes:

| file | size | for |
|---|---|---|
| `~/Desktop/<SLUG>/cover/<SLUG>-cover-3000.jpg` | 3000x3000, bar, q95 | DistroKid |
| `~/Coding/tinnitus-blog/public/images/<SITE_SLUG>.jpg` | 1200x800, no bar, q80, ~75 KB | the /zen page (shown 16:9 and 4:3 with object-fit cover, and as the share image) |

**The bar**, measured off the Jungle Stillness cover and checked against it
at 800 px (glyph starts within 1 px): black, 5.25% of the height,
`www.tinnitushelp.me` in Courier New regular, grey 214, spanning 73.5% of the
width, centred. No stroke: the reference's ink is 2031 px at 800, no stroke
gives 1958, stroke 1 gives 2526.

## DistroKid

The user uploads; never upload for them.

- The six (or so) WAVs plus the 3000 cover. Track titles exactly as in the
  spec. Same artist name as the earlier albums (ask if unknown).
- Genre ambient or new age. Instrumental.
- **YouTube Content ID off.** Our own session videos use these beds, and
  YouTube reportedly does not accept noise or nature audio into Content ID
  anyway.
- Approval and store links take days. The site page waits for them.

## The site page

Only once the user has the store links. In `~/Coding/tinnitus-blog`:

- `content/zen/<SITE_SLUG>.mdx`. Copy the structure of the newest page
  (`jungle-stillness.mdx`): frontmatter `title, date, description, image,
  tags: ['sounds']`; an opening `<Blockquote>`, one `<Image>`,
  `<StreamingPlatforms>` with all five links, `###` sections, a track table
  (`| **Track** | description |`, each description true to its measured
  bands), the "How to enjoy" `#### <Highlighter>` list, two `<AdComponent />`
  and a closing `<Blockquote>`. Internal links bold with `/blog/` and `/zen/`
  prefixes.
- The image is already at `public/images/<SITE_SLUG>.jpg`.
- `yarn build` must pass (the site is a static export on Cloudflare
  Workers). Then check the page on the dev server (`npm run start`).
- **Publish the measured band table on the page** (Colors of Calm, the
  first page to do it, 2026-11-21): one row per track, the five bands as
  rounded percentages, plus a "which one for your tinnitus" list that reads
  straight off it. Check every claim in the copy against the numbers before
  commit: the first draft said two tracks were the "only" ones above 4 kHz
  when a third had 22% there.
- A six-column table is fine on a phone: the page wraps tables in a
  horizontally scrolling box, and the page itself does not scroll sideways
  (checked at 375 px).
- The view counter 404s on the dev server (`/api/views/...`); it only
  exists in the production Worker.
- **A push to `main` there is a production deploy** and fires a social
  notification. Commit and push only when the user says so, and never with
  AI attribution.
- Add the album's tracks as unused rows to
  `~/Coding/video-edit-automation/docs/video/projects/tinnitus-sounds.md`, so
  session videos can use them.
