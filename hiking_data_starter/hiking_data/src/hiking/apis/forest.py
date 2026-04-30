"""Korea Forest Service (산림청) API client.

Public data portal: 산림청_산림공간정보_등산로정보
https://www.data.go.kr/data/15058682/openapi.do
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from hiking.config import settings

BASE_URL = "http://apis.data.go.kr/1400000/service/cultureInfoService2"
DEFAULT_TIMEOUT = 10.0


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def fetch_mountain_list(
    page_no: int = 1,
    num_of_rows: int = 100,
) -> dict[str, Any]:
    """Fetch one page of mountain information.

    Args:
        page_no: 1-indexed page number.
        num_of_rows: Items per page (max 100).

    Returns:
        Parsed JSON response from the API.

    Raises:
        httpx.HTTPError: If the API returns a non-2xx response after retries.
    """
    params = {
        "serviceKey": settings.data_go_kr_key,
        "_type": "json",
        "pageNo": page_no,
        "numOfRows": num_of_rows,
    }

    response = httpx.get(
        f"{BASE_URL}/mntInfoOpenAPI2",
        params=params,
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def extract_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull the list of mountain items out of a Forest Service response.

    Returns an empty list if the structure is unexpected.
    """
    try:
        items = response["response"]["body"]["items"]["item"]
    except (KeyError, TypeError):
        return []

    if isinstance(items, dict):
        return [items]
    return items
