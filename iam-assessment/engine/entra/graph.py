import requests
from typing import Any, Dict, List, Optional

GRAPH = "https://graph.microsoft.com/v1.0"

def graph_get(token: str, path: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    r = requests.get(
        f"{GRAPH}{path}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()

def graph_list_all(token: str, path: str, params: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    url = f"{GRAPH}{path}"
    while True:
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        items.extend(data.get("value", []))
        next_link = data.get("@odata.nextLink")
        if not next_link:
            break
        url = next_link
        params = None
    return items
