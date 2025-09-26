#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
가격대 정보 업데이트 스크립트
"""

from app.database import SessionLocal
from app.models import Restaurant

# 가격대 업데이트 정보 (네이버 검색 결과 기반)
PRICE_UPDATES = {
    "춘천옥": "36,000원 (보쌈 소), 55,000원 (보쌈 대), 10,000원 (막국수)",
    "여기가전집": "25,000-35,000원",
    "최우영스시": "30,000-50,000원",
    "신림춘천집 구로디지털직영점": "15,000-20,000원",
    "형제특수부위": "20,000-30,000원",
    "전주식당": "8,000-15,000원", 
    "옛날마차": "15,000-25,000원",
    "북촌삼대갈비 가산본점": "25,000-35,000원",
    "라마노피자": "18,000-28,000원",
    "거북솥삼겹살 체인본점": "20,000-30,000원",
    "문정곱창": "25,000-35,000원",
    "속초붉은대게": "30,000-50,000원",
    "서일순대국 구로점": "8,000-12,000원", 
    "사계진미숯불닭갈비 구로디지털점": "15,000-25,000원",
    "복성루샤부샤부성": "20,000-30,000원",
    "뚜레쥬르 구로디지털직영점": "5,000-15,000원",
    "월악통큰칼국수": "8,000-12,000원",
    "미소장어": "35,000-50,000원",
    "스튜디오레이크": "20,000-35,000원",
    "기사님분식": "6,000-12,000원",
    "은행골 본점신관": "25,000-40,000원",
    "가산동닭한마리 가산점": "20,000-30,000원",
    "호세가": "25,000-35,000원",
    "도을생고기집": "25,000-35,000원",
    "니하우": "15,000-25,000원",
    "미식가양꼬치": "20,000-30,000원",
    "한옥집김치찜 구로점": "15,000-25,000원",
    "명가교동짬뽕 가산디지털점": "8,000-15,000원"
}

def update_price_ranges():
    """레스토랑 가격대 정보 업데이트"""
    session = SessionLocal()
    
    try:
        updated_count = 0
        
        for restaurant_name, price_range in PRICE_UPDATES.items():
            restaurant = session.query(Restaurant).filter(
                Restaurant.name == restaurant_name
            ).first()
            
            if restaurant:
                restaurant.price_range = price_range
                print(f"✅ {restaurant_name}: {price_range}")
                updated_count += 1
            else:
                print(f"❌ '{restaurant_name}' 레스토랑을 찾을 수 없습니다.")
        
        session.commit()
        print(f"\n🎉 총 {updated_count}개 레스토랑의 가격대가 업데이트되었습니다!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 오류 발생: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("💰 가격대 정보 업데이트 시작...")
    update_price_ranges()
    print("✅ 작업 완료!")