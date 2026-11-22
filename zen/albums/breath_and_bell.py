"""Breath and Bell - six breathing patterns, each marked by soft chimes over
a noise bed: a high chime where the inhale starts, a lower one where the
exhale starts, nothing on the holds.

Picked 2026-11-22. The patterns are the ones the session videos use
(video-edit-automation docs/video/projects/tinnitus.md), ordered as an arc:
even breaths first, then the holds, then the long exhales. 6-6-6-6 and the
physiological sigh were left out (the hardest hold; a few breaths, not ten
minutes). Titles are evocative only; each pattern is named on the page.

Decisions (2026-11-22):
- Chimes at +6 dB (strike peak over the bed's RMS), picked over 0 and +12.
- Pink bed for 1-4, brown for 5-6, so the album darkens toward the close.
- A5 (880 Hz) on the inhale, D5 (587 Hz) on the exhale, 4 s ring.

Measured on the released WAVs (percent of energy per band over a 30 s
window from 0:30, the bed alone in brackets, LUFS, sample peak dBFS):

| # | track        | pattern | breaths | <200 | 200-1k | 1k-4k | 4k-8k | >8k | LUFS  | peak |
|---|--------------|---------|---------|------|--------|-------|-------|-----|-------|------|
| 1 | Open Window  | 5-5     | 58 | 41.7 (42.3) | 20.2 (19.7) | 16.8 | 8.5 | 12.8 | -18.2 | -5.1 |
| 2 | Steady Tide  | 6-6     | 49 | 39.3 (41.0) | 23.4 (20.2) | 16.2 | 8.4 | 12.7 | -18.2 | -5.7 |
| 3 | Three Stones | 4-4-4   | 49 | 39.8 (40.0) | 20.8 (20.5) | 17.2 | 8.8 | 13.5 | -18.2 | -5.4 |
| 4 | Quiet Square | 4-4-4-4 | 36 | 41.0 (41.9) | 21.5 (20.0) | 16.2 | 8.4 | 12.8 | -18.2 | -5.5 |
| 5 | Falling Leaf | 4-8     | 49 | 83.0 (88.9) | 14.5 (8.8)  |  1.9 | 0.3 |  0.2 | -18.0 | -2.1 |
| 6 | Night Harbor | 4-7-8   | 30 | 86.2 (89.3) | 11.6 (8.5)  |  1.7 | 0.3 |  0.2 | -18.0 | -2.0 |

The chimes add 1 to 6 points in 200 Hz-1 kHz and next to nothing above
4 kHz: a breathing guide over a balanced (1-4) or dark (5-6) bed, not a
high-frequency masker. Each track: 5 s of bed, then whole breaths, the last
strike ringing out before the 3 s fade.
"""

from zen.album import Track
from zen.chime import Breath, Chimes
from zen.noise import Bed

TITLE = "Breath and Bell"
SLUG = "breath-and-bell"
SITE_SLUG = "breathing-chimes"      # /zen/breathing-chimes, public/images/breathing-chimes.jpg

DRIFT = 1.5
BED = Bed("pink", drift_db=DRIFT)
DARK = Bed("brown", drift_db=DRIFT)     # the close darkens (user's pick, 2026-11-22)

TRACKS = [
    Track(1, "Open Window", BED, 101, Chimes(Breath(5, 0, 5))),
    Track(2, "Steady Tide", BED, 113, Chimes(Breath(6, 0, 6))),
    Track(3, "Three Stones", BED, 127, Chimes(Breath(4, 4, 4))),
    Track(4, "Quiet Square", BED, 131, Chimes(Breath(4, 4, 4, 4))),
    Track(5, "Falling Leaf", DARK, 149, Chimes(Breath(4, 0, 8))),
    Track(6, "Night Harbor", DARK, 157, Chimes(Breath(4, 7, 8))),
]
