# IP 변경 감지 및 전체 개발 환경 자동 설정
param(
    [switch]$UpdateFrontend
)

Write-Host "=== 동적 IP 개발 환경 설정 ===" -ForegroundColor Magenta

# 1. 현재 IP 감지 (개선된 방식)
$currentIP = $null
try {
    # 활성 상태인 모든 네트워크 연결에서 사설 IP 주소를 찾습니다.
    $ipAddresses = Get-NetIPAddress -AddressFamily IPv4 -AddressState Preferred | ForEach-Object { $_.IPAddress }
    $currentIP = $ipAddresses | Where-Object { $_ -like "192.168.*" -or $_ -like "10.*" -or ($ipAddress -like "172.16.*" -or $ipAddress -like "172.17.*" -or $ipAddress -like "172.18.*" -or $ipAddress -like "172.19.*" -or $ipAddress -like "172.2*.*" -or $ipAddress -like "172.30.*" -or $ipAddress -like "172.31.*") } | Select-Object -First 1

    if ($currentIP) {
        Write-Host "활성 네트워크에서 IP 발견: $currentIP" -ForegroundColor Green
    }
} catch {
    Write-Host "IP 주소 자동 감지 중 오류 발생: $($_.Exception.Message)" -ForegroundColor Red
}

if (-not $currentIP) {
    $currentIP = "127.0.0.1"
    Write-Host "로컬 네트워크 IP를 찾을 수 없어 localhost를 사용합니다." -ForegroundColor Yellow
}

# 2. 프론트엔드 설정 업데이트 (선택적)
if ($UpdateFrontend) {
    $frontendConfigFile = ".\frontend\constants\config.js"
    $configContent = @"
export const API_CONFIG = {
  BASE_URL: 'http://$currentIP:8000',
  TIMEOUT: 10000
};

export const getCurrentIP = () => '$currentIP';
"@
    
    try {
        $configContent | Out-File -FilePath $frontendConfigFile -Encoding UTF8 -Force
        Write-Host "프론트엔드 설정 업데이트 완료: $currentIP" -ForegroundColor Green
    } catch {
        Write-Host "프론트엔드 설정 업데이트 실패" -ForegroundColor Red
    }
}

# 3. 백엔드 서버 실행
Write-Host "백엔드 서버 시작: http://$currentIP:8000" -ForegroundColor Cyan

# 환경 변수 설정
$env:ANONYMIZED_TELEMETRY="False"
$env:CHROMA_TELEMETRY_OPTOUT="True"
$env:PASSLIB_SUPPRESS_BCRYPT_WARNINGS="True"
$env:CURRENT_IP=$currentIP

# 기존 프로세스 정리
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force

# 서버 실행 (오류 확인을 위해 직접 실행)
uvicorn backend.app.main:app --host $currentIP --port 8000 --reload

Write-Host "개발 환경 설정 완료!" -ForegroundColor Green
Write-Host "백엔드 URL: http://$currentIP:8000" -ForegroundColor White
Write-Host "API 문서: http://$currentIP:8000/docs" -ForegroundColor White