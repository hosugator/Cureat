from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import chromadb

from .config import settings # 새로 만든 settings 객체를 임포트

# PostgreSQL 연결 URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    # PostgreSQL 데이터베이스 세션을 반환하는 의존성 함수
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Vector DB 설정 (ChromaDB)
vector_db_client = chromadb.PersistentClient(path="./chroma_db_storage")
# restaurants 컬렉션 가져오기 (없으면 생성)
restaurant_collection = vector_db_client.get_or_create_collection(name="restaurants")

def get_vector_db_collection():
    # 벡터 DB의 restaurants 컬렉션을 반환
    return restaurant_collection