"""Tests for the song file format and the linter.

These run without the engine - that is the point of keeping parsing and
validation separate from rendering.
"""

import pytest

from song_automation.core.song import (
    Song, SongError, lint, parse_song_text, _syllables,
)

GOOD = """# Night Shift
style: dark trap, 808 sub bass, triplet hi-hats, sparse piano, male rap vocal
bpm: 140
key: F minor
time: 4/4
language: en
duration: 40
seed: 4242
---
[verse]
Clock hit twelve and the city went quiet
Everybody sleeping, I was wide awake

[hook]
I don't talk about it, I just move
Put it on the table, watch me prove
"""


def test_parses_a_good_song():
    song = parse_song_text(GOOD)
    assert song.title == "Night Shift"
    assert song.bpm == 140
    assert song.key == "F minor"
    assert song.seed == 4242
    assert song.duration == 40
    assert "[verse]" in song.lyrics
    assert song.slug == "night-shift"


def test_good_song_has_no_warnings():
    assert lint(parse_song_text(GOOD)) == []


def test_payload_disables_random_seed_when_seed_is_pinned():
    # The engine defaults use_random_seed to True and will otherwise throw
    # the seed away, which is the whole reason this flag is managed here.
    payload = parse_song_text(GOOD).to_payload()
    assert payload["use_random_seed"] is False
    assert payload["seed"] == 4242


def test_payload_enables_random_seed_when_unpinned():
    song = parse_song_text(GOOD.replace("seed: 4242\n", ""))
    payload = song.to_payload()
    assert payload["use_random_seed"] is True
    assert "seed" not in payload


def test_explicit_seed_argument_overrides_the_file():
    payload = parse_song_text(GOOD).to_payload(seed=99)
    assert payload["seed"] == 99
    assert payload["use_random_seed"] is False


def test_missing_separator_is_an_error():
    with pytest.raises(SongError, match="---"):
        parse_song_text("# Title\nstyle: pop\n")


def test_missing_style_is_an_error():
    with pytest.raises(SongError, match="style"):
        parse_song_text("# T\nbpm: 120\n---\n[verse]\nwords\n")


def test_unknown_header_key_is_an_error():
    # Silently ignoring it would surface as a wrong-sounding render later.
    with pytest.raises(SongError, match="tempo"):
        parse_song_text("# T\nstyle: pop\ntempo: 120\n---\n[verse]\nwords\n")


def test_bad_language_is_an_error():
    with pytest.raises(SongError, match="not supported"):
        parse_song_text("# T\nstyle: pop\nlanguage: klingon\n---\n[verse]\nw\n")


def test_out_of_range_bpm_is_an_error():
    with pytest.raises(SongError, match="bpm"):
        parse_song_text("# T\nstyle: pop\nbpm: 999\n---\n[verse]\nw\n")


def test_empty_lyrics_rejected_unless_instrumental():
    with pytest.raises(SongError, match="no lyrics"):
        parse_song_text("# T\nstyle: pop\n---\n")

    song = parse_song_text("# T\nstyle: lofi beat\ninstrumental: true\n---\n")
    assert song.instrumental
    assert song.to_payload()["lyrics"] == "[Instrumental]"


def test_lint_flags_bpm_written_into_the_style():
    song = parse_song_text(GOOD.replace("style: dark trap,", "style: 140 bpm dark trap,"))
    assert any("bpm" in w.lower() for w in lint(song))


def test_lint_flags_lopsided_sections():
    song = parse_song_text(GOOD.replace(
        "Put it on the table, watch me prove",
        "Put it on the table and watch me prove it to every single one of them",
    ))
    assert any("syllable" in w for w in lint(song))


def test_lint_flags_missing_seed():
    song = parse_song_text(GOOD.replace("seed: 4242\n", ""))
    assert any("reproducible" in w for w in lint(song))


def test_lint_flags_untagged_lyrics():
    song = parse_song_text("# T\nstyle: a, b, c, d vocal\nseed: 1\nduration: 60\n---\njust words\n")
    assert any("tags" in w for w in lint(song))


def test_lint_flags_a_duration_too_short_for_the_words():
    # Eight lines in the engine's 10s minimum is 1.25s a line, well under the
    # ~2s floor. Four lines in 10s is merely brisk and should not warn.
    cramped = GOOD.replace("duration: 40", "duration: 10").replace(
        "Put it on the table, watch me prove",
        "Put it on the table, watch me prove\n"
        "Counting up the hours like I owed them\n"
        "Nobody gets paid for the noise they make\n"
        "Clock hit twelve and the city went quiet\n"
        "Everybody sleeping, I was wide awake\n"
        "I don't talk about it, I just move",
    )
    assert any("tight" in w for w in lint(parse_song_text(cramped)))


def test_lint_does_not_flag_a_merely_brisk_duration():
    song = parse_song_text(GOOD.replace("duration: 40", "duration: 15"))
    assert not any("tight" in w for w in lint(song))


def test_syllable_counter_is_roughly_right():
    assert _syllables("I don't talk about it, I just move") == pytest.approx(9, abs=2)
    assert _syllables("move") == 1


def test_staging_rewrites_paths_the_engine_would_reject():
    # The engine refuses absolute paths unless they sit inside the system temp
    # dir, so sources are copied there before a cover/repaint request.
    import os
    import tempfile
    from pathlib import Path

    from song_automation.core.render import _stage_for_engine

    src = Path(tempfile.mkdtemp()) / "track.flac"
    src.write_bytes(b"not really audio")
    temp_root = Path(os.path.realpath(tempfile.gettempdir()))

    staged, temporary = _stage_for_engine(src)
    try:
        assert os.path.isabs(staged)
        # Must survive the server's own realpath comparison.
        assert temp_root in Path(os.path.realpath(staged)).parents
    finally:
        if temporary:
            os.unlink(staged)


def test_silent_final_e_is_english_only():
    # German "Kette" and "Name" are two syllables each. Applying the English
    # silent-e rule to them undercut every German line ending in a schwa.
    assert _syllables("Kette", "de") == 2
    assert _syllables("Name", "de") == 2
    assert _syllables("move", "en") == 1
    assert _syllables("table", "en") == 2


def test_accented_vowels_count_as_syllables():
    # Before umlauts were in the character class, "würd" split into "w" + "rd"
    # and scored 2 instead of 1 - right only by accident.
    assert _syllables("würd", "de") == 1
    assert _syllables("gäb", "de") == 1
    assert _syllables("für", "de") == 1


def test_german_lines_count_close_to_truth():
    import pytest
    pairs = [
        ("Kapuze auf, ich tu so, als würd ich sie nicht kennen", 14),
        ("GÄB DIE KETTE für die Art, wie sie mein Name sagt", 13),
    ]
    for line, actual in pairs:
        assert _syllables(line, "de") == pytest.approx(actual, abs=2)


def test_syllable_lint_is_skipped_for_non_latin_scripts():
    # A vowel-group counter says nothing about Japanese, so the lint says so
    # rather than reporting a confident wrong number.
    song = parse_song_text(
        "# T\nstyle: a, b, c, d vocal\nlanguage: ja\nseed: 1\nduration: 60\n"
        "---\n[verse]\nなにか\nもっとながいぎょう\n"
    )
    notes = lint(song)
    assert any("not checked" in w for w in notes)
    assert not any("syllable" in w and "vary" in w for w in notes)


def test_repaint_sends_lyrics_and_keeps_each_seed():
    # Without lyrics the engine repaints a vocal range with nothing to sing,
    # which is how a dropped line came back as mumble. And two repaints of one
    # range must not overwrite each other.
    import tempfile
    from pathlib import Path

    from song_automation.core.client import JobResult
    from song_automation.core.render import render_repaint

    work = Path(tempfile.mkdtemp())
    src = work / "track.flac"
    src.write_bytes(b"not really audio")
    sent = []

    class FakeEngine:
        def submit(self, payload):
            sent.append(dict(payload))
            return "job"

        def poll(self, task_id, on_progress=None):
            out = work / f"engine-{len(sent)}.flac"
            out.write_bytes(b"audio")
            return JobResult("job", str(out), 100 + len(sent), 8.0, None, "",
                             None, {})

    a = render_repaint(src, "trap", 31, 59, work / "out", engine=FakeEngine(),
                       lyrics="[verse]\nline one\n")
    b = render_repaint(src, "trap", 31, 59, work / "out", engine=FakeEngine())
    assert sent[0]["lyrics"] == "[verse]\nline one\n"
    assert "lyrics" not in sent[1]
    assert a.path != b.path and a.path.exists() and b.path.exists()
