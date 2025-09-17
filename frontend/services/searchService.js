// 이 파일은 실제 검색 백엔드 API와의 통신을 담당합니다.
// 개발 환경에서는 searchServiceTest.js를 사용하고,
// 프로덕션 환경에서는 실제 API를 호출합니다.

import { search as testSearch } from './searchServiceTest';
import { API_BASE_URL, DEFAULT_HEADERS, checkResponseStatus } from './networkConfig';

/**
 * 검색어를 기반으로 음식점 추천을 받는 함수
 * @param {string} query 검색어 또는 프롬프트
 * @param {number} userId 사용자 ID
 * @returns {Promise<object>} 추천 결과 (answer, restaurants)
 */
export const search = async (query, userId = 1) => {
  // 개발 모드에서도 실제 API 호출 (mock 분기 주석 처리)
  // if (__DEV__) {
  //   console.log('Using mock search service in development mode.');
  //   return testSearch(query);
  // }

  try {
    const response = await fetch(`${API_BASE_URL}/recommendations`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify({
        user_id: userId,
        prompt: query
      }),
    });

    checkResponseStatus(response);

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('추천 API 호출 중 오류 발생:', error);
    throw new Error('추천 검색 오류가 발생했습니다.');
  }
};

/**
 * 데이트 코스 생성을 요청하는 함수
 * @param {object} courseData 코스 생성 데이터 {user_id, location, start_time, end_time, theme}
 * @returns {Promise<object>} 코스 생성 결과
 */
export const createDateCourse = async (courseData) => {
  if (__DEV__) {
    console.log('개발 모드: 데이트 코스 생성 테스트');
    return { 
      success: true, 
      message: '데이트 코스 생성 성공 (테스트)', 
      course: courseData 
    };
  }

  try {
    const response = await fetch(`${API_BASE_URL}/date-course`, {
      method: 'POST',
      headers: DEFAULT_HEADERS,
      body: JSON.stringify(courseData),
    });

    checkResponseStatus(response);

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('데이트 코스 생성 API 호출 중 오류 발생:', error);
    throw new Error('데이트 코스 생성 오류가 발생했습니다.');
  }
};
