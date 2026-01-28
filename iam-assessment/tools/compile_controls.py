import hashlib
import datetime as dt
import json
import os
import sys
from pathlib import Path
from datetime import date, datetime
from typing import Any, Dict, List, Tuple

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTROLS_DIR = ROOT / "controls"
SCHEMA_PATH = ROOT / "schemas" / "control.schema.json"
DIST_DIR = ROOT / "dist"
DIST_PATH = DIST_DIR / "controls.json"


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_control_files(controls_dir: Path) -> List[Path]:
    files: List[Path] = []
    for p in controls_dir.rglob("*.yml"):
        # skip meta/config files
        if p.name in {"_meta.yml", "domains.yml", "scoring.yml"}:
            continue
        files.append(p)
    for p in controls_dir.rglob("*.yaml"):
        if p.name in {"_meta.yaml", "domains.yaml", "scoring.yaml"}:
            continue
        files.append(p)
    return sorted(files)


def validate_schema(control: Dict[str, Any], validator: Draft202012Validator, source_path: Path) -> List[str]:
    errors = []
    for err in sorted(validator.iter_errors(control), key=lambda e: e.path):
        loc = ".".join([str(x) for x in err.path]) if err.path else "(root)"
        errors.append(f"{source_path}: schema error at {loc}: {err.message}")
    return errors


def enforce_registry_rules(
    controls: List[Dict[str, Any]],
    control_paths: List[Path],
    domain_ids: set[str],
    scoring_cfg: Dict[str, Any]
) -> List[str]:
    errors: List[str] = []

    # Unique IDs
    seen: Dict[str, Path] = {}
    for c, p in zip(controls, control_paths):
        cid = c.get("id")
        if cid in seen:
            errors.append(f"{p}: duplicate id '{cid}' already used in {seen[cid]}")
        else:
            seen[cid] = p

    # Domain exists
    for c, p in zip(controls, control_paths):
        d = c.get("domain")
        if d not in domain_ids:
            errors.append(f"{p}: domain '{d}' not found in controls/domains.yml")

    # Scoring bounds + required levels
    scale = scoring_cfg.get("scale", {})
    min_score = int(scale.get("min", 0))
    max_score = int(scale.get("max", 2))
    required_levels = set(scoring_cfg.get("levels_required", [0, 1, 2]))

    for c, p in zip(controls, control_paths):
        levels = c.get("scoring", {}).get("levels", [])
        scores = [lvl.get("score") for lvl in levels]

        # Ensure all scores are ints and within bounds (schema already helps, but belt+suspenders)
        for s in scores:
            if not isinstance(s, int):
                errors.append(f"{p}: scoring level score must be int, got {type(s).__name__}")
                continue
            if s < min_score or s > max_score:
                errors.append(f"{p}: scoring score {s} outside scale {min_score}-{max_score}")

        # Ensure required level set covered (0/1/2)
        if not required_levels.issubset(set(scores)):
            missing = sorted(list(required_levels.difference(set(scores))))
            errors.append(f"{p}: scoring.levels missing required scores {missing} (found {sorted(set(scores))})")

        # No duplicate score entries
        if len(scores) != len(set(scores)):
            errors.append(f"{p}: scoring.levels contains duplicate score values {scores}")

    # Weight bounds (again, schema covers, but allow config driven bounds too)
    wcfg = scoring_cfg.get("weight", {"min": 1, "max": 5})
    wmin = int(wcfg.get("min", 1))
    wmax = int(wcfg.get("max", 5))
    for c, p in zip(controls, control_paths):
        w = c.get("weight")
        if not isinstance(w, int) or w < wmin or w > wmax:
            errors.append(f"{p}: weight {w} outside configured bounds {wmin}-{wmax}")

    return errors


def normalize_domains(domains: Any) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], List[str]]:
    errors: List[str] = []
    domain_list: List[Dict[str, Any]] = []

    if isinstance(domains, dict) and "domains" in domains:
        if isinstance(domains["domains"], list):
            domain_list = domains["domains"]
        else:
            errors.append("controls/domains.yml: 'domains' must be a list")
    elif isinstance(domains, list):
        domain_list = domains
    elif isinstance(domains, dict):
        # Support legacy map-style domains keyed by id.
        for did, info in domains.items():
            if not isinstance(info, dict):
                errors.append(f"controls/domains.yml: domain '{did}' must be an object")
                continue
            entry = dict(info)
            if "id" in entry and entry["id"] != did:
                errors.append(
                    f"controls/domains.yml: domain key '{did}' does not match entry id '{entry['id']}'"
                )
            entry.setdefault("id", did)
            domain_list.append(entry)
    else:
        errors.append("controls/domains.yml: unsupported structure for domains")

    domain_map: Dict[str, Dict[str, Any]] = {}
    for entry in domain_list:
        if not isinstance(entry, dict):
            errors.append("controls/domains.yml: each domain must be an object")
            continue
        did = entry.get("id")
        if not isinstance(did, str) or not did:
            errors.append("controls/domains.yml: each domain must have a non-empty string 'id'")
            continue
        if did in domain_map:
            errors.append(f"controls/domains.yml: duplicate domain id '{did}'")
            continue
        domain_map[did] = entry

    return domain_list, domain_map, errors


def normalize_control(control: Dict[str, Any]) -> Dict[str, Any]:
    # Keep as-is but ensure predictable key ordering in JSON output
    # (JSON dump will handle ordering via sort_keys=True)
    return control


def to_json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: to_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_json_safe(v) for v in value]
    return value


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def canonical_json_bytes(obj: Any) -> bytes:
    """
    Deterministic JSON encoding for hashing:
    - sort_keys=True ensures stable ordering
    - separators remove whitespace differences
    - ensure_ascii=False avoids needless escaping differences
    """
    # Convert datetimes/dates to ISO strings before canonical encoding.
    s = json.dumps(to_json_safe(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    # Load config
    meta = load_yaml(CONTROLS_DIR / "_meta.yml")
    domains_raw = load_yaml(CONTROLS_DIR / "domains.yml")
    scoring_cfg = load_yaml(CONTROLS_DIR / "scoring.yml")
    schema = load_json(SCHEMA_PATH)

    validator = Draft202012Validator(schema)

    control_files = find_control_files(CONTROLS_DIR)
    if not control_files:
        print("No control files found under controls/**.yml", file=sys.stderr)
        return 2

    controls: List[Dict[str, Any]] = []
    errors: List[str] = []

    domains, domain_map, domain_errors = normalize_domains(domains_raw)
    errors.extend(domain_errors)

    for path in control_files:
        data = load_yaml(path)
        if not isinstance(data, dict):
            errors.append(f"{path}: control file must be a YAML object at top level")
            continue

        # Schema validation per control
        errors.extend(validate_schema(data, validator, path))
        controls.append(data)

    # Cross-control rules
    if not errors:
        errors.extend(enforce_registry_rules(controls, control_files, set(domain_map.keys()), scoring_cfg))

    if errors:
        print("Control registry validation failed:\n", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 1

        # Build base registry (no build metadata yet)
    registry_base = {
        "meta": meta,
        "scoring": scoring_cfg,
        "domains": domains,
        "controls": sorted([normalize_control(c) for c in controls], key=lambda x: x["id"]),
        "counts": {
            "controls": len(controls),
            "domains": len(domains)
        }
    }

    # Hash canonical representation of the base registry
    registry_bytes = canonical_json_bytes(registry_base)
    registry_hash = sha256_hex(registry_bytes)

    # Add build metadata AFTER hashing (so timestamp doesn't change hash)
    registry = dict(registry_base)
    registry["build"] = {
        "compiled_at": utc_now_iso(),
        "registry_hash": registry_hash,
        "compiler": "tools/compile_controls.py"
    }

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Write controls.json (pretty for humans)
    with DIST_PATH.open("w", encoding="utf-8") as f:
        json.dump(to_json_safe(registry), f, indent=2, sort_keys=True, ensure_ascii=False)

    # Write controls.sha256 (common format: "<hash>  <filename>")
    sha_path = DIST_DIR / "controls.sha256"
    with sha_path.open("w", encoding="utf-8") as f:
        f.write(f"{registry_hash}  {DIST_PATH.name}\n")

    print(f"Wrote {DIST_PATH} with {len(controls)} controls.")
    print(f"Wrote {sha_path} (sha256 registry_hash={registry_hash}).")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
