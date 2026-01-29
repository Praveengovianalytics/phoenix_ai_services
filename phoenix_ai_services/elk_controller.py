import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


def query_elk(
    *,
    base_url: str,
    index: str,
    query: str,
    size: int = 10,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    if not base_url:
        raise ValueError("ELK base URL is required.")
    if not index:
        raise ValueError("ELK index is required.")

    payload = {
        "query": {"query_string": {"query": query}},
        "size": size,
    }
    url = f"{base_url.rstrip('/')}/{index}/_search"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"ApiKey {api_key}"

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise ValueError(f"ELK query failed: {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"ELK query failed: {exc.reason}") from exc
