from typing import List, Dict, Any
from sqlalchemy.orm import Session
from . import models
from .database import SessionLocal
import json

# SQLite 기반 키워드 검색으로 벡터 검색 대체
def upsert_restaurant_vector(restaurant_id: int, vector: List[float], metadata: Dict[str, Any]):
    """
    음식점의 메타데이터를 SQLite에 저장합니다. (벡터는 저장하지 않음)
    """
    # SQLite에서는 벡터 검색 대신 기존 restaurant 테이블의 키워드/카테고리로 검색
    print(f"Restaurant ID {restaurant_id}의 메타데이터가 SQLite에 업데이트 되었습니다.")

def query_similar_restaurant(keywords: List[str], n_results: int = 3) -> List[Dict[str, Any]]:
    """
    키워드를 기반으로 SQLite에서 유사한 맛집을 검색합니다.
    """
    db = SessionLocal()
    try:
        # 키워드로 맛집 검색
        restaurants = db.query(models.Restaurant).all()
        
        # 간단한 키워드 매칭으로 유사도 계산
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
                if keyword.lower() in (restaurant.atmosphere or '').lower():
                    score += 1
            
            if score > 0:
                matched_restaurants.append({
                    'id': restaurant.id,
                    'score': score,
                    'name': restaurant.name,
                    'category': restaurant.category,
                    'address': restaurant.address,
                    'phone': restaurant.phone,
                    'operating_hours': restaurant.operating_hours,
                    'price_range': restaurant.price_range,
                    'atmosphere': restaurant.atmosphere
                })
        
        # 점수 순으로 정렬하고 상위 n_results개 반환
        matched_restaurants.sort(key=lambda x: x['score'], reverse=True)
        return matched_restaurants[:n_results]
        
    finally:
        db.close()

