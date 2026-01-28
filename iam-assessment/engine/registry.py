import json
from pathlib import Path
from typing import Any, Dict

def load_registry(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "build" not in data or "registry_hash" not in data["build"]:
        raise ValueError("controls.json missing build.registry_hash")
    return data

def registry_hash(registry: Dict[str, Any]) -> str:
    return registry["build"]["registry_hash"]
