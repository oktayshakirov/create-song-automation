"""The song file format: frontmatter for the knobs, body for the lyrics.

A song is one markdown file so that the words and the settings that produced
them stay together and diff cleanly. The parser is deliberately strict about
the handful of things the engine silently ignores - a typo in a key name
should be an error here, not a surprise in the render.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Languages the engine's vocal model accepts (acestep/constants.py).
VALID_LANGUAGES = {
    "ar", "az", "bg", "bn", "ca", "cs", "da", "de", "el", "en",
    "es", "fa", "fi", "fr", "he", "hi", "hr", "ht", "hu", "id",
    "is", "it", "ja", "ko", "la", "lt", "ms", "ne", "nl", "no",
    "pa", "pl", "pt", "ro", "ru", "sa", "sk", "sr", "sv", "sw",
    "ta", "te", "th", "tl", "tr", "uk", "ur", "vi", "yue", "zh",
    "unknown",
}

KNOWN_KEYS = {
    "style", "bpm", "key", "time", "language", "duration", "seed",
    "steps", "instrumental", "format", "takes",
}

# Tags the model reads as directives rather than singing. Not exhaustive -
# the model tolerates free text in brackets - but these are the documented
# ones, and a tag outside this set is worth a warning.
STRUCTURE_TAGS = {
    "intro", "verse", "pre-chorus", "chorus", "bridge", "outro", "hook",
    "build", "drop", "breakdown", "instrumental", "guitar solo",
    "piano interlude", "fade out", "silence", "refrain", "post-chorus",
}
VOCAL_TAGS = {
    "raspy vocal", "whispered", "falsetto", "powerful belting",
    "spoken word", "harmonies", "call and response", "ad-lib",
}
ENERGY_TAGS = {
    "high energy", "low energy", "building energy", "explosive",
    "melancholic", "euphoric", "dreamy", "aggressive", "anthemic",
}

TAG_RE = re.compile(r"\[([^\]]+)\]")


class SongError(ValueError):
    """The song file is malformed or asks for something the engine rejects."""


@dataclass
class Song:
    """A parsed song file, resolved into engine parameters."""

    title: str
    style: str
    lyrics: str
    path: Optional[Path] = None
    bpm: Optional[int] = None
    key: str = ""
    time_signature: str = ""
    language: str = "en"
    duration: Optional[float] = None
    seed: Optional[int] = None
    steps: int = 8
    instrumental: bool = False
    audio_format: str = "flac"
    takes: int = 1
    extra: Dict[str, str] = field(default_factory=dict)

    @property
    def slug(self) -> str:
        s = re.sub(r"[^a-z0-9]+", "-", self.title.lower()).strip("-")
        return s or "untitled"

    def to_payload(self, seed: Optional[int] = None) -> Dict[str, object]:
        """Build the /release_task body for this song.

        ``use_random_seed`` is forced False whenever we have a seed, because
        the engine defaults it True and will otherwise discard the seed.
        """
        chosen = seed if seed is not None else self.seed
        payload: Dict[str, object] = {
            "task_type": "text2music",
            "prompt": self.style,
            "lyrics": "[Instrumental]" if self.instrumental else self.lyrics,
            "instrumental": self.instrumental,
            "vocal_language": self.language,
            "inference_steps": self.steps,
            "batch_size": 1,
            "audio_format": self.audio_format,
            "use_random_seed": chosen is None,
        }
        if chosen is not None:
            payload["seed"] = chosen
        if self.bpm is not None:
            payload["bpm"] = self.bpm
        if self.key:
            payload["key_scale"] = self.key
        if self.time_signature:
            payload["time_signature"] = self.time_signature
        if self.duration is not None:
            payload["audio_duration"] = self.duration
        return payload


def parse_song(path: str | Path) -> Song:
    """Read and validate a song markdown file."""
    path = Path(path)
    if not path.exists():
        raise SongError(f"no song file at {path}")
    return parse_song_text(path.read_text(encoding="utf-8"), path=path)


def parse_song_text(text: str, path: Optional[Path] = None) -> Song:
    if "---" not in text:
        raise SongError(
            "song file needs a '---' line separating the header from the lyrics"
        )
    header_part, _, body = text.partition("\n---")
    header_lines = header_part.strip().splitlines()
    if not header_lines:
        raise SongError("song file is empty")

    title_line = header_lines[0].strip()
    if not title_line.startswith("#"):
        raise SongError("first line must be the title, as '# Title'")
    title = title_line.lstrip("#").strip()
    if not title:
        raise SongError("title is empty")

    fields: Dict[str, str] = {}
    for line in header_lines[1:]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise SongError(f"header line is not 'key: value': {line!r}")
        key, _, value = line.partition(":")
        key = key.strip().lower()
        if key not in KNOWN_KEYS:
            raise SongError(
                f"unknown header key {key!r}. Known keys: {sorted(KNOWN_KEYS)}"
            )
        fields[key] = value.strip()

    lyrics = body.lstrip("\n").rstrip() + "\n"
    instrumental = _as_bool(fields.get("instrumental", "false"))
    if not instrumental and not lyrics.strip():
        raise SongError(
            "no lyrics. Write them under the '---', or set 'instrumental: true'."
        )

    style = fields.get("style", "").strip()
    if not style:
        raise SongError(
            "'style:' is required - it is the single biggest lever on the "
            "result. See docs/prompting.md."
        )

    language = fields.get("language", "en").strip().lower()
    if language not in VALID_LANGUAGES:
        raise SongError(
            f"language {language!r} is not supported. "
            f"Supported: {', '.join(sorted(VALID_LANGUAGES))}"
        )

    audio_format = fields.get("format", "flac").strip().lower()
    if audio_format not in {"flac", "wav", "wav32", "mp3", "opus", "aac"}:
        raise SongError(f"format {audio_format!r} is not one the engine writes")

    return Song(
        title=title,
        style=style,
        lyrics=lyrics,
        path=path,
        bpm=_as_int(fields.get("bpm"), "bpm", 30, 300),
        key=fields.get("key", "").strip(),
        time_signature=fields.get("time", "").strip(),
        language=language,
        duration=_as_float(fields.get("duration"), "duration", 10, 600),
        seed=_as_int(fields.get("seed"), "seed", None, None),
        steps=_as_int(fields.get("steps"), "steps", 1, 200) or 8,
        instrumental=instrumental,
        audio_format=audio_format,
        takes=_as_int(fields.get("takes"), "takes", 1, 8) or 1,
    )


def lint(song: Song) -> List[str]:
    """Return human-readable warnings. Never raises; nothing here is fatal.

    These encode the engine's documented failure modes, so that a bad render
    is predicted before it costs 80 seconds rather than diagnosed after.
    """
    warnings: List[str] = []

    # The style prompt is capped at 512 characters by the model.
    if len(song.style) > 512:
        warnings.append(
            f"style is {len(song.style)} chars; the model caps the caption at 512 "
            "and will truncate."
        )
    if len(song.lyrics) > 4096:
        warnings.append(
            f"lyrics are {len(song.lyrics)} chars; the model caps them at 4096."
        )

    # Tempo and key belong in the dedicated fields, not the caption: the
    # engine's own guide says putting them in the caption degrades control.
    lowered = song.style.lower()
    if re.search(r"\b\d{2,3}\s*bpm\b", lowered):
        warnings.append(
            "style mentions BPM. Use the 'bpm:' field instead - tempo in the "
            "caption fights the parameter."
        )
    if re.search(r"\b(major|minor)\b", lowered) and not song.key:
        warnings.append(
            "style names a key but 'key:' is unset. Use the field so the "
            "engine does not have to guess."
        )

    # guidance_scale is a no-op on turbo, so prompt adherence comes only from
    # the text. Vague captions therefore drift badly on this model.
    if len(song.style.split(",")) < 3 and len(song.style.split()) < 8:
        warnings.append(
            "style is thin. On the turbo model there is no guidance dial, so "
            "the caption is the only adherence lever - name genre, instruments, "
            "timbre and vocal character."
        )

    if not song.instrumental:
        tags = [t.strip().lower() for t in TAG_RE.findall(song.lyrics)]
        if not tags:
            warnings.append(
                "lyrics have no [section] tags. The model uses them to shape "
                "the arrangement over time - see docs/lyrics.md."
            )
        known = STRUCTURE_TAGS | VOCAL_TAGS | ENERGY_TAGS
        for tag in tags:
            base = tag.split("-")[0].strip()
            if base not in known and tag not in known:
                warnings.append(f"[{tag}] is not a documented tag; it may be sung aloud.")

        # Syllable alignment: the model maps syllables onto beats, so wildly
        # uneven lines inside a section sing badly. Only checked where the
        # counter means something - see _NON_LATIN_LANGUAGES.
        sections = (
            {} if song.language in _NON_LATIN_LANGUAGES
            else _sections(song.lyrics)
        )
        if song.language in _NON_LATIN_LANGUAGES:
            warnings.append(
                f"syllable balance not checked: the counter is Latin-script only "
                f"and says nothing useful about {song.language!r}. Check line "
                "lengths by ear."
            )
        for section, lines in sections.items():
            counts = [
                _syllables(ln, song.language) for ln in lines if ln.strip()
            ]
            if len(counts) >= 2 and max(counts) - min(counts) > 6:
                warnings.append(
                    f"[{section}] line lengths vary a lot ({min(counts)}-{max(counts)} "
                    "syllables). Keep lines in one section within ~2 of each other."
                )

    # Duration sanity: too little room for the words is the most common
    # cause of a rushed, garbled vocal.
    if song.duration is not None and not song.instrumental:
        lines = [l for l in song.lyrics.splitlines() if l.strip() and not l.strip().startswith("[")]
        if lines and song.duration < len(lines) * 2.0:
            warnings.append(
                f"{len(lines)} lyric lines in {song.duration:.0f}s is tight "
                "(~2s/line is the floor). Expect a rushed vocal; lengthen or cut."
            )
    if song.duration is None:
        warnings.append("no 'duration:' - the model will choose one. Set it for repeatable runs.")

    if song.seed is None:
        warnings.append(
            "no 'seed:' - this take will not be reproducible. Render once, then "
            "paste the reported seed back into the file to lock a good take."
        )
    if song.steps != 8:
        warnings.append(
            f"steps is {song.steps}; the installed turbo model is tuned for 8. "
            "Higher only helps on the base model."
        )
    return warnings


def _sections(lyrics: str) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    current = "untagged"
    for line in lyrics.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1].strip().lower()
            out.setdefault(current, [])
            continue
        if stripped:
            out.setdefault(current, []).append(stripped)
    return out


# Languages whose syllables this counter cannot see at all: it works by
# counting vowel groups in a Latin alphabet, which says nothing useful about
# a logographic or abugida script. The lint skips the check for these rather
# than report a confident wrong number.
_NON_LATIN_LANGUAGES = {
    "zh", "yue", "ja", "ko", "th", "he", "ar", "fa", "ur", "hi", "bn", "pa",
    "ta", "te", "ne", "sa", "el", "bg", "ru", "uk", "sr",
}

# Accented vowels carry syllables too. Without these in the character class,
# "wuerd" spelled properly as "würd" reduces to "wrd" and the count is right
# only by accident.
_WORD_RE = re.compile(r"[a-zà-öø-ÿ']+", re.IGNORECASE)
_VOWEL_RE = re.compile(r"[aeiouyàáâãäåèéêëìíîïòóôõöùúûüýÿ]+", re.IGNORECASE)


# Languages where a terminal -e is silent. In German it is not: "Kette" and
# "Name" are two syllables each, and applying the English rule to them
# undercounts every line that ends in a schwa.
_SILENT_FINAL_E = {"en", "fr"}


def _syllables(line: str, language: str = "en") -> int:
    """Rough syllable count for Latin-script lyrics.

    Counts vowel groups, which is a decent proxy in English and workable in
    German and the Romance languages. It is only ever used to compare lines
    against each other inside one section, so a consistent bias is harmless
    where an inconsistent one would not be.
    """
    silent_e = language in _SILENT_FINAL_E
    total = 0
    for word in _WORD_RE.findall(line.lower()):
        count = len(_VOWEL_RE.findall(word))
        if (
            silent_e
            and word.endswith("e")
            and count > 1
            and not word.endswith(("le", "ee", "ye"))
        ):
            count -= 1
        total += max(1, count)
    return total


def _as_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _as_int(value, name, lo, hi):
    if value in (None, ""):
        return None
    try:
        parsed = int(str(value).strip())
    except ValueError as exc:
        raise SongError(f"{name} must be a whole number, got {value!r}") from exc
    if lo is not None and parsed < lo:
        raise SongError(f"{name} must be >= {lo}, got {parsed}")
    if hi is not None and parsed > hi:
        raise SongError(f"{name} must be <= {hi}, got {parsed}")
    return parsed


def _as_float(value, name, lo, hi):
    if value in (None, ""):
        return None
    try:
        parsed = float(str(value).strip())
    except ValueError as exc:
        raise SongError(f"{name} must be a number, got {value!r}") from exc
    if parsed < lo or parsed > hi:
        raise SongError(f"{name} must be between {lo} and {hi}, got {parsed}")
    return parsed
