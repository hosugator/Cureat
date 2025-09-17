/**
 * 사용자 로그인을 처리하는 테스트용 함수
 * 실제 백엔드 서버 없이 로그인 성공/실패를 시뮬레이션합니다.
 * @param {string} email - 사용자 이메일
 * @param {string} password - 사용자 비밀번호
 * @returns {Promise<object>} - 로그인 응답 데이터 (가상의 토큰 등)
 */
export const login = async (email, password) => {
  // 네트워크 지연 시뮬레이션 (2초)
  await new Promise(resolve => setTimeout(resolve, 2000));

  try {
    // 테스트를 위한 더미 데이터
    if (email === 'test@test.com' && password === '1234') {
      console.log('로그인 성공!');
      return {
        token: 'mock-auth-token-12345',
        user: {
          id: 'user-123',
          email: 'test@test.com',
          name: '테스트 유저'
        }
      };
    } else {
      console.log('로그인 실패: 잘못된 자격 증명');
      throw new Error('이메일 또는 비밀번호가 잘못되었습니다.');
    }
  } catch (error) {
    console.error('로그인 테스트 중 오류 발생:', error);
    throw error;
  }
};
