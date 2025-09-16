from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import date

# User 스키마
class UserBase(BaseModel):
    name: str
    birthdate: date
    gender: str
    email: EmailStr
    phone: str
    address: str
    interests: Optional[str] = None
    allergies: bool = False
    allergies_detail: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    
    class Config:
        orm_mode = True

# Restaurant 스키마
class RestaurantBase(BaseModel):
    name: str
    category: str
    address: str
    phone: Optional[str] = None
    summary_menu: Optional[str] = None
    summary_price: Optional[str] = None
    summary_opening_hours: Optional[str] = None
    image_url: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    pass

class Restaurant(RestaurantBase):
    id: int
    vector: Optional[List[float]] = None
    
    class Config:
        orm_mode = True

# Review 스키마
class ReviewBase(BaseModel):
    content: str
    rating: int
    is_ad: bool = False

class ReviewCreate(ReviewBase):
    user_id: int
    restaurant_id: int

class Review(ReviewBase):
    id: int
    user_id: int
    restaurant_id: int
    created_at: date
    
    class Config:
        orm_mode = True

# SearchLog 스키마
class SearchLogBase(BaseModel):
    search_query: str
    search_type: str

class SearchLogCreate(SearchLogBase):
    user_id: int

class SearchLog(SearchLogBase):
    id: int
    user_id: int
    created_at: date
    
    class Config:
        orm_mode = True
