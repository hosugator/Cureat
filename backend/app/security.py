import logging
from passlib.context import CryptContext

# bcrypt 관련 로깅 경고 억제
logging.getLogger('passlib').setLevel(logging.ERROR)

# Bcrypt 알고리즘을 사용하는 암호 컨텍스트 생성
# 호환성을 위해 rounds 명시적 설정
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # 성능과 보안의 균형
)

def verify_password(plain_password, hashed_password):
    """평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부를 반환합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """평문 비밀번호를 해시하여 반환합니다."""
    return pwd_context.hash(password)
