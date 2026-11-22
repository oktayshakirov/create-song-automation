"""Zen tools: the noise colours land where the album copy says they do, and
the chimes land on the breath. Fast, no network, no ffmpeg."""

import numpy as np

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


from zen.chime import Breath, Chimes, breath_times, mix, strike  # noqa: E402


def test_strike_starts_soft_and_rings_out():
    """No click at the onset, and gone well before the next strike."""
    x = strike(880.0, 4.0, 1)[:, 0]
    assert abs(x[0]) < 1e-3
    assert np.max(np.abs(x[int(4.0 * SR):])) < 10 ** (-50 / 20)


def test_breaths_are_whole_and_land_on_the_phases():
    c = Chimes(Breath(4, 7, 8))
    ins, outs, n = breath_times(600.0, c)
    assert n == len(ins) == len(outs) == 30
    assert ins[0] == c.lead_in and outs[0] == c.lead_in + 11
    assert ins[-1] + 19 + c.ring + 3 <= 600


def test_no_exhale_chime_without_an_exhale():
    assert breath_times(60.0, Chimes(Breath(5)))[1] == []


def test_chimes_sit_level_db_over_the_bed():
    bed = render(30.0, Bed("pink"), 3)
    x, _ = mix(bed, Chimes(Breath(5, 0, 5), jitter_db=0.0, level_db=6.0), 3)
    k = 10 * SR
    rms = np.sqrt(np.mean(bed[k:-k] ** 2))
    added = np.max(np.abs((x - bed)))
    assert abs(20 * np.log10(added / rms) - 6.0) < 0.1
