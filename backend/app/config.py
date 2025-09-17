import os
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

# --- .env 파일 경로를 프로젝트 루트로 명확히 지정 ---
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    print(f"'.env' 파일을 다음 경로에서 로드합니다: {env_path}")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"경고: .env 파일을 찾을 수 없습니다. 경로: {env_path}")

class Settings:
    """
    애플리케이션 전체의 설정을 관리하는 클래스입니다.
    .env 파일에서 환경 변수를 읽어와 속성으로 제공합니다.
    """
    # 데이터베이스 URL은 database.py에서 직접 관리하도록 주석 처리
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+pg8000://user:password@localhost/db")

    # JWT 토큰
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # 네이버 검색 API (지역/블로그/웹 검색용)
    NAVER_CLIENT_ID: str = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET: str = os.getenv("NAVER_CLIENT_SECRET")
    
    # 카카오 API
    KAKAO_REST_KEY: str = os.getenv("KAKAO_REST_KEY")

    # Google Gemini API
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

    # 웹 스크래핑
    SCRAPINGBEE_KEY: str = os.getenv("SCRAPINGBEE_KEY")
    
    # ChromaDB 설정
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    CHROMA_COLLECTION_NAME: str = "restaurants"

# 설정 객체 인스턴스 생성
settings = Settings()
