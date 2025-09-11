from sqlalchemy import Column, Integer, String
from .database import UserBase

class User(UserBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    preference = Column(String, nullable=True)
