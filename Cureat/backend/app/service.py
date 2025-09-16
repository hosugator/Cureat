import os
import requests
import json
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from . import models, schemas, nlpService
from sqlalchemy.orm import Session

# .env 파일에서 환경변수 로드
load_dotenv()

# API Key 및 모델 설정
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# 네이버 API 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 사용할 Gemini 모델 객체 생성
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# 외부 API 호출 헬퍼 함수
def _call_naver_api(url: str, params: dict = None, headers: dict = None):
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"네이버 API 호출 중 오류 발생: {url}, {e}")
        return None

# 네이버 장소 검증 함수
def verify_place_with_naver(place_name: str):
    place_info = _call_naver_api(
        "https://openapi.naver.com/v1/search/local.json",
        params={"query": place_name, "display": 1},
        headers={
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
    )
    if place_info and place_info.get('items'):
        return place_info['items'][0]
    return None

# --- 맛집 추천 기능 ---
async def get_recommendation_for_user(user: models.User, prompt: str, db: Session):
    # 이 부분은 현재 단계에서는 구현되지 않았습니다.
    # 벡터 검색 및 Gemini API를 통한 맛집 추천 로직이 여기에 들어갈 예정입니다.
    # 추후 사용자의 검색 프롬프트와 DB의 벡터를 비교하여 관련성 높은 음식점을 반환합니다.
    
    # 예시 응답 반환 (추후 실제 로직으로 대체)
    return schemas.RecommendationResponse(
        answer="아직 구현되지 않은 기능입니다. 곧 만나보실 수 있습니다!",
        restaurants=[]
    )

# --- 데이트 코스 추천 기능 ---
async def create_date_course(request: schemas.CourseRequest, user: models.User):
    # 이 부분은 현재 단계에서는 구현되지 않았습니다.
    # Gemini API를 통해 데이트 코스를 추천하는 로직이 여기에 들어갈 예정입니다.
    
    # 예시 응답 반환 (추후 실제 로직으로 대체)
    return schemas.CourseResponse(
        answer="아직 구현되지 않은 기능입니다. 곧 만나보실 수 있습니다!",
        courses=[]
    )
