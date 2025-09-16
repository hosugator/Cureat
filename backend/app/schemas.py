from pydantic import BaseModel, Field, EmailStr # pydantic의 BaseModel, Field, EmailStr, validator 임포트
from typing import Optional, List # Optional 임포트
from datetime import date, datetime # date, datetime 임포트
import re # 정규표현식 모듈 임포트


# --- 사용자 관련 스키마 ---
class UserCreate(BaseModel):
    """회원가입 요청 시 사용할 데이터 모델"""
    name: str = Field(..., min_length=2, max_length=50, description="사용자 이름", example="홍길동")
    birthdate: date = Field(..., description="생년월일", example="1995-10-24")
    gender: str = Field(..., description="성별", example="남자")
    email: EmailStr = Field(..., description="이메일 주소", example="user@example.com")
    phone: str = Field(..., min_length=10, max_length=11, description="연락처 (하이픈 제외)", example="01012345678")
    address: str = Field(..., description="집 주소", example="서울시 강남구 테헤란로")
    interests: Optional[str] = Field(None, description="관심사 (쉼표로 구분)", example="데이트, 회식, 가족모임")
    allergies: bool = Field(False, description="알러지 여부")
    allergies_detail: Optional[str] = Field(None, description="알러지 상세 정보", example="땅콩, 새우")
    password: str = Field(..., min_length=8, max_length=20, description="비밀번호", example="1q2w3e4r!")

class User(BaseModel):
    """API 응답으로 보낼 사용자 정보 모델 (비밀번호 제외)"""
    id: int = Field(..., description="사용자 고유 ID", example=1)
    name: str = Field(..., description="사용자 이름", example="홍길동")
    birthdate: date = Field(..., description="생년월일", example="1995-10-24")
    gender: str = Field(..., description="성별", example="남자")
    email: EmailStr = Field(..., description="이메일 주소", example="user@example.com")
    phone: str = Field(..., description="연락처", example="01012345678")
    address: str = Field(..., description="주소", example="서울시 강남구 테헤란로")
    interests: Optional[str] = Field(None, description="관심사", example="데이트, 회식, 가족모임")
    allergies: bool = Field(..., description="알러지 여부")
    allergies_detail: Optional[str] = Field(None, description="알러지 상세 정보", example="땅콩, 새우")
    is_verified: bool = Field(..., description="이메일 인증 여부")

    class Config:
        orm_mode = True

# --- 음식점 및 추천 관련 스키마 ---
class RestaurantDetail(BaseModel):
    """음식점 상세 정보 모델"""
    name: str = Field(..., description="가게 이름", example="규카츠정")
    address: Optional[str] = Field(None, description="가게 주소", example="서울 강남구 강남대로102길 14")
    image_url: Optional[str] = Field(None, description="가게 대표 이미지 URL")
    mapx: Optional[str] = Field(None, description="가게 위치 X 좌표 (경도)")
    mapy: Optional[str] = Field(None, description="가게 위치 Y 좌표 (위도)")
    
    summary_pros: Optional[List[str]] = Field(None, description="AI가 요약한 음식점 장점 3가지")
    summary_cons: Optional[List[str]] = Field(None, description="AI가 요약한 음식점 단점 3가지")
    keywords: Optional[List[str]] = Field(None, description="AI가 추출한 음식점 키워드 5가지")
    nearby_attractions: Optional[List[str]] = Field(None, description="AI가 추천하는 주변 놀거리 3가지")
    signature_menu: Optional[str] = Field(None, description="AI가 추천하는 대표 메뉴")
    summary_phone: Optional[str] = Field(None, description="전화번호")
    summary_parking: Optional[str] = Field(None, description="주차 정보")
    summary_price: Optional[str] = Field(None, description="가격대")
    summary_opening_hours: Optional[str] = Field(None, description="영업시간")
    
    view_count: int = Field(0, description="조회수")
    like_count: int = Field(0, description="좋아요 수")
    dislike_count: int = Field(0, description="싫어요 수")
    comment_count: int = Field(0, description="댓글 수")
    share_count: int = Field(0, description="공유 수")
    is_favorite_count: int = Field(0, description="즐겨찾기 수")

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    """맛집 추천 요청 모델"""
    prompt: str = Field(..., description="사용자의 맛집 추천 요청 메시지", example="강남역 근처에서 데이트하기 좋은 파스타 맛집 알려줘")

class RecommendationResponse(BaseModel):
    """맛집 추천 응답 모델"""
    answer: str = Field(..., description="AI의 응답 메시지", example="요청 조건에 맞는 맛집을 추천합니다!")
    restaurants: List[RestaurantDetail] = Field(..., description="추천된 음식점 목록")

class CourseRequest(BaseModel):
    """코스 추천 요청 모델"""
    location: str = Field(..., description="중심 위치", example="서울 강남역")
    start_time: str = Field(..., description="코스 시작 시간", example="14:00")
    end_time: str = Field(..., description="코스 종료 시간", example="20:00")
    theme: str = Field(..., description="코스 테마", example="분위기 좋은 곳에서 저녁 먹고 싶어")

class CourseDetail(BaseModel):
    """하나의 데이트 코스를 나타내는 모델"""
    title: str = Field(..., description="코스 제목", example="성수동 감성 카페와 예술 산책")
    steps: List[RestaurantDetail] = Field(..., description="코스에 포함된 각 장소 목록")

class CourseResponse(BaseModel):
    """코스 추천 응답 모델"""
    courses: List[CourseDetail] = Field(..., description="추천된 데이트 코스 목록")

# --- 리뷰 관련 스키마 ---
class ReviewCreate(BaseModel):
    """리뷰 생성 요청 모델"""
    restaurant_id: int = Field(..., description="리뷰를 작성할 음식점의 고유 ID", example=123)
    content: str = Field(..., min_length=10, description="리뷰 내용", example="음식이 정말 맛있고 분위기도 좋았어요!")
    rating: int = Field(..., ge=1, le=5, description="평점 (1~5)", example=5)

class Review(ReviewCreate):
    """리뷰 정보 응답 모델"""
    id: int = Field(..., description="리뷰 고유 ID", example=1)
    created_at: datetime = Field(..., description="리뷰 작성 시간")
    class Config:
        orm_mode = True

# --- 인증 관련 스키마 ---
class Token(BaseModel):
    """액세스 토큰 응답 모델"""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field("bearer", example="bearer")

class TokenData(BaseModel):
    """토큰에 포함될 데이터 모델"""
    email: Optional[str] = None
