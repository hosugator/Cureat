from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, recommend

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# DB 의존성
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# 기존 유저 / 맛집 / 리뷰 엔드포인트
# -----------------------------
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/")
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

# -----------------------------
# LLM 기반 추천 엔드포인트
# -----------------------------
@app.get("/recommendations/{user_id}", response_model=list[schemas.Restaurant])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    restaurants = recommend.recommend_restaurants(db, user_id)
    if not restaurants:
        raise HTTPException(status_code=404, detail="추천할 맛집이 없습니다")
    return restaurants
