from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash # 비밀번호 해싱 함수 임포트
from datetime import date
from typing import List, Optional, Dict, Any

# 유저 관련 CRUD 함수
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    # 이메일로 사용자 조회
    # 1. 입력받은 비밀번호를 안전하게 해싱
    hashed_password = get_password_hash(user.password)
    
    # 2. schemas.py의 birthdate가 date 타입이므로 문자열 변환 필용 없음
    # 3. 데이터베이스 모델(models.py) 객체 생성
    db_user = models.User(
        name=user.name,
        birthdate=user.birthdate,
        gender=user.gender,
        email=user.email,
        phone=user.phone,
        address=user.address,
        interests=user.interests,
        allergies=user.allergies,
        allergies_detail=user.allergies_detail,
        hashed_password=hashed_password,
        is_verified=True, # 이메일 인증 필드 추가 (기본값 False)
    )
    
    # 4. 생성된 객체를 세션에 추가하고 데이터베이스에 커밋
    db.add(db_user) # 세션에 추가
    db.commit() # 변경사항 커밋
    db.refresh(db_user) # 새로 생성된 사용자 정보 갱신
    return db_user # 생성된 사용자 반환

# 식당 관련 CRUD 함수
def get_restaurant_by_id(db: Session, restaurant_id: int):
    """ID로 음식점을 조회합니다."""
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()

def get_or_create_restaurant_in_postgres(db: Session, name: str, address: str) -> models.Restaurant:
    """ 
    DB에 맛집이 있으면 정보를 가져오고, 없으면 새로 생성
    이름과 주소를 기준으로 중복 확인
    """
    restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.name == name,
        models.Restaurant.address == address
    ).first()
    if restaurant:
        return restaurant
    
    db_restaurant = models.Restaurant(name=name, address=address)
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

# 리뷰 & 검색로그 CRUD 함수
def create_review(db: Session, review: schemas.ReviewCreate, user_id: int):
    """새로운 리뷰를 생성"""
    db_review = models.Review(**review.dict(), user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def create_search_log(db: Session, user_id: int, query: str):
    """새로운 검색 로그를 생성"""
    db_log = models.SearchLog(user_id=user_id, query=query)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log