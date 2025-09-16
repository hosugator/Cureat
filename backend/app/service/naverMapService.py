import requests
import logging
from typing import Dict, Any, List, Optional

from ..config import settings # 상대 경로로 수정

# 네이버 API 설정
NAVER_SEARCH_CLIENT_ID = settings.NAVER_SEARCH_CLIENT_ID
NAVER_SEARCH_CLIENT_SECRET = settings.NAVER_SEARCH_CLIENT_SECRET

# API 엔드포인트
NAVER_LOCAL_URL = "https://openapi.naver.com/v1/search/local.json"
NAVER_IMAGE_URL = "https://openapi.naver.com/v1/search/image.json"
NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"

def _naver_api_request(url: str, params: dict) -> Dict[str, Any]:
    """네이버 API 공통 요청 함수"""
    if not NAVER_SEARCH_CLIENT_ID or not NAVER_SEARCH_CLIENT_SECRET:
        logging.warning("네이버 API 자격 증명이 .env 파일에 설정되지 않았습니다.")
        return {}

    headers = {
        "X-Naver-Client-Id": NAVER_SEARCH_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_SEARCH_CLIENT_SECRET,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://localhost:8000"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5.0)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"네이버 API 오류 - 상태코드: {response.status_code}, 응답: {response.text}")
            return {}
            
    except requests.exceptions.RequestException as e:
        logging.error(f"네이버 API 요청 중 오류 발생: {e}")
        return {}
        
def search_local_places(query: str, display: int = 30) -> List[Dict[str, Any]]:
    """네이버 지역 검색 API를 사용하여 장소를 검색합니다."""
    params = {
        "query": query,
        "display": min(display, 30),
        "start": 1,
        "sort": "random"
    }
    
    result = _naver_api_request(NAVER_LOCAL_URL, params)
    return result.get("items", [])

def search_restaurant_reviews(restaurant_name: str, count: int = 30) -> List[Dict[str, Any]]:
    """맛집 리뷰 블로그를 검색합니다."""
    params = {
        "query": f"{restaurant_name} 후기 리뷰",
        "display": min(count, 30),
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

