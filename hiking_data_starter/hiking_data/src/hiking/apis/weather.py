"""Mountain Weather API Client (산림청 국립산림과학원_산악기상정보)."""

from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from hiking.config import settings

BASE_URL = "http://apis.data.go.kr/1400377/mtweather"
DEFAULT_TIMEOUT = 10.0

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def fetch_mountain_weather(
    local_area: str,
    page_no: int = 1,
    num_of_rows: int = 10,
) -> dict[str, Any]:
    """Fetch weather information for a specific mountain/region.
    
    Args:
        local_area: 지역명 (예: 서울, 강원)
        page_no: 1-indexed page number.
        num_of_rows: Items per page.
    """
    params = {
        "serviceKey": settings.data_go_kr_key,
        "_type": "json",
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "localArea": local_area
    }

    try:
        response = httpx.get(
            f"{BASE_URL}/mountListSearch",
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Weather API Error: {e}")
        return {}

def extract_weather(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract weather items from response."""
    try:
        items = response["response"]["body"]["items"]["item"]
    except (KeyError, TypeError):
        return []

    if isinstance(items, dict):
        return [items]
    return items
