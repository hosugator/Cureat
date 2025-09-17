from passlib.context import CryptContext

# Bcrypt 알고리즘을 사용하는 암호 컨텍스트 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """평문 비밀번호와 해시된 비밀번호를 비교하여 일치 여부를 반환합니다."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """평문 비밀번호를 해시하여 반환합니다."""
    return pwd_context.hash(password)
