from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from datetime import timedelta

# 프로젝트 내부 모듈
from . import models, schemas, crud, service, auth
from .database import get_db

# 환경 변수 로드
load_dotenv()

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

# API 문서에 표시될 태그 메타데이터
tags_metadata = [
    {
        "name": "인증",
        "description": "사용자 인증 및 토큰 발급을 위한 API",
    },
    {
        "name": "사용자",
        "description": "사용자 생성, 조회 등 사용자 관련 API",
    },
    {
        "name": "추천",
        "description": "AI 기반 맛집 및 데이트 코스 추천 API",
    },
    {
        "name": "리뷰",
        "description": "맛집 리뷰 생성 및 관리를 위한 API",
    },
]

# FastAPI 앱 생성
app = FastAPI(
    title="Cureat API",
    description="AI 기반 맛집 추천 서비스 Cureat의 API 문서입니다.",
    version="1.0.0",
    openapi_tags=tags_metadata
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 인증 엔드포인트 ---
@app.post(
    "/token", 
    response_model=schemas.Token, 
    tags=["인증"],
    summary="로그인 및 액세스 토큰 발급",
    description="사용자 이메일(username 필드)과 비밀번호를 `form-data` 형식으로 전송하여 로그인하고, 인증 성공 시 JWT 액세스 토큰을 발급받습니다."
)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- 라우터 ---
@app.get("/", tags=["상태"], summary="API 상태 확인")
async def root():
    """
    API 서버의 현재 동작 상태를 확인합니다. "정상 작동중" 메시지를 반환하면 서버가 준비된 상태입니다.
    """
    return {"message": "Cureat API가 정상적으로 작동중입니다."}

@app.post(
    "/users/", 
    response_model=schemas.User, 
    tags=["사용자"],
    status_code=status.HTTP_201_CREATED,
    summary="신규 사용자 회원가입",
    responses={
        400: {"description": "이미 등록된 이메일일 경우 발생합니다."}
    }
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자를 생성(회원가입)합니다.

    - **name**: 사용자 이름
    - **birthdate**: 생년월일 (YYYY-MM-DD)
    - **gender**: 성별
    - **email**: 이메일 주소 (고유해야 함)
    - **phone**: 연락처 (하이픈 제외)
    - **password**: 비밀번호 (8자 이상 20자 이하)
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="이미 등록된 이메일입니다."
        )
    return crud.create_user(db=db, user=user)

@app.get(
    "/users/me", 
    response_model=schemas.User, 
    tags=["사용자"],
    summary="현재 로그인된 사용자 정보 조회",
    responses={
        401: {"description": "인증되지 않았거나 토큰이 만료되었을 경우 발생합니다."}
    }
)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """
    현재 로그인된 사용자(요청 시 사용된 토큰의 소유자)의 상세 정보를 조회합니다.
    """
    return current_user

@app.post(
    "/chat/recommendation", 
    response_model=schemas.RecommendationResponse, 
    tags=["추천"],
    summary="AI 맛집 추천 받기",
    responses={
        401: {"description": "인증되지 않았거나 토큰이 만료되었을 경우 발생합니다."}
    }
)
def get_recommendation(request: schemas.ChatRequest, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    사용자의 요청 메시지(`prompt`)와 사용자 프로필(관심사, 알러지 등)을 기반으로 AI가 개인화된 맛집을 추천합니다.
    """
    crud.create_search_log(db, user_id=current_user.id, query=request.prompt)
    result = service.get_personalized_recommendation(db, request, current_user)
    return result

@app.post(
    "/chat/course", 
    response_model=schemas.CourseResponse, 
    tags=["추천"],
    summary="AI 데이트 코스 추천 받기",
    responses={
        401: {"description": "인증되지 않았거나 토큰이 만료되었을 경우 발생합니다."}
    }
)
def get_course_recommendation(request: schemas.CourseRequest, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    사용자가 입력한 위치, 시간, 테마를 바탕으로 AI가 최적의 데이트 코스를 추천합니다.
    """
    result = service.create_date_course(db, request, current_user)
    return result

@app.post(
    "/reviews/", 
    response_model=schemas.Review, 
    tags=["리뷰"],
    status_code=status.HTTP_201_CREATED,
    summary="맛집 리뷰 작성",
    responses={
        401: {"description": "인증되지 않았거나 토큰이 만료되었을 경우 발생합니다."},
        404: {"description": "리뷰를 작성하려는 음식점이 DB에 존재하지 않을 경우 발생합니다."}
    }
)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    """
    특정 음식점(`restaurant_id`)에 대한 리뷰를 작성합니다.
    """
    db_restaurant = crud.get_restaurant_by_id(db, restaurant_id=review.restaurant_id)
    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="해당 음식점을 찾을 수 없습니다.")
    return crud.create_review(db=db, review=review, user_id=current_user.id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)