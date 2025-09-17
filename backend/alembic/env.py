import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine # create_engine 추가
from sqlalchemy import pool

from alembic import context

# --- 프로젝트 경로 설정 ---
# backend/alembic/env.py가 backend/app 폴더를 참조할 수 있도록 경로를 추가합니다.
sys.path.append(os.path.join(sys.path[0], '..'))

# --- 프로젝트 모듈 임포트 ---
from app.models import Base # models.py에서 Base 객체를 가져옵니다.

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- 모델 메타데이터 설정 ---
# Alembic이 자동 생성(autogenerate) 기능을 사용할 때 참조할 모델의 메타데이터를 설정합니다.
target_metadata = Base.metadata

# --- 데이터베이스 URL ---
# alembic.ini 대신 여기에 직접 URL을 명시하여 인코딩 문제를 회피합니다.
DATABASE_URL = "postgresql+pg8000://postgres:password@localhost:5432/fastapi_db"


def run_migrations_offline() -> None:
    """'오프라인' 모드로 마이그레이션을 실행합니다."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """'온라인' 모드로 마이그레이션을 실행합니다."""
    # alembic.ini의 설정을 사용하는 대신, 직접 생성한 엔진을 사용합니다.
    connectable = create_engine(DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
