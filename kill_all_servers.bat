@echo off
echo 모든 개발 서버를 종료

echo Python 프로세스 종료
taskkill /IM python.exe /F 2>nul
taskkill /IM pythonw.exe /F 2>nul

echo Node.js 프로세스 종료
taskkill /IM node.exe /F 2>nul
taskkill /IM npm.cmd /F 2>nul

echo 특정 포트 프로세스 종료
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8083') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /PID %%a /F 2>nul

echo 모든 프로세스가 종료되었습니다.
pause