import httpx
from typing import Any, Optional

async def fetch_data_from_api(url: str) -> Optional[dict[str, Any]]:
    """
    Fetch JSON data from a given API endpoint asynchronously.
    Matches the logic of make_request from currency.py
    """
    headers = {
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None