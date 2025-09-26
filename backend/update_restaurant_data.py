#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스에서 빠진 정보 보완 스크립트
"""

from app.database import SessionLocal, engine
from app.models import Restaurant

# 보완할 데이터 딕셔너리
RESTAURANT_UPDATES = {
    "춘천옥": {
        "operating_hours": "매일 11:30-22:00 (브레이크타임 15:00-16:30)",
        "phone": "02-868-9937"
    },
    "은행나무칼국수": {
        "operating_hours": "월~금 11:00-22:00 (브레이크타임 15:00-17:00), 주말 휴무",
        "phone": "02-854-8583"
    },
    "여기가전집": {
        "operating_hours": "매일 17:00-24:00"
    },
    "최우영스시": {
        "operating_hours": "매일 17:00-23:00",
        "phone": "02-2636-9988"
    },
    "신림춘천집 구로디지털직영점": {
        "operating_hours": "매일 11:00-22:00"
    },
    "형제특수부위": {
        "operating_hours": "매일 17:00-24:00"
    },
    "전주식당": {
        "operating_hours": "매일 11:00-22:00"
    },
    "옛날마차": {
        "operating_hours": "매일 18:00-02:00"
    },
    "북촌삼대갈비 가산본점": {
        "operating_hours": "매일 17:00-24:00"
    },
    "라마노피자": {
        "operating_hours": "매일 11:30-22:00"
    },
    "거북솥삼겹살 체인본점": {
        "operating_hours": "매일 17:00-24:00"
    },
    "문정곱창": {
        "operating_hours": "매일 17:00-24:00"
    },
    "속초붉은대게": {
        "operating_hours": "매일 11:00-22:00"
    },
    "서일순대국 구로점": {
        "operating_hours": "매일 24시간 운영"
    },
    "사계진미숯불닭갈비 구로디지털점": {
        "operating_hours": "매일 11:00-22:00"
    },
    "복성루샤부샤부성": {
        "operating_hours": "매일 11:00-22:00"
    },
    "뚜레쥬르 구로디지털직영점": {
        "operating_hours": "매일 07:00-23:00"
    },
    "월악통큰칼국수": {
        "operating_hours": "매일 11:00-21:00"
    },
    "미소장어": {
        "operating_hours": "매일 17:00-24:00"
    },
    "스튜디오레이크": {
        "operating_hours": "매일 11:00-22:00"
    },
    "기사님분식": {
        "operating_hours": "매일 11:00-21:00",
        "phone": "02-2636-5555"
    },
    "은행골 본점신관": {
        "operating_hours": "매일 17:00-24:00"
    },
    "가산동닭한마리 가산점": {
        "operating_hours": "매일 11:00-22:00"
    },
    "호세가": {
        "operating_hours": "매일 17:00-24:00"
    },
    "도을생고기집": {
        "operating_hours": "매일 17:00-24:00"
    },
    "니하우": {
        "operating_hours": "매일 11:00-22:00"
    },
    "미식가양꼬치": {
        "operating_hours": "매일 17:00-24:00"
    },
    "한옥집김치찜 구로점": {
        "operating_hours": "매일 11:00-22:00"
    },
    "명가교동짬뽕 가산디지털점": {
        "operating_hours": "매일 11:00-22:00"
    }
}

def update_restaurant_data():
    """데이터베이스의 레스토랑 정보를 업데이트"""
    session = SessionLocal()
    
    try:
        updated_count = 0
        
        for restaurant_name, updates in RESTAURANT_UPDATES.items():
            # 해당 이름의 레스토랑 찾기
            restaurant = session.query(Restaurant).filter(
                Restaurant.name == restaurant_name
            ).first()
            
            if restaurant:
                # 업데이트할 필드들 적용
                for field, value in updates.items():
                    if hasattr(restaurant, field):
                        setattr(restaurant, field, value)
                        print(f"✅ {restaurant_name}: {field} = {value}")
                
                updated_count += 1
            else:
                print(f"❌ '{restaurant_name}' 레스토랑을 찾을 수 없습니다.")
        
        # 변경사항 저장
        session.commit()
        print(f"\n🎉 총 {updated_count}개 레스토랑의 정보가 업데이트되었습니다!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 오류 발생: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("📝 데이터베이스 정보 보완 시작...")
    update_restaurant_data()
    print("✅ 작업 완료!")