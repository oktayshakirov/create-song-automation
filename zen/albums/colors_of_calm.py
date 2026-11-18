"""Colors of Calm - six noise colours, bright to dark. Released 2026-11.

The first album made with /create-zen. The /zen catalogue had one noise album
(White Noise Therapy) and no pink, grey, green or brown at all, while the
site's most specific sound post is brown-vs-white noise.

Decisions (2026-11-18):
- Drifting over steady: the user picked Rose Haze with a +-1.5 dB slow level
  wander over the steady version, for every track.
- Grey Balance measured brighter than its name (56% above 8 kHz); kept.
- Cover: Option B (layered dusk hills, one colour per layer) from ChatGPT,
  square and a 3:2 extension of the same picture.

Measured on the released WAVs (percent of energy per band, LUFS):

| # | track        | <200 | 200-1k | 1k-4k | 4k-8k | >8k | LUFS  |
|---|--------------|------|--------|-------|-------|-----|-------|
| 1 | Silver Veil  |  1.7 |    6.6 |  24.9 |  32.2 | 34.5| -18.0 |
| 2 | Rose Haze    | 42.0 |   19.8 |  16.5 |   8.6 | 13.1| -18.2 |
| 3 | Grey Balance | 15.7 |    6.9 |   7.8 |  13.3 | 56.3| -18.6 |
| 4 | Green Meadow | 17.3 |   55.9 |  26.2 |   0.5 |  0.0| -18.0 |
| 5 | Deep Brown   | 87.2 |   10.3 |   1.9 |   0.3 |  0.3| -18.0 |
| 6 | Velvet Night | 92.5 |    7.5 |   0.0 |   0.0 |  0.0| -18.0 |

The released files were rendered by an earlier script with the same colours,
seeds and mastering; re-rendering from this spec gives the same sound, not
byte-identical samples.
"""

from zen.album import Track
from zen.noise import Bed

TITLE = "Colors of Calm"
SLUG = "colors-of-calm"
SITE_SLUG = "noise-colors"          # /zen/noise-colors, public/images/noise-colors.jpg

DRIFT = 1.5
TRACKS = [
    Track(1, "Silver Veil", Bed("white", tilt_hz=12000, drift_db=DRIFT), 11),
    Track(2, "Rose Haze", Bed("pink", drift_db=DRIFT), 23),
    Track(3, "Grey Balance", Bed("grey", drift_db=DRIFT), 37),
    Track(4, "Green Meadow", Bed("green", drift_db=DRIFT), 41),
    Track(5, "Deep Brown", Bed("brown", drift_db=DRIFT), 53),
    Track(6, "Velvet Night", Bed("brown", tilt_hz=500, drift_db=DRIFT), 67),
]
