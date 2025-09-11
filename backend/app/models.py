from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .database import Base

# 유저
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    preference = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    reviews = relationship("Review", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")

# 맛집
class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    text_embedding = Column(Vector(1536), nullable=True)
    image_embedding = Column(Vector(512), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    reviews = relationship("Review", back_populates="restaurant")

# 리뷰
class Review(Base):
    __tablename__ = "reviews"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    restaurant_id = Column(String, ForeignKey("restaurants.id"))
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    review_embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")
    summary = relationship("ReviewSummary", back_populates="review", uselist=False)

# 리뷰 요약
class ReviewSummary(Base):
    __tablename__ = "review_summaries"
    id = Column(String, primary_key=True, index=True)
    review_id = Column(String, ForeignKey("reviews.id"), unique=True)
    keywords = Column(Text, nullable=True)
    positive_summary = Column(Text, nullable=True)
    negative_summary = Column(Text, nullable=True)
    full_summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    review = relationship("Review", back_populates="summary")

# 추천 기록
class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    restaurant_id = Column(String, ForeignKey("restaurants.id"))
    recommendation_score = Column(Integer, nullable=True)
    recommendation_type = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="recommendations")
