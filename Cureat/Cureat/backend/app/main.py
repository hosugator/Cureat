import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, service
from .database import SessionLocal, engine, get_db, create_all_tables, enable_pgvector_extension

# .env 파일에서 환경변수 로드
load_dotenv()

# API Key 및 모델 설정
# Gemini API 설정
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# 사용할 Gemini 모델 객체 생성
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Naver API 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# FastAPI 앱 인스턴스 생성
app = FastAPI()

# 앱 시작 시 실행될 이벤트 핸들러
@app.on_event("startup")
def on_startup():
    print("FastAPI 애플리케이션 시작...")
    # 데이터베이스 테이블 생성
    create_all_tables()
    # pgvector 확장 활성화
    enable_pgvector_extension()
    print("테이블 생성 및 pgvector 확장 활성화 완료.")

# API 라우터
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/recommendation/", response_model=schemas.RecommendationResponse)
async def get_recommendation(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    # 사용자 정보 조회
    user = crud.get_user_by_id(db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 추천 서비스 호출
    return await service.get_recommendation_for_user(user, request.prompt, db)
