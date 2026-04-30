"""Tourism API Client (한국관광공사 예측 집중률, 빅데이터, 자원 수요 정보 등)."""

from typing import Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from hiking.config import settings

# Various base URLs for KTO APIs
TOUR_API_BASE = "http://apis.data.go.kr/B551011/KorService1"
BIGDATA_BASE = "http://apis.data.go.kr/B551011/DataLabService"
PHOTO_API_BASE = "http://apis.data.go.kr/B551011/PhotoGalleryService1"
DEFAULT_TIMEOUT = 10.0

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def fetch_tourism_photos(
    keyword: str,
    page_no: int = 1,
    num_of_rows: int = 10,
) -> dict[str, Any]:
    """Fetch tourism photos using keywords (한국관광공사 관광사진 정보)."""
    params = {
        "serviceKey": settings.data_go_kr_key,
        "MobileOS": "ETC",
        "MobileApp": "PeakFit",
        "_type": "json",
        "keyword": keyword,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
    }

    try:
        response = httpx.get(
            f"{PHOTO_API_BASE}/gallerySearchList1",
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Photo API Error: {e}")
        return {}

def extract_items(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract standard items from Tour/BigData API response."""
    try:
        items = response["response"]["body"]["items"]["item"]
    except (KeyError, TypeError):
        return []
    if isinstance(items, dict):
        return [items]
    return items

def fetch_tourism_bigdata(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    """Generic fetcher for KTO BigData/Demand APIs.
    Endpoints include:
    - 관광지 집중률 방문자 추이 예측 정보
    - 지역별 관광 수요 강도 / 지역별 관광 자원 수요
    """
    params["serviceKey"] = settings.data_go_kr_key
    params["MobileOS"] = "ETC"
    params["MobileApp"] = "PeakFit"
    params["_type"] = "json"

    try:
        response = httpx.get(
            f"{BIGDATA_BASE}/{endpoint}",
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"BigData API Error: {e}")
        return {}
