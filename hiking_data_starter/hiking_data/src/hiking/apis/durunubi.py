"""Durunubi (Korea Trail) API client.

Public data portal: https://www.data.go.kr/data/15101974/openapi.do

This module is the template for the other three APIs. To add 산림청 / 기상청 / 국립공원공단,
copy this file, change BASE_URL + endpoint + params, and adjust extract_items() for the
response shape.
"""

from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from hiking.config import settings

BASE_URL = "http://apis.data.go.kr/B551011/Durunubi"
DEFAULT_TIMEOUT = 10.0


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def fetch_course_list(
    page_no: int = 1,
    num_of_rows: int = 100,
) -> dict[str, Any]:
    """Fetch one page of trail courses.

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
        "MobileOS": "ETC",
        "MobileApp": "HikingDataApp",
        "_type": "json",
        "pageNo": page_no,
        "numOfRows": num_of_rows,
    }

    response = httpx.get(
        f"{BASE_URL}/courseList",
        params=params,
        timeout=DEFAULT_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def extract_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull the list of course items out of a Durunubi response.

    Returns an empty list if the structure is unexpected (rather than crashing) so the
    caller can decide how to handle it.
    """
    try:
        items = response["response"]["body"]["items"]["item"]
    except (KeyError, TypeError):
        return []

    # Some endpoints return a single dict when there's only one result
    if isinstance(items, dict):
        return [items]
    return items
