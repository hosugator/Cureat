from pydantic import BaseModel
from typing import Optional

# User
class UserBase(BaseModel):
    name: str
    preference: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

# Restaurant
class RestaurantBase(BaseModel):
    name: str
    category: str
    location: str
    description: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    class Config:
        orm_mode = True

# Review
class ReviewBase(BaseModel):
    content: str
    rating: int
    restaurant_id: int

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    class Config:
        orm_mode = True

# AppReview
class AppReviewBase(BaseModel):
    user_id: int
    content: str
    rating: int

class AppReviewCreate(AppReviewBase):
    pass

class AppReview(AppReviewBase):
    id: int
    class Config:
        orm_mode = True
