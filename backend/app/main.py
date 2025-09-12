import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI

# .env 파일에서 환경변수 로드

# API Key 및 모델 설정
# Gemini API 설정
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

app = FastAPI()
# Naver API 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# 사용할 Gemini 모델 객체 생성
# gemini_model = genai.Model.get("gemini-1.5-flash")
# 수정된 코드
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# 외부 API 호출 함수

def verify_place_with_naver(place_name: str):
    """네이버 검색 API로 장소의 실존 여부와 정보 검증"""
    # 이전 답변에서 제공한 네이버 검색 API 호출 코드
    url = "https://openapi.naver.com/v1/search/local.json"
    params = {"query": place_name, "display": 1}
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json().get("items", [])
        return search_results[0] if search_results else None
    except requests.exceptions.RequestException as e:
        print(f"네이버 검색 API 호출 중 오류 발생: {e}")
        return None
    
    