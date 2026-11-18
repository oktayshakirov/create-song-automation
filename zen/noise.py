"""Noise colours for sound-therapy albums, generated rather than recorded.

A noise colour is a specification, not a recording: pink is equal energy per
octave, brown falls 6 dB per octave. Generating it means any length, no loop
seam, and audio that is ours on every platform. The video repo has the same
engine for session beds (`video_automation/core/soundbed.py`); this is the
album copy, with grey noise and a slow level drift added.

**Nothing here is a treatment.** `band_energy` is how a track's description
stays honest: measure, then write the copy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import butter, iirnotch, lfilter, sosfilt

SR = 48000


def _white(n, rng):
    return rng.normal(0.0, 1.0, n).astype(np.float32)


def _pink(n, rng):
    """Equal energy per octave: the standard 3-pole IIR approximation."""
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1.0, -2.494956002, 2.017265875, -0.522189400]
    return lfilter(b, a, _white(n, rng)).astype(np.float32)


def _brown(n, rng):
    """-6 dB per octave. The 25 Hz highpass removes DC drift and the sub-bass
    that loudness normalisation cannot hear but still has to make room for:
    at 12 Hz the brown tracks clipped at -18 LUFS (measured, Colors of Calm)."""
    w = np.cumsum(_white(n, rng)).astype(np.float32)
    return sosfilt(butter(2, 25.0, btype="high", fs=SR, output="sos"), w).astype(np.float32)


def _green(n, rng):
    """Mid-weighted, the "nature" colour: pink band-passed 120 Hz-2.2 kHz."""
    return sosfilt(butter(2, [120.0, 2200.0], btype="band", fs=SR, output="sos"),
                   _pink(n, rng)).astype(np.float32)


def _a_weight_db(f):
    f2 = np.maximum(f, 1e-3) ** 2
    ra = (12194.0 ** 2 * f2 ** 2) / ((f2 + 20.6 ** 2)
                                     * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2))
                                     * (f2 + 12194.0 ** 2))
    return 20 * np.log10(ra) + 2.0


def _grey(n, rng):
    """White shaped by inverse A-weighting so every band sounds about equally
    loud. Boost capped at +15 dB, nothing lifted above 10 kHz. Measured: 56%
    of its energy sits above 8 kHz, so it is bright, not dark."""
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.clip(-_a_weight_db(f), -3.0, 15.0)
    g[f > 10000] = np.minimum(g[f > 10000], 0.0)
    g = 10 ** (g / 20)
    g[f < 20] = 0.0
    return np.fft.irfft(np.fft.rfft(rng.normal(0, 1, n)) * g, n).astype(np.float32)


COLOURS = {"white": _white, "pink": _pink, "brown": _brown,
           "green": _green, "grey": _grey}


@dataclass(frozen=True)
class Bed:
    """One generated track. `colour` is the base; the rest shapes it.

    tilt_hz   gentle 2nd-order lowpass (12000 softens white, 500 makes a sleep brown)
    notch_hz  notched therapy: a ~35 dB hole at this frequency (cascaded biquads)
    drift_db  slow random level wander, +- this many dB over 30-90 s (1.5 was
              the user's pick over steady, 2026-11-18)
    """
    colour: str = "pink"
    tilt_hz: float | None = None
    notch_hz: float | None = None
    notch_q: float = 6.0
    drift_db: float = 0.0


def drift_env(n: int, seed: int, depth_db: float) -> np.ndarray:
    """Noise lowpassed to ~1/45 Hz at a 10 Hz control rate, scaled to
    +-depth_db and interpolated up. A 0.02 Hz filter at 48 kHz is numerically
    useless, hence the control rate."""
    rate = 10
    m = n // (SR // rate) + 2
    r = np.random.default_rng(seed + 5000).normal(0, 1, m + rate * 600)
    r = sosfilt(butter(2, 1 / 45, btype="low", fs=rate, output="sos"), r)[rate * 600:]
    r = r / (np.max(np.abs(r)) or 1.0) * depth_db
    return (10 ** (np.interp(np.arange(n) / SR, np.arange(m) / rate, r) / 20)).astype(np.float32)


def render(duration: float, bed: Bed, seed: int, fade: float = 3.0) -> np.ndarray:
    """Stereo float32 at SR, peak 0.9, with equal-power fades.

    The channels come from different seeds: identical channels collapse to a
    point between the ears, which is fatiguing over ten minutes."""
    n = int(duration * SR)
    chans = []
    for ch in range(2):
        x = COLOURS[bed.colour](n, np.random.default_rng(seed + ch * 977))
        if bed.tilt_hz:
            x = sosfilt(butter(2, bed.tilt_hz, btype="low", fs=SR, output="sos"), x)
        if bed.notch_hz:
            b, a = iirnotch(bed.notch_hz, bed.notch_q, SR)
            x = lfilter(b, a, lfilter(b, a, x))
        chans.append(np.asarray(x, dtype=np.float32))
    x = np.stack(chans, axis=1)
    if bed.drift_db:
        x *= drift_env(n, seed, bed.drift_db)[:, None]
    k = int(fade * SR)
    ramp = np.sin(np.linspace(0, np.pi / 2, k, dtype=np.float32)) ** 2
    x[:k] *= ramp[:, None]
    x[-k:] *= ramp[::-1][:, None]
    return (x / (np.max(np.abs(x)) or 1.0) * 0.9).astype(np.float32)


def band_energy(x: np.ndarray) -> dict[str, float]:
    """Percent of energy per band, over 30 s. Run it before writing any copy
    about what a track masks: album descriptions have overclaimed before."""
    mono = x.mean(axis=1) if x.ndim > 1 else x
    seg = mono[:SR * 30] * np.hanning(min(len(mono), SR * 30))
    S = np.abs(np.fft.rfft(seg)) ** 2
    fr = np.fft.rfftfreq(len(seg), 1 / SR)
    tot = S.sum() or 1.0
    band = lambda lo, hi: round(100.0 * S[(fr >= lo) & (fr < hi)].sum() / tot, 1)
    return {"<200": band(0, 200), "200-1k": band(200, 1000), "1k-4k": band(1000, 4000),
            "4k-8k": band(4000, 8000), ">8k": band(8000, SR / 2)}
