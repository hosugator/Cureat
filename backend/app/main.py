# app/main.py

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
import json
import numpy as np
import os
from PIL import Image
import io

from . import models, schemas, database, llm_service

# FastAPI 앱 초기화
app = FastAPI(
    title="맛집 추천 API",
    description="PostgreSQL + pgvector + FastAPI + LLM 기반의 맛집 추천 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 앱 시작 시 DB 테이블 생성 및 pgvector 확장 활성화
@app.on_event("startup")
async def startup_event():
    database.create_all_tables()
    database.enable_pgvector_extension()
    print("✅ Database tables created and pgvector extension enabled.")

# DB 세션 의존성
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

### ----------------------------------------------------
###                   User Endpoints
### ----------------------------------------------------
@app.post("/users/", response_model=schemas.User, summary="새 사용자 생성")
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[schemas.User], summary="모든 사용자 조회")
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()

@app.get("/users/{user_id}", response_model=schemas.User, summary="특정 사용자 조회")
async def read_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

### ----------------------------------------------------
###                 Restaurant Endpoints
### ----------------------------------------------------
@app.post("/restaurants/", response_model=schemas.Restaurant, summary="새 맛집 생성 및 설명 임베딩")
async def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    text_emb = None
    if restaurant.description:
        text_emb = llm_service.get_text_embedding(restaurant.description)

    db_restaurant = models.Restaurant(
        **restaurant.dict(),
        text_embedding=text_emb.tolist() if text_emb is not None and text_emb.size > 0 else None,
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

@app.get("/restaurants/", response_model=List[schemas.Restaurant], summary="모든 맛집 조회")
async def read_restaurants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Restaurant).offset(skip).limit(limit).all()

@app.get("/restaurants/{restaurant_id}", response_model=schemas.Restaurant, summary="특정 맛집 조회")
async def read_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.post("/restaurants/{restaurant_id}/upload_image", summary="맛집 이미지 업로드 및 임베딩 저장")
async def upload_restaurant_image(
    restaurant_id: str,
    file: UploadFile = File(..., description="업로드할 이미지 파일"),
    db: Session = Depends(get_db),
):
    restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    image_data = await file.read()
    image_emb = llm_service.get_image_embedding(Image.open(io.BytesIO(image_data)))

    if image_emb.size == 0:
        raise HTTPException(status_code=500, detail="Failed to generate image embedding")

    restaurant.image_embedding = image_emb.tolist()
    db.commit()
    return {"message": "✅ Image embedding saved successfully"}

### ----------------------------------------------------
###                   Review Endpoints
### ----------------------------------------------------
def create_review_summary_task(review_id: str, review_content: str, db_session: Session):
    try:
        summary_data = llm_service.summarize_review_with_llm(review_content)
        db_summary = models.ReviewSummary(
            id=str(uuid.uuid4()),
            review_id=review_id,
            keywords=summary_data.get("keywords"),
            positive_summary=summary_data.get("positive_summary"),
            negative_summary=summary_data.get("negative_summary"),
            full_summary=summary_data.get("full_summary"),
            sentiment=summary_data.get("sentiment"),
        )
        db_session.add(db_summary)
        db_session.commit()
    except Exception as e:
        print(f"❌ Background task failed: {e}")
        db_session.rollback()
    finally:
        db_session.close()

@app.post("/reviews/", response_model=schemas.Review, summary="새 리뷰 작성 및 요약 요청")
async def create_review(
    review: schemas.ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    review_emb = llm_service.get_text_embedding(review.content)

    db_review = models.Review(
        **review.dict(),
        review_embedding=review_emb.tolist() if review_emb.size > 0 else None,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    background_db_session = database.SessionLocal()
    background_tasks.add_task(
        create_review_summary_task,
        review_id=db_review.id,
        review_content=db_review.content,
        db_session=background_db_session,
    )
    return db_review

@app.get("/reviews/", response_model=List[schemas.Review], summary="모든 리뷰 조회")
async def read_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Review).offset(skip).limit(limit).all()

@app.get("/reviews/{review_id}/summary", response_model=schemas.ReviewSummary, summary="리뷰 요약 조회")
async def get_review_summary(review_id: str, db: Session = Depends(get_db)):
    summary = db.query(models.ReviewSummary).filter(models.ReviewSummary.review_id == review_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Review summary not found")
    return summary

### ----------------------------------------------------
###               Recommendation Endpoints
### ----------------------------------------------------
@app.get("/recommendations/{user_id}", response_model=List[schemas.RecommendedRestaurant], summary="사용자 맞춤 맛집 추천")
async def get_recommendations_for_user(user_id: str, top_n: int = 5, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.preference:
        raise HTTPException(status_code=400, detail="User preference not set")

    # 1️⃣ 카테고리 기반 후보 필터
    preferred_categories = [p.strip() for p in user.preference.split(",") if p.strip()]
    candidate_restaurants = db.query(models.Restaurant).filter(
        models.Restaurant.category.in_(preferred_categories)
    ).all()

    if not candidate_restaurants:
        candidate_restaurants = db.query(models.Restaurant).all()
        if not candidate_restaurants:
            return []

    # 2️⃣ 유저 리뷰 임베딩 평균
    user_reviews = db.query(models.Review).filter(
        models.Review.user_id == user_id,
        models.Review.review_embedding.isnot(None),
    ).all()

    if not user_reviews:
        return [
            schemas.RecommendedRestaurant(restaurant=rest, similarity_score=1.0)
            for rest in candidate_restaurants[:top_n]
        ]

    user_embedding = np.mean([np.array(r.review_embedding) for r in user_reviews], axis=0)

    # 3️⃣ 하이브리드 점수 계산
    restaurant_scores = []
    for rest in candidate_restaurants:
        score = 0.0
        if rest.text_embedding:
            score += llm_service.cosine_similarity(user_embedding, np.array(rest.text_embedding)) * 0.7
        if rest.image_embedding:
            score += llm_service.cosine_similarity(user_embedding, np.array(rest.image_embedding)) * 0.3
        if rest.category in preferred_categories:
            score += 0.05
        restaurant_scores.append((rest, score))

    restaurant_scores.sort(key=lambda x: x[1], reverse=True)

    recommendations = []
    for rest, score in restaurant_scores[:top_n]:
        recommendations.append(
            schemas.RecommendedRestaurant(restaurant=rest, similarity_score=score)
        )
        db_rec = models.Recommendation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            restaurant_id=rest.id,
            recommendation_score=int(score * 100),
            recommendation_type="hybrid",
        )
        db.add(db_rec)
    db.commit()
    return recommendations

### ----------------------------------------------------
###             API 문서 저장 Endpoints
### ----------------------------------------------------
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    return app.openapi()

@app.get("/save-openapi-docs", summary="OpenAPI 명세서 JSON 파일로 저장")
async def save_openapi_docs(
    filename: str = "openapi_spec.json",
    output_dir: str = "./docs_output",
):
    openapi_data = app.openapi()
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(openapi_data, f, indent=2, ensure_ascii=False)
        return JSONResponse(content={"message": f"✅ Saved to {file_path}"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save docs: {e}")
