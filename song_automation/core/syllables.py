"""Syllable counts for flow checking.

A heuristic, not a dictionary. It is right on most words and off by one on
some, which is fine for its only job: spotting a line that is far longer than
its neighbours and will be rushed or mangled when sung. Do not use it to
decide that two lines with 9 and 10 syllables are uneven.

Words that matter and come out wrong go in OVERRIDES, checked by ear.
"""
from __future__ import annotations

import re

OVERRIDES = {
    "ai": 2,          # spoken as letters
    "api": 3,
    "anthropic": 3,
    "claude": 1,
    "every": 2,
    "business": 2,
    "fire": 1,
    "hour": 1,
    "hours": 1,
    "our": 1,
    "prompt": 1,
    "prompts": 1,
    "tokens": 2,
    "usage": 2,
}

# Syllables in the spoken name of each letter, for acronyms.
_LETTER = {c: 1 for c in "abcdefghijklmnopqrstuvxyz"}
_LETTER["w"] = 3

_WORD = re.compile(r"[A-Za-z']+|\d+")


def word(w: str) -> int:
    if w.isdigit():
        # Digits are flagged by the checker anyway; count them as words so
        # the flow check still roughly works on a draft.
        return max(1, len(w))
    if w.isupper() and 2 <= len(w) <= 5 and w.lower() not in OVERRIDES:
        return sum(_LETTER.get(c, 1) for c in w.lower())
    w = w.lower().replace("'", "")
    if w in OVERRIDES:
        return OVERRIDES[w]
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    stem = re.sub(r"(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$", "", w)
    stem = re.sub(r"^y", "", stem)
    # The suffix rule spares a final "le" on purpose, so its e still counts:
    # bot-tle, lit-tle.
    return max(1, len(re.findall(r"[aeiouy]{1,2}", stem)))


def line(text: str) -> int:
    return sum(word(w) for w in _WORD.findall(text))
