from typing import List, Dict, Any, Optional, Tuple
import os
import re
import json
import math
import time
import logging
import difflib
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from readability import Document

# --- 프로젝트 내부 모듈 Import ---
from . import models, schemas, crud, nlpService
from .service.gemini_service import gemini_service
from .service import naverSearchService # 네이버 서비스 임포트 추가
from .config import settings # settings 객체 임포트

# ------------------------------
# 초기 설정
# ------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 환경 변수 및 상수 ---
KAKAO_REST_KEY = settings.KAKAO_REST_KEY
SCRAPINGBEE_KEY = settings.SCRAPINGBEE_KEY
KAKAO_WEB_SEARCH_URL = "https://dapi.kakao.com/v2/search/web"
KAKAO_LOCAL_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
REQUEST_TIMEOUT = 5.0
AD_REVIEW_PATTERNS = [r"소정의\s*원고료", r"체험단", r"업체로부터\s*제공", r"광고\s*참고", r"협찬"]

# ------------------------------
# 외부 API 및 크롤링 헬퍼 (카카오, 공통)
# ------------------------------
def _kakao_get(url: str, params: dict) -> Dict[str, Any]:
    if not KAKAO_REST_KEY:
        raise ValueError("KAKAO_REST_KEY가 설정되지 않았습니다.")
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"카카오 API 오류: {e}")
        return {}

def kakao_search_web(query: str, size: int = 5) -> List[Dict[str, Any]]:
    """카카오 웹 검색 API를 사용하여 웹 문서를 검색합니다."""
    if not KAKAO_REST_KEY:
        logging.warning("KAKAO_REST_KEY가 설정되지 않아 빈 결과를 반환합니다.")
        return []
    params = {"query": query, "size": size}
    result = _kakao_get(KAKAO_WEB_SEARCH_URL, params)
    return result.get("documents", [])

def kakao_search_local(query: str, size: int = 15) -> List[Dict[str, Any]]:
    """카카오 로컬 검색 API를 사용하여 맛집을 검색합니다."""
    if not KAKAO_REST_KEY:
        logging.warning("KAKAO_REST_KEY가 설정되지 않아 빈 결과를 반환합니다.")
        return []
    
    params = {
        "query": query,
        "category_group_code": "FD6",  # 음식점 카테고리
        "size": size,
        "sort": "accuracy"  # 정확도 순
    }
    
    try:
        result = _kakao_get(KAKAO_LOCAL_SEARCH_URL, params)
        places = result.get("documents", [])
        
        # 네이버 API 형식과 맞추기 위해 데이터 변환
        formatted_places = []
        for place in places:
            formatted_place = {
                "title": place.get("place_name", ""),
                "address": place.get("road_address_name") or place.get("address_name", ""),
                "roadAddress": place.get("road_address_name", ""),
                "mapx": place.get("x", ""),  # 경도
                "mapy": place.get("y", ""),  # 위도
                "telephone": place.get("phone", ""),
                "category": place.get("category_name", ""),
                "source": "kakao"  # 출처 표시
            }
            formatted_places.append(formatted_place)
        
        logging.info(f"카카오 로컬 검색 결과: {len(formatted_places)}개")
        return formatted_places
        
    except Exception as e:
        logging.error(f"카카오 로컬 검색 중 오류: {e}")
        return []

def _clean_html(text: str) -> str:
    return re.sub(r"<\/?b>", "", text or "").strip()

def cross_validate_restaurants(naver_results: List[Dict], kakao_results: List[Dict]) -> List[Dict]:
    """네이버와 카카오 검색 결과를 교차검증하여 중복 제거 및 데이터 품질 향상"""
    
    all_results = []
    for item in naver_results:
        item["source"] = "naver"
        all_results.append(item)
    for item in kakao_results:
        item["source"] = "kakao"
        all_results.append(item)
    
    unique_restaurants = {}
    
    for restaurant in all_results:
        name = _clean_html(restaurant.get("title", "")).strip()
        address = restaurant.get("address", "").strip()
        
        if not name or not address:
            continue
            
        normalized_name = re.sub(r'[^\w가-힣]', '', name.lower())
        normalized_address = re.sub(r'[^\w가-힣0-9]', '', address.lower())
        key = f"{normalized_name}_{normalized_address[:10]}"
        
        if key in unique_restaurants:
            unique_restaurants[key]["cross_validated"] = True
            unique_restaurants[key]["sources"] = list(set(
                unique_restaurants[key].get("sources", []) + [restaurant["source"]]
            ))
            if len(restaurant.get("address", "")) > len(unique_restaurants[key].get("address", "")):
                unique_restaurants[key]["address"] = restaurant["address"]
                unique_restaurants[key]["roadAddress"] = restaurant.get("roadAddress", "")
        else:
            restaurant["cross_validated"] = False
            restaurant["sources"] = [restaurant["source"]]
            unique_restaurants[key] = restaurant
    
    validated_results = list(unique_restaurants.values())
    validated_results.sort(key=lambda x: (
        -int(x.get("cross_validated", False)),
        -len(x.get("sources", [])),
        x.get("title", "")
    ))
    
    logging.info(f"교차검증 완료: 총 {len(validated_results)}개 (교차검증된 것: {sum(1 for r in validated_results if r.get('cross_validated'))})개")
    return validated_results

def get_places(query: str, max_results: int = 15) -> List[Dict[str, Any]]:
    """네이버와 카카오 API를 모두 사용하여 장소 목록을 가져오고 교차 검증합니다."""
    num_each = math.ceil(max_results / 2)
    
    naver_places = naverSearchService.search_local_places(query, display=num_each)
    kakao_places = kakao_search_local(query, size=num_each)
    
    validated_places = cross_validate_restaurants(naver_places, kakao_places)
    return validated_places[:max_results]

def generate_personalized_recommendations(candidates: List[Dict], user: Optional[models.User], prompt: str, max_recommendations: int = 5) -> List[Dict]:
    """Gemini AI를 사용하여 개인화된 맛집 추천을 생성합니다."""
    if not candidates:
        return []
    
    user_context = ""
    if user:
        user_context = f"""
사용자 정보:
- 이름: {user.name}
- 관심사: {user.interests or '없음'}
- 알레르기: {user.allergies_detail if user.allergies else '없음'}
"""
    
    restaurant_info = []
    for i, restaurant in enumerate(candidates[:20]):
        name = _clean_html(restaurant.get("title", ""))
        address = restaurant.get("address", "")
        category = restaurant.get("category", "")
        cross_validated = restaurant.get("cross_validated", False)
        sources = restaurant.get("sources", [])
        
        info = f"""
{i+1}. 이름: {name}
   주소: {address}
   카테고리: {category}
   교차검증: {'예' if cross_validated else '아니요'}
   출처: {', '.join(sources)}
"""
        restaurant_info.append(info)
    
    gemini_prompt = f"""
다음은 "{prompt}" 검색에 대한 맛집 후보 목록입니다.
{user_context}
맛집 후보 목록:
{''.join(restaurant_info)}

위 맛집들 중에서 다음 조건을 고려하여 최고의 {max_recommendations}개를 추천해주세요:
1. 사용자의 관심사와 알레르기 정보 고려
2. 검색 프롬프트와의 적합성
3. 교차검증된 맛집 우선 고려
4. 다양한 카테고리 고려

각 추천에 대해 다음 JSON 형식으로 응답해주세요:
{{
    "recommendations": [
        {{
            "restaurant_number": 1,
            "reason": "추천 이유를 상세히 설명"
        }}
    ]
}}
JSON 형식으로만 응답하고 다른 텍스트는 포함하지 마세요.
"""
    
    try:
        gemini_response = gemini_service.generate_content(gemini_prompt)
        if not gemini_response:
            logging.warning("Gemini 응답이 비어있음. 기본 추천 사용")
            return candidates[:max_recommendations]
        
        json_start = gemini_response.find('{')
        json_end = gemini_response.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = gemini_response[json_start:json_end]
            recommendation_data = json.loads(json_str)
            
            recommendations = []
            for rec in recommendation_data.get("recommendations", []):
                restaurant_num = rec.get("restaurant_number", 1) - 1
                if 0 <= restaurant_num < len(candidates):
                    recommended_restaurant = candidates[restaurant_num].copy()
                    recommended_restaurant["reason"] = rec.get("reason", "")
                    recommendations.append(recommended_restaurant)
            
            logging.info(f"Gemini 개인화 추천 완료: {len(recommendations)}개")
            return recommendations
        else:
            raise ValueError("JSON 형식을 찾을 수 없음")
            
    except (json.JSONDecodeError, ValueError) as e:
        logging.warning(f"Gemini 응답 파싱 실패: {e}. 기본 추천 사용")
        return candidates[:max_recommendations]
    except Exception as e:
        logging.error(f"Gemini 개인화 추천 중 오류: {e}")
        return candidates[:max_recommendations]

def get_personalized_recommendation(db, request, user):
    """
    사용자 맞춤형 맛집 추천 데이터를 생성합니다.
    (user가 None일 경우, 비로그인 사용자로 간주하여 일반적인 추천을 제공)
    """
    prompt = f"'{request.prompt}'와(과) 관련된 최고의 맛집 5곳을 추천해줘. 각 맛집의 특징과 대표 메뉴를 반드시 포함해줘."
    if user:
        user_info = f"사용자 정보: 관심사({user.interests}), 알러지({user.allergies_detail if user.allergies else '없음'})"
        prompt = f"'{request.prompt}'에 대한 맛집 추천을 찾고 있어. {user_info}를 고려해서, 최고의 맛집 5곳을 추천해줘. 각 맛집의 특징과 대표 메뉴를 반드시 포함해줘."

    try:
        # 네이버+카카오 API로 맛집 후보 수집 및 교차검증
        candidates = get_places(request.prompt, max_results=10)
        if not candidates:
            return {
                "answer": "죄송합니다. 해당 조건에 맞는 맛집을 찾을 수 없습니다.",
                "restaurants": []
            }
        # Gemini AI로 개인화 추천 생성
        personalized_recommendations = generate_personalized_recommendations(
            candidates=candidates,
            user=user,
            prompt=request.prompt,
            max_recommendations=5
        )
        # 추천된 맛집 상세 정보 수집 (DB 연동 등 필요시 확장)
        restaurants = []
        for recommendation in personalized_recommendations:
            name = _clean_html(recommendation.get("title", ""))
            address = recommendation.get("roadAddress") or recommendation.get("address", "")
            if not name or not address:
                continue
            details = get_restaurant_details(db, name, address)
            if details:
                details["recommendation_reason"] = recommendation.get("reason", "")
                details["cross_validated"] = recommendation.get("cross_validated", False)
                details["sources"] = recommendation.get("sources", [])
                restaurants.append(details)
        validated_count = sum(1 for r in restaurants if r.get('cross_validated'))
        total_searched = len(candidates)
        if user:
            personalized_message = (
                f"안녕하세요 {user.name}님!\n\n"
                f"'{request.prompt}' 검색을 위해 카카오와 네이버 API에서 총 {total_searched}개의 맛집을 수집하고 교차검증했습니다.\n"
                f"그 중 {validated_count}개는 두 플랫폼 모두에서 확인된 신뢰도 높은 맛집입니다."
            )
            if user.interests:
                personalized_message += f" 관심사({user.interests})"
            if user.allergies and user.allergies_detail:
                personalized_message += f" 및 알레르기 정보({user.allergies_detail})"
            personalized_message += f"를 고려하여 가장 적합한 {len(restaurants)}곳을 선별했습니다."
        else:
            personalized_message = (
                f"'{request.prompt}' 검색 결과입니다.\n\n"
                f"카카오와 네이버 API에서 총 {total_searched}개의 맛집을 수집하고 교차검증하여\n"
                f"{validated_count}개의 신뢰도 높은 맛집을 포함한 {len(restaurants)}곳을 추천드립니다."
            )
        return {
            "answer": personalized_message,
            "restaurants": restaurants
        }
    except Exception as e:
        logging.error(f"추천 생성 중 오류: {e}")
        return {
            "answer": "추천 생성 중 오류가 발생했습니다.",
            "restaurants": []
        }

def fetch_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except Exception:
        try:
            if SCRAPINGBEE_KEY:
                scrapingbee_url = f"https://app.scrapingbee.com/api/v1/?api_key={SCRAPINGBEE_KEY}&url={url}"
                response = requests.get(scrapingbee_url, timeout=10)
                response.raise_for_status()
                return response.text
        except Exception:
            pass
    return ""

def extract_main_text_from_html(html: str) -> str:
    try:
        doc = Document(html)
        return doc.summary()
    except Exception:
        return ""

def extract_review_snippets_from_text(text: str) -> List[str]:
    keywords = ["맛있", "추천", "별로", "최고", "불친절", "친절", "가격", "가성비", "재방문", "웨이팅", "대박", "최악", "분위기", "데이트", "가족", "아이"]
    sentences = re.split(r'[.!?]', text)
    return [s.strip() for s in sentences if any(kw in s for kw in keywords) and len(s.strip()) > 10][:10]

def cross_validate_review_sets(naver_snips: List[str], daum_snips: List[str]) -> Tuple[List[str], int]:
    all_reviews = naver_snips + daum_snips
    unique_reviews = []
    for review in all_reviews:
        is_duplicate = any(difflib.SequenceMatcher(None, review, existing).ratio() > 0.8 for existing in unique_reviews)
        if not is_duplicate:
            unique_reviews.append(review)
    
    trust_score = min(len(unique_reviews) * 10, 100)
    ad_count = sum(1 for review in unique_reviews if any(re.search(pattern, review) for pattern in AD_REVIEW_PATTERNS))
    trust_score = max(trust_score - ad_count * 5, 0)
    
    return unique_reviews[:20], trust_score

def advanced_crawl_restaurant_details(name: str) -> Dict[str, Any]:
    naver_query = f"{name} 리뷰 맛집"
    daum_query = f"{name} 후기 음식점"
    
    naver_results = kakao_search_web(naver_query, 3)
    daum_results = kakao_search_web(daum_query, 3)
    
    all_snippets = []
    for result in naver_results + daum_results:
        html = fetch_html(result.get("url", ""))
        if html:
            main_text = extract_main_text_from_html(html)
            snippets = extract_review_snippets_from_text(main_text)
            all_snippets.extend(snippets)
    
    unique_reviews, trust_score = cross_validate_review_sets(all_snippets[:10], all_snippets[10:])
    
    return {
        "crawled_reviews": unique_reviews,
        "review_trust_score": trust_score
    }

def llm_summarize_details(name: str, crawled_info: Dict[str, Any]) -> Dict[str, Any]:
    if not crawled_info.get("crawled_reviews"):
        return {"error": "크롤링된 리뷰가 없습니다."}
    
    try:
        reviews_text = "\n".join(crawled_info["crawled_reviews"])
        summary_result = gemini_service.summarize_restaurant_info(name, reviews_text)
        
        return {
            "summary_pros": summary_result.get("pros", []),
            "summary_cons": summary_result.get("cons", []),
            "keywords": summary_result.get("keywords", []),
            "nearby_attractions": summary_result.get("nearby_attractions", []),
            "signature_menu": summary_result.get("signature_menu", ""),
            "summary_phone": summary_result.get("phone", ""),
            "summary_parking": summary_result.get("parking", ""),
            "summary_price": summary_result.get("price", ""),
            "summary_opening_hours": summary_result.get("opening_hours", ""),
            "review_trust_score": crawled_info.get("review_trust_score", 0)
        }
    except Exception as e:
        logging.error(f"LLM 요약 중 오류: {e}")
        return {"error": str(e)}

def get_restaurant_details(db: Session, name: str, address: str) -> Optional[Dict[str, Any]]:
    try:
        restaurant = crud.get_or_create_restaurant_in_postgres(db, name, address)
        logging.info(f"'{name}' 레스토랑 정보를 반환합니다 (SQLite only)")
        return restaurant_to_dict(restaurant)
    except Exception as e:
        logging.error(f"레스토랑 상세 정보 조회 중 오류: {e}")
        return None

def create_date_course(db: Session, request: schemas.CourseRequest, user: models.User) -> Dict[str, Any]:
    try:
        course_details = [
            {"time": "14:00", "activity": f"{request.location}에서 카페 데이트"},
            {"time": "16:00", "activity": f"{request.location} 근처 산책"},
            {"time": "18:00", "activity": f"{request.location}에서 저녁 식사"},
            {"time": "20:00", "activity": "영화 관람"}
        ]
        if request.budget:
            course_details.append({"time": "예산", "activity": f"총 예산: {request.budget}"})
        if request.preferences:
            course_details[0]["activity"] += f" ({request.preferences} 고려)"
        return {"course": course_details}
    except Exception as e:
        logging.error(f"코스 생성 중 오류: {e}")
        return {"course": []}

def restaurant_to_dict(restaurant: models.Restaurant) -> Dict[str, Any]:
    return {
        "name": restaurant.name,
        "address": restaurant.address,
        "image_url": restaurant.image_url,
        "summary_pros": [],
        "summary_cons": [],
        "keywords": [],
        "nearby_attractions": []
    }