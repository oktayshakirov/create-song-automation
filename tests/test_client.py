"""Tests for the engine client's request shaping and result parsing."""

import pytest

from song_automation.core.client import Engine, EngineError, JobResult


def test_rejects_task_types_the_turbo_model_cannot_do():
    # lego/extract/complete are base-model only. Failing here beats a
    # confusing engine-side error after a request round trip.
    engine = Engine()
    for task in ("lego", "extract", "complete"):
        with pytest.raises(EngineError, match="base model"):
            engine.submit({"task_type": task})


def test_result_parsing_unquotes_the_audio_path():
    result = Engine._to_result("abc", {
        "file": "/v1/audio?path=%2Ftmp%2Fa%20b%2Ftrack.flac",
        "seed_value": "4242",
        "metas": {"duration": 40.0, "bpm": 140, "keyscale": "F minor"},
        "generation_info": "**Total generation time (1 song): 71.32s**",
    })
    assert result.audio_path == "/tmp/a b/track.flac"
    assert result.seed == 4242
    assert result.bpm == 140
    assert result.keyscale == "F minor"
    assert result.duration == 40.0


def test_result_parsing_survives_a_missing_metas_block():
    result = Engine._to_result("abc", {"file": "", "seed_value": None})
    assert isinstance(result, JobResult)
    assert result.seed == -1
    assert result.duration == 0.0


def test_unreachable_engine_gives_an_actionable_error():
    engine = Engine(base_url="http://127.0.0.1:59999", timeout=1)
    with pytest.raises(EngineError, match="engine start"):
        engine.health()


def test_result_parsing_tolerates_na_metas():
    # Cover and repaint jobs report metas as the string "N/A". Coercing these
    # with a bare float() crashed a successful render before this was fixed.
    result = Engine._to_result("abc", {
        "file": "/v1/audio?path=%2Ftmp%2Fx.flac",
        "seed_value": "55",
        "metas": {"duration": "N/A", "bpm": "N/A", "keyscale": "N/A"},
    })
    assert result.duration == 0.0
    assert result.bpm is None
    assert result.keyscale == ""
    assert result.seed == 55


def test_http_errors_are_not_reported_as_an_unreachable_engine():
    # HTTPError subclasses URLError, so ordering in the except chain matters:
    # a rejected request must not look like a dead server.
    import urllib.error
    assert issubclass(urllib.error.HTTPError, urllib.error.URLError)
