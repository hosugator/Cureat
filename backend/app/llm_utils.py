import os
import numpy as np
from openai import OpenAI
from PIL import Image

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> np.ndarray:
    """
    OpenAI 임베딩 생성
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding)

def get_image_embedding(image: Image) -> np.ndarray:
    """
    이미지 임베딩 생성 (더미 구현)
    실제로는 CLIP 같은 모델 API를 사용해야 합니다.
    """
    # 실제 구현 시, 이미지 처리 및 임베딩 API 호출 로직이 들어갑니다.
    # 예: from clip_model import get_embedding_from_image
    # return get_embedding_from_image(image)
    return np.random.rand(512)

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    코사인 유사도 계산
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))