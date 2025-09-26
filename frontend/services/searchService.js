// 이 파일은 실제 검색 백엔드 API와의 통신을 담당합니다.
// 개발 환경에서는 searchServiceTest.js를 사용하고,
// 프로덕션 환경에서는 실제 API를 호출합니다.

import { search as testSearch } from './searchServiceTest';
import { API_BASE_URL, DEFAULT_HEADERS, checkResponseStatus } from './networkConfig';

/**
 * 자연어 프롬프트 기반 맛집 검색 함수
 * @param {string} query 사용자가 검색창에 입력한 자연어 (예: "강남역 근처 데이트하기 좋은 이탈리안 레스토랑")
 * @param {number} userId 로그인한 사용자 ID (DB에서 개인화 데이터 조회용)
 * @returns {Promise<object>} 검색 결과 (restaurants, summary)
 */
export const search = async (query, userId = null) => {
  try {
    // 자연어 쿼리와 사용자 ID만 전달
    // 백엔드에서 userId로 DB 개인화 데이터를 조회하고 자연어를 분석
    const params = new URLSearchParams({
      prompt: query,
      ...(userId && { user_id: userId })
    });

    const response = await fetch(`${API_BASE_URL}/search/prompt?${params}`, {
      method: 'GET',
      headers: DEFAULT_HEADERS,
    });

    checkResponseStatus(response);

    const data = await response.json();
    
    // 백엔드 응답을 프론트엔드 형식에 맞게 조정
    if (data && data.restaurants && data.restaurants.length > 0) {
      return {
        answer: data.summary || "검색 결과입니다.",
        restaurants: data.restaurants.map((restaurant, index) => {
          // JSON 문자열이면 파싱
          const parseJsonField = (field) => {
            if (typeof field === 'string') {
              try {
                return JSON.parse(field);
              } catch (e) {
                return [];
              }
            }
            return Array.isArray(field) ? field : [];
          };

          return {
            id: restaurant.id || `restaurant-${index}`,
            name: restaurant.name,
            address: restaurant.address,
            phone: restaurant.phone || '',
            operating_hours: restaurant.operating_hours || '',
            rating: "4.5", // 기본값
            reviews: "100+", // 기본값
            description: parseJsonField(restaurant.pros).join(', ') || restaurant.name,
            image: restaurant.image_url || "https://via.placeholder.com/300x200?text=No+Image",
            signature_dishes: parseJsonField(restaurant.signature_dishes),
            price_range: restaurant.price_range || '',
            pros: parseJsonField(restaurant.pros),
            cons: parseJsonField(restaurant.cons),
            keywords: parseJsonField(restaurant.keywords),
            category: restaurant.category || '',
            atmosphere: restaurant.atmosphere || ''
          };
        })
      };
    } else {
      throw new Error(data.message || data.summary || '조건에 맞는 검색 결과가 없습니다.');
    }
  } catch (error) {
    console.error('프롬프트 기반 검색 API 호출 중 오류 발생:', error);
    throw new Error('검색 오류가 발생했습니다.');
  }
};

/**
 * 기존 추천 시스템 (하위 호환성을 위해 유지)
 * @param {string} query 검색어 또는 프롬프트
 * @param {number} userId 사용자 ID
 * @returns {Promise<object>} 추천 결과 (answer, restaurants)
 */
export const getRecommendations = async (query, userId = 1) => {
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
