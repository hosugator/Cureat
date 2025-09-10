from sqlalchemy.orm import Session
from . import models, llm_utils
import numpy as np

def recommend_restaurants(db: Session, user_id: int, top_n: int = 5):
    """
    유저 리뷰 기반 LLM 임베딩 추천
    """
    # 1. 유저 리뷰 가져오기
    reviews = db.query(models.Review).filter(models.Review.user_id == user_id).all()
    if not reviews:
        return []

    # 2. 유저 리뷰 임베딩 평균
    user_embedding = np.mean([llm_utils.get_embedding(r.content) for r in reviews], axis=0)

    # 3. 모든 맛집 가져오기
    restaurants = db.query(models.Restaurant).all()

    # 4. 맛집 설명 임베딩 + 유사도 계산
    restaurant_scores = []
    for r in restaurants:
        if not r.description:
            continue
        rest_emb = llm_utils.get_embedding(r.description)
        score = llm_utils.cosine_similarity(user_embedding, rest_emb)
        restaurant_scores.append((r, score))

    # 5. 유사도 기준 상위 N개
    restaurant_scores.sort(key=lambda x: x[1], reverse=True)
    top_restaurants = [r[0] for r in restaurant_scores[:top_n]]
    return top_restaurants