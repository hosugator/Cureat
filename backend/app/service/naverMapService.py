import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

load_dotenv()

# 네이버 API 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# API 엔드포인트
NAVER_LOCAL_URL = "https://openapi.naver.com/v1/search/local.json"
NAVER_IMAGE_URL = "https://openapi.naver.com/v1/search/image"
NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"

def _naver_api_request(url: str, params: dict) -> Dict[str, Any]:
    """네이버 API 공통 요청 함수"""
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return {}
    
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"네이버 API 요청 중 오류 발생: {e}")
        return {}

def search_local_places(query: str, display: int = 5) -> List[Dict[str, Any]]:
    """네이버 지역 검색 API를 사용하여 장소를 검색합니다."""
    params = {
        "query": query,
        "display": min(display, 5),  # 최대 5개
        "start": 1,
        "sort": "random"
    }
    
    result = _naver_api_request(NAVER_LOCAL_URL, params)
    return result.get("items", [])

def get_place_details(place_name: str, address: str = "") -> Optional[Dict[str, Any]]:
    """특정 장소의 상세 정보를 가져옵니다."""
    query = f"{place_name} {address}".strip()
    places = search_local_places(query, display=1)
    
    if places:
        place = places[0]
        return {
            "name": place.get("title", "").replace("<b>", "").replace("</b>", ""),
            "address": place.get("address", ""),
            "road_address": place.get("roadAddress", ""),
            "phone": place.get("telephone", ""),
            "mapx": place.get("mapx", ""),
            "mapy": place.get("mapy", ""),
            "link": place.get("link", "")
        }
    return None

def search_restaurant_images(restaurant_name: str, count: int = 1) -> List[str]:
    """맛집 이미지를 검색합니다."""
    params = {
        "query": f"{restaurant_name} 음식 맛집",
        "display": min(count, 10),
        "start": 1,
        "sort": "sim",
        "filter": "medium"
    }
    
    result = _naver_api_request(NAVER_IMAGE_URL, params)
    items = result.get("items", [])
    
    return [item.get("link", "") for item in items if item.get("link")]

def search_restaurant_reviews(restaurant_name: str, count: int = 5) -> List[Dict[str, Any]]:
    """맛집 리뷰 블로그를 검색합니다."""
    params = {
        "query": f"{restaurant_name} 후기 리뷰",
        "display": min(count, 10),
        "start": 1,
        "sort": "sim"
    }
    
    result = _naver_api_request(NAVER_BLOG_URL, params)
    items = result.get("items", [])
    
    reviews = []
    for item in items:
        reviews.append({
            "title": item.get("title", "").replace("<b>", "").replace("</b>", ""),
            "description": item.get("description", "").replace("<b>", "").replace("</b>", ""),
            "link": item.get("link", ""),
            "blogger_name": item.get("bloggername", ""),
            "post_date": item.get("postdate", "")
        })
    
    return reviews

def verify_place_existence(place_name: str, address: str = "") -> bool:
    """장소의 실존 여부를 확인합니다."""
    place_details = get_place_details(place_name, address)
    return place_details is not None

def get_nearby_attractions(location: str, count: int = 3) -> List[str]:
    """주변 놀거리를 검색합니다."""
    query = f"{location} 관광지 놀거리"
    places = search_local_places(query, display=count)
    
    attractions = []
    for place in places:
        name = place.get("title", "").replace("<b>", "").replace("</b>", "")
        if name:
            attractions.append(name)
    
    return attractions[:count]

