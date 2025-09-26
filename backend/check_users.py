#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스에 있는 사용자 정보 조회 스크립트
"""

from app.database import SessionLocal
from app.models import User

def get_all_users():
    """데이터베이스의 모든 사용자 정보 조회"""
    session = SessionLocal()
    
    try:
        # 모든 사용자 조회
        users = session.query(User).all()
        
        print(f'👥 총 사용자 수: {len(users)}명')
        
        if not users:
            print('📭 등록된 사용자가 없습니다.')
            return
        
        print('\n📋 사용자 목록:')
        print('-' * 80)
        
        for i, user in enumerate(users, 1):
            print(f'{i}. 사용자 정보:')
            print(f'   ID: {user.id}')
            print(f'   이름: {user.name}')
            print(f'   이메일: {user.email}')
            print(f'   생년월일: {user.birthdate}')
            print(f'   성별: {user.gender}')
            print(f'   전화번호: {user.phone}')
            print(f'   주소: {user.address}')
            print(f'   관심사: {user.interests or "없음"}')
            print(f'   알레르기 여부: {"있음" if user.allergies else "없음"}')
            print(f'   알레르기 상세: {user.allergies_detail or "없음"}')
            print(f'   계정 활성화: {"예" if user.is_active else "아니오"}')
            print(f'   이메일 인증: {"완료" if user.is_verified else "미완료"}')
            print('-' * 80)
        
        # 통계 정보
        print('\n📊 사용자 통계:')
        active_count = sum(1 for user in users if user.is_active)
        verified_count = sum(1 for user in users if user.is_verified)
        male_count = sum(1 for user in users if user.gender == '남자')
        female_count = sum(1 for user in users if user.gender == '여자')
        
        print(f'- 활성 사용자: {active_count}명')
        print(f'- 이메일 인증 완료: {verified_count}명')
        print(f'- 남성: {male_count}명, 여성: {female_count}명')
        
        if users:
            from datetime import date
            ages = []
            for user in users:
                if user.birthdate:
                    age = date.today().year - user.birthdate.year
                    ages.append(age)
            
            if ages:
                print(f'- 평균 나이: {sum(ages)/len(ages):.1f}세')
                print(f'- 나이 범위: {min(ages)}세 ~ {max(ages)}세')
        
    except Exception as e:
        print(f'❌ 오류 발생: {e}')
    finally:
        session.close()

if __name__ == "__main__":
    get_all_users()