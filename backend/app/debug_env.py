import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 네이버 API 키 확인
naver_id = os.getenv("NAVER_CLIENT_ID")
naver_secret = os.getenv("NAVER_CLIENT_SECRET")

print("=== 환경변수 디버깅 ===")
print(f"NAVER_CLIENT_ID: {'설정됨' if naver_id else '설정안됨'}")
print(f"NAVER_CLIENT_SECRET: {'설정됨' if naver_secret else '설정안됨'}")

if naver_id:
    print(f"CLIENT_ID 길이: {len(naver_id)}자")
    print(f"CLIENT_ID 첫 5자: {naver_id[:5]}...")
    
if naver_secret:
    print(f"CLIENT_SECRET 길이: {len(naver_secret)}자")
    print(f"CLIENT_SECRET 첫 5자: {naver_secret[:5]}...")

print("\n=== .env 파일 위치 확인 ===")
import pathlib
env_path = pathlib.Path(".env")
if env_path.exists():
    print(f".env 파일 찾음: {env_path.absolute()}")
else:
    print(".env 파일을 찾을 수 없습니다.")
