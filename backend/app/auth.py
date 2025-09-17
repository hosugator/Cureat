import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import crud, schemas, models
from .database import get_db
from .security import verify_password

# --- 설정 ---
# 환경변수에서 비밀 키를 가져옵니다. 없는 경우 기본값을 사용합니다.
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_in_env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 토큰 만료 시간 (분)

# OAuth2PasswordBearer는 "/token" 엔드포인트에서 토큰을 가져옵니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- 인증 함수 ---
def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """사용자 이메일과 비밀번호를 확인하여 인증합니다."""
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """주어진 데이터로 액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 의존성 ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    토큰을 검증하고 현재 사용자를 반환하는 의존성 함수입니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    현재 사용자가 활성 상태인지 확인하는 의존성 함수입니다.
    (현재는 is_active 필드가 없으므로, 사용자 객체를 그대로 반환합니다.)
    """
    # 추후 is_active 필드를 확인하는 로직 추가 가능
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
