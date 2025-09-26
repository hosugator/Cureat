from typing import List, Dict, Any
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal
import json

def upsert_restaurant(restaurant_id: str, vector: List[float], metadata: Dict[str, Any]):
    """맛집의 메타데이터를 SQLite에 저장하거나 업데이트 (벡터는 무시)"""
    db = SessionLocal()
    try:
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == int(restaurant_id)).first()
        if restaurant:
            # 메타데이터를 restaurant 테이블의 기존 필드에 업데이트
            if 'category' in metadata:
                restaurant.category = metadata['category']
            if 'keywords' in metadata:
                if isinstance(metadata['keywords'], list):
                    restaurant.keywords = json.dumps(metadata['keywords'])
                else:
                    restaurant.keywords = str(metadata['keywords'])
            if 'atmosphere' in metadata:
                restaurant.atmosphere = metadata['atmosphere']
            
            db.commit()
            print(f"Restaurant ID {restaurant_id} 메타데이터가 SQLite에 업데이트 되었습니다.")
    finally:
        db.close()
    
def query_similar_restaurants(keywords: List[str], n_results: int = 3) -> List[Dict[str, Any]]:
    """키워드를 기반으로 SQLite에서 유사한 맛집을 검색합니다."""
    db = SessionLocal()
    try:
        restaurants = db.query(models.Restaurant).all()
        
        matched_restaurants = []
        for restaurant in restaurants:
            score = 0
            for keyword in keywords:
                if keyword.lower() in (restaurant.name or '').lower():
                    score += 3
                if keyword.lower() in (restaurant.category or '').lower():
                    score += 2
                if keyword.lower() in (restaurant.keywords or '').lower():
                    score += 1
            
            if score > 0:
                matched_restaurants.append({
                    'id': restaurant.id,
                    'name': restaurant.name,
                    'category': restaurant.category,
                    'address': restaurant.address,
                    'keywords': restaurant.keywords,
                    'score': score
                })
        
        # 점수 순으로 정렬
        matched_restaurants.sort(key=lambda x: x['score'], reverse=True)
        return matched_restaurants[:n_results]
        
    finally:
        db.close()

def get_restaurant_by_id(restaurant_id: str) -> Dict[str, Any]:
    """SQLite에서 맛집 정보를 ID로 조회합니다."""
    db = SessionLocal()
    try:
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == int(restaurant_id)).first()
        if restaurant:
            return {
                'id': restaurant.id,
                'name': restaurant.name,
                'category': restaurant.category,
                'address': restaurant.address,
                'keywords': restaurant.keywords
            }
        return {}
    finally:
        db.close()

def check_restaurant_exists(restaurant_id: str) -> bool:
    """SQLite에 해당 맛집 정보가 이미 있는지 확인합니다."""
    db = SessionLocal()
    try:
        restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == int(restaurant_id)).first()
        return restaurant is not None
    finally:
        db.close()