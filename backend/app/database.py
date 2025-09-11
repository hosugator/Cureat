from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. 사용자 DB
USER_DB_URL = "postgresql://postgres:213427@localhost:5432/user_db"
user_engine = create_engine(USER_DB_URL)
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
UserBase = declarative_base()

# 2. 벡터 DB (맛집 + 맛집 리뷰)
VECTOR_DB_URL = "postgresql://postgres:213427@localhost:5432/vector_db"
vector_engine = create_engine(VECTOR_DB_URL)
VectorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)
VectorBase = declarative_base()

# 3. 앱 리뷰 DB
APPREVIEW_DB_URL = "postgresql://postgres:213427@localhost:5432/appreview_db"
appreview_engine = create_engine(APPREVIEW_DB_URL)
AppReviewSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=appreview_engine)
AppReviewBase = declarative_base()

# 4. 임베딩 DB
EMBED_DB_URL = "postgresql://postgres:213427@localhost:5432/embed_db"
embed_engine = create_engine(EMBED_DB_URL)
EmbedSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=embed_engine)
EmbedBase = declarative_base()
