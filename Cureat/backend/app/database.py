import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL 연결 URL (환경 변수에서 불러옴)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:12345678@localhost:5432/fastapi_db"
)

# SQLAlchemy 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 세션 관리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 모델의 기본 클래스
Base = declarative_base()

# DB 세션 의존성 주입
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Postgres에 pgvector 확장 활성화
def enable_pgvector_extension():
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("pgvector 확장 활성화 완료")
        except Exception as e:
            print(f"pgvector 확장 활성화 오류: {e}")
            conn.rollback()

# 모든 테이블 생성
def create_all_tables():
    Base.metadata.create_all(bind=engine)
