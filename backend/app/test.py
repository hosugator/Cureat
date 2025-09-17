# backend/app/test_crawler_no_db.py

import json
import logging
import os
import pathlib
from dotenv import load_dotenv

# .env 파일 로드
project_root = pathlib.Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)
print(f"환경변수 로드 완료: {env_path}")
print(f"NAVER_SEARCH_CLIENT_ID: {os.getenv('NAVER_SEARCH_CLIENT_ID')}")

# 테스트에 필요한 모듈들을 상대 경로로 임포트합니다.
from . import service
from . import vectorDBService
from . import crud
from .service import naverMapService as naver_service # 네이버 서비스 임포트

# 로깅 기본 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_test_without_db():
    """
    DB 연결 없이 특정 음식점에 대한 크롤링 및 LLM 요약 기능을 테스트하고,
    결과를 JSON 파일로 저장합니다.
    """
    
    # --- 테스트할 음식점 정보 ---
    TEST_RESTAURANT_NAME = "강남역 맛집"
    # --------------------------

    print(f"--- '{TEST_RESTAURANT_NAME}'에 대한 정보 수집 테스트 시작 (DB 연결 없음) ---")
    
    # DB에 의존하는 함수들을 임시 함수로 대체 (Monkey Patching)
    def mock_get_restaurant_from_vector_db(restaurant_id):
        print(f"[Mock] 벡터 DB 조회 건너뛰기: {restaurant_id}")
        return None

    def mock_upsert_restaurant_to_vector_db(restaurant_id, vector, metadata):
        print(f"[Mock] 벡터 DB 저장 건너뛰기: {restaurant_id}")

    def mock_get_or_create_in_postgres(db, name, address):
        print(f"[Mock] PostgreSQL 저장 건너뛰기: {name}")
        return None

    # 원래 함수들을 임시 함수로 잠시 교체
    original_vector_get = vectorDBService.get_restaurant_by_id
    original_vector_upsert = vectorDBService.upsert_restaurant
    original_postgres_create = crud.get_or_create_restaurant_in_postgres
    
    vectorDBService.get_restaurant_by_id = mock_get_restaurant_from_vector_db
    vectorDBService.upsert_restaurant = mock_upsert_restaurant_to_vector_db
    crud.get_or_create_restaurant_in_postgres = mock_get_or_create_in_postgres

    try:
        # service.py의 로직 중 DB와 직접적인 관련이 없는 부분을 테스트
        print("\n1. 네이버 API로 후보군 검색...")
        print(f"naver_service 모듈: {naver_service}")
        print(f"search_naver_local 함수: {naver_service.search_naver_local}")
        candidates = naver_service.search_naver_local(TEST_RESTAURANT_NAME, display=30)
        
        if not candidates:
            raise Exception("네이버 API에서 음식점 정보를 찾지 못했습니다.")

        candidate = candidates[0]
        name = service._clean_html(candidate.get("title", ""))
        address = candidate.get("roadAddress") or candidate.get("address", "")
        
        print(f"   -> 후보 찾음: {name} ({address})")

        print("\n2. 블로그/웹사이트 크롤링 및 리뷰 교차 검증...")
        crawled_info = service.advanced_crawl_restaurant_details(name)

        if not crawled_info.get("crawled_reviews"):
            raise Exception("리뷰 크롤링에 실패했습니다.")
        
        print(f"   -> {len(crawled_info['crawled_reviews'])}개의 리뷰 스니펫 수집 완료 (신뢰도 점수: {crawled_info['review_trust_score']})")

        print("\n3. Gemini(LLM) API로 정보 요약...")
        summary_data = service.llm_summarize_details(name, crawled_info)

        if not summary_data:
            raise Exception("LLM 요약에 실패했습니다.")

        print("   -> AI 요약 완료!")

        # 최종 결과 조합
        final_result = {
            "name": name,
            "address": address,
            "crawled_info": crawled_info,
            "summary_data": summary_data
        }

        # 결과를 JSON 파일로 저장
        output_filename = "crawled_results.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n--- 테스트 성공! ---")
        print(f"결과가 '{output_filename}' 파일에 저장되었습니다.")

    except Exception as e:
        print(f"\n--- 테스트 중 오류 발생 ---")
        print(f"오류: {e}")
        print("\n[확인 사항]")
        print("- .env 파일에 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, GOOGLE_API_KEY 등이 올바르게 설정되었나요?")
        print("- 인터넷 연결에 문제가 없나요?")

    finally:
        # 테스트가 끝나면 원래 함수들로 복원
        vectorDBService.get_restaurant_by_id = original_vector_get
        vectorDBService.upsert_restaurant = original_vector_upsert
        crud.get_or_create_restaurant_in_postgres = original_postgres_create
        print("\n--- 테스트 종료 ---")

if __name__ == "__main__":
    run_test_without_db()
