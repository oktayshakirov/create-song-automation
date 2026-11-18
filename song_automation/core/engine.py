"""Lifecycle for the local ACE-Step server.

The vendored repo ships start_*_macos.sh launchers, but they are unusable
unattended: they use bash 4 parameter expansion (``${var^^}``) against the
bash 3.2 that macOS ships, and they stop for an interactive update prompt.
We launch the server process directly instead.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional

from song_automation.core.client import Engine, EngineError

ENGINE_HOME = Path(
    os.environ.get("ACESTEP_HOME", Path.home() / ".local/share/ace-step/ACE-Step-1.5")
)
LOG_PATH = Path(os.environ.get("SONG_ENGINE_LOG", Path.home() / ".local/share/ace-step/server.log"))
PID_PATH = Path(os.environ.get("SONG_ENGINE_PID", Path.home() / ".local/share/ace-step/server.pid"))

# Chosen for a 16GB Apple Silicon machine: the turbo DiT plus the small LM.
# The XL DiT and the 1.7B/4B LMs do not leave room on this box.
LM_MODEL = os.environ.get("SONG_LM_MODEL", "acestep-5Hz-lm-0.6B")

# The engine treats these four as one indivisible "main model". Its integrity
# check (check_main_model_exists) requires *all* of them to hold weights, and
# if any is missing it re-downloads the entire ~10GB snapshot - not just the
# gap. acestep-5Hz-lm-1.7B is in here despite us loading the 0.6B, so deleting
# it to reclaim 3.5GB silently arms a 10GB re-download on the next cold start.
MAIN_MODEL_COMPONENTS = (
    "acestep-v15-turbo",
    "vae",
    "Qwen3-Embedding-0.6B",
    "acestep-5Hz-lm-1.7B",
)

ENV = {
    # Native Apple Silicon acceleration for the language model half.
    "ACESTEP_LM_BACKEND": "mlx",
    "TOKENIZERS_PARALLELISM": "false",
    # Without this the MPS allocator caps out mid-render and the job dies with
    # "MPS backend out of memory" on a 16GB machine.
    "PYTORCH_MPS_HIGH_WATERMARK_RATIO": "0.0",
}


def missing_main_components() -> list[str]:
    """Main-model components the engine would re-download the whole snapshot for.

    Returns an empty list when the install is intact, or when there are no
    checkpoints at all (a first run is a legitimate full download, not a gap).
    """
    checkpoints = ENGINE_HOME / "checkpoints"
    if not checkpoints.exists():
        return []
    present = [c for c in MAIN_MODEL_COMPONENTS if (checkpoints / c).is_dir()]
    if not present:
        return []
    return [c for c in MAIN_MODEL_COMPONENTS if not _holds_weights(checkpoints / c)]


def _holds_weights(path: Path) -> bool:
    if not path.is_dir():
        return False
    return any(
        p.suffix in {".safetensors", ".bin", ".pt", ".pth", ".gguf"}
        for p in path.rglob("*")
    )


def warn_if_incomplete() -> Optional[str]:
    """Return a warning when a partial main model would trigger a big re-download."""
    missing = missing_main_components()
    if not missing:
        return None
    return (
        "WARNING: these main-model components are missing: "
        + ", ".join(missing)
        + ".\nThe engine checks the main model as a unit, so the next cold "
        "init will re-download the whole ~10GB snapshot rather than just "
        "these. Restore them, or accept the re-download."
    )


def uv_binary() -> str:
    found = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
    if not Path(found).exists():
        raise EngineError(
            "uv is not installed. Install it with:\n"
            "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        )
    return found


def start(wait: bool = True, timeout: float = 900.0) -> str:
    """Start the engine if it is not already up.

    On a cold machine this also downloads ~7GB of weights on first use, which
    is why the default timeout is generous.
    """
    engine = Engine()
    if engine.is_up():
        return "already running"
    warning = warn_if_incomplete()
    if warning:
        print(warning)
    if not ENGINE_HOME.exists():
        raise EngineError(
            f"no ACE-Step checkout at {ENGINE_HOME}. See docs/engine.md for setup."
        )

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, **ENV}
    with open(LOG_PATH, "ab") as log:
        proc = subprocess.Popen(
            [uv_binary(), "run", "acestep-api",
             "--host", "127.0.0.1", "--port", "8001",
             "--lm-model-path", LM_MODEL],
            cwd=str(ENGINE_HOME),
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            start_new_session=True,
        )
    PID_PATH.write_text(str(proc.pid))

    if not wait:
        return f"starting (pid {proc.pid})"

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise EngineError(
                f"engine exited during startup (code {proc.returncode}). "
                f"Last lines of {LOG_PATH}:\n{tail_log(15)}"
            )
        if engine.is_up():
            return f"listening (pid {proc.pid})"
        time.sleep(3)
    raise EngineError(f"engine did not come up within {timeout:.0f}s; see {LOG_PATH}")


def ensure_ready(timeout: float = 900.0) -> None:
    """Start the engine if needed and block until the weights are resident.

    ``is_up`` only means it is listening; the first request against a cold
    server otherwise blocks for minutes while the DiT loads.
    """
    engine = Engine()
    if not engine.is_up():
        start(wait=True, timeout=timeout)
    if engine.is_ready():
        return
    # /v1/init is synchronous and loads ~8GB, which takes minutes. The default
    # 30s client timeout is far too short, and a timeout here does not cancel
    # the work - the server keeps loading - so we swallow it and fall through
    # to polling health, which is the real readiness signal either way.
    try:
        engine._post(  # noqa: SLF001
            "/v1/init",
            {"model": "acestep-v15-turbo", "init_llm": True},
            timeout=int(timeout),
        )
    except EngineError:
        pass

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if engine.is_ready():
            return
        time.sleep(5)
    raise EngineError(f"weights not resident within {timeout:.0f}s; see {LOG_PATH}")


def stop() -> str:
    """Stop the engine, freeing roughly 8GB of memory."""
    if not PID_PATH.exists():
        return "no pid file; nothing to stop"
    try:
        pid = int(PID_PATH.read_text().strip())
    except ValueError:
        PID_PATH.unlink(missing_ok=True)
        return "unreadable pid file, removed"
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
    except ProcessLookupError:
        PID_PATH.unlink(missing_ok=True)
        return f"process {pid} was already gone"
    PID_PATH.unlink(missing_ok=True)
    return f"stopped {pid}"


def status() -> dict:
    engine = Engine()
    if not engine.is_up():
        return {"up": False}
    health = engine.health()
    return {
        "up": True,
        "ready": bool(health.get("models_initialized")),
        "dit": health.get("loaded_model"),
        "lm": health.get("loaded_lm_model"),
        "tasks": engine.supported_task_types(),
    }


def tail_log(lines: int = 20) -> str:
    if not LOG_PATH.exists():
        return f"(no log at {LOG_PATH})"
    data = LOG_PATH.read_bytes().decode(errors="replace")
    # The engine writes tqdm progress bars with carriage returns; split on
    # both so the tail is readable.
    return "\n".join(data.replace("\r", "\n").splitlines()[-lines:])
