import requests
import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from readability.readability import Document
import google.generativeai as genai
import re

# 환경 변수 로드
load_dotenv()

# API 키 설정
KAKAO_REST_KEY = os.getenv("KAKAO_REST_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Gemini AI 설정
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None
    logging.warning(
        "Google API 키가 설정되지 않았습니다. Gemini AI 기능이 비활성화됩니다."
    )

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RestaurantRecommender:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    def parse_user_query_with_gemini(self, query: str) -> Dict[str, Any]:
        """Gemini AI를 이용해 사용자 쿼리에서 프로필 정보 추출"""
        prompt = f"""
        사용자의 맛집 검색 쿼리를 분석하여 다음 JSON 형식으로 변환해주세요.
        정보가 명시적으로 없으면 "정보 없음"으로 표기해주세요.
        
        **사용자 쿼리:**
        "{query}"
        
        **JSON 형식:**
        ```json
        {{
          "location": "원하는 지역 (예: 강남역, 홍대)",
          "age": "나이대 (예: 20대)",
          "gender": "성별 (예: 여성)",
          "purpose": "방문 목적 (예: 데이트, 회식, 가족식사)",
          "atmosphere": "원하는 분위기 (예: 조용한, 힙한, 가성비 좋은)"
        }}
        ```
        """
        try:
            response = model.generate_content(prompt)
            clean_response = re.search(
                r"```json\s*(\{.*?\})\s*```", response.text, re.DOTALL
            )
            if clean_response:
                return json.loads(clean_response.group(1))
            else:
                json_str = response.text[
                    response.text.find("{") : response.text.rfind("}") + 1
                ]
                return json.loads(json_str)
        except Exception as e:
            logging.error(f"Gemini AI 쿼리 분석 오류: {e}")
            return {
                "location": "정보 없음",
                "age": "정보 없음",
                "gender": "정보 없음",
                "purpose": "정보 없음",
                "atmosphere": "정보 없음",
            }

    def kakao_search_local(self, query: str) -> List[Dict[str, Any]]:
        """카카오 지역 검색 API로 맛집 후보 목록을 최대한 많이 검색 (최대 45곳)"""
        if not KAKAO_REST_KEY:
            logging.error("카카오 API 키가 설정되지 않았습니다.")
            return []

        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}

        restaurants = []
        # 30곳을 안정적으로 확보하기 위해 API가 허용하는 최대치(3페이지, 45곳)를 요청
        for page in range(1, 4):
            params = {
                "query": query,
                "size": 15,
                "page": page,
                "category_group_code": "FD6",
            }
            try:
                response = self.session.get(
                    url, headers=headers, params=params, timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get("documents", [])
                    restaurants.extend(documents)
                    if data["meta"]["is_end"]:
                        break  # 마지막 페이지면 중단
                else:
                    logging.error(
                        f"카카오 API 오류 (Page {page}): {response.status_code} - {response.text}"
                    )
                    break
            except Exception as e:
                logging.error(f"카카오 API 요청 오류 (Page {page}): {e}")
                break

        logging.info(f"카카오 API: 총 {len(restaurants)}개 맛집 후보 찾음")
        return restaurants

    def kakao_search_web(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """카카오 웹 검색 API로 리뷰 검색 (정보 수집 강화를 위해 size 기본값 증가)"""
        if not KAKAO_REST_KEY:
            return []

        url = "https://dapi.kakao.com/v2/search/web"
        headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
        params = {"query": f"{query} 후기 맛집", "size": size}

        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("documents", [])
            else:
                logging.error(f"카카오 웹 검색 오류: {response.status_code}")
                return []
        except Exception as e:
            logging.error(f"카카오 웹 검색 요청 오류: {e}")
            return []

    def fetch_page_content(self, url: str) -> str:
        """웹페이지 내용 크롤링"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                doc = Document(response.text)
                soup = BeautifulSoup(doc.summary(), "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                return text[:2500]  # 분석할 텍스트 양 소폭 증가
            return ""
        except Exception as e:
            logging.warning(f"페이지 크롤링 실패 {url}: {e}")
            return ""

    def analyze_restaurant_with_gemini(
        self, kakao_info: Dict[str, Any], reviews: List[str]
    ) -> Dict[str, Any]:
        """Gemini AI로 개별 맛집 정보 분석 및 요약"""
        if not model or not reviews:
            return {}

        reviews_text = "\n- ".join(reviews)
        restaurant_name = kakao_info.get("place_name", "알 수 없음")

        prompt = f"""
        당신은 레스토랑 데이터 분석가입니다. 아래의 식당 기본 정보와 크롤링된 리뷰들을 바탕으로, 요청된 JSON 형식에 맞춰 정보를 요약하고 분석해주세요.

        **기본 정보:**
        - 상호명: {restaurant_name}
        - 주소: {kakao_info.get('address_name', '')}
        - 전화번호: {kakao_info.get('phone', '')}
        - 카테고리: {kakao_info.get('category_name', '').split(' > ')[-1].strip()}

        **수집된 리뷰:**
        - {reviews_text}

        **요청:**
        위 정보를 바탕으로 다음 JSON 구조를 완성해주세요. 모든 필드는 반드시 채워져야 합니다. 정보가 부족할 경우, 리뷰 내용에 기반하여 최대한 추론해주세요.
        - `signature_dishes`와 `price_range`는 리뷰에서 언급된 메뉴와 가격을 기반으로 작성해주세요.
        - `pros`와 `cons`는 각각 3개씩 구체적인 장점과 단점을 명확하게 요약해주세요.
        - `keywords`는 해당 식당의 특징을 가장 잘 나타내는 키워드 5개를 선정해주세요.

        ```json
        {{
          "name": "{restaurant_name}",
          "phone": "{kakao_info.get('phone', '정보 없음')}",
          "address": "{kakao_info.get('address_name', '정보 없음')}",
          "signature_dishes": ["대표메뉴1", "대표메뉴2"],
          "price_range": "예: 1-2만원대",
          "pros": ["구체적인 장점 1", "구체적인 장점 2", "구체적인 장점 3"],
          "cons": ["구체적인 단점 1", "구체적인 단점 2", "구체적인 단점 3"],
          "keywords": ["키워드1", "키워드2", "키워드3", "키워드4", "키워드5"]
        }}
        ```
        """

        try:
            response = model.generate_content(prompt)
            clean_response = re.search(
                r"```json\s*(\{.*?\})\s*```", response.text, re.DOTALL
            )
            if clean_response:
                json_str = clean_response.group(1)
                analysis = json.loads(json_str)
                logging.info(f"Gemini 분석 완료: {restaurant_name}")
                return analysis
            else:
                json_str = response.text[
                    response.text.find("{") : response.text.rfind("}") + 1
                ]
                analysis = json.loads(json_str)
                logging.info(f"Gemini 분석 완료 (폴백): {restaurant_name}")
                return analysis
        except Exception as e:
            logging.error(f"Gemini AI 분석 오류 ({restaurant_name}): {e}")
            return {}

    def get_top_recommendations(
        self, user_profile: Dict[str, Any], all_restaurants_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """분석된 맛집 데이터와 사용자 프로필을 기반으로 최종 3곳 추천"""
        if not model or not all_restaurants_data:
            return all_restaurants_data[:3]

        logging.info("Gemini AI를 통해 사용자 맞춤 추천을 시작합니다...")
        restaurants_json_str = json.dumps(
            all_restaurants_data, ensure_ascii=False, indent=2
        )

        prompt = f"""
        당신은 사용자의 취향에 맞춰 맛집을 추천하는 전문가입니다.

        **사용자 프로필:**
        - 나이: {user_profile['age']}
        - 성별: {user_profile['gender']}
        - 방문 목적: {user_profile['purpose']}
        - 원하는 분위기: {user_profile['atmosphere']}
        - 희망 지역: {user_profile['location']}

        **분석된 맛집 후보 목록 (JSON):**
        {restaurants_json_str}

        **요청:**
        위 사용자 프로필과 가장 잘 맞는 맛집 3곳을 위의 후보 목록에서 선정해주세요.
        결과는 반드시 제공된 맛집 후보 목록의 JSON 객체 3개를 포함하는 JSON 배열 형식이어야 합니다.
        다른 설명이나 텍스트 없이 JSON 배열만 출력해주세요.
        """

        try:
            response = model.generate_content(prompt)
            clean_response = re.search(
                r"```json\s*(\[.*?\])\s*```", response.text, re.DOTALL
            )
            if clean_response:
                json_str = clean_response.group(1)
                top_3 = json.loads(json_str)
                logging.info(f"Gemini AI 추천 완료: {len(top_3)}개 맛집 선정")
                return top_3
            else:
                json_str = response.text[
                    response.text.find("[") : response.text.rfind("]") + 1
                ]
                top_3 = json.loads(json_str)
                logging.info(f"Gemini AI 추천 완료 (폴백): {len(top_3)}개 맛집 선정")
                return top_3
        except Exception as e:
            logging.error(f"Gemini AI 추천 생성 오류: {e}")
            return all_restaurants_data[:3]

    def process_restaurants(
        self, query: str, target_count: int = 30
    ) -> List[Dict[str, Any]]:
        """맛집 검색, 크롤링, 분석 전체 프로세스 실행 (목표 수량 달성까지)"""
        # 1. 카카오 API로 넉넉하게 맛집 후보 검색 (최대 45곳)
        candidate_restaurants = self.kakao_search_local(query)

        if not candidate_restaurants:
            logging.warning("검색된 맛집 후보가 없습니다.")
            return []

        analyzed_results = []

        # 2. 각 후보에 대해 크롤링 및 Gemini 분석 실행
        for i, restaurant in enumerate(candidate_restaurants):
            # 목표 수량(30개)을 채웠으면 중단
            if len(analyzed_results) >= target_count:
                logging.info(
                    f"목표 맛집 수량 {target_count}개를 달성하여 분석을 종료합니다."
                )
                break

            place_name = restaurant.get("place_name")
            logging.info(
                f"({i+1}/{len(candidate_restaurants)}) '{place_name}' 정보 수집 시도... (현재 {len(analyzed_results)}/{target_count}개 성공)"
            )

            # **정보 수집 강화**: 웹 페이지 10곳을 검색하여 리뷰 탐색
            web_results = self.kakao_search_web(place_name, size=10)

            all_reviews = []
            for web_result in web_results:
                url = web_result.get("url", "")
                content = self.fetch_page_content(url)
                if content:
                    reviews_on_page = [
                        line.strip()
                        for line in content.split("\n")
                        if len(line.strip()) > 15
                        and any(
                            k in line
                            for k in ["맛", "분위기", "가격", "서비스", "추천"]
                        )
                    ]
                    all_reviews.extend(reviews_on_page)

            if all_reviews:
                # 리뷰가 존재할 경우에만 Gemini 분석 실행
                analysis = self.analyze_restaurant_with_gemini(
                    restaurant, list(set(all_reviews))[:15]
                )  # 중복제거, 15개로 제한
                if analysis:
                    analyzed_results.append(analysis)
            else:
                # 리뷰를 못 찾았으면 건너뛰고 다음 후보로 진행
                logging.warning(f"리뷰를 찾지 못해 '{place_name}' 분석을 건너뜁니다.")

        logging.info(f"총 {len(analyzed_results)}개의 맛집 분석을 완료했습니다.")
        return analyzed_results


def save_to_json(data: List[Dict[str, Any]], filename: str = None):
    """결과를 JSON 파일로 저장"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"restaurant_recommendations_{timestamp}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"전체 결과 저장 완료: {filename}")
        return filename
    except Exception as e:
        logging.error(f"파일 저장 오류: {e}")
        return None


def print_summary(results: List[Dict[str, Any]], user_profile: Dict[str, Any]):
    """사용자에게 최종 추천 맛집 3곳 요약 정보 출력"""
    print("\n" + "=" * 80)
    print(f"'{user_profile['location']}' 지역, 사용자 맞춤 맛집 추천 TOP 3")
    print("=" * 80)

    if not results:
        print("\n추천할 맛집을 찾지 못했습니다. 다른 키워드로 시도해보세요.")
        return

    for i, result in enumerate(results, 1):
        name = result.get("name", "알 수 없음")

        print(f"\n추천 {i}: {name}")
        print("-" * 50)
        print(f"전화번호: {result.get('phone', '정보 없음')}")
        print(f"주소: {result.get('address', '정보 없음')}")
        print(f"대표 메뉴: {', '.join(result.get('signature_dishes', ['-']))}")
        print(f"가격대: {result.get('price_range', '-')}")
        print(f"장점: {', '.join(result.get('pros', ['-']))}")
        print(f"단점: {', '.join(result.get('cons', ['-']))}")
        print(f"키워드: {', '.join(result.get('keywords', ['-']))}")


# def main():
#     """메인 실행 함수"""
#     if not KAKAO_REST_KEY or not GOOGLE_API_KEY:
#         print(
#             "오류: KAKAO_REST_KEY 또는 GOOGLE_API_KEY 환경변수가 설정되지 않았습니다."
#         )
#         print(".env 파일을 확인해주세요.")
#         return

#     recommender = RestaurantRecommender()

#     print("AI 맛집 추천 프로그램")
#     print("=" * 50)

#     # 1. 사용자 입력 받기
#     user_profile = {
#         "location": input("원하는 지역을 입력하세요 (예: 강남역, 홍대): ").strip()
#         or "강남역",
#         "age": input("나이를 입력하세요 (예: 20대): ").strip() or "20대",
#         "gender": input("성별을 입력하세요 (예: 여성): ").strip() or "여성",
#         "purpose": input(
#             "방문 목적을 입력하세요 (예: 데이트, 회식, 가족식사): "
#         ).strip()
#         or "데이트",
#         "atmosphere": input(
#             "원하는 분위기를 입력하세요 (예: 조용한, 힙한, 가성비 좋은): "
#         ).strip()
#         or "분위기 좋은",
#     }

#     # 2. **수정된 부분**: 검색어는 지역명으로 단순화
#     search_query = f"{user_profile['location']} 맛집"
#     print(f"\n'{search_query}' 키워드로 맛집 후보를 검색합니다.")
#     print(
#         f"이후 AI가 '{user_profile['purpose']}', '{user_profile['atmosphere']}' 등의 세부 조건을 반영하여 추천합니다."
#     )
#     print("목표 수량(30개)을 채울 때까지 진행되므로 시간이 걸릴 수 있습니다...")
#     all_analyzed_data = recommender.process_restaurants(search_query, target_count=30)

#     if not all_analyzed_data:
#         print("\n분석할 맛집 정보를 수집하지 못했습니다. 프로그램을 종료합니다.")
#         return

#     # 3. 분석된 전체 데이터를 JSON 파일로 저장
#     save_to_json(all_analyzed_data)

#     # 4. 사용자 프로필에 가장 근접한 3가지 자료 추천
#     top_3_recommendations = recommender.get_top_recommendations(
#         user_profile, all_analyzed_data
#     )

#     # 5. 사용자에게 최종 결과 출력
#     print_summary(top_3_recommendations, user_profile)

#     print("\n" + "=" * 80)
#     print("작업 완료! 전체 분석 데이터는 JSON 파일로 저장되었습니다.")


# if __name__ == "__main__":
#     main()
