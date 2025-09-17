// frontend/services/searchService.js

import { search as testSearch } from './searchServiceTest';

const API_BASE_URL = 'http://192.168.45.54:8000'; // <-- 당신의 맥북 IP 주소로 수정하세요.

/**
 * 백엔드로 검색어를 전송하여 로그를 남기는 함수
 * @param {string} query 사용자가 입력한 검색어
 */
export const saveSearchLog = async (query) => {
  if (!query) {
    console.log('전송할 검색어가 없습니다.');
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/search-log`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: query }),
    });

    if (!response.ok) {
      throw new Error(`API 호출 중 오류 발생: ${response.status}`);
    }

    const data = await response.json();
    console.log('로그 저장 백엔드 응답:', data.message);

    return data;
  } catch (error) {
    console.error('로그 저장 API 호출 중 오류 발생:', error);
    throw new Error('통신 오류가 발생했습니다.');
  }
};


/**
 * ⚡️ 백엔드에 동적 검색을 요청하고 결과를 받는 함수
 * @param {string} query 사용자가 입력한 검색어 (자연어)
 * @returns {Promise<object[]>} AI 추천 결과 목록
 */
export const search = async (query) => {
  if (!query) {
    console.log('전송할 검색어가 없습니다.');
    return [];
  }

  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: query }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`백엔드 API 호출 중 오류 발생: ${response.status} - ${errorData.detail}`);
    }

    const data = await response.json();
    console.log('백엔드 응답:', data.message);
    
    // ⚡️ 수정된 부분: 받은 데이터 객체에서 'results' 배열만 반환합니다.
    return data.results;

  } catch (error) {
    console.error('검색 API 호출 중 오류 발생:', error);
    throw new Error('검색 오류가 발생했습니다.');
  }
};