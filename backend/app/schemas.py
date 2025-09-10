from typing import Optional
from pydantic import BaseModel, Field, conint

# -------------------------------
# User
# -------------------------------
class UserBase(BaseModel):
    name: str = Field(..., example="홍길동")
    preference: Optional[str] = Field(None, example="한식, 카페")

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

# -------------------------------
# Restaurant
# -------------------------------
class RestaurantBase(BaseModel):
    name: str = Field(..., example="홍대돈까스")
    category: str = Field(..., example="한식")
    location: str = Field(..., example="서울 홍대")
    description: Optional[str] = Field(None, example="돈까스 전문 맛집")

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    class Config:
        orm_mode = True

# -------------------------------
# Review
# -------------------------------
class ReviewBase(BaseModel):
    content: str = Field(..., example="정말 맛있었어요!")
    rating: conint(ge=1, le=5) = Field(..., example=5)
    user_id: int = Field(..., example=1)
    restaurant_id: int = Field(..., example=1)

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    class Config:
        orm_mode = True
