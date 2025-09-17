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
        from_attributes = True


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
    
    signature_menu: Optional[str] = Field(None, description="대표 메뉴")
    summary_phone: Optional[str] = Field(None, description="전화번호")
    summary_parking: Optional[str] = Field(None, description="주차 정보")
    summary_price: Optional[str] = Field(None, description="가격대")
    summary_opening_hours: Optional[str] = Field(None, description="영업 시간")

class ChatRequest(BaseModel):
    """맛집 추천 요청 모델"""
    user_id: Optional[int] = Field(None, description="사용자 ID (비로그인 시 null)")
    prompt: str = Field(..., description="사용자의 맛집 추천 요청 메시지", example="강남역 근처에서 데이트하기 좋은 파스타 맛집 알려줘")

class RecommendationResponse(BaseModel):
    """맛집 추천 응답 모델"""
    answer: str = Field(..., description="AI의 응답 메시지", example="요청 조건에 맞는 맛집을 추천합니다!")
    restaurants: List[RestaurantDetail] = Field(default_factory=list, description="추천 음식점 목록")

class CourseRequest(BaseModel):
    user_id: int = Field(..., description="사용자 ID")
    location: str = Field(..., description="데이트 지역", example="강남")
    budget: Optional[str] = Field(None, description="예산", example="10만원")
    preferences: Optional[str] = Field(None, description="선호사항", example="실내 활동, 조용한 곳")

class CourseDetail(BaseModel):
    time: str = Field(..., description="시간")
    activity: str = Field(..., description="활동")

class CourseResponse(BaseModel):
    course: List[CourseDetail] = Field(default_factory=list, description="데이트 코스 추천")

# --- 리뷰 관련 스키마 ---
class ReviewCreate(BaseModel):
    restaurant_id: int = Field(..., description="음식점 ID")
    content: str = Field(..., description="리뷰 내용")
    rating: int = Field(..., ge=1, le=5, description="평점 (1-5)")

class Review(ReviewCreate):
    id: int = Field(..., description="리뷰 ID")
    user_id: int = Field(..., description="작성자 ID")
    created_at: datetime = Field(..., description="작성 시간")

    class Config:
        from_attributes = True

# --- 인증 관련 스키마 ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None