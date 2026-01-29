import json
from pathlib import Path
from typing import Any, Dict


def registry_path() -> Path:
    return Path(__file__).resolve().parents[2] / "dist" / "controls.json"


def load_registry() -> Dict[str, Any]:
    path = registry_path()
    data = json.loads(path.read_text(encoding="utf-8"))
    if "build" not in data or "registry_hash" not in data["build"]:
        raise ValueError("controls.json missing build.registry_hash")
    return data


def registry_hash(registry: Dict[str, Any]) -> str:
    return registry["build"]["registry_hash"]

