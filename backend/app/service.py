import os
import re
import json
import math
import time
import logging
import difflib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import google.generativeai as genai
from bs4 import BeautifulSoup
from readability import Document

# --- 프로젝트 내부 모듈 Import ---
from . import models, schemas, crud, nlpService
from . import vectorDBService as vector_db_service
from .service.gemini_service import gemini_service # Gemini 서비스 임포트

# ------------------------------
# 초기 설정
# ------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# .env 파일에서 API 키를 가져옵니다.
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
KAKAO_REST_KEY = os.getenv("KAKAO_REST_KEY")
SCRAPINGBEE_KEY = os.getenv("SCRAPINGBEE_KEY")
# GOOGLE_API_KEY 변수는 gemini_service에서 사용하므로 여기서는 제거합니다.

# ------------------------------
# 외부 API 및 크롤링 헬퍼
# ------------------------------
def _naver_get(url: str, params: dict) -> Dict[str, Any]:
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID or "", "X-Naver-Client-Secret": NAVER_CLIENT_SECRET or ""}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logging.warning(f"Naver API Error: {e}")
        return {}

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

def _clean_html(text: str) -> str:
    return re.sub(r"<\/?b>", "", text or "").strip()

def _safe_json_loads(raw: str, fallback: dict = None) -> dict:
    if fallback is None: fallback = {}
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match: return fallback
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return fallback

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
    keywords = ["맛있", "추천", "별로", "최고", "불친절", "친절", "가격", "가성비", "재방문", "웨이팅", "대박", "최악", "분위기", "데이트", "오빠", "언니", "여자친구", "남자친구", "남친"
                "가족", "아이", "유아", "여친", "남친"]
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
    
    naver_items = _naver_get(NAVER_BLOG_SEARCH_URL, {"query": query, "display": 5}).get("items", [])
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
    naver_place = search_naver_local(f"{name} {address}", display=1)
    image_url = fetch_image_url(name) if naver_place else None
    
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
    # 간단한 조건 파싱 (향후 NLP 기반으로 고도화)
    conditions = {"region": request.prompt, "theme": "", "mood": "", "purpose": ""}
    for interest in (user.interests or "").split(','):
        if interest in request.prompt:
            conditions["purpose"] = interest

    search_queries = [f"{conditions['region']} {conditions['purpose']} 맛집", f"{conditions['region']} {conditions['theme']} 맛집"]
    
    candidates = []
    for q in search_queries:
        candidates.extend(search_naver_local(q, display=5))
    
    top_candidates = list({item['link']: item for item in candidates if item.get("link")}.values())[:3]

    restaurants = []
    for item in top_candidates:
        name = _clean_html(item.get("title", ""))
        address = item.get("roadAddress") or item.get("address", "")
        if name and address:
            details = get_restaurant_details(db, name, address)
            if details:
                restaurants.append(details)

    if not restaurants:
        return {"answer": "요청 조건에 맞는 맛집을 찾지 못했어요.", "restaurants": []}
    return {"answer": "요청 조건에 맞는 맛집을 추천합니다!", "restaurants": restaurants}

# ------------------------------
# 핵심 비즈니스 로직 (코스 추천)
# ------------------------------
def create_date_course(db: Session, request: schemas.CourseRequest, user: models.User) -> Dict[str, Any]:
    # (공유해주신 정교한 코스 생성 로직을 여기에 통합하고,
    # 각 장소를 get_restaurant_details로 처리하여 상세 정보를 채워넣습니다.)
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
                # 각 장소의 상세 정보를 가져옵니다.
                naver_search_result = search_naver_local(name, display=1)
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
            continue # 파싱 실패 시 해당 코스는 건너뜀

    return {"courses": final_courses}

# ------------------------------
# 누락된 헬퍼 함수들
# ------------------------------
def search_naver_local(query: str, display: int = 5) -> List[Dict[str, Any]]:
    """네이버 지역 검색 API를 사용하여 맛집 정보를 검색합니다."""
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []
    
    params = {"query": query, "display": display}
    result = _naver_get(NAVER_LOCAL_URL, params)
    return result.get("items", [])

def fetch_image_url(restaurant_name: str) -> str:
    """네이버 이미지 검색 API를 사용하여 맛집 이미지 URL을 가져옵니다."""
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return ""
    
    params = {"query": f"{restaurant_name} 음식", "display": 1}
    result = _naver_get(NAVER_IMAGE_URL, params)
    items = result.get("items", [])
    return items[0].get("link", "") if items else ""

def kakao_search_web(query: str, size: int = 5) -> List[Dict[str, Any]]:
    """카카오 웹 검색 API를 사용하여 웹 문서를 검색합니다."""
    if not KAKAO_REST_KEY:
        return []
    
    params = {"query": query, "size": size}
    result = _kakao_get(KAKAO_WEB_SEARCH_URL, params)
    return result.get("documents", [])

