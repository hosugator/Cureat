@echo off
echo === 현재 개발 환경 IP 정보 ===
echo.

echo [네트워크 어댑터 정보]
ipconfig | findstr /C:"IPv4"

echo.
echo [8000번 포트 사용 현황]
netstat -ano | findstr :8000

echo.
echo [추천 백엔드 실행 명령어]
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr "IPv4"') do (
    for /f "tokens=1" %%j in ("%%i") do (
        if not "%%j"=="127.0.0.1" (
            echo python -m uvicorn backend.app.main:app --host %%j --port 8000 --reload
        )
    )
)

pause