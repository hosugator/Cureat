import { API_BASE_URL, DEFAULT_HEADERS, checkResponseStatus } from './networkConfig';

// API 엔드포인트
const API_URL = API_BASE_URL;

// 개발 모드일 경우 테스트용 함수를 임포트
let testLogin;
if (__DEV__) {
  testLogin = require('./authServiceTest').login;
}

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
    // FastAPI OAuth2PasswordRequestForm 형식으로 전송
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/token`, {
      method: 'POST',
      body: formData, // JSON이 아닌 FormData로 전송
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

/**
 * 사용자 회원가입을 처리하는 함수
 * @param {object} userData - 사용자 회원가입 데이터
 * @returns {Promise<object>} - 회원가입 응답 데이터
 */
export const signup = async (userData) => {
  if (__DEV__) {
    // 개발 모드에서는 테스트용 응답 반환
    console.log('개발 모드: 회원가입 테스트');
    return { success: true, message: '회원가입 성공 (테스트)', user: userData };
  }

  try {
    const response = await fetch(`${API_URL}/users/signup`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(userData),
    });
    
    checkResponseStatus(response);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || '회원가입에 실패했습니다.');
    }

    return data;
  } catch (error) {
    console.error('회원가입 API 호출 중 오류 발생:', error);
    throw error;
  }
};
