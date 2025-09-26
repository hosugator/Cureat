import { API_BASE_URL, DEFAULT_HEADERS, checkResponseStatus } from './networkConfig';

/**
 * 신규 사용자 회원가입을 요청하는 함수
 * @param {object} userData 회원가입 폼 데이터
 * @returns {Promise<object>} 생성된 사용자 정보
 */
export const signUp = async (userData) => {
  try {
    console.log('회원가입 요청 데이터:', JSON.stringify(userData, null, 2)); // 요청 데이터 로깅
    
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(userData),
    });

    console.log('서버 응답 상태:', response.status); // 응답 상태 로깅

    // 서버가 어떤 바디를 줬는지 항상 확인
    const responseText = await response.text();
    console.log('서버 응답 원문:', responseText); // 응답 원문 로깅
    
    let responseData;
    try { 
      responseData = JSON.parse(responseText); 
    } catch (e) { 
      responseData = { raw: responseText }; 
    }

    if (!response.ok) {
      // 더 상세한 에러 로깅
      console.error('회원가입 실패 - 서버 응답:', {
        status: response.status,
        statusText: response.statusText,
        body: responseData,
      });
      
      // 서버가 보낸 메시지를 클라이언트에서도 확인하기 쉽게 재포장
      const errorMessage = responseData?.detail || responseData?.message || JSON.stringify(responseData);
      throw new Error(`HTTP ${response.status} ${response.statusText} - ${errorMessage}`);
    }

    console.log('회원가입 성공:', responseData); // 성공 로깅
    return responseData;
  } catch (error) {
    console.error('회원가입 API 호출 중 오류 발생:', error);
    throw error; // 상위에서 화면 처리
  }
};
