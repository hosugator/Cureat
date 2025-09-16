from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from datetime import datetime

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

def verify_password(plain_password, hashed_password): 
    return pwd_context.verify(plain_password, hashed_password) 

def get_password_hash(password): 
    return pwd_context.hash(password) 

# 유저 관련 CRUD 함수
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """ID로 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
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
        is_verified=False, 
    )
    db.add(db_user) 
    db.commit() 
    db.refresh(db_user) 
    return db_user 

# 음식점 정보 저장 함수 (새로 추가)
def save_restaurant_info_and_vector(db: Session, place_name: str, place_info: dict, vector: list):
    """음식점 정보를 업데이트하고 벡터를 저장합니다."""
    
    # 중복 확인
    db_restaurant = db.query(models.Restaurant).filter(models.Restaurant.name == place_name).first()
    
    # 만약 음식점이 이미 존재하면 업데이트, 없으면 새로 생성
    if db_restaurant:
        db_restaurant.summary_place = place_info.get("summary_place")
        db_restaurant.summary_address = place_info.get("summary_address")
        db_restaurant.summary_category = place_info.get("summary_category")
        db_restaurant.summary_description = place_info.get("summary_description")
        db_restaurant.summary_feature_menu = place_info.get("summary_feature_menu")
        db_restaurant.summary_phone = place_info.get("summary_phone")
        db_restaurant.summary_parking = place_info.get("summary_parking")
        db_restaurant.summary_price = place_info.get("summary_price")
        db_restaurant.summary_opening_hours = place_info.get("summary_opening_hours")
        db_restaurant.image_url = place_info.get("image_url")
        db_restaurant.vector = vector
    else:
        db_restaurant = models.Restaurant(
            name=place_name,
            summary_place=place_info.get("summary_place"),
            summary_address=place_info.get("summary_address"),
            summary_category=place_info.get("summary_category"),
            summary_description=place_info.get("summary_description"),
            summary_feature_menu=place_info.get("summary_feature_menu"),
            summary_phone=place_info.get("summary_phone"),
            summary_parking=place_info.get("summary_parking"),
            summary_price=place_info.get("summary_price"),
            summary_opening_hours=place_info.get("summary_opening_hours"),
            image_url=place_info.get("image_url"),
            vector=vector
        )
        db.add(db_restaurant)

    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant