import datetime as dt
import json
from pathlib import Path
from engine.models import Evidence
from engine.entra.auth import get_token
from engine.entra.graph import graph_list_all, graph_get

def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def collect_entra(out_path: Path) -> None:
    token = get_token()

    ca_policies = graph_list_all(token, "/identity/conditionalAccess/policies")
    roles = graph_list_all(token, "/directoryRoles")
    # role members can be heavy; do it for key roles first (MVP)
    role_members = {}
    for r in roles:
        rid = r["id"]
        role_members[r.get("displayName", rid)] = graph_list_all(token, f"/directoryRoles/{rid}/members")

    # Optional: Identity Protection policies may require licensing
    # If it errors, just skip for now.
    idp_policies = []
    try:
        idp_policies = graph_list_all(token, "/identityProtection/riskPolicies")
    except Exception:
        idp_policies = []

    # Facts (very MVP)
    facts = {
        "ca_policy_count": len(ca_policies),
        "directory_roles_count": len(roles),
        "has_identity_protection_policies": len(idp_policies) > 0,
        # Example heuristics you’ll refine:
        "has_any_ca_enabled": any(p.get("state") == "enabled" for p in ca_policies),
    }

    ev = Evidence(
        source="entra",
        collected_at=utc_now_iso(),
        artifacts={
            "conditional_access_policies": ca_policies,
            "directory_roles": roles,
            "directory_role_members": role_members,
            "identity_protection_policies": idp_policies,
        },
        facts=facts,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(ev.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
