# FastAPI + DB (SQLite → PostgreSQL) 스타터

완전 처음부터 **서버(API) + 데이터베이스(DB)**를 만드는 연습용 프로젝트입니다.
기본은 **SQLite(파일 DB)**로 시작하고, 나중에 **PostgreSQL**로 바꿀 수 있도록 구조를 잡았습니다.

## 0) 준비물
- Python 3.10 이상
- (권장) VS Code
- Windows라면 PowerShell, macOS/Linux라면 터미널

## 1) 프로젝트 실행 (로컬, SQLite)
```bash
# 1) 폴더로 이동
cd fastapi_db_server_starter

# 2) 가상환경 생성
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

# 3) 패키지 설치
pip install -r requirements.txt

# 4) (선택) 환경파일 생성
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
# 기본은 SQLite를 사용하므로 .env는 비워둬도 됩니다.

# 5) 샘플 데이터 넣기
python app/seed.py

# 6) 서버 실행
uvicorn app.main:app --reload
```
- 브라우저에서: http://127.0.0.1:8000/docs 에 접속 → 자동 문서에서 API 테스트 가능
- 헬스 체크: http://127.0.0.1:8000/health

## 2) 기본 API
- `GET /restaurants` 맛집 목록 조회 (쿼리로 `city`, `category`, `min_rating` 필터 가능)
- `POST /restaurants` 맛집 생성
- `GET /restaurants/{id}` 단건 조회
- `PUT /restaurants/{id}` 전체 업데이트
- `PATCH /restaurants/{id}` 부분 업데이트
- `DELETE /restaurants/{id}` 삭제

## 3) DB를 PostgreSQL로 전환 (선택)
1. PostgreSQL 설치(로컬/클라우드) 후 데이터베이스를 하나 만듭니다.
2. `.env` 파일에 아래 형식으로 `DATABASE_URL`을 설정합니다.
   ```env
   DATABASE_URL=postgresql+psycopg2://username:password@host:5432/dbname
   ```
3. 서버 실행 시 자동으로 테이블이 생성됩니다. (초기 스키마 기준)

> 운영 단계에서는 Alembic 같은 **마이그레이션** 도구를 추가하는 것을 권장합니다.

## 4) 배포 개요 (아주 간단 요약)
- **가벼운 배포**: Render, Railway, Fly.io, AWS Lightsail, DigitalOcean 등 PaaS/VPS에 올리고
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - 리버스 프록시(Nginx) 또는 플랫폼 설정으로 포트 노출
- **DB**: 클라우드 PostgreSQL(예: Supabase, Neon, RDS 등)을 사용하고 `DATABASE_URL`만 교체

## 5) 구조
```text
fastapi_db_server_starter/
├─ app/
│  ├─ main.py         # FastAPI 엔트리포인트 + 라우터
│  ├─ database.py     # DB 연결/세션 관리
│  ├─ models.py       # SQLModel 모델(테이블)
│  ├─ crud.py         # DB 조작 로직
│  ├─ seed.py         # 샘플 데이터 주입
│  └─ __init__.py
├─ requirements.txt
├─ .env.example
└─ README.md
```

## 6) 자주 하는 실수 체크리스트
- 가상환경 활성화를 깜빡하지 않았는지?
- `uvicorn app.main:app --reload`에서 모듈 경로가 올바른지?
- Windows에서 `copy`, macOS/Linux에서 `cp` 명령 혼동 주의
- `.env`의 `DATABASE_URL` 오타 주의 (특히 `postgresql+psycopg2://` 접두어)

---
질문이 생기면 `README.md`와 `/docs` 자동 문서에서부터 확인해 보세요!

## 🚀 실행 방법

PostgreSQL에 DB 만들기

CREATE DATABASE food_db;


서버 실행

uvicorn app.main:app --reload


브라우저에서 API 확인

http://127.0.0.1:8000/docs