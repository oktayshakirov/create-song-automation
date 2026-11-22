"""Soft chimes that mark a breathing pattern over a noise bed.

Built for Breath and Bell (2026-11): a high chime where each inhale starts, a
lower one where each exhale starts, nothing on the holds. The same synth is
meant for the backlog's Starlight accents and Focus blocks, so the strike
(`strike`) is separate from the schedule (`breath_times`).

The strike is additive: a few inharmonic partials (ratios of a struck bar,
the 2.76 and 5.40 that make it read as a chime and not a sine beep) with a
soft 12 ms raised-cosine attack, so it never clicks, and an exponential decay
that is faster on the upper partials, so the bright edge goes first and what
rings on is the fundamental. A 2nd-order lowpass at 5 kHz keeps it off the
range where bright accents bother some listeners (docs/zen.md).

Timing is exact on purpose: it is a guide to breathe to, so only the
loudness of each strike varies (+- `jitter_db`), never when it lands.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import butter, sosfilt

from zen.noise import SR

# (frequency ratio, relative amplitude, decay time as a fraction of `ring`)
PARTIALS = ((1.0, 1.0, 1.0), (2.0, 0.18, 0.6), (2.76, 0.30, 0.45),
            (5.40, 0.08, 0.25))


@dataclass(frozen=True)
class Breath:
    """One breath in seconds: inhale, hold, exhale and the hold after it."""
    inhale: float
    hold: float = 0.0
    exhale: float = 0.0
    rest: float = 0.0

    @property
    def period(self) -> float:
        return self.inhale + self.hold + self.exhale + self.rest


@dataclass(frozen=True)
class Chimes:
    """Chimes on a breathing pattern.

    inhale_hz / exhale_hz  fundamental of each strike (A5 and D5: a fifth down
                           on the way out)
    level_db               strike peak against the bed's RMS level
    ring                   seconds for the fundamental to fall 60 dB
    lead_in                seconds of bed before the first breath
    """
    breath: Breath
    inhale_hz: float = 880.0
    exhale_hz: float = 587.33
    level_db: float = 6.0
    ring: float = 4.0
    lead_in: float = 5.0
    jitter_db: float = 0.75


def strike(hz: float, ring: float, seed: int) -> np.ndarray:
    """One chime, stereo float32, peak 1.0. The two channels get slightly
    different partial phases and a 0.3 cent detune, so it has width without
    moving."""
    n = int(ring * 1.1 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    att = int(0.012 * SR)
    env_a = np.ones(n)
    env_a[:att] = 0.5 - 0.5 * np.cos(np.pi * np.arange(att) / att)
    chans = []
    for ch, cents in ((0, -0.15), (1, 0.15)):
        f0 = hz * 2 ** (cents / 1200)
        x = np.zeros(n)
        for ratio, amp, dec in PARTIALS:
            tau = ring * dec / 6.91            # T60 to time constant
            x += amp * np.exp(-t / tau) * np.sin(2 * np.pi * f0 * ratio * t
                                                 + rng.uniform(0, 2 * np.pi))
        x = sosfilt(butter(2, 5000.0, btype="low", fs=SR, output="sos"), x * env_a)
        chans.append(x)
    x = np.stack(chans, axis=1)
    x[-int(0.2 * SR):] *= np.linspace(1, 0, int(0.2 * SR))[:, None]
    return (x / np.max(np.abs(x))).astype(np.float32)


def breath_times(duration: float, c: Chimes) -> tuple[list[float], list[float], int]:
    """(inhale starts, exhale starts, whole breaths). Only whole breaths: the
    last one ends at least `ring` seconds plus the 3 s fade before the end, so
    no strike is cut off and no breath is left hanging."""
    b = c.breath
    breaths = int((duration - c.lead_in - c.ring - 3.0) // b.period)
    ins = [c.lead_in + k * b.period for k in range(breaths)]
    outs = [t + b.inhale + b.hold for t in ins] if b.exhale else []
    return ins, outs, breaths


def render_chimes(duration: float, c: Chimes, seed: int) -> tuple[np.ndarray, int]:
    """The chime layer alone, stereo, peak 1.0 before jitter. Returns it with
    the number of whole breaths."""
    n = int(duration * SR)
    out = np.zeros((n, 2), dtype=np.float32)
    rng = np.random.default_rng(seed + 7000)
    ins, outs, breaths = breath_times(duration, c)
    for hz, times, s in ((c.inhale_hz, ins, 1), (c.exhale_hz, outs, 2)):
        if not times:
            continue
        sound = strike(hz, c.ring, seed + s)
        for t in times:
            i = int(round(t * SR))
            g = 10 ** (rng.uniform(-c.jitter_db, c.jitter_db) / 20)
            seg = sound[: n - i]
            out[i:i + len(seg)] += g * seg
    return out, breaths


def mix(bed: np.ndarray, c: Chimes, seed: int) -> tuple[np.ndarray, int]:
    """Bed plus chimes, the strike peak `level_db` above the bed's RMS.
    Measured on the bed after its fade-in, so the fades do not count."""
    k = min(len(bed) // 4, 10 * SR)
    rms = float(np.sqrt(np.mean(bed[k:-k] ** 2)))
    layer, breaths = render_chimes(len(bed) / SR, c, seed)
    return (bed + layer * rms * 10 ** (c.level_db / 20)).astype(np.float32), breaths
