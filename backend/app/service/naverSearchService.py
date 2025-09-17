import requests
import logging
from typing import Dict, Any, List, Optional

from ..config import settings # 상대 경로로 수정

# 네이버 검색 API 설정 (.env 파일의 올바른 키 사용)
NAVER_SEARCH_CLIENT_ID = settings.NAVER_CLIENT_ID  # NAVER_CLIENT_ID 사용
NAVER_SEARCH_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET  # NAVER_CLIENT_SECRET 사용

# API 엔드포인트 (v1) - 검색 API 하나에 모든 검색 포함
NAVER_LOCAL_URL = "https://openapi.naver.com/v1/search/local.json"   # 지역 검색
NAVER_BLOG_URL = "https://openapi.naver.com/v1/search/blog.json"     # 블로그 검색  
NAVER_WEB_URL = "https://openapi.naver.com/v1/search/webkr.json"     # 웹문서 검색
NAVER_IMAGE_URL = "https://openapi.naver.com/v1/search/image.json"   # 이미지 검색

def _naver_api_request(url: str, params: dict) -> Dict[str, Any]:
    """네이버 API 공통 요청 함수"""
    if not NAVER_SEARCH_CLIENT_ID or not NAVER_SEARCH_CLIENT_SECRET:
        logging.warning("네이버 API 자격 증명이 .env 파일에 설정되지 않았습니다.")
        return {}

    # 검색 Open API는 필수 헤더 두 개면 충분합니다.
    headers = {
        "X-Naver-Client-Id": NAVER_SEARCH_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_SEARCH_CLIENT_SECRET,
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5.0)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(
                "네이버 API 오류 - 상태코드: %s, URL: %s, Params: %s, 응답: %s",
                response.status_code,
                url,
                params,
                response.text,
            )
            return {}
            
    except requests.exceptions.RequestException as e:
        logging.error(f"네이버 API 요청 중 오류 발생: {e}")
        return {}

def search_local_places(query: str, display: int = 5, start: int = 1) -> List[Dict[str, Any]]:
    """네이버 지역 검색 API 호출"""
    params = {"query": query, "display": min(display, 5), "start": start, "sort": "comment"} # 정확도순 -> 인기순
    result = _naver_api_request(NAVER_LOCAL_URL, params)
    return result.get("items", []) if result else []

def search_blog_posts(query: str, display: int = 10, start: int = 1) -> List[Dict[str, Any]]:
    """네이버 블로그 검색 API 호출"""
    params = {"query": query, "display": min(display, 100), "start": start, "sort": "sim"}
    result = _naver_api_request(NAVER_BLOG_URL, params)
    return result.get("items", []) if result else []

def search_web_documents(query: str, display: int = 10, start: int = 1) -> List[Dict[str, Any]]:
    """네이버 웹 검색 API 호출"""
    params = {"query": query, "display": min(display, 100), "start": start, "sort": "sim"}
    result = _naver_api_request(NAVER_WEB_URL, params)
    return result.get("items", []) if result else []

# 지도 API 함수들 제거 - 웹 크롤링에는 검색 API만 필요
def get_naver_restaurant_recommendations(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    네이버 API 기반 맛집 추천 함수 (카카오 서비스와 동일한 로직)
    
    Args:
        query (str): 사용자 검색 쿼리
        max_results (int): 최대 결과 수
        
    Returns:
        Dict[str, Any]: {"answer": str, "restaurants": List[RestaurantDetail]}
    """
    try:
        # 지역 검색
        local_results = search_local_places(query, display=max_results)
        
        if not local_results:
            return {
                "answer": "네이버 검색 결과가 없습니다. 다른 키워드로 시도해주세요.",
                "restaurants": []
            }
        
        # 간단한 결과 변환 (상세 크롤링 없이)
        restaurants = []
        for place in local_results:
            restaurant_data = {
                "name": place.get("title", "").replace("<b>", "").replace("</b>", ""),
                "address": place.get("roadAddress") or place.get("address", ""),
                "phone": place.get("telephone", ""),
                "summary_pros": f"{place.get('category', '')} 맛집",
                "summary_cons": "",
                "keywords": [place.get('category', '').split('>')[0] if '>' in place.get('category', '') else place.get('category', '')],
                "nearby_attractions": "",
                "signature_menu": "",
                "summary_phone": place.get("telephone", ""),
                "summary_parking": "",
                "summary_price": "",
                "summary_opening_hours": ""
            }
            restaurants.append(restaurant_data)
        
        answer = f"'{query}' 네이버 검색 결과 {len(restaurants)}개의 맛집을 찾았습니다!"
        
        return {
            "answer": answer,
            "restaurants": restaurants
        }
        
    except Exception as e:
        logging.error(f"네이버 맛집 추천 중 오류 발생: {e}")
        return {
            "answer": "죄송합니다. 네이버 검색에 일시적인 문제가 발생했습니다.",
            "restaurants": []
        }

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

