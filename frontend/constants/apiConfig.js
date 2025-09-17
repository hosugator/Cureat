// 동적 IP 환경을 위한 API 설정
class ApiConfig {
  constructor() {
    this.baseURL = this.detectBackendURL();
  }

  // 백엔드 URL 자동 감지
  detectBackendURL() {
    // 1. 환경 변수에서 확인
    if (process.env.EXPO_PUBLIC_API_URL) {
      return process.env.EXPO_PUBLIC_API_URL;
    }

    // 2. 현재 디바이스의 네트워크 정보로 추정
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }

    // 3. 개발 중일 때는 일반적인 로컬 네트워크 IP 시도
    const commonIPs = [
      'http://192.168.45.20:8000',
      'http://192.168.1.20:8000',
      'http://192.168.0.20:8000',
      'http://10.0.0.20:8000',
      'http://localhost:8000'
    ];

    return commonIPs[0]; // 기본값
  }

  // 백엔드 연결 테스트
  async testConnection(url = this.baseURL) {
    try {
      const response = await fetch(`${url}/health`, { 
        method: 'GET',
        timeout: 3000 
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  // 사용 가능한 백엔드 URL 찾기
  async findWorkingBackendURL() {
    const candidateURLs = [
      'http://192.168.45.20:8000',
      'http://127.0.0.1:8000',
      'http://localhost:8000',
      'http://192.168.1.20:8000',
      'http://10.0.0.20:8000'
    ];

    for (const url of candidateURLs) {
      if (await this.testConnection(url)) {
        this.baseURL = url;
        console.log(`백엔드 서버 발견: ${url}`);
        return url;
      }
    }

    console.warn('작동하는 백엔드 서버를 찾을 수 없습니다.');
    return null;
  }

  getBaseURL() {
    return this.baseURL;
  }
}

// 싱글톤 인스턴스
const apiConfig = new ApiConfig();

export default apiConfig;
export { ApiConfig };