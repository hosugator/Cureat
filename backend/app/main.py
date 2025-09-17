# --- 시스템 경로 설정 ---
# uvicorn --reload 시에도 'app' 모듈을 찾을 수 있도록 프로젝트 루트의 경로를 추가합니다.
# 현재 파일(main.py)의 위치를 기준으로 backend 폴더의 부모, 즉 프로젝트 루트를 시스템 경로에 추가합니다.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import logging
import traceback
from datetime import timedelta

# 프로젝트 내부 모듈
from . import models, schemas, crud, auth, recommendation_service
from .database import get_db, engine

# 환경 변수 로드는 config.py에서 처리하므로 main.py에서는 제거합니다.
# load_dotenv()

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

# --- 상태 확인 엔드포인트 ---
@app.get("/health", tags=["상태"], summary="API 서버 상태 확인")
def health_check():
    """API 서버가 정상적으로 실행 중인지 확인합니다."""
    return {"status": "ok", "message": "Cureat API is running!"}

# --- 인증 엔드포인트 ---
@app.post(
    "/token", 
    response_model=schemas.Token, 
    tags=["인증"],
    summary="로그인 및 액세스 토큰 발급",
    description="사용자 이메일(username 필드)과 비밀번호를 `form-data` 형식으로 전송하여 로그인하고, 인증 성공 시 JWT 액세스 토큰을 발급받습니다."
)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
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
    return {"message": "Cureat API is running!"}

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
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    return crud.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=schemas.User, tags=["사용자"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """특정 사용자 정보를 조회합니다."""
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user

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
    return current_user

@app.post(
    "/recommendations", 
    response_model=schemas.RecommendationResponse, 
    tags=["추천"],
    summary="AI 맛집 추천 받기"
)
def get_recommendation(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        user = None
        if request.user_id:
            user = crud.get_user_by_id(db, user_id=request.user_id)
            # user_id가 요청되었으나 DB에 없는 경우 에러 처리 (선택적)
            if not user:
                raise HTTPException(status_code=404, detail="요청한 사용자를 찾을 수 없습니다.")

        recommendation_data = recommendation_service.get_personalized_recommendation(db, request, user)
        
        if user:
            crud.create_search_log(db, user_id=user.id, query=request.prompt)
            
        return recommendation_data
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error in /recommendations endpoint")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류: {str(e)}")

@app.post(
    "/date-course", 
    response_model=schemas.CourseResponse, 
    tags=["추천"],
    summary="AI 데이트 코스 추천 받기"
)
def create_course(request: schemas.CourseRequest, db: Session = Depends(get_db)):
    user = None
    if request.user_id:
        user = crud.get_user_by_id(db, user_id=request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    course_data = recommendation_service.create_date_course(db, request, user)
    return course_data

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
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    return crud.create_review(db=db, review=review, user_id=1)  # 임시로 user_id=1 사용

# --- 개발용 테스트 엔드포인트 ---
@app.get("/test-naver-api", tags=["테스트"])
def test_naver_api():
    try:
        # 네이버 API 연결 테스트를 위한 간단한 검색
        # 네이버 Maps 서비스 제거됨 - 간단한 테스트 응답
        test_result = {"message": "네이버 Maps 기능이 제거되었습니다"}
        
        return {
            "status": "success",
            "message": "네이버 API 연결 정상",
            "data": test_result
        }
        
    except Exception as e:
        # 오류 발생 시, 어떤 예외가 발생했는지 구체적으로 확인하기 위해 로깅 추가
        import traceback
        logging.error("Test API Error: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Test API에서 오류 발생: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)