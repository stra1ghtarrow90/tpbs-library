from typing import Any, Dict, List, Optional, Tuple


def _weighted_score(items: List[Tuple[int, int]], max_score: int) -> Optional[float]:
    if not items:
        return None
    weighted = sum(weight * score for weight, score in items)
    total = sum(weight * max_score for weight, _ in items)
    if total == 0:
        return None
    return round((weighted / total) * 100.0, 2)


def build_report(registry: Dict[str, Any], assessment: Dict[str, Any]) -> Dict[str, Any]:
    scoring = registry.get("scoring", {})
    scale = scoring.get("scale", {})
    max_score = int(scale.get("max", 2))

    controls = registry.get("controls", [])
    domain_meta = {d["id"]: d for d in registry.get("domains", [])}

    items = assessment["items"]
    items_by_control = {item["control_id"]: item for item in items}

    domain_controls: Dict[str, List[Dict[str, Any]]] = {}
    for c in controls:
        domain_controls.setdefault(c["domain"], []).append(c)

    assessed_controls: List[Tuple[int, int]] = []
    assessed_count = 0

    for item in items:
        if item["status"] == "assessed" and item["score"] is not None:
            assessed_count += 1
            assessed_controls.append((item["weight"], item["score"]))

    domain_reports: List[Dict[str, Any]] = []
    for domain_id in sorted(domain_controls.keys()):
        d_controls = sorted(domain_controls[domain_id], key=lambda x: x["id"])
        assessed_items: List[Tuple[int, int]] = []
        for c in d_controls:
            item = items_by_control.get(c["id"])
            if item and item["status"] == "assessed" and item["score"] is not None:
                assessed_items.append((item["weight"], item["score"]))
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
    for item in items:
        if item["status"] != "assessed" or item["score"] is None:
            continue
        risk_score = (max_score - item["score"]) * item["weight"]
        risk_items.append(
            {
                "control_id": item["control_id"],
                "domain": item["domain"],
                "weight": item["weight"],
                "score": item["score"],
                "risk_score": risk_score,
                "title": item["control"].get("title", ""),
                "finding": item["finding_text"],
            }
        )

    risk_items = sorted(
        risk_items,
        key=lambda x: (-x["risk_score"], -x["weight"], x["control_id"]),
    )

    return {
        "registry_hash": assessment["registry_hash"],
        "assessed_at": assessment.get("assessed_at"),
        "summary": {
            "overall_score": overall_score,
            "controls_assessed": assessed_count,
            "controls_total": len(items),
            "controls_not_assessed": len(items) - assessed_count,
        },
        "domains": domain_reports,
        "top_risks": risk_items[:5],
    }

