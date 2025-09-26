import re
from typing import List

# 선택적 import - 라이브러리가 없어도 서버가 실행되도록 처리
try:
    from konlpy.tag import Okt
    okt = Okt()
    KONLPY_AVAILABLE = True
except ImportError:
    print("⚠️ KoNLPy가 설치되지 않았습니다. 형태소 분석 기능이 제한됩니다.")
    okt = None
    KONLPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    print("⚠️ sentence-transformers가 설치되지 않았습니다. 벡터 변환 기능이 제한됩니다.")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# 모델 로딩
# 한국어 처리에 특화된 사전 학습된 백터 변환 모델 로드
vector_model = None
if SENTENCE_TRANSFORMERS_AVAILABLE:
    try:
        vector_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        print("✅ SentenceTransformer 모델 로딩 성공")
    except Exception as e:
        print(f"⚠️ 모델 로딩 중 오류 발생: {e}")
        print("인터넷 연결을 확인하거나 'pip install sentence-transformers'를 실행해주세요.")
        vector_model = None

# 데이터 전처리 (텍스트 정제 및 토큰화) 모델
def preprocess_text(text: str) -> str:
    """입력된 텍스트를 분석에 용이하도록 정제
    1. 한글, 공백을 제외한 모든 특수문자, 이모티콘 등 제거
    2. 형태소 분석을 통해 의미있는 품사(명사, 형용사, 동사)만 추출
    3. 불필요한 단어(불용어)와 한 글자 단어 제거
    """
    
    # 1. 정규 표현식을 사용하여 한글, 공백, 외 문자 제거
    text = re.sub(r"[^ㄱ-ㅎㅏ-ㅣ가-힣\s]", "", text)
    
    # KoNLPy가 없는 경우 기본 처리
    if not KONLPY_AVAILABLE or not okt:
        # 간단한 공백 분할과 기본 필터링
        words = text.split()
        stopwords = ['하다', '있다', '되다', '그', '않다', '없다', '나', '말', '사람', '이', '보다', '등', '같다', '것']
        return " ".join([word for word in words if word not in stopwords and len(word) > 1])
    
    # 2. 형태소 분석 및 품사 태깅(단어의 원형 복원 포함)
    try:
        tokens = okt.pos(text, stem=True)
    except Exception as e:
        print(f"⚠️ 형태소 분석 중 오류: {e}")
        return text
    
    # 3. 불용어 리스트 정의 (필요에 따라 계속 추가 가능)
    stopwords = ['하다', '있다', '되다', '그', '않다', '없다', '나', '말', '사람', '이', '보다', '등', '같다', '것']

    # 4. 의미있는 품사이면서 불용어가 아니고, 두 글자 이상 단어만 필터링
    meaningful_tokens = [
        word for word, pos in tokens 
        if pos in ['Noun', 'Adjective', 'Verb'] and word not in stopwords and len(word) > 1
    ]
    
    # 정제된 토큰들을 공백으로 구분된 하나의 문자열로 합쳐서 반환
    return " ".join(meaningful_tokens)

# 키워드 추출 (벡터 대신 사용)
def text_to_keywords(text: str) -> List[str]:
    """입력된 텍스트에서 키워드를 추출합니다"""
    # 간단한 키워드 추출 (실제로는 더 복잡한 NLP 처리 가능)
    preprocessed_text = preprocess_text(text)
    
    # 기본적인 키워드들
    food_keywords = ['한식', '중식', '일식', '양식', '카페', '치킨', '피자', '파스타', '스테이크', '초밥', '라멘']
    location_keywords = ['강남', '신촌', '홍대', '명동', '이태원', '압구정', '청담', '삼성동']
    mood_keywords = ['데이트', '회식', '친구', '가족', '혼밥', '조용한', '시끌벅적한']
    
    extracted_keywords = []
    text_lower = preprocessed_text.lower()
    
    for keyword in food_keywords + location_keywords + mood_keywords:
        if keyword in text_lower:
            extracted_keywords.append(keyword)
    
    return extracted_keywords