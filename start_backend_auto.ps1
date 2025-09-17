# 현재 IP 자동 감지하여 백엔드 서버 실행
$currentIP = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi").IPAddress | Where-Object { $_ -like "192.168.*" -or $_ -like "10.*" -or $_ -like "172.*" }

if (-not $currentIP) {
    $currentIP = "127.0.0.1"
    Write-Host "외부 IP를 찾을 수 없어 localhost를 사용합니다." -ForegroundColor Yellow
} else {
    Write-Host "현재 IP 주소: $currentIP" -ForegroundColor Green
}

# 환경 변수 설정
$env:ANONYMIZED_TELEMETRY="False"
$env:CHROMA_TELEMETRY_OPTOUT="True" 
$env:PASSLIB_SUPPRESS_BCRYPT_WARNINGS="True"

Write-Host "백엔드 서버를 $currentIP:8000 에서 시작합니다..." -ForegroundColor Cyan

# 기존 프로세스 종료
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force

# 백엔드 서버 실행
python -m uvicorn backend.app.main:app --host $currentIP --port 8000 --reload