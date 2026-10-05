"""HTTP client for the local ACE-Step 1.5 engine.

The engine is the vendored ACE-Step checkout running its REST server. We talk
to it over HTTP rather than importing ``acestep.inference`` in-process because
the models occupy ~8GB of a 16GB machine: a long-lived warm server renders in
~80s, while an in-process import pays a full model load on every invocation.

Everything the engine gets wrong by default is corrected here, in one place,
rather than at each call site. See ``docs/engine.md``.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

DEFAULT_BASE_URL = "http://127.0.0.1:8001"

# Task types the installed turbo DiT actually accepts. lego/extract/complete
# are base-model only - see docs/tasks.md.
TURBO_TASK_TYPES = {"text2music", "repaint", "cover", "cover-nofsq"}

# Lossless by default. The engine's own default is 128kbps mp3, which is not a
# master. Overridable per render for quick throwaway auditions.
DEFAULT_AUDIO_FORMAT = "flac"


class EngineError(RuntimeError):
    """The engine is unreachable, rejected the request, or failed a job."""


@dataclass
class JobResult:
    """One finished generation, as the engine reported it."""

    task_id: str
    audio_path: str
    seed: int
    duration: float
    bpm: Optional[int]
    keyscale: str
    generation_seconds: Optional[float]
    raw: Dict[str, Any]


class Engine:
    """A thin, honest wrapper over the ACE-Step REST API."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ---------------------------------------------------------------- health

    def health(self) -> Dict[str, Any]:
        """Return the engine's health payload, or raise if it is not up."""
        return self._get("/health")

    def is_up(self) -> bool:
        try:
            self.health()
            return True
        except EngineError:
            return False

    def is_ready(self) -> bool:
        """True once the DiT weights are resident, not merely once it listens."""
        try:
            return bool(self.health().get("models_initialized"))
        except EngineError:
            return False

    def inventory(self) -> Dict[str, Any]:
        """Loaded DiT/LM models and the task types the DiT supports."""
        return self._get("/v1/model_inventory")

    def supported_task_types(self) -> List[str]:
        inv = self.inventory()
        for model in inv.get("models", []):
            if model.get("is_loaded"):
                return list(model.get("supported_task_types", []))
        return []

    # ------------------------------------------------------------ generation

    def submit(self, payload: Dict[str, Any]) -> str:
        """Queue a job and return its task id."""
        task_type = payload.get("task_type", "text2music")
        if task_type not in TURBO_TASK_TYPES:
            raise EngineError(
                f"task_type {task_type!r} is not supported by the loaded turbo "
                f"model (it accepts {sorted(TURBO_TASK_TYPES)}). "
                "lego/extract/complete need the base model - see docs/tasks.md."
            )
        data = self._post("/release_task", payload)
        task_id = data.get("task_id")
        if not task_id:
            raise EngineError(f"engine returned no task_id: {data!r}")
        return task_id

    def poll(
        self,
        task_id: str,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress=None,
    ) -> JobResult:
        """Block until the job finishes, then return its result.

        The engine's status codes are 0 queued/running, 1 succeeded, 2 failed.
        """
        started = time.monotonic()
        last_stage = None
        while True:
            status, result = self._query(task_id)
            stage = (result or {}).get("stage")
            if on_progress and stage and stage != last_stage:
                on_progress(stage)
                last_stage = stage

            if status == 1:
                return self._to_result(task_id, result or {})
            if status == 2:
                raise EngineError(
                    f"job {task_id} failed: {(result or {}).get('stage', 'no reason given')}"
                )
            if time.monotonic() - started > timeout:
                raise EngineError(f"job {task_id} still unfinished after {timeout:.0f}s")
            time.sleep(interval)

    def _query(self, task_id: str):
        # NOTE: the field is `task_id_list`. Sending `task_ids` returns
        # {"data": []} with HTTP 200, which is indistinguishable from "still
        # running" and will hang a poll loop forever.
        data = self._post("/query_result", {"task_id_list": [task_id]}, unwrap=False)
        items = data.get("data") or []
        if not items:
            raise EngineError(
                f"engine knows nothing about task {task_id} - it may have been "
                "restarted, or the request key was wrong (must be task_id_list)"
            )
        item = items[0]
        result = item.get("result")
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                result = {}
        if isinstance(result, list):
            result = result[0] if result else {}
        return item.get("status"), (result if isinstance(result, dict) else {})

    @staticmethod
    def _to_result(task_id: str, result: Dict[str, Any]) -> JobResult:
        file_ref = result.get("file") or ""
        if "path=" in file_ref:
            audio_path = urllib.parse.unquote(file_ref.split("path=", 1)[1])
        else:
            audio_path = file_ref
        metas = result.get("metas") or {}
        info = result.get("generation_info") or ""
        seconds = None
        for token in info.replace("*", "").split():
            if token.endswith("s)") or token.endswith("s"):
                try:
                    seconds = float(token.rstrip("s)").split(":")[-1])
                    break
                except ValueError:
                    continue
        # Cover and repaint jobs report metas as the string "N/A" rather than
        # numbers, so every field here is coerced defensively.
        return JobResult(
            task_id=task_id,
            audio_path=audio_path,
            seed=_as_int(result.get("seed_value"), -1),
            duration=_as_float(metas.get("duration"), 0.0),
            bpm=_as_int(metas.get("bpm"), None),
            keyscale=_clean(metas.get("keyscale")),
            generation_seconds=seconds,
            raw=result,
        )

    # ------------------------------------------------------------- transport

    def _get(self, path: str) -> Dict[str, Any]:
        return self._request("GET", path, None)

    def _post(self, path: str, payload: Dict[str, Any], unwrap: bool = True,
              timeout: Optional[int] = None):
        return self._request("POST", path, payload, unwrap=unwrap, timeout=timeout)

    def _request(self, method: str, path: str, payload, unwrap: bool = True,
                 timeout: Optional[int] = None):
        url = self.base_url + path
        body = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=body, method=method)
        if body:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                raw = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            # HTTPError subclasses URLError, so it must be caught first or a
            # rejected request is misreported as an unreachable engine.
            detail = ""
            try:
                detail = exc.read().decode(errors="replace")[:600]
            except Exception:  # noqa: BLE001 - diagnostics only
                pass
            raise EngineError(
                f"engine rejected {method} {path} with HTTP {exc.code}: {detail or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise EngineError(
                f"cannot reach the engine at {self.base_url} ({exc.reason}). "
                "Start it with: python -m song_automation engine start"
            ) from exc
        except json.JSONDecodeError as exc:
            raise EngineError(f"engine returned non-JSON from {path}") from exc

        if not unwrap:
            return raw
        if raw.get("code") not in (200, None):
            raise EngineError(f"engine error on {path}: {raw.get('error')!r}")
        return raw.get("data", raw)


def _as_int(value, default):
    """Coerce an engine field to int, tolerating None and "N/A"."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _as_float(value, default):
    """Coerce an engine field to float, tolerating None and "N/A"."""
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def _clean(value) -> str:
    """Blank out the engine's "N/A" placeholder so callers can test falsiness."""
    text = str(value or "").strip()
    return "" if text.upper() in {"N/A", "NONE"} else text
