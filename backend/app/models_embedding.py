from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector
from .database import EmbedBase

class Embedding(EmbedBase):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    vector = Column(Vector(1536))  # OpenAI text-embedding-3-small 차원
