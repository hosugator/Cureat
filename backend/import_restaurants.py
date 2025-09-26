#!/usr/bin/env python3
"""
JSON 파일에서 음식점 데이터를 읽어서 DB에 import하는 스크립트
사용법: python import_restaurants.py <json_file_path>
"""

import json
import sys
import os
from typing import List, Dict, Any
import logging

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import crud
from app.database import SessionLocal, engine
from app.models import Base

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_restaurant_data(restaurant: Dict[str, Any]) -> bool:
    """
    음식점 데이터가 유효한지 검증
    """
    required_fields = ['name', 'address']
    
    for field in required_fields:
        if not restaurant.get(field):
            logger.warning(f"필수 필드 '{field}' 누락: {restaurant}")
            return False
    
    return True

def normalize_restaurant_data(restaurant: Dict[str, Any]) -> Dict[str, Any]:
    """
    JSON 데이터를 DB 스키마에 맞게 정규화
    """
    normalized = {
        'name': restaurant.get('name', '').strip(),
        'address': restaurant.get('address', '').strip(),
        'phone': restaurant.get('phone', '').strip(),
        'operating_hours': restaurant.get('operating_hours', '').strip(),
        'signature_dishes': restaurant.get('signature_dishes', []),
        'price_range': restaurant.get('price_range', '').strip(),
        'pros': restaurant.get('pros', []),
        'cons': restaurant.get('cons', []),
        'keywords': restaurant.get('keywords', []),
        'category': restaurant.get('category', '').strip(),
        'atmosphere': restaurant.get('atmosphere', '').strip()
    }
    
    # 리스트 타입 데이터 검증
    for list_field in ['signature_dishes', 'pros', 'cons', 'keywords']:
        if not isinstance(normalized[list_field], list):
            normalized[list_field] = []
    
    return normalized

def import_restaurants_from_json(json_file_path: str) -> Dict[str, int]:
    """
    JSON 파일에서 음식점 데이터를 읽어서 DB에 import
    
    Args:
        json_file_path (str): JSON 파일 경로
        
    Returns:
        Dict[str, int]: 처리 결과 통계
    """
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {json_file_path}")
    
    logger.info(f"JSON 파일 읽기 시작: {json_file_path}")
    
    # JSON 파일 읽기
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파일 형식 오류: {e}")
    except Exception as e:
        raise Exception(f"파일 읽기 오류: {e}")
    
    # 데이터 형식 확인
    if isinstance(data, dict) and 'restaurants' in data:
        restaurants = data['restaurants']
    elif isinstance(data, list):
        restaurants = data
    else:
        raise ValueError("JSON 데이터는 음식점 배열이거나 {'restaurants': [...]} 형식이어야 합니다")
    
    logger.info(f"총 {len(restaurants)}개의 음식점 데이터 발견")
    
    # DB 세션 생성
    db = SessionLocal()
    
    stats = {
        'total': len(restaurants),
        'created': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    try:
        for i, restaurant in enumerate(restaurants, 1):
            try:
                logger.info(f"처리 중 ({i}/{len(restaurants)}): {restaurant.get('name', 'Unknown')}")
                
                # 데이터 검증
                if not validate_restaurant_data(restaurant):
                    stats['skipped'] += 1
                    continue
                
                # 데이터 정규화
                normalized_data = normalize_restaurant_data(restaurant)
                
                # DB에 저장 또는 업데이트
                existing_restaurant = db.query(crud.models.Restaurant).filter(
                    crud.models.Restaurant.name == normalized_data['name'],
                    crud.models.Restaurant.address == normalized_data['address']
                ).first()
                
                if existing_restaurant:
                    # 기존 데이터 업데이트
                    crud.create_or_update_restaurant_with_analysis(db, normalized_data)
                    stats['updated'] += 1
                    logger.info(f"✅ 업데이트: {normalized_data['name']}")
                else:
                    # 새 데이터 생성
                    crud.create_or_update_restaurant_with_analysis(db, normalized_data)
                    stats['created'] += 1
                    logger.info(f"🆕 생성: {normalized_data['name']}")
                    
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"❌ 오류 ({restaurant.get('name', 'Unknown')}): {e}")
                continue
        
        logger.info("=" * 50)
        logger.info("🎉 Import 완료!")
        logger.info(f"📊 결과 통계:")
        logger.info(f"   - 총 데이터: {stats['total']}개")
        logger.info(f"   - 새로 생성: {stats['created']}개")
        logger.info(f"   - 업데이트: {stats['updated']}개")
        logger.info(f"   - 건너뜀: {stats['skipped']}개")
        logger.info(f"   - 오류: {stats['errors']}개")
        logger.info("=" * 50)
        
        return stats
        
    finally:
        db.close()

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python import_restaurants.py <json_file_path>")
        print("예시: python import_restaurants.py restaurants_data.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    try:
        # DB 테이블 생성 (없는 경우)
        Base.metadata.create_all(bind=engine)
        
        # JSON 데이터 import
        stats = import_restaurants_from_json(json_file_path)
        
        print("\n✅ Import 성공!")
        print(f"새로 생성: {stats['created']}개, 업데이트: {stats['updated']}개")
        
    except Exception as e:
        logger.error(f"❌ Import 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()