from sqlalchemy.orm import Session
from . import models_embedding

def save_embedding(db: Session, text: str, vector):
    emb = models_embedding.Embedding(input_text=text, vector=vector)
    db.add(emb)
    db.commit()
    db.refresh(emb)
    return emb
