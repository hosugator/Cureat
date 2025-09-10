from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, recommend, llm_utils
from PIL import Image
import io

models.Base.metadata.create_all(bind=database.engine)
database.enable_pgvector_extension()

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

@app.post("/restaurants/", response_model=schemas.Restaurant)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    return crud.create_restaurant(db, restaurant)

@app.post("/reviews/", response_model=schemas.Review)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    return crud.create_review(db, review)

# -----------------------------
# LLM 기반 추천 엔드포인트
# -----------------------------
@app.get("/recommendations/{user_id}", response_model=list[schemas.Restaurant])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    restaurants = recommend.recommend_restaurants(db, user_id)
    if not restaurants:
        raise HTTPException(status_code=404, detail="추천할 맛집이 없습니다")
    return restaurants

# -----------------------------
# pgvector 기반 이미지 업로드 엔드포인트
# -----------------------------
@app.post("/restaurants/{restaurant_id}/upload_image")
def upload_restaurant_image(
    restaurant_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    restaurant = crud.get_restaurant(db, restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    image_data = file.file.read()
    image = Image.open(io.BytesIO(image_data))
    
    # 이미지 임베딩 생성 및 저장
    image_emb = llm_utils.get_image_embedding(image)
    restaurant.image_embedding = image_emb
    db.commit()
    return {"message": "Image embedding saved successfully"}