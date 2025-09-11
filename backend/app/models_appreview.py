from sqlalchemy import Column, Integer, Text
from .database import AppReviewBase

class AppReview(AppReviewBase):
    __tablename__ = "app_reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
