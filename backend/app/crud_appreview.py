from sqlalchemy.orm import Session
from . import models_appreview, schemas

def create_appreview(db: Session, review: schemas.AppReviewCreate):
    db_review = models_appreview.AppReview(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review
