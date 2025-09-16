#!/usr/bin/env python3
# 네이버 API 직접 테스트
import os
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

client_id = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")

# 1. 블로그 검색 API 테스트 (공식 예제와 동일)
print("\n=== 블로그 검색 API 테스트 ===")
encText = urllib.parse.quote("강남역 규카츠정")
url = "https://openapi.naver.com/v1/search/blog?query=" + encText

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

try:
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        print("블로그 검색 성공!")
        print(response_body.decode('utf-8')[:500])  # 처음 500자만 출력
    else:
        print("Error Code:", rescode)
except Exception as e:
    print("블로그 검색 오류:", e)

# 2. 지역 검색 API 테스트
print("\n=== 지역 검색 API 테스트 ===")
encText = urllib.parse.quote("강남역 규카츠정")
url = "https://openapi.naver.com/v1/search/local.json?query=" + encText

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

try:
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        print("지역 검색 성공!")
        print(response_body.decode('utf-8')[:500])  # 처음 500자만 출력
    else:
        print("Error Code:", rescode)
except Exception as e:
    print("지역 검색 오류:", e)