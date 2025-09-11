import numpy as np
from sqlalchemy.orm import Session
from . import models_vector, llm_utils

def recommend_restaurants(db: Session, user_reviews, top_n=5):
    if not user_reviews:
        return []
    user_embedding = np.mean([llm_utils.get_embedding(r.content) for r in user_reviews], axis=0)
    restaurants = db.query(models_vector.Restaurant).all()
    scores = []
    for r in restaurants:
        if not r.description:
            continue
        rest_emb = llm_utils.get_embedding(r.description)
        score = llm_utils.cosine_similarity(user_embedding, rest_emb)
        scores.append((r, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in scores[:top_n]]
