import numpy as np

def get_text_embedding(text: str) -> np.ndarray:
    """
    더미 텍스트 임베딩 생성
    실제로는 OpenAI Embedding API를 호출해야 하지만,
    지금은 실행 확인용으로 난수 벡터를 반환합니다.
    """
    return np.random.rand(1536)

def get_image_embedding(image_bytes: bytes) -> np.ndarray:
    """
    더미 이미지 임베딩 생성
    실제로는 CLIP 같은 모델을 써야 하지만,
    지금은 실행 확인용으로 난수 벡터를 반환합니다.
    """
    return np.random.rand(512)

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    코사인 유사도 계산
    """
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

def summarize_review_with_llm(review_content: str) -> dict:
    """
    더미 리뷰 요약
    실제로는 LLM을 호출해야 하지만,
    지금은 고정된 요약 데이터를 반환합니다.
    """
    return {
        "keywords": "맛, 분위기",
        "positive_summary": "음식이 맛있고 분위기가 좋음",
        "negative_summary": "가격이 다소 비쌈",
        "full_summary": f"요약된 리뷰: {review_content[:20]}...",
        "sentiment": "positive"
     }

# import numpy as np
# from openai import OpenAI

# client = OpenAI()

# def get_text_embedding(text: str):
#     """텍스트 임베딩"""
#     if not text:
#         return np.array([])
#     resp = client.embeddings.create(model="text-embedding-3-small", input=text)
#     return np.array(resp.data[0].embedding)

# def get_image_embedding(image_bytes: bytes):
#     """이미지 임베딩 (모델에 따라 수정 필요)"""
#     return np.random.rand(512)  # 실제 구현 시 CLIP, BLIP 등 사용

# def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray):
#     return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# def summarize_review_with_llm(content: str):
#     """리뷰 요약"""
#     prompt = f"리뷰를 긍정 요약, 부정 요약, 키워드, 감정 분석을 해줘:\n\n{content}"
#     resp = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     text = resp.choices[0].message.content
#     return {
#         "keywords": "맛, 분위기",
#         "positive_summary": "음식이 맛있다.",
#         "negative_summary": "가격이 조금 비싸다.",
#         "full_summary": text,
#         "sentiment": "positive"
#     }
