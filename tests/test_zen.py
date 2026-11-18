"""Zen tools: the noise colours land where the album copy says they do, and
the cover bar is where the reference cover has it. Fast, no network, no
ffmpeg."""

import numpy as np
from PIL import Image

from zen.cover import add_bar
from zen.noise import Bed, band_energy, drift_env, render, SR


def _bands(bed, seed=3):
    return band_energy(render(35.0, bed, seed))


def test_brown_is_mostly_below_200hz():
    assert _bands(Bed("brown"))["<200"] > 80


def test_white_tilted_still_reaches_high():
    b = _bands(Bed("white", tilt_hz=12000))
    assert b["4k-8k"] + b[">8k"] > 60


def test_green_has_nothing_high():
    b = _bands(Bed("green"))
    assert b["200-1k"] > 40 and b["4k-8k"] + b[">8k"] < 2


def test_notch_removes_the_band():
    x = render(35.0, Bed("white", notch_hz=6000), 3).mean(axis=1)[:SR * 30]
    S = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1 / SR)
    at = S[(f > 5950) & (f < 6050)].mean()
    near = S[(f > 2000) & (f < 3000)].mean()
    assert 10 * np.log10(near / at) > 25


def test_channels_are_decorrelated():
    x = render(10.0, Bed("pink"), 3)
    assert abs(np.corrcoef(x[:, 0], x[:, 1])[0, 1]) < 0.1


def test_drift_stays_within_depth():
    env_db = 20 * np.log10(drift_env(SR * 120, 7, 1.5))
    assert env_db.max() <= 1.5 + 1e-3 and env_db.min() >= -1.5 - 1e-3
    assert env_db.max() - env_db.min() > 1.0


def test_render_is_reproducible_by_seed():
    a = render(5.0, Bed("pink", drift_db=1.5), 11)
    b = render(5.0, Bed("pink", drift_db=1.5), 11)
    assert np.array_equal(a, b)


def test_bar_matches_reference_geometry():
    """At the size DistroKid gets: bar 42/800 of the height, text from x 103 to
    691 of 800 (measured off the Jungle Stillness cover)."""
    k = 3000 / 800
    img = add_bar(Image.new("RGB", (3000, 3000), (255, 255, 255)))
    a = np.asarray(img.convert("L")).astype(int)
    bar = round(42 * k)
    assert a[bar - 1].min() == 0 and a[bar].min() == 255
    cols = np.nonzero((a[:bar] > 110).any(axis=0))[0]
    # Glyph starts match the reference within 1 px; the last glyph ends at
    # ~687 against 691 because the reference is a soft upscaled webp.
    assert abs(cols.min() / k - 103) <= 1.5 and abs(cols.max() / k - 691) <= 5
