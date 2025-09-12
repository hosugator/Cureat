from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# PostgreSQL 연결 URL (환경 변수에서 불러옴)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:12345678@localhost:5432/fastapi_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def enable_pgvector_extension():
    """Postgres에 pgvector 확장 활성화"""
    with engine.connect() as conn:
        try:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
        except Exception as e:
            print(f"pgvector 확장 활성화 오류: {e}")
            conn.rollback()

def create_all_tables():
    Base.metadata.create_all(bind=engine)