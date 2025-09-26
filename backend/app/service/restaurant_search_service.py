import requests
import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from bs4 import BeautifulSoup
try:
    from readability.readability import Document
except ImportError:
    # readability 라이브러리가 없는 경우 기본 BeautifulSoup 사용
    Document = None
import re

# 상대 import로 통일
from ..config import settings
from .naverSearchService import search_local_places, search_blog_posts, search_web_documents, get_restaurant_representative_image
from .kakaoService import search_web as kakao_search_web
from .gemini_service import gemini_service
from .nlp_processor import nlp_processor
from .. import crud
from ..database import SessionLocal

class RestaurantSearchService:
    """
    프롬프트 기반 맛집 검색 서비스
    네이버와 카카오 API를 활용하여 검색하고, LLM으로 요약 및 검증
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def kakao_search_local(self, query: str) -> List[Dict[str, Any]]:
        """카카오 지역 검색 API로 맛집 후보 검색 (최대 45곳)"""
        if not settings.KAKAO_REST_KEY:
            logging.error("카카오 API 키가 설정되지 않았습니다.")
            return []
        
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_KEY}"}
        
        restaurants = []
        # 최대 3페이지까지 검색하여 45곳 확보
        for page in range(1, 4): 
            params = {"query": query, "size": 15, "page": page, "category_group_code": "FD6"}
            try:
                response = self.session.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get('documents', [])
                    restaurants.extend(documents)
                    if data['meta']['is_end']:
                        break
                else:
                    logging.error(f"카카오 API 오류 (Page {page}): {response.status_code} - {response.text}")
                    break
            except Exception as e:
                logging.error(f"카카오 API 요청 오류 (Page {page}): {e}")
                break
        
        logging.info(f"카카오 API: 총 {len(restaurants)}개 맛집 후보 찾음")
        return restaurants

    def fetch_page_content(self, url: str) -> str:
        """웹페이지 내용 크롤링 (개선된 에러 핸들링)"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                if Document:
                    doc = Document(response.text)
                    soup = BeautifulSoup(doc.summary(), 'html.parser')
                else:
                    # readability가 없는 경우 기본 BeautifulSoup 사용
                    soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                return text[:2500]  # 분석할 텍스트 양 제한
            elif response.status_code == 403:
                # 접근 거부는 일반적이므로 debug 레벨로 처리
                logging.debug(f"페이지 접근 거부 (403): {url}")
            elif response.status_code == 404:
                # 페이지 없음도 일반적이므로 debug 레벨로 처리
                logging.debug(f"페이지 없음 (404): {url}")
            else:
                # 기타 HTTP 에러만 warning으로 처리
                logging.warning(f"페이지 크롤링 HTTP 에러 ({response.status_code}): {url}")
            return ""
        except requests.exceptions.Timeout:
            logging.debug(f"페이지 크롤링 타임아웃: {url}")
            return ""
        except requests.exceptions.ConnectionError:
            logging.debug(f"페이지 연결 실패: {url}")
            return ""
        except Exception as e:
            # 예상치 못한 에러만 warning으로 처리
            logging.warning(f"페이지 크롤링 예외 {url}: {e}")
            return ""

    def analyze_restaurant_with_gemini(self, kakao_info: Dict[str, Any], reviews: List[str]) -> Dict[str, Any]:
        """Gemini AI로 개별 맛집 정보 분석, 이미지/키워드/장단점/설명 포함"""
        if not gemini_service or not reviews:
            return {}

        reviews_text = '\n- '.join(reviews)
        restaurant_name = kakao_info.get('place_name', '알 수 없음')
        address = kakao_info.get('address_name', '정보 없음')
        phone = kakao_info.get('phone', '정보 없음')
        category = kakao_info.get('category_name', '').split(' > ')[-1].strip() if kakao_info.get('category_name') else '정보 없음'
        # 대표 이미지 크롤링
        image_url = get_restaurant_representative_image(restaurant_name)

        prompt = f"""
        당신은 레스토랑 데이터 분석가이자 카피라이터입니다. 아래의 식당 기본 정보와 크롤링된 리뷰들을 바탕으로, 요청된 JSON 형식에 맞춰 정보를 요약하고 분석해주세요.

        **기본 정보:**
        - 상호명: {restaurant_name}
        - 주소: {address}
        - 전화번호: {phone}
        - 카테고리: {category}
        - 대표 이미지 URL: {image_url}

        **수집된 리뷰:**
        - {reviews_text}

        **요청:**
        위 정보를 바탕으로 다음 JSON 구조를 완성해주세요. 모든 필드는 반드시 채워져야 합니다.
        - `operating_hours`는 리뷰에서 언급된 운영시간을 기반으로 작성하고, 정보가 없으면 일반적인 식당 운영시간으로 추론해주세요.
        - `signature_dishes`와 `price_range`는 리뷰에서 언급된 메뉴와 가격을 기반으로 작성해주세요.
        - `pros`와 `cons`는 각각 3개씩 구체적인 장점과 단점을 명확하게 요약해주세요.
        - `keywords`는 해당 식당의 특징을 가장 잘 나타내는 키워드 5개를 선정해주세요.
        - **리뷰 내용에서 명확한 정보를 찾을 수 없는 경우, '정보 없음'으로 명시해주세요. 절대로 정보를 추측하거나 만들어내지 마세요.**

        ```json
        {{
          "name": "{restaurant_name}",
          "phone": "{phone}",
          "address": "{address}",
          "category": "{category}",
          "operating_hours": "예: 11:00-22:00 (월~일), 브레이크타임 15:00-17:00",
          "signature_dishes": ["대표메뉴1", "대표메뉴2"],
          "price_range": "예: 1-2만원대",
          "pros": ["구체적인 장점 1", "구체적인 장점 2", "구체적인 장점 3"],
          "cons": ["구체적인 단점 1", "구체적인 단점 2", "구체적인 단점 3"],
          "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"],
          "description": "여기에 자연스러운 한글 설명문을 작성하세요.",
          "image_url": "{image_url}"
        }}
        ```
        """

        try:
            response = gemini_service.generate_content(prompt)
            clean_response = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if clean_response:
                json_str = clean_response.group(1)
                analysis = json.loads(json_str)
            else:
                json_str = response[response.find('{'):response.rfind('}')+1]
                analysis = json.loads(json_str)
            # image_url이 없으면 직접 추가
            if 'image_url' not in analysis:
                analysis['image_url'] = image_url
            # 필수 필드 보장 (빈 값이라도)
            for k in ['keywords','pros','cons','description']:
                if k not in analysis:
                    analysis[k] = [] if k in ['keywords','pros','cons'] else ''
            logging.info(f"Gemini 분석 완료: {restaurant_name}")
            return analysis
        except Exception as e:
            logging.error(f"Gemini AI 분석 오류 ({restaurant_name}): {e}")
            return {}

    def get_top_recommendations(self, user_profile: Dict[str, Any], all_restaurants_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """분석된 맛집 데이터와 사용자 DB 프로필을 기반으로 최종 3곳 추천"""
        if not gemini_service or not all_restaurants_data:
            return all_restaurants_data[:3] 

        logging.info("Gemini AI를 통해 사용자 맞춤 추천을 시작합니다...")
    # restaurants_json_str = json.dumps(all_restaurants_data, ensure_ascii=False, indent=2)

        # DB에서 가져온 핵심 개인화 데이터 활용
        profile_info = ""
        if user_profile:
            profile_info = f"""
        **사용자 개인화 정보 (핵심 데이터):**
        - 연령대: {user_profile.get('age_group', '정보 없음')}
        - 성별: {user_profile.get('gender', '정보 없음')}
        - 알레르기: {'있음' if user_profile.get('allergies') else '없음'}
        - 알레르기 상세: {user_profile.get('allergies_detail', '정보 없음')}
        - 관심사: {user_profile.get('interests', '정보 없음')}
        - 검색 쿼리: {user_profile.get('query', '정보 없음')}
            """
        else:
            profile_info = "**사용자 정보:** 비로그인 사용자 (개인화 데이터 없음)"

        prompt = f"""
        당신은 사용자의 개인화 데이터를 기반으로 맛집을 추천하는 전문 AI입니다.

        {profile_info}

    **분석된 맛집 후보 목록 (JSON):**
    ...

        **추천 기준:**
        1. 사용자의 알레르기 정보를 반드시 고려하여 안전한 맛집 우선 선별
        2. 연령대와 성별에 적합한 분위기와 메뉴 고려
        3. 관심사와 매칭되는 음식 스타일 우선 선별
        4. 검색 쿼리의 의도와 일치하는 맛집 추천

        **요청:**
        위 개인화 정보와 가장 잘 맞는 맛집 3곳을 후보 목록에서 선정해주세요.
        결과는 반드시 제공된 맛집 후보 목록의 JSON 객체 3개를 포함하는 JSON 배열 형식이어야 합니다.
        다른 설명이나 텍스트 없이 JSON 배열만 출력해주세요.
        """
        
        try:
            response = gemini_service.generate_content(prompt)
            clean_response = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if clean_response:
                json_str = clean_response.group(1)
                top_3 = json.loads(json_str)
                logging.info(f"Gemini AI 추천 완료: {len(top_3)}개 맛집 선정")
                return top_3
            else:
                json_str = response[response.find('['):response.rfind(']')+1]
                top_3 = json.loads(json_str)
                logging.info(f"Gemini AI 추천 완료 (폴백): {len(top_3)}개 맛집 선정")
                return top_3
        except Exception as e:
            logging.error(f"Gemini AI 추천 생성 오류: {e}")
            return all_restaurants_data[:3]

    def search_with_naver_verification(self, query: str, kakao_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """네이버 검색으로 카카오 결과 검증 및 추가 정보 수집"""
        verified_results = []
        
        for restaurant in kakao_results:
            restaurant_name = restaurant.get('place_name', '')
            if not restaurant_name:
                continue
                
            # 네이버에서 해당 맛집 검색
            naver_local_results = search_local_places(f"{restaurant_name} {restaurant.get('address_name', '')}", display=3)
            naver_blog_results = search_blog_posts(f"{restaurant_name} 후기", display=5)
            
            # 검증: 네이버에서도 찾아지는 맛집만 유효한 것으로 간주
            if naver_local_results:
                # 추가 정보 수집
                additional_info = {
                    'naver_verified': True,
                    'naver_reviews_count': len(naver_blog_results),
                    'naver_rating': naver_local_results[0].get('rating', '정보없음') if naver_local_results else '정보없음'
                }
                restaurant.update(additional_info)
                verified_results.append(restaurant)
        
        logging.info(f"네이버 검증 완료: {len(verified_results)}개 맛집이 검증됨")
        return verified_results

    def process_restaurants(self, query: str, user_profile: Dict[str, Any], target_count: int = 10) -> List[Dict[str, Any]]:
        """맛집 검색, 크롤링, 분석 전체 프로세스 실행 (다중 쿼리 지원, DB 중복방지)"""
        from .. import crud
        db = SessionLocal()
        # 1. 다중 쿼리로 맛집 후보 검색
        all_candidate_restaurants = []
        search_queries = user_profile.get('search_queries', [query])
        for search_query in search_queries:
            logging.info(f"카카오 API로 '{search_query}' 검색 시작...")
            candidates = self.kakao_search_local(search_query)
            all_candidate_restaurants.extend(candidates)
        # 중복 제거 (place_name + address 기준)
        seen = set()
        candidate_restaurants = []
        for restaurant in all_candidate_restaurants:
            key = f"{restaurant.get('place_name', '')}-{restaurant.get('address_name', '')}"
            if key not in seen:
                seen.add(key)
                candidate_restaurants.append(restaurant)
        if not candidate_restaurants:
            logging.warning("카카오에서 검색된 맛집 후보가 없습니다.")
            return []
        # 2. 네이버로 검증 (카카오에서 먼저 검색, 네이버에서 검증)
        logging.info("네이버 API로 검증 시작...")
        verified_restaurants = self.search_with_naver_verification(query, candidate_restaurants)
        if not verified_restaurants:
            logging.warning("네이버 검증을 통과한 맛집이 없습니다.")
            return []
        analyzed_results = []
        # 3. 각 검증된 후보에 대해 DB 중복 체크 후, 새 맛집만 크롤링 및 Gemini 분석 실행
        for i, restaurant in enumerate(verified_restaurants):
            if len(analyzed_results) >= target_count:
                logging.info(f"목표 맛집 수량 {target_count}개를 달성하여 분석을 종료합니다.")
                break
            place_name = restaurant.get('place_name')
            address = restaurant.get('address_name', '')
            # DB에 이미 분석된 맛집이 있으면 재분석하지 않고 바로 사용
            existing = db.query(crud.models.Restaurant).filter(
                crud.models.Restaurant.name == place_name,
                crud.models.Restaurant.address == address,
                crud.models.Restaurant.signature_dishes.isnot(None)
            ).first()
            if existing:
                logging.info(f"DB에 이미 분석된 맛집 존재: {place_name} ({address}) - DB 데이터 재사용")
                analyzed_results.append(crud.convert_db_restaurant_to_dict(existing))
                continue
            logging.info(f"({i+1}/{len(verified_restaurants)}) '{place_name}' 정보 수집 시도... (현재 {len(analyzed_results)}/{target_count}개 성공)")
            # 웹 검색으로 리뷰 수집
            web_results = kakao_search_web(f"{place_name} 후기 맛집", size=10)
            all_reviews = []
            for web_result in web_results:
                url = web_result.get('url', '')
                content = self.fetch_page_content(url)
                if content:
                    reviews_on_page = [
                        line.strip() for line in content.split('\n')
                        if len(line.strip()) > 15 and any(k in line for k in ["맛", "분위기", "가격", "서비스", "추천"])
                    ]
                    all_reviews.extend(reviews_on_page)
            if all_reviews:
                # Gemini AI로 분석
                analysis = self.analyze_restaurant_with_gemini(restaurant, list(set(all_reviews))[:15])
                if analysis:
                    # 대표 이미지 추가
                    representative_image = get_restaurant_representative_image(place_name)
                    analysis['image_url'] = representative_image
                    # DB에도 저장
                    crud.create_or_update_restaurant_with_analysis(db, analysis)
                    analyzed_results.append(analysis)
            else:
                logging.debug(f"리뷰를 찾지 못해 '{place_name}' 분석을 건너뜁니다.")
        db.close()
        logging.info(f"총 {len(analyzed_results)}개의 맛집 분석을 완료했습니다.")
        return analyzed_results

    def search_db_restaurants_with_ai(self, prompt: str, user_profile: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        AI를 사용하여 DB에서 프롬프트와 개인화 데이터에 맞는 맛집 검색
        """
        db = SessionLocal()
        try:
            # DB에서 모든 AI 분석 완료된 맛집 가져오기
            db_restaurants = crud.get_all_restaurants_from_db(db)
            
            if not db_restaurants:
                logging.info("DB에 AI 분석된 맛집이 없습니다.")
                return []
            
            # DB 맛집을 딕셔너리로 변환
            db_restaurants_dict = [crud.convert_db_restaurant_to_dict(r) for r in db_restaurants]
            
            logging.info(f"DB에서 {len(db_restaurants_dict)}개 맛집 발견, AI로 적합성 분석 중...")
            
            # AI로 적합한 맛집 필터링
            if gemini_service:
                matching_restaurants = self.filter_restaurants_by_ai(prompt, user_profile, db_restaurants_dict)
                logging.info(f"AI 필터링 결과: {len(matching_restaurants)}개 맛집이 조건에 부합")
                return matching_restaurants
            else:
                # Gemini가 없으면 키워드 기반 기본 필터링
                return self.filter_restaurants_by_keywords(prompt, db_restaurants_dict)
                
        finally:
            db.close()

    def filter_restaurants_by_ai(self, prompt: str, user_profile: Dict[str, Any], restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        AI를 사용하여 프롬프트와 개인화 데이터에 맞는 맛집 필터링
        """
        if not restaurants:
            return []
        
        # 사용자 프로필 정보 준비
        profile_info = ""
        if user_profile:
            profile_info = f"""
        **사용자 개인화 정보:**
        - 연령대: {user_profile.get('age_group', '정보 없음')}
        - 성별: {user_profile.get('gender', '정보 없음')}
        - 알레르기: {'있음' if user_profile.get('allergies') else '없음'}
        - 알레르기 상세: {user_profile.get('allergies_detail', '정보 없음')}
        - 관심사: {user_profile.get('interests', '정보 없음')}
            """
        else:
            profile_info = "**사용자 정보:** 비로그인 사용자"

        restaurants_json = json.dumps(restaurants, ensure_ascii=False, indent=2)
        
        prompt_text = f"""
        너는 맛집 추천 전문가야. 사용자가 요구하는 조건에 부합하는 맛집을 찾아서 추천해줘.

        **사용자 검색 쿼리:** {prompt}
        
        {profile_info}

        **DB에 저장된 맛집 목록:**
        {restaurants_json}

        **요청:**
        위 맛집 목록에서 사용자의 검색 의도와 개인화 데이터에 같거나 비슷한 맛집을 찾아.
        아래 기준은 반드시 고려해야 해.:
        1. 알레르기 정보가 있다면 해당 식재료가 포함될 가능성이 높은 맛집은 제외
        2. 검색 쿼리의 지역, 음식 메뉴, 목적, 분위기, 테마와 일치하는 맛집 우선
        3. 사용자 연령대와 성별에 적합한 분위기의 맛집 선별
        4. 관심사와 매칭되는 음식 스타일 우선
        5. API로 검색은 하되 반드시 LLM으로 최종 검토 할 것.
        6. 반드시 사진도 찾아서 image_url 필드에 포함시킬 것.

        결과는 누락되는 부분 없이 정확하게 찾아서 DB에 확실하게 저장할 것.
        """
        
        try:
            response = gemini_service.generate_content(prompt_text)
            
            # JSON 추출
            clean_response = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if clean_response:
                json_str = clean_response.group(1)
                filtered_restaurants = json.loads(json_str)
                return filtered_restaurants
            else:
                # 코드 블록이 없는 경우
                json_str = response[response.find('['):response.rfind(']')+1]
                filtered_restaurants = json.loads(json_str)
                return filtered_restaurants
                
        except Exception as e:
            logging.error(f"AI 맛집 필터링 오류: {e}")
            # AI 실패 시 키워드 기반 폴백
            return self.filter_restaurants_by_keywords(prompt, restaurants)

    def filter_restaurants_by_keywords(self, prompt: str, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        키워드 기반 기본 맛집 필터링 (AI 폴백용)
        """
        prompt_lower = prompt.lower()
        matching_restaurants = []
        
        for restaurant in restaurants:
            # 이름, 주소, 키워드에서 매칭 확인
            name = restaurant.get('name', '').lower()
            address = restaurant.get('address', '').lower()
            keywords = ' '.join(restaurant.get('keywords', [])).lower()
            category = restaurant.get('category', '').lower()
            
            # 간단한 키워드 매칭
            if (any(keyword in prompt_lower for keyword in [name, category]) or
                any(keyword in name or keyword in keywords for keyword in prompt_lower.split())):
                matching_restaurants.append(restaurant)
        
        return matching_restaurants

    def deduplicate_restaurants(self, db_restaurants: List[Dict[str, Any]], crawled_restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        DB 맛집과 크롤링 맛집 중복 제거
        """
        # DB 맛집의 이름-주소 조합으로 중복 체크용 집합 생성
        db_keys = set()
        for restaurant in db_restaurants:
            key = f"{restaurant.get('name', '').strip()}|{restaurant.get('address', '').strip()}"
            db_keys.add(key)
        
        # 크롤링 맛집에서 중복 제거
        unique_crawled = []
        for restaurant in crawled_restaurants:
            key = f"{restaurant.get('name', '').strip()}|{restaurant.get('address', '').strip()}"
            if key not in db_keys:
                unique_crawled.append(restaurant)
            else:
                logging.info(f"중복 맛집 제외: {restaurant.get('name')}")
        
        logging.info(f"중복 제거 결과: 크롤링 맛집 {len(crawled_restaurants)}개 → 유니크 {len(unique_crawled)}개")
        return unique_crawled

    def save_restaurants_to_db(self, restaurants: List[Dict[str, Any]]):
        """
        맛집 데이터를 DB에만 저장 (JSON 저장 완전 제거)
        """
        db = SessionLocal()
        try:
            saved_count = 0
            for restaurant_data in restaurants:
                try:
                    crud.create_or_update_restaurant_with_analysis(db, restaurant_data)
                    saved_count += 1
                except Exception as e:
                    logging.error(f"맛집 DB 저장 오류 ({restaurant_data.get('name')}): {e}")
                    raise Exception(f"DB 저장 오류: {restaurant_data.get('name')} - {e}")
            logging.info(f"DB 저장 완료: {saved_count}개 맛집")
        finally:
            db.close()

    def search_restaurants_by_prompt(self, prompt: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        하이브리드 프롬프트 기반 맛집 검색 메인 함수 (단계별 상세 예외 메시지 반환)
        """
        if not user_profile:
            user_profile = {}
        user_profile['query'] = prompt
        try:
            logging.info(f" 하이브리드 맛집 검색 시작: '{prompt}'")
            # 0단계: 자연어에서 핵심 키워드 추출
            try:
                logging.info(" 0단계: LLM으로 자연어에서 핵심 키워드 추출...")
                extracted_keywords = nlp_processor.extract_keywords_with_llm(prompt)
                search_queries = nlp_processor.generate_search_queries(extracted_keywords)
            except Exception as e:
                logging.error(f"[0단계] LLM 키워드 추출 오류: {e}")
                import traceback; logging.error(traceback.format_exc())
                return {"restaurants": [], "summary": "[0단계] LLM 키워드 추출 오류", "error": str(e)}

            user_profile.update({
                'extracted_location': extracted_keywords.get('location'),
                'extracted_food_type': extracted_keywords.get('food_type'),
                'extracted_mood': extracted_keywords.get('mood'),
                'extracted_weather': extracted_keywords.get('weather'),
                'search_queries': search_queries
            })
            logging.info(f" 추출된 키워드 - 위치: {extracted_keywords.get('location')}, 음식: {extracted_keywords.get('food_type')}, 분위기: {extracted_keywords.get('mood')}")
            logging.info(f"🔎 생성된 검색 쿼리: {search_queries}")

            # 1단계: DB에서 AI로 기존 맛집 검색
            try:
                logging.info(" 1단계: DB에서 기존 맛집 AI 검색...")
                db_matching_restaurants = self.search_db_restaurants_with_ai(prompt, user_profile)
            except Exception as e:
                logging.error(f"[1단계] DB 검색 오류: {e}")
                import traceback; logging.error(traceback.format_exc())
                return {"restaurants": [], "summary": "[1단계] DB 검색 오류", "error": str(e)}

            # 2단계: 크롤링으로 새로운 맛집 발굴
            try:
                crawl_target = 10 if db_matching_restaurants else 30
                logging.info(f" 2단계: 크롤링으로 새로운 맛집 발굴... (DB 매칭: {len(db_matching_restaurants)}개, 크롤링 목표: {crawl_target}개)")
                crawled_restaurants = self.process_restaurants(prompt, user_profile, target_count=crawl_target)
            except Exception as e:
                logging.error(f"[2단계] 크롤링 오류: {e}")
                import traceback; logging.error(traceback.format_exc())
                return {"restaurants": [], "summary": "[2단계] 크롤링 오류", "error": str(e)}

            # 3단계: 중복 제거
            try:
                logging.info(" 3단계: 중복 맛집 제거...")
                unique_new_restaurants = self.deduplicate_restaurants(db_matching_restaurants, crawled_restaurants)
            except Exception as e:
                logging.error(f"[3단계] 중복 제거 오류: {e}")
                import traceback; logging.error(traceback.format_exc())
                return {"restaurants": [], "summary": "[3단계] 중복 제거 오류", "error": str(e)}

            # 4단계: 새로운 맛집을 DB에만 저장
            try:
                if unique_new_restaurants:
                    logging.info(f" 4단계: {len(unique_new_restaurants)}개 새 맛집을 DB에 저장...")
                    self.save_restaurants_to_db(unique_new_restaurants)
                else:
                    logging.info(" 4단계: 저장할 새로운 맛집이 없습니다.")
            except Exception as e:
                logging.error(f"[4단계] DB 저장 오류: {e}")
                import traceback; logging.error(traceback.format_exc())
                return {"restaurants": [], "summary": "[4단계] DB 저장 오류", "error": str(e)}

            # 5단계: 전체 맛집 풀에서 최적 추천
            try:
                all_restaurants = db_matching_restaurants + unique_new_restaurants
                if not all_restaurants:
                    return {
                        "restaurants": [],
                        "summary": "DB와 크롤링 모두에서 조건에 맞는 맛집을 찾지 못했습니다.",
                        "db_matches": 0,
                        "new_discoveries": 0
                    }
                logging.info("5단계: 최종 맞춤 추천 생성...")
                top_recommendations = self.get_top_recommendations(user_profile, all_restaurants)
            except Exception as e:
                logging.error(f"[5단계] 추천 생성 오류: {e}")
                import traceback; logging.error(traceback.format_exc())
                return {"restaurants": [], "summary": "[5단계] 추천 생성 오류", "error": str(e)}

            # 결과 요약
            db_count = len(db_matching_restaurants)
            new_count = len(unique_new_restaurants)
            total_count = len(top_recommendations)
            keyword_summary = f" {extracted_keywords.get('location', '전체 지역')}"
            if extracted_keywords.get('food_type'):
                keyword_summary += f" | {extracted_keywords.get('food_type')}"
            if extracted_keywords.get('mood'):
                keyword_summary += f" | {extracted_keywords.get('mood')}"
            if extracted_keywords.get('weather'):
                keyword_summary += f" | {extracted_keywords.get('weather')}"
            summary = f"{keyword_summary}\n하이브리드 검색 완료: DB {db_count}곳 + 신규발굴 {new_count}곳 → 최종 {total_count}곳 추천!"
            return {
                "restaurants": top_recommendations,
                "summary": summary,
                "extracted_keywords": extracted_keywords,
                "search_queries_used": search_queries,
                "db_matches": db_count,
                "new_discoveries": new_count,
                "total_analyzed": len(all_restaurants)
            }
        except Exception as e:
            logging.error(f"[알 수 없는 단계] 하이브리드 맛집 검색 중 오류 발생: {e}")
            import traceback; logging.error(traceback.format_exc())
            return {
                "restaurants": [],
                "summary": "[알 수 없는 단계] 검색 중 오류가 발생했습니다.",
                "error": str(e)
            }

    # save_to_json 및 json 저장 기능 완전 제거

    def get_restaurant_images_bulk(self, restaurant_names: List[str]) -> Dict[str, str]:
        """
        여러 맛집의 대표 이미지를 한번에 가져옵니다.
        
        Args:
            restaurant_names (List[str]): 맛집 이름 리스트
            
        Returns:
            Dict[str, str]: {맛집이름: 이미지URL} 딕셔너리
        """
        images = {}
        for name in restaurant_names:
            try:
                image_url = get_restaurant_representative_image(name)
                if image_url:
                    images[name] = image_url
                    logging.info(f"이미지 수집 완료: {name}")
                else:
                    images[name] = None
                    logging.debug(f"이미지 없음: {name}")
            except Exception as e:
                logging.debug(f"이미지 수집 오류 ({name}): {e}")
                images[name] = None
        
        return images


# 서비스 인스턴스 생성
restaurant_search_service = RestaurantSearchService()