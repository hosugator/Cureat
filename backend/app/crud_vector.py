from sqlalchemy.orm import Session
from . import models_vector, schemas

def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate):
    db_restaurant = models_vector.Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def get_restaurants(db: Session, skip=0, limit=10):
    return db.query(models_vector.Restaurant).offset(skip).limit(limit).all()

def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models_vector.Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review
