import { API_BASE_URL, DEFAULT_HEADERS, checkResponseStatus } from './networkConfig';

// API 엔드포인트
const API_URL = API_BASE_URL;

// 개발 모드일 경우 테스트용 함수를 임포트
// let testLogin;
// if (__DEV__) {
//   testLogin = require('./authServiceTest').login;
// }

/**
 * 사용자 로그인을 처리하는 함수 (환경에 따라 다르게 작동)
 * @param {string} email - 사용자 이메일
 * @param {string} password - 사용자 비밀번호
 * @returns {Promise<object>} - 로그인 응답 데이터 (토큰 등)
 */
export const login = async (email, password) => {
  // 개발 모드에서도 실제 API 호출하도록 수정
  // if (__DEV__) {
  //   // 개발 모드에서는 테스트용 함수 사용
  //   return testLogin(email, password);
  // }

  try {
    // FastAPI OAuth2PasswordRequestForm 형식에 맞추기 위해 URLSearchParams 사용
    const body = new URLSearchParams();
    body.append('username', email);
    body.append('password', password);

    const response = await fetch(`${API_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: body.toString(),
    });
    
    checkResponseStatus(response);
    const data = await response.json();
    
    console.log('로그인 성공 응답:', data); // 디버깅용 로그

    return data;
  } catch (error) {
    console.error('로그인 API 호출 중 오류 발생:', error);
    throw error;
  }
};
