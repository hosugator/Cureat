# app/schemas.py

from typing import Optional, List # 타입 힌트 사용을 위해 임포트
from pydantic import BaseModel, Field # Pydantic BaseModel 및 Field 사용을 위해 임포트
from datetime import datetime # 날짜/시간 타입 사용을 위해 임포트
import uuid # UUID 생성 및 사용을 위해 임포트

# UUID 문자열을 생성하는 헬퍼 함수
def generate_uuid() -> str:
    return str(uuid.uuid4())

# User 관련 Pydantic 스키마
class UserBase(BaseModel):
    name: str = Field(..., example="김철수") # 사용자 이름, 필수 필드, 예시 값
    preference: Optional[str] = Field(None, example="한식, 카페") # 사용자 선호 카테고리, 선택 필드, 예시 값

class UserCreate(UserBase):
    # 사용자 생성 시 ID는 자동으로 생성되도록 default_factory 사용
    id: str = Field(default_factory=generate_uuid)

class User(UserBase):
    id: str # 사용자 ID
    created_at: datetime # 생성 시간
    updated_at: datetime # 업데이트 시간
    class Config:
        orm_mode = True # SQLAlchemy ORM 객체를 Pydantic 모델로 변환할 수 있도록 설정

# Restaurant 관련 Pydantic 스키마
class RestaurantBase(BaseModel):
    name: str = Field(..., example="맛있는 식당") # 맛집 이름, 필수 필드
    category: str = Field(..., example="한식") # 맛집 카테고리, 필수 필드
    location: str = Field(..., example="서울 강남구") # 맛집 위치, 필수 필드
    description: Optional[str] = Field(None, example="깔끔하고 정갈한 한정식 전문점입니다.") # 맛집 상세 설명, 선택 필드

class RestaurantCreate(RestaurantBase):
    # 맛집 생성 시 ID는 자동으로 생성되도록 default_factory 사용
    id: str = Field(default_factory=generate_uuid)

class Restaurant(RestaurantBase):
    id: str # 맛집 ID
    created_at: datetime # 생성 시간
    updated_at: datetime # 업데이트 시간
    class Config:
        orm_mode = True # ORM 객체 변환 설정

# Review 관련 Pydantic 스키마
class ReviewBase(BaseModel):
    user_id: str = Field(..., example="uuid-of-user") # 리뷰 작성 사용자 ID, 필수 필드
    restaurant_id: str = Field(..., example="uuid-of-restaurant") # 리뷰 대상 맛집 ID, 필수 필드
    content: str = Field(..., example="음식이 정말 맛있고 분위기도 좋았습니다!") # 리뷰 내용, 필수 필드
    rating: int = Field(..., ge=1, le=5, example=5) # 평점 (1~5), 필수 필드, 범위 제한

class ReviewCreate(ReviewBase):
    # 리뷰 생성 시 ID는 자동으로 생성되도록 default_factory 사용
    id: str = Field(default_factory=generate_uuid)

class Review(ReviewBase):
    id: str # 리뷰 ID
    created_at: datetime # 생성 시간
    updated_at: datetime # 업데이트 시간
    class Config:
        orm_mode = True # ORM 객체 변환 설정

# ReviewSummary (리뷰 요약) 관련 Pydantic 스키마
class ReviewSummaryBase(BaseModel):
    review_id: str # 요약 대상 리뷰 ID
    keywords: Optional[str] = None # 요약 키워드 (콤마로 구분된 문자열)
    positive_summary: Optional[str] = None # 긍정적인 요약
    negative_summary: Optional[str] = None # 부정적인 요약
    full_summary: Optional[str] = None # 전체 요약
    sentiment: Optional[str] = None # 전반적인 감정 (예: 'positive', 'neutral', 'negative')

class ReviewSummary(ReviewSummaryBase):
    id: str # 요약 ID
    created_at: datetime # 생성 시간
    class Config:
        orm_mode = True # ORM 객체 변환 설정

# Recommendation (추천 이력) 관련 Pydantic 스키마 (선택 사항)
class Recommendation(BaseModel):
    id: str # 추천 기록 ID
    user_id: str # 추천을 받은 사용자 ID
    restaurant_id: str # 추천된 맛집 ID
    recommendation_score: Optional[int] = None # 추천 시 점수
    recommendation_type: Optional[str] = None # 추천 방식
    created_at: datetime # 생성 시간
    class Config:
        orm_mode = True # ORM 객체 변환 설정

# 추천 응답을 위한 스키마
# 추천된 맛집 정보와 함께 유사도 점수를 포함합니다.
class RecommendedRestaurant(BaseModel):
    restaurant: Restaurant # 추천된 맛집 정보 (Restaurant 스키마 사용)
    similarity_score: float # 유사도 점수