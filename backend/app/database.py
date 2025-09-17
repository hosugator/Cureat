from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 로컬 개발용 SQLite 설정
# 데이터베이스 파일은 프로젝트 루트 디렉토리에 'cureat.db'라는 이름으로 생성됩니다.
SQLALCHEMY_DATABASE_URL = "sqlite:///./cureat.db"

engine = create_engine(
    # SQLite는 동시성 처리를 위해 check_same_thread 옵션이 필요합니다.
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()