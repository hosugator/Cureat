import re
from konlpy.tag import Okt
from sentence_transformers import SentenceTransformer
from typing import List

# 한국어 처리에 특화된 사전 학습된 벡터 변환 모델 로드
try:
    vector_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
except Exception as e:
    print(f"모델 로딩 중 오류 발생: {e}")
    print("인터넷 연결을 확인하거나 'pip install sentence-transformers'를 실행해주세요.")
    vector_model = None
    
# 형태소 분석을 위해 Okt 객체 생성
okt = Okt()

# 데이터 전처리 함수 (텍스트 정제 및 토큰화)
def preprocess_text(text: str) -> str:
    # 1. 한글, 공백을 제외한 모든 문자 제거
    text = re.sub(r"[^ㄱ-ㅎㅏ-ㅣ가-힣\s]", "", text)
    
    # 2. 형태소 분석 및 품사 태깅
    tokens = okt.pos(text, stem=True)
    
    # 3. 불용어 리스트 정의 (필요에 따라 계속 추가 가능)
    stopwords = ['하다', '있다', '되다', '그', '않다', '없다', '나', '말', '사람', '이', '보다', '등', '같다']
    
    # 4. 명사, 형용사, 동사만 추출하고 불용어 제거
    filtered_tokens = [
        word for word, pos in tokens 
        if pos in ['Noun', 'Adjective', 'Verb'] and word not in stopwords and len(word) > 1
    ]
    
    return " ".join(filtered_tokens)

# 텍스트를 벡터로 변환하는 함수
def get_text_vector(text: str) -> List[float]:
    if vector_model:
        preprocessed_text = preprocess_text(text)
        embeddings = vector_model.encode(preprocessed_text, convert_to_tensor=False)
        return embeddings.tolist()
    else:
        return []

# 벡터 유사도 계산 함수
def calculate_similarity(vector1: List[float], vector2: List[float]) -> float:
    # 벡터 유사도 계산 로직
    # ...
    return 0.0
