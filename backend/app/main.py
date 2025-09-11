from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database, schemas, crud_user, crud_vector, crud_appreview, crud_embedding, recommend, models_user, models_vector, models_appreview, models_embedding

# 테이블 생성
models_user.User.metadata.create_all(bind=database.user_engine)
models_vector.Restaurant.metadata.create_all(bind=database.vector_engine)
models_vector.Review.metadata.create_all(bind=database.vector_engine)
models_appreview.AppReview.metadata.create_all(bind=database.appreview_engine)
models_embedding.Embedding.metadata.create_all(bind=database.embed_engine)

app = FastAPI()

# DB 의존성
def get_user_db():
    db = database.UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_vector_db():
    db = database.VectorSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_appreview_db():
    db = database.AppReviewSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_embed_db():
    db = database.EmbedSessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------
# User API
# -----------------------
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_user_db)):
    return crud_user.create_user(db, user)

@app.get("/users/", response_model=list[schemas.User])
def list_users(db: Session = Depends(get_user_db)):
    return crud_user.get_users(db)

# -----------------------
# Restaurant & Review API
# -----------------------
@app.post("/restaurants/", response_model=schemas.Restaurant)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_vector_db)):
    return crud_vector.create_restaurant(db, restaurant)

@app.post("/reviews/", response_model=schemas.Review)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_vector_db)):
    return crud_vector.create_review(db, review)

@app.get("/recommendations/{user_id}", response_model=list[schemas.Restaurant])
def get_recommendations(user_id: int, db: Session = Depends(get_vector_db), user_db: Session = Depends(get_user_db)):
    user_reviews = db.query(models_vector.Review).filter(models_vector.Review.id == user_id).all()
    restaurants = recommend.recommend_restaurants(db, user_reviews)
    if not restaurants:
        raise HTTPException(status_code=404, detail="추천할 맛집이 없습니다")
    return restaurants

# -----------------------
# App Review API
# -----------------------
@app.post("/app_reviews/", response_model=schemas.AppReview)
def create_app_review(review: schemas.AppReviewCreate, db: Session = Depends(get_appreview_db)):
    return crud_appreview.create_appreview(db, review)

# -----------------------
# Embedding API
# -----------------------
@app.post("/embeddings/")
def save_embedding(text: str, db: Session = Depends(get_embed_db)):
    from . import llm_utils
    vec = llm_utils.get_embedding(text)
    return crud_embedding.save_embedding(db, text, vec)
