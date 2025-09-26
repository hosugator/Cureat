from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash # 비밀번호 해싱 함수 임포트
from datetime import date
from typing import List, Optional, Dict, Any

# 유저 관련 CRUD 함수
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    """전화번호로 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.phone == phone).first()

def get_user_by_id(db: Session, user_id: int):
    """ID로 사용자를 조회합니다."""
    return db.query(models.User).filter(models.User.id == user_id).first()

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
        allergies=user.allergies if user.allergies is not None else False, # allergies 기본값 처리
        allergies_detail=user.allergies_detail,
        hashed_password=hashed_password,
        is_verified=True  # 이메일 인증 필드 추가 (기본값 True)
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

def get_or_create_restaurant(db: Session, name: str, address: str) -> models.Restaurant:
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

def create_or_update_restaurant_with_analysis(db: Session, restaurant_data: Dict[str, Any]) -> models.Restaurant:
    """
    AI 분석 데이터와 함께 맛집 정보를 생성하거나 업데이트
    """
    import json
    
    # 기존 맛집 확인 (이름과 주소로)
    existing_restaurant = db.query(models.Restaurant).filter(
        models.Restaurant.name == restaurant_data.get('name'),
        models.Restaurant.address == restaurant_data.get('address')
    ).first()
    
    if existing_restaurant:
        # 기존 맛집 업데이트
        existing_restaurant.phone = restaurant_data.get('phone')
        existing_restaurant.operating_hours = restaurant_data.get('operating_hours')
        existing_restaurant.signature_dishes = json.dumps(restaurant_data.get('signature_dishes', []), ensure_ascii=False)
        existing_restaurant.price_range = restaurant_data.get('price_range')
        existing_restaurant.pros = json.dumps(restaurant_data.get('pros', []), ensure_ascii=False)
        existing_restaurant.cons = json.dumps(restaurant_data.get('cons', []), ensure_ascii=False)
        existing_restaurant.keywords = json.dumps(restaurant_data.get('keywords', []), ensure_ascii=False)
        existing_restaurant.category = restaurant_data.get('category')
        existing_restaurant.atmosphere = restaurant_data.get('atmosphere')
        
        db.commit()
        db.refresh(existing_restaurant)
        return existing_restaurant
    else:
        # 새 맛집 생성
        new_restaurant = models.Restaurant(
            name=restaurant_data.get('name'),
            address=restaurant_data.get('address'),
            phone=restaurant_data.get('phone'),
            operating_hours=restaurant_data.get('operating_hours'),
            signature_dishes=json.dumps(restaurant_data.get('signature_dishes', []), ensure_ascii=False),
            price_range=restaurant_data.get('price_range'),
            pros=json.dumps(restaurant_data.get('pros', []), ensure_ascii=False),
            cons=json.dumps(restaurant_data.get('cons', []), ensure_ascii=False),
            keywords=json.dumps(restaurant_data.get('keywords', []), ensure_ascii=False),
            category=restaurant_data.get('category'),
            atmosphere=restaurant_data.get('atmosphere')
        )
        
        db.add(new_restaurant)
        db.commit()
        db.refresh(new_restaurant)
        return new_restaurant

def search_restaurants_in_db(db: Session, query: str, limit: int = 50) -> List[models.Restaurant]:
    """
    DB에서 쿼리와 관련된 맛집 검색
    이름, 주소, 키워드, 카테고리에서 검색
    """
    from sqlalchemy import or_, func
    
    search_term = f"%{query}%"
    
    restaurants = db.query(models.Restaurant).filter(
        or_(
            models.Restaurant.name.ilike(search_term),
            models.Restaurant.address.ilike(search_term),
            models.Restaurant.keywords.ilike(search_term),
            models.Restaurant.category.ilike(search_term),
            models.Restaurant.atmosphere.ilike(search_term)
        )
    ).limit(limit).all()
    
    return restaurants

def get_all_restaurants_from_db(db: Session) -> List[models.Restaurant]:
    """
    DB에 저장된 모든 맛집 조회 (AI 분석 완료된 것만)
    """
    restaurants = db.query(models.Restaurant).filter(
        models.Restaurant.signature_dishes.isnot(None)  # AI 분석 데이터가 있는 것만
    ).all()
    
    return restaurants

def convert_db_restaurant_to_dict(restaurant: models.Restaurant) -> Dict[str, Any]:
    """
    DB Restaurant 모델을 딕셔너리로 변환
    """
    import json
    
    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "phone": restaurant.phone or "",
        "operating_hours": restaurant.operating_hours or "",
        "signature_dishes": json.loads(restaurant.signature_dishes) if restaurant.signature_dishes else [],
        "price_range": restaurant.price_range or "",
        "pros": json.loads(restaurant.pros) if restaurant.pros else [],
        "cons": json.loads(restaurant.cons) if restaurant.cons else [],
        "keywords": json.loads(restaurant.keywords) if restaurant.keywords else [],
        "category": restaurant.category or "",
        "atmosphere": restaurant.atmosphere or "",
        "created_at": restaurant.created_at.isoformat() if restaurant.created_at else "",
        "updated_at": restaurant.updated_at.isoformat() if restaurant.updated_at else ""
    }

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

def get_user_personalization_profile(db: Session, user_id: int) -> Dict[str, Any]:
    """
    사용자 ID로 검색에 필요한 핵심 개인화 데이터만 조회
    - 나이대, 성별, 알레르기 여부/상세정보, 관심사만 포함
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return {}
    
    # 생년월일에서 연령대 계산
    from datetime import date
    today = date.today()
    age = today.year - user.birthdate.year
    if today.month < user.birthdate.month or (today.month == user.birthdate.month and today.day < user.birthdate.day):
        age -= 1
    
    # 연령대 구간으로 변환
    if age < 20:
        age_group = "10대"
    elif age < 30:
        age_group = "20대"
    elif age < 40:
        age_group = "30대"
    elif age < 50:
        age_group = "40대"
    else:
        age_group = "50대 이상"
    
    # 검색에 필요한 핵심 개인화 데이터만 반환
    profile = {
        "user_id": user.id,
        "age_group": age_group,           # 나이대
        "gender": user.gender,            # 성별
        "allergies": user.allergies,      # 알레르기 여부
        "allergies_detail": user.allergies_detail or "",  # 알레르기 상세정보
        "interests": user.interests or "" # 관심사
    }
    
    return profile