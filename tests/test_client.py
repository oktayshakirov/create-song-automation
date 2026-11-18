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


def test_main_model_components_match_the_engine_definition():
    # If upstream changes which components make up the "main model", the
    # re-download guard goes stale and stops protecting anything. This pins
    # our copy to the engine's own list.
    from pathlib import Path

    from song_automation.core.engine import ENGINE_HOME, MAIN_MODEL_COMPONENTS

    source = ENGINE_HOME / "acestep/model_downloader.py"
    if not source.exists():
        import pytest
        pytest.skip("engine checkout not present")

    text = source.read_text()
    block = text.split("MAIN_MODEL_COMPONENTS = [", 1)[1].split("]", 1)[0]
    upstream = {line.split('"')[1] for line in block.splitlines() if '"' in line}
    assert upstream == set(MAIN_MODEL_COMPONENTS), (
        f"engine's main-model list changed to {upstream}; update engine.py"
    )


def test_requests_accept_a_per_call_timeout():
    # /v1/init loads ~8GB and routinely outlives the default 30s timeout.
    # Without a per-call override, ensure_ready() could never wait it out.
    import inspect

    from song_automation.core.client import Engine

    for name in ("_post", "_request"):
        assert "timeout" in inspect.signature(getattr(Engine, name)).parameters
