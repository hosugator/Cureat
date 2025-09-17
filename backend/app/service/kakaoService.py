import requests
import logging
from typing import Dict, Any, List

from app.config import settings

# Kakao API 설정
KAKAO_API_KEY = settings.KAKAO_REST_KEY
KAKAO_WEB_SEARCH_URL = "https://dapi.kakao.com/v2/search/web"

def _kakao_api_request(url: str, params: dict) -> Dict[str, Any]:
    """Kakao API 공통 요청 함수"""
    if not KAKAO_API_KEY:
        logging.warning("Kakao API 키가 .env 파일에 설정되지 않았습니다.")
        return {}

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5.0)
        
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Kakao API 오류 - 상태코드: {response.status_code}, 응답: {response.text}")
            return {}
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Kakao API 요청 중 오류 발생: {e}")
        return {}

def search_web(query: str, size: int = 5) -> List[Dict[str, Any]]:
    """Kakao 웹 검색 API를 사용하여 웹 문서를 검색합니다."""
    params = {
        "query": query,
        "size": size,
    }
    
    result = _kakao_api_request(KAKAO_WEB_SEARCH_URL, params)
    
    if result and 'documents' in result:
        return result['documents']
    else:
        return []
