import re
from konlpy.tag import Okt
from sentence_transformers import SentenceTransformer
from typing import List

# 모델 로딩
# 한국어 처리에 특화된 사전 학습된 백터 변환 모델 로드
# 이 코드가 처음 실행될 때 모델을 다운로드하며, 몇 분 정도 소요될 수 있음

try:
    vector_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
except Exception as e:
    print(f"모델 로딩 중 오류 발생: {e}")
    print("인터넷 연결을 확인하거나 'pip install sentence-transformers'를 실행해주세요.")
    vector_model = None
    
# 형태소 분석을 위해 Okt 객체 생성
okt = Okt()

# 데이터 전처리 (텍스트 정제 및 토큰화) 모델
def preprocess_text(text: str) -> str:
    """입력된 텍스트를 분석에 용이하도록 정제
    1. 한글, 공백을 제외한 모든 특수문자, 이모티콘 등 제거
    2. 형태소 분석을 통해 의미있는 품사(명사, 형용사, 동사)만 추출
    3. 불필요한 단어(불용어)와 한 글자 단어 제거
    """
    
    # 1. 정규 표현식을 사용하여 한글, 공백, 외 문자 제거
    text = re.sub(r"[^ㄱ-ㅎㅏ-ㅣ가-힣\s]", "", text)
    
    # 2. 형태소 분석 및 품사 태깅(단어의 원형 복원 포함)
    tokens = okt.pos(text, stem=True)
    
    # 3. 불용어 리스트 정의 (필요에 따라 계속 추가 가능)
    stopwords = ['하다', '있다', '되다', '그', '않다', '없다', '나', '말', '사람', '이', '보다', '등', '같다', '것']

    # 4. 의미있는 품사이면서 불용어가 아니고, 두 글자 이상 단어만 필터링
    meaningful_tokens = [
        word for word, pos in tokens 
        if pos in ['Noun', 'Adjective', 'Verb'] and word not in stopwords and len(word) > 1
    ]
    
    # 정제된 토큰들을 공백으로 구분된 하나의 문자열로 합쳐서 반환
    return " ".join(meaningful_tokens)

# 백터 변환 모델
def text_to_vector(text: str) -> List[float]:
    """입력된 텍스트를 벡터로 변환"""
    if not vector_model:
        raise ValueError("벡터 변환 모델이 로드되지 않았습니다.")
    
    # 1. 텍스트 전처리 (노이즈 제거)
    preprocessed_text = preprocess_text(text)
    
    # 2. 전처리된 텍스트를 벡터로 변환
    vector = vector_model.encode(preprocessed_text)
    
    # 3. DB에 저장하기 쉽도록 numpy 배열을 리스트로 변환하여 반환
    return vector.tolist()