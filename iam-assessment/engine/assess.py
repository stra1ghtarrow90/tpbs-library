import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .registry import load_registry, registry_hash


def load_findings(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "registry_hash" not in data:
        raise ValueError("findings.json missing registry_hash")
    if "findings" in data and not isinstance(data["findings"], list):
        raise ValueError("findings.json findings must be a list")
    return data


def _validate_findings(
    findings: List[Dict[str, Any]],
    valid_control_ids: set[str],
    min_score: int,
    max_score: int,
) -> Dict[str, Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}
    errors: List[str] = []

    for entry in findings:
        if not isinstance(entry, dict):
            errors.append("finding entry must be an object")
            continue
        cid = entry.get("control_id")
        if not isinstance(cid, str) or not cid:
            errors.append("finding.control_id must be a non-empty string")
            continue
        if cid in seen:
            errors.append(f"duplicate finding for control_id '{cid}'")
            continue
        score = entry.get("score")
        if not isinstance(score, int):
            errors.append(f"finding.score must be int for control_id '{cid}'")
            continue
        if score < min_score or score > max_score:
            errors.append(
                f"finding.score {score} out of range {min_score}-{max_score} for control_id '{cid}'"
            )
            continue
        seen[cid] = entry

    unknown = sorted([cid for cid in seen.keys() if cid not in valid_control_ids])
    if unknown:
        errors.append(f"unknown control_id(s) in findings: {', '.join(unknown)}")

    if errors:
        raise ValueError("Invalid findings:\n- " + "\n- ".join(errors))

    return seen


def _weighted_score(items: List[Tuple[int, int]], max_score: int) -> Optional[float]:
    if not items:
        return None
    weighted = sum(weight * score for weight, score in items)
    total = sum(weight * max_score for weight, _ in items)
    if total == 0:
        return None
    return round((weighted / total) * 100.0, 2)


def generate_report(registry_path: Path, findings_path: Path, out_path: Path) -> Dict[str, Any]:
    registry = load_registry(registry_path)
    findings_doc = load_findings(findings_path)

    if findings_doc["registry_hash"] != registry_hash(registry):
        raise ValueError(
            "registry_hash mismatch: findings.json has "
            f"{findings_doc['registry_hash']}, registry has {registry_hash(registry)}"
        )

    scoring = registry.get("scoring", {})
    scale = scoring.get("scale", {})
    min_score = int(scale.get("min", 0))
    max_score = int(scale.get("max", 2))

    findings_list = findings_doc.get("findings", [])
    controls = registry.get("controls", [])
    control_ids = {c["id"] for c in controls}
    findings_map = _validate_findings(findings_list, control_ids, min_score, max_score)

    domain_meta = {d["id"]: d for d in registry.get("domains", [])}
    domain_controls: Dict[str, List[Dict[str, Any]]] = {}
    for c in controls:
        domain_controls.setdefault(c["domain"], []).append(c)

    merged_controls: List[Dict[str, Any]] = []
    assessed_controls: List[Tuple[int, int]] = []
    assessed_count = 0

    for control in sorted(controls, key=lambda x: x["id"]):
        cid = control["id"]
        finding = findings_map.get(cid)
        if finding is None:
            merged = dict(control)
            merged["finding"] = {
                "status": "not_assessed",
                "score": None,
                "text": "",
                "evidence_refs": [],
            }
        else:
            score = finding["score"]
            assessed_count += 1
            assessed_controls.append((control["weight"], score))
            merged = dict(control)
            merged["finding"] = {
                "status": "assessed",
                "score": score,
                "text": str(finding.get("finding", "")),
                "evidence_refs": list(finding.get("evidence_refs", [])),
            }
        merged_controls.append(merged)

    domain_reports: List[Dict[str, Any]] = []
    for domain_id in sorted(domain_controls.keys()):
        d_controls = sorted(domain_controls[domain_id], key=lambda x: x["id"])
        assessed_items = []
        for c in d_controls:
            f = findings_map.get(c["id"])
            if f is not None:
                assessed_items.append((c["weight"], f["score"]))
        domain_score = _weighted_score(assessed_items, max_score)
        domain_reports.append(
            {
                "id": domain_id,
                "name": domain_meta.get(domain_id, {}).get("name", ""),
                "description": domain_meta.get(domain_id, {}).get("description", ""),
                "score": domain_score,
                "controls_assessed": len(assessed_items),
                "controls_total": len(d_controls),
                "weight": sum(c["weight"] for c in d_controls),
            }
        )

    overall_score = _weighted_score(assessed_controls, max_score)

    risk_items: List[Dict[str, Any]] = []
    for control in sorted(controls, key=lambda x: x["id"]):
        finding = findings_map.get(control["id"])
        if finding is None:
            continue
        score = finding["score"]
        risk_score = (max_score - score) * control["weight"]
        risk_items.append(
            {
                "control_id": control["id"],
                "domain": control["domain"],
                "weight": control["weight"],
                "score": score,
                "risk_score": risk_score,
                "title": control["title"],
                "finding": str(finding.get("finding", "")),
            }
        )
    risk_items = sorted(
        risk_items,
        key=lambda x: (-x["risk_score"], -x["weight"], x["control_id"]),
    )

    report = {
        "registry_hash": registry_hash(registry),
        "assessed_at": findings_doc.get("assessed_at"),
        "scope": findings_doc.get("scope", {}),
        "summary": {
            "overall_score": overall_score,
            "controls_assessed": assessed_count,
            "controls_total": len(controls),
            "controls_not_assessed": len(controls) - assessed_count,
        },
        "domains": domain_reports,
        "controls": merged_controls,
        "top_risks": risk_items[:5],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    registry_path = root / "dist" / "controls.json"
    findings_path = root / "assessments" / "findings.json"
    out_path = root / "dist" / "report.json"
    generate_report(registry_path, findings_path, out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
