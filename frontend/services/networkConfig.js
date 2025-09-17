// 네트워크 설정 및 API 기본 URL 관리
import { Platform } from 'react-native';

// 개발 환경에서 로컬 서버 URL 설정
const getLocalServerUrl = () => {
  if (__DEV__) {
    // 현재 개발 서버 IP 주소 사용
    return 'http://192.168.45.20:8000';
  } else {
    // 프로덕션 환경에서는 실제 서버 URL
    return 'https://cureat.onrender.com';
  }
};

export const API_BASE_URL = getLocalServerUrl();

// 네트워크 요청 기본 헤더
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

// 타임아웃 설정 (밀리초)
export const REQUEST_TIMEOUT = 10000;

// API 응답 상태 확인 함수
export const checkResponseStatus = (response) => {
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response;
};

export default {
  API_BASE_URL,
  DEFAULT_HEADERS,
  REQUEST_TIMEOUT,
  checkResponseStatus,
};