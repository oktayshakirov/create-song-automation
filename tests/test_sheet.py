import pytest

from song_automation.core import check, export, sheet, syllables

SAMPLE = """# Test Song
Notes for humans, never exported.
Style: funny trap, 140 bpm
Banned: never say this
---
[Intro]
(yeah)

[Hook]
I hit my limit
> joke rests on SOURCES row 1
Come back at three

[Verse 1]
One two buckle my shoe
Line two
Line three

[Beat drop]

[Hook]
"""


def test_parse_fields_and_title():
    s = sheet.parse_text(SAMPLE)
    assert s.title == "Test Song"
    assert s.field("style") == "funny trap, 140 bpm"
    assert s.banned == ["never say this"]
    assert s.notes == ["joke rests on SOURCES row 1"]


def test_empty_repeat_is_filled_from_first_occurrence():
    played = sheet.parse_text(SAMPLE).expanded()
    hooks = [p for p in played if p.kind == "hook"]
    assert len(hooks) == 2
    assert hooks[1].lines == hooks[0].lines
    assert hooks[1].repeat_of == "Hook"


def test_direction_tag_exports_bare():
    out = export.lyrics(sheet.parse_text(SAMPLE))
    assert "[Beat drop]\n\n[Hook]" in out
    assert "joke rests" not in out


def test_kind_strips_numbers_and_parentheses():
    assert sheet.Section("Verse 2").kind == "verse"
    assert sheet.Section("Hook (final)").kind == "hook"


def test_sung_drops_adlibs():
    s = sheet.Section("Hook", ["(yeah)", "I hit my limit (skrrt)"])
    assert s.sung == ["I hit my limit"]


def test_missing_separator_and_title():
    with pytest.raises(sheet.SheetError):
        sheet.parse_text("# T\n[Hook]\nx\n")
    with pytest.raises(sheet.SheetError):
        sheet.parse_text("Style: x\n---\n[Hook]\nx\n")


def test_clean_sample_has_no_errors():
    found = check.run(sheet.parse_text(SAMPLE))
    assert [f for f in found if f.level == "error"] == []


def test_check_catches_the_house_rules():
    bad = """# T
Banned: god's plan
---
[Hook]
It’s god's plan — really
I owe 20 dollars
"""
    msgs = [f.message for f in check.run(sheet.parse_text(bad))]
    assert any("missing" in m for m in msgs)            # no Style
    assert any("curly apostrophe" in m for m in msgs)
    assert any("em dash" in m for m in msgs)
    assert any("digits" in m for m in msgs)
    assert any("banned phrase" in m for m in msgs)
    assert any("plays once" in m for m in msgs)


def test_empty_first_verse_is_an_error():
    s = sheet.parse_text("# T\nStyle: x\n---\n[Hook]\na\n[Verse 1]\n[Hook]\n")
    assert any(f.level == "error" and f.where == "Verse 1"
               for f in check.run(s))


def test_flow_flags_a_line_far_longer_than_its_section():
    s = sheet.parse_text("""# T
Style: x
---
[Hook]
a
[Verse 1]
I ran out of tokens
I ran out of time
I ran out of patience
and then I ran out of every single reason to keep believing in tomorrow
[Hook]
""")
    assert any("rushed" in f.message for f in check.run(s))


@pytest.mark.parametrize("w,n", [
    ("limit", 2), ("reached", 1), ("Claude", 1), ("usage", 2),
    ("tomorrow", 3), ("little", 2), ("AI", 2), ("API", 3),
    ("you've", 1), ("rate", 1), ("subscription", 3), ("Anthropic", 3),
])
def test_syllables(w, n):
    assert syllables.word(w) == n
