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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서비스에 네이버 API 키가 설정되지 않았습니다."
        )

    headers = {
        "X-Naver-Client-Id": NAVER_SEARCH_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_SEARCH_CLIENT_SECRET,
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5.0)
        response.raise_for_status()  # 2xx 상태 코드가 아닐 경우 HTTPError 발생
        return response.json()
            
    except requests.exceptions.HTTPError as e:
        logging.error(
            "네이버 API 오류 - 상태코드: %s, URL: %s, Params: %s, 응답: %s",
            e.response.status_code,
            url,
            params,
            e.response.text,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="네이버 API 서비스에 문제가 발생했습니다."
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"네이버 API 요청 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="네이버 API 요청 중 네트워크 오류가 발생했습니다."
        )

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
    네이버 API 기반 맛집 추천 함수 (요구사항 반영)
    1. 대표 키워드 5개, 대표메뉴 2~3개, 실제 주소/전화번호, 이미지, LLM 설명 포함
    """
    try:
        local_results = search_local_places(query, display=max_results)
        if not local_results:
            return {
                "answer": "네이버 검색 결과가 없습니다. 다른 키워드로 시도해주세요.",
                "restaurants": []
            }

        restaurants = []
        for place in local_results:
            name = place.get("title", "").replace("<b>", "").replace("</b>", "")
            address = place.get("roadAddress") or place.get("address", "")
            phone = place.get("telephone", "")
            category = place.get("category", "")

            # 1. 대표 키워드 5개 추출 (카테고리, query, 기타 키워드)
            keywords = []
            if category:
                keywords += [c.strip() for c in category.split(">") if c.strip()]
            if query not in keywords:
                keywords.append(query)
            # 블로그/웹 검색에서 추가 키워드 추출 (상위 5개)
            blog_items = search_blog_posts(name, display=10)
            for item in blog_items:
                desc = item.get("description", "")
                for word in desc.replace("<b>", "").replace("</b>", "").split():
                    if word not in keywords and len(keywords) < 5:
                        keywords.append(word)
            keywords = keywords[:5]

            # 2. 대표메뉴 2~3개 추출 (블로그/웹에서 메뉴명 패턴 추출)
            signature_menu = []
            for item in blog_items:
                desc = item.get("description", "")
                # 간단한 메뉴명 패턴: ~메뉴, ~정식, ~세트, ~덮밥 등
                for token in desc.replace("<b>", "").replace("</b>", "").split():
                    if any(x in token for x in ["메뉴", "정식", "세트", "덮밥", "라면", "국수", "돈까스", "스테이크", "파스타", "김밥", "초밥", "탕", "찌개", "구이", "튀김", "샐러드"]):
                        if token not in signature_menu:
                            signature_menu.append(token)
                    if len(signature_menu) >= 3:
                        break
                if len(signature_menu) >= 3:
                    break
            signature_menu = ", ".join(signature_menu[:3])

            # 3. 실제 음식 이미지 (대표 이미지)
            image_url = get_restaurant_representative_image(name)

            # 4. LLM을 통한 자연스러운 설명 생성 (임시: 블로그 첫 설명 활용, 실제론 LLM 연동 필요)
            description = ""
            if blog_items:
                description = blog_items[0].get("description", "").replace("<b>", "").replace("</b>", "")
            else:
                description = f"{name}은(는) {category} 맛집입니다."
            # 실제 LLM 연동 시: description = call_llm_generate_description(name, address, category, signature_menu, ...)

            restaurant_data = {
                "name": name,
                "address": address,
                "phone": phone,
                "image_url": image_url,
                "description": description,
                "keywords": keywords,
                "signature_menu": signature_menu,
                "summary_pros": f"{category} 맛집",
                "summary_cons": "",
                "summary_phone": phone,
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

def search_restaurant_images(restaurant_name: str, count: int = 5) -> List[str]:
    """
    네이버 이미지 검색 API로 맛집 사진을 검색합니다.
    
    Args:
        restaurant_name (str): 맛집 이름
        count (int): 검색할 이미지 수 (최대 100)
        
    Returns:
        List[str]: 이미지 URL 리스트
    """
    params = {
        "query": f"{restaurant_name} 맛집 음식 사진",
        "display": min(count, 100),
        "start": 1,
        "sort": "sim",
        "filter": "large"  # 큰 이미지만 필터링
    }
    
    result = _naver_api_request(NAVER_IMAGE_URL, params)
    items = result.get("items", [])
    
    image_urls = []
    for item in items:
        # 이미지 URL 추출
        image_url = item.get("link", "")
        if image_url and image_url.startswith(("http://", "https://")):
            image_urls.append(image_url)
    
    return image_urls

def get_restaurant_representative_image(restaurant_name: str) -> Optional[str]:
    """
    맛집의 대표 이미지 URL을 가져옵니다.
    
    Args:
        restaurant_name (str): 맛집 이름
        
    Returns:
        Optional[str]: 대표 이미지 URL (없으면 None)
    """
    try:
        images = search_restaurant_images(restaurant_name, count=3)
        if images:
            # 첫 번째 이미지를 대표 이미지로 사용
            return images[0]
        else:
            logging.warning(f"'{restaurant_name}'의 이미지를 찾을 수 없습니다.")
            return None
    except Exception as e:
        logging.error(f"'{restaurant_name}' 이미지 검색 중 오류: {e}")
        return None

