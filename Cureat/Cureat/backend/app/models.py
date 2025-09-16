from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean, DateTime
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func 
from .database import Base 
from pgvector.sqlalchemy import Vector # pgvector 임포트
from sqlalchemy import Index # 인덱스 추가를 위한 임포트

class User(Base): 
    __tablename__ = "users" 
    
    user_id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, nullable=False) 
    birthdate = Column(Date, nullable=False) 
    gender = Column(String, nullable=False) 
    email = Column(String, unique=True, index=True, nullable=False) 
    phone = Column(String, nullable=False, unique=True) 
    address = Column(String, nullable=False) 
    hashed_password = Column(String, nullable=False) 
    interests = Column(String, nullable=True) 
    allergies = Column(Boolean, default=True) 
    allergies_detail = Column(String, nullable=True) 
    is_active = Column(Boolean, default=True) 
    is_verified = Column(Boolean, default=False) 
    search_logs = relationship("SearchLog", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    
class Restaurant(Base): 
    __tablename__ = "restaurants" 
    
    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, index=True, nullable=False)
    summary_place = Column(String, nullable=True) 
    summary_address = Column(String, nullable=True)
    summary_category = Column(String, nullable=True)
    summary_description = Column(String, nullable=True)
    summary_feature_menu = Column(String, nullable=True) 
    summary_phone = Column(String, nullable=True) 
    summary_parking = Column(String, nullable=True) 
    summary_price = Column(String, nullable=True) 
    summary_opening_hours = Column(String, nullable=True) 
    image_url = Column(String, nullable=True) 
    
    vector = Column(Vector(1536), nullable=True) # 벡터 임베딩 (1536차원)
    
    reviews = relationship("Review", back_populates="restaurant") 

class Review(Base): 
    __tablename__ = "reviews" 
    
    id = Column(Integer, primary_key=True, index=True) 
    user_id = Column(Integer, ForeignKey("users.user_id")) 
    restaurant_id = Column(Integer, ForeignKey("restaurants.id")) 
    content = Column(Text, nullable=False) 
    rating = Column(Integer, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
    is_ad = Column(Boolean, default=False) 
    user = relationship("User", back_populates="reviews") 
    restaurant = relationship("Restaurant", back_populates="reviews") 
    
class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    query = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="search_logs")

# pgvector HNSW 인덱스 추가 (음식점 벡터 검색 속도 향상)
Index('idx_restaurant_vector', Restaurant.vector, postgresql_using='hnsw', postgresql_with={'m': 16, 'ef_construction': 64})