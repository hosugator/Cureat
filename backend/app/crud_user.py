from sqlalchemy.orm import Session
from . import models_user, schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models_user.User(name=user.name, preference=user.preference)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip=0, limit=10):
    return db.query(models_user.User).offset(skip).limit(limit).all()
