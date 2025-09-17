from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship # SQLAlchemy 관계
from sqlalchemy.sql import func # SQLAlchemy 함수
from .database import Base # SQLAlchemy3 Base 가져오기
# pgvector는 PostgreSQL 전용이므로 SQLite 사용 시 제거

class User(Base): # User 모델 정의
    __tablename__ = "users" # 테이블 이름
    
    # 유저 기본 정보
    id = Column(Integer, primary_key=True, index=True) # 사용자 ID
    name = Column(String, nullable=False) # 이름
    birthdate = Column(Date, nullable=False) # 생년월일
    gender = Column(String, nullable=False) # 성별
    email = Column(String, unique=True, index=True, nullable=False) # 이메일
    phone = Column(String, nullable=False, unique=True) # 전화번호
    address = Column(String, nullable=False) # 주소
    hashed_password = Column(String, nullable=False) # 해시된 비밀번호
    
    # 개인화 데이터
    interests = Column(String, nullable=True) # 관심사
    allergies = Column(Boolean, default=True) # 알레르기 여부
    allergies_detail = Column(String, nullable=True) # 알레르기 상세 정보
    
    # 계정 상태
    is_active = Column(Boolean, default=True) # 활성화 여부
    is_verified = Column(Boolean, default=False) # 이메일 인증 여부
    
    # 관계 설정
    search_logs = relationship("SearchLog", back_populates="user") # 검색 로그
    reviews = relationship("Review", back_populates="user") # 리뷰


# 음식점 모델
class Restaurant(Base):
    """맛집 최소 정보 (PostgreSQL에 저장) - 리뷰 연결용"""
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key=True, index=True) # 음식점 ID
    name = Column(String, index=True, nullable=False) # 음식점 이름
    address = Column(String, nullable=False) # 음식점 주소
    # 이름과 주소 조합으로 고유성 유지
    image_url = Column(String, nullable=True) # 음식점 이미지 URL
        
    reviews = relationship("Review", back_populates="restaurant") # 리뷰
    
    
class Review(Base): # Review 모델 정의 (사용자 리뷰 저장용)
    __tablename__ = "reviews" # 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True) # 리뷰 ID
    user_id = Column(Integer, ForeignKey("users.id")) # 사용자 ID
    restaurant_id = Column(Integer, ForeignKey("restaurants.id")) # 음식점 ID
    content = Column(Text, nullable=False) # 리뷰 내용
    rating = Column(Integer, nullable=False) # 평점
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 생성 시간
    is_ad = Column(Boolean, default=False) # 광고성 리뷰 여부
    user = relationship("User", back_populates="reviews") # 사용자와의 관계
    restaurant = relationship("Restaurant", back_populates="reviews") # 음식점과의 관계
    
# 검색 기록 저장 모델    
class SearchLog(Base): # SearchLog 모델 정의
    __tablename__ = "search_logs" # 테이블 이름
    
    id = Column(Integer, primary_key=True, index=True) # 검색 로그 ID
    user_id = Column(Integer, ForeignKey("users.id")) # 사용자 ID
    query = Column(String, nullable=False) # 검색어
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) # 검색 시간
    user = relationship("User", back_populates="search_logs") # 사용자와의 관계