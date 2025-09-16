import os
import re
import json
import logging
import difflib
from typing import List, Dict, Any, Optional, Tuple

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup
from readability import Document

# --- 프로젝트 내부 모듈 Import ---
from backend.app import models, schemas, crud, nlpService
from backend.app import vectorDBService as vector_db_service
from backend.app.service.gemini_service import gemini_service
from backend.app.service import naverMapService
from backend.app.config import settings # settings 객체 임포트

# ------------------------------
# 초기 설정
# ------------------------------
# load_dotenv()는 config.py에서 처리
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 환경 변수 및 상수 ---
KAKAO_REST_KEY = settings.KAKAO_REST_KEY
SCRAPINGBEE_KEY = settings.SCRAPINGBEE_KEY
KAKAO_WEB_SEARCH_URL = "https://dapi.kakao.com/v2/search/web"
REQUEST_TIMEOUT = 5.0
AD_REVIEW_PATTERNS = [r"소정의\s*원고료", r"체험단", r"업체로부터\s*제공", r"광고\s*참고", r"협찬"]

# ------------------------------
# 외부 API 및 크롤링 헬퍼 (카카오, 공통)
# ------------------------------
def _kakao_get(url: str, params: dict) -> Dict[str, Any]:
    if not KAKAO_REST_KEY: return {}
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logging.warning(f"Kakao API Error: {e}")
        return {}

def kakao_search_web(query: str, size: int = 5) -> List[Dict[str, Any]]:
    """카카오 웹 검색 API를 사용하여 웹 문서를 검색합니다."""
    if not KAKAO_REST_KEY:
        return []
    params = {"query": query, "size": size}
    result = _kakao_get(KAKAO_WEB_SEARCH_URL, params)
    return result.get("documents", [])

def _clean_html(text: str) -> str:
    return re.sub(r"<\/?b>", "", text or "").strip()

def fetch_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    try:
        r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception:
        if SCRAPINGBEE_KEY:
            params = {"api_key": SCRAPINGBEE_KEY, "url": url, "render_js": "true"}
            try:
                rr = requests.get("https://app.scrapingbee.com/api/v1/", params=params, timeout=20)
                rr.raise_for_status()
                return rr.text
            except Exception as e2:
                logging.warning(f"ScrapingBee fetch failed for {url}: {e2}")
    return ""

def extract_main_text_from_html(html: str) -> str:
    try:
        doc = Document(html)
        return BeautifulSoup(doc.summary(), "html.parser").get_text(separator="\n").strip()
    except Exception:
        return ""

def extract_review_snippets_from_text(text: str) -> List[str]:
    keywords = ["맛있", "추천", "별로", "최고", "불친절", "친절", "가격", "가성비", "재방문", "웨이팅", "대박", "최악", "분위기", "데이트", "가족", "아이"]
    sentences = re.split(r'[.。!?\n]', text or "")
    snippets = {s.strip() for s in sentences if len(s.strip()) > 20 and any(k in s for k in keywords)}
    return sorted(list(snippets), key=len, reverse=True)[:20]

def cross_validate_review_sets(naver_snips: List[str], daum_snips: List[str]) -> Tuple[List[str], int]:
    merged_texts, cross_count = [], 0
    used_daum_indices = set()
    for n_snip in naver_snips:
        best_match = False
        for i, d_snip in enumerate(daum_snips):
            if i in used_daum_indices: continue
            if difflib.SequenceMatcher(None, n_snip, d_snip).ratio() > 0.6:
                used_daum_indices.add(i)
                cross_count += 1
                best_match = True
                break
        merged_texts.append(n_snip)
    
    for i, d_snip in enumerate(daum_snips):
        if i not in used_daum_indices:
            merged_texts.append(d_snip)
            
    total_snips = len(merged_texts)
    score = int((cross_count * 2 / max(total_snips, 1)) * 100) if total_snips else 0
    return merged_texts, min(score, 100)

def advanced_crawl_restaurant_details(name: str) -> Dict[str, Any]:
    logging.info(f"[CRAWL] '{name}' 리뷰 교차검증 수집 시작")
    query = f"{name} 후기"
    
    naver_items = naverMapService.search_restaurant_reviews(name, count=5)
    naver_snips = [snip for item in naver_items for snip in extract_review_snippets_from_text(extract_main_text_from_html(fetch_html(item.get("link", "")))) if not any(re.search(p, snip) for p in AD_REVIEW_PATTERNS)]
    
    daum_items = kakao_search_web(query, size=5)
    daum_snips = [snip for item in daum_items for snip in extract_review_snippets_from_text(extract_main_text_from_html(fetch_html(item.get("url", "")))) if not any(re.search(p, snip) for p in AD_REVIEW_PATTERNS)]

    merged, score = cross_validate_review_sets(naver_snips, daum_snips)
    return {"crawled_reviews": merged, "review_trust_score": score} if merged else {}

# ------------------------------
# LLM 요약 로직
# ------------------------------
def llm_summarize_details(name: str, crawled_info: Dict[str, Any]) -> Dict[str, Any]:
    if not gemini_service: 
        logging.warning("Gemini 서비스가 초기화되지 않았습니다.")
        return {}
        
    prompt = f"""
    너는 맛집 요약 전문가야. 아래 "크롤링 정보"를 읽고 반드시 아래 JSON 형식으로만 응답해줘.
    [크롤링 정보]
    {json.dumps(crawled_info, ensure_ascii=False, indent=2)}
    [JSON 형식]
    {{
      "summary_pros": ["장점1","장점2","장점3"],
      "summary_cons": ["단점1","단점2","단점3"],
      "keywords": ["키워드1","키워드2","키워드3","키워드4","키워드5"],
      "signature_menu": "대표 메뉴", "price_range": "가격대", "opening_hours": "영업시간",
      "parking": "주차 정보", "phone": "전화번호",
      "nearby_attractions": ["주변 놀거리1","주변 놀거리2","주변 놀거리3"]
    }}"""
    
    return gemini_service.generate_json_content(prompt)

# ------------------------------
# 핵심 비즈니스 로직 (맛집 추천)
# ------------------------------
def get_restaurant_details(db: Session, name: str, address: str) -> Optional[Dict[str, Any]]:
    restaurant_id = f"{name}_{address}"

    existing_data = vector_db_service.get_restaurant_by_id(restaurant_id)
    if existing_data:
        logging.info(f"[CACHE HIT] '{name}' 정보를 벡터 DB에서 바로 반환")
        return existing_data

    logging.info(f"[CACHE MISS] '{name}' 신규 처리 시작")
    crawled_info = advanced_crawl_restaurant_details(name)
    if not crawled_info.get("crawled_reviews"): return None

    summary_data = llm_summarize_details(name, crawled_info)
    
    # 네이버 Local 검색으로 최종 정보 보정
    naver_place = naverMapService.search_local_places(f"{name} {address}", display=1)
    image_urls = naverMapService.search_restaurant_images(name, count=1)
    image_url = image_urls[0] if image_urls else None
    
    vector_text = " ".join(summary_data.get("keywords", [])) + " " + " ".join(summary_data.get("summary_pros", []))
    vector = nlpService.text_to_vector(vector_text)
    
    metadata = {
        "name": name, "address": address, "image_url": image_url,
        "mapx": naver_place[0].get("mapx") if naver_place else "",
        "mapy": naver_place[0].get("mapy") if naver_place else "",
        "review_trust_score": crawled_info.get("review_trust_score", 0),
        **summary_data
    }
    
    vector_db_service.upsert_restaurant(restaurant_id, vector, metadata)
    crud.get_or_create_restaurant_in_postgres(db, name=name, address=address)
    
    return metadata

def get_personalized_recommendation(db: Session, request: schemas.ChatRequest, user: models.User) -> Dict[str, Any]:
    # 1. 사용자 요청 기반 검색어 생성
    conditions = {"region": request.prompt, "theme": "", "mood": "", "purpose": ""}
    for interest in (user.interests or "").split(','):
        if interest in request.prompt:
            conditions["purpose"] = interest
    search_query = f"{conditions['region']} {conditions['purpose']} 맛집".strip()
    logging.info(f"생성된 검색어: {search_query}")

    # 2. 네이버와 카카오에서 각각 30개씩 후보군 검색
    logging.info("네이버와 카카오에서 후보군 검색 시작...")
    naver_candidates = naverMapService.search_local_places(search_query, display=30)
    kakao_candidates = kakao_search_web(search_query, size=30) # kakao_search_web은 웹문서 검색이므로, 카카오 로컬 API로 변경하는 것을 고려해야 합니다.
    
    # 3. 후보군 통합 및 중복 제거 (이름과 주소를 기준으로)
    all_candidates = {}
    for item in naver_candidates:
        name = _clean_html(item.get("title", ""))
        address = item.get("roadAddress") or item.get("address", "")
        if name and address:
            all_candidates[f"{name}_{address}"] = {"name": name, "address": address, "source": "naver"}
            
    for item in kakao_candidates:
        name = _clean_html(item.get("title", ""))
        # 카카오 웹 검색은 주소 정보가 부정확하므로, 이름만으로 키를 생성합니다.
        if name and f"{name}_" not in str(all_candidates.keys()):
             all_candidates[f"{name}_{item.get('url')}"] = {"name": name, "address": "", "source": "kakao"} # 주소는 나중에 검증단계에서 채움
    
    logging.info(f"총 {len(all_candidates)}개의 후보군 통합 완료.")

    # 4. 네이버 지도로 실존 장소 검증 및 상세 정보 수집
    logging.info("네이버 지도를 통해 실존 장소 검증 시작...")
    verified_restaurants = []
    for key, cand in all_candidates.items():
        if len(verified_restaurants) >= 5: # 최종 추천 수를 5개로 제한
            break
        
        # 네이버 지도 API로 상세 정보 요청하여 실존 여부 검증
        place_details = naverMapService.get_place_details(cand["name"], cand["address"])
        if place_details and place_details.get("road_address"): # 주소가 명확한 경우만 채택
            # 검증된 장소에 대해서만 LLM 요약 등 상세 정보 처리
            details = get_restaurant_details(db, place_details["name"], place_details["road_address"])
            if details:
                verified_restaurants.append(details)
                logging.info(f"  -> 검증 성공 및 정보 수집 완료: {place_details['name']}")
    
    logging.info(f"총 {len(verified_restaurants)}개의 음식점 최종 추천.")

    if not verified_restaurants:
        return {"answer": "요청 조건에 맞는 맛집을 찾지 못했어요. 검색어를 바꿔서 시도해보세요.", "restaurants": []}
    return {"answer": "요청 조건에 맞는 맛집을 추천합니다!", "restaurants": verified_restaurants}

# ------------------------------
# 핵심 비즈니스 로직 (코스 추천)
# ------------------------------
def create_date_course(db: Session, request: schemas.CourseRequest, user: models.User) -> Dict[str, Any]:
    logging.info(f"'{request.theme}' 테마의 코스 생성 요청")
    
    if not gemini_service:
        logging.warning("Gemini 서비스가 초기화되지 않았습니다.")
        return {"courses": []}

    prompt = f"""
    너는 최고의 데이트 코스 플래너야. 아래 제약 조건에 맞춰 최적의 데이트 코스 3가지를 제안해줘.
    [제약 조건]
    - 지역: {request.location}
    - 일정: {request.start_time} 부터 {request.end_time} 까지
    - 테마/목적: {request.theme}
    [답변 형식]
    각 코스를 "코스 1: [코스 제목] | [장소1] -> [장소2]..." 형식으로 추천해줘.
    """
    
    raw_response = gemini_service.generate_content(prompt)
    
    if not raw_response:
        return {"courses": []}

    course_lines = [line.strip() for line in raw_response.split('\n') if line.strip().startswith("코스")]
    
    final_courses = []
    for line in course_lines:
        try:
            title_part, steps_part = line.split("|", 1)
            course_title = title_part.split(":", 1)[1].strip().strip('[]')
            place_names = [name.strip() for name in steps_part.split("->")]
            
            course_steps_details = []
            for name in place_names:
                naver_search_result = naverMapService.search_local_places(name, display=1)
                if naver_search_result:
                    item = naver_search_result[0]
                    place_name = _clean_html(item.get("title",""))
                    place_address = item.get("roadAddress") or item.get("address", "")
                    details = get_restaurant_details(db, place_name, place_address)
                    if details:
                        course_steps_details.append(schemas.RestaurantDetail(**details))
            
            if course_steps_details:
                final_courses.append(schemas.CourseDetail(title=course_title, steps=course_steps_details))
        except Exception as e:
            logging.warning(f"코스 파싱 중 오류 발생: {e} (line: {line})")
            continue

    return {"courses": final_courses}

