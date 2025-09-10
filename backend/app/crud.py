from sqlalchemy.orm import Session
from . import models, schemas

# -------------------------------
# User CRUD
# -------------------------------
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, preference=user.preference)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

# -------------------------------
# Restaurant CRUD
# -------------------------------
def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate):
    db_restaurant = models.Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def get_restaurants(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Restaurant).offset(skip).limit(limit).all()

# -------------------------------
# Review CRUD
# -------------------------------
def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Review).offset(skip).limit(limit).all()
