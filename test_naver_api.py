#!/usr/bin/env python
"""
네이버 검색 API 직접 테스트
"""
import requests
import json
import sys
import os
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_naver_api():
    print("=== 네이버 검색 API 직접 테스트 ===")
    
    # .env에서 직접 읽기
    from backend.app.config import settings
    
    client_id = settings.NAVER_CLIENT_ID
    client_secret = settings.NAVER_CLIENT_SECRET
    
    print(f"Client ID: {client_id[:10]}...")
    print(f"Client Secret: {client_secret[:5]}...")
    
    # 네이버 지역 검색 API 테스트
    url = "https://openapi.naver.com/v1/search/local.json"
    params = {
        "query": "강남역 맛집",
        "display": 5,
        "start": 1,
        "sort": "random"
    }
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"\nAPI 요청:")
    print(f"URL: {url}")
    print(f"Params: {params}")
    print(f"Headers: X-Naver-Client-Id: {client_id[:10]}...")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"\n응답 상태코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 호출 성공!")
            print(f"총 결과 수: {data.get('total', 0)}")
            print(f"반환된 결과 수: {len(data.get('items', []))}")
            
            for i, item in enumerate(data.get('items', [])[:3]):
                print(f"\n{i+1}. {item.get('title', '')}")
                print(f"   주소: {item.get('address', '')}")
                print(f"   카테고리: {item.get('category', '')}")
                
        else:
            print("❌ API 호출 실패!")
            print(f"응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_naver_api()