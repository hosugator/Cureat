import requests
import logging
from typing import Dict, Any, List
from fastapi import HTTPException, status

# 상대 import로 통일
from ..config import settings

# Kakao API 설정
KAKAO_API_KEY = settings.KAKAO_REST_KEY
KAKAO_WEB_SEARCH_URL = "https://dapi.kakao.com/v2/search/web"

def _kakao_api_request(url: str, params: dict) -> Dict[str, Any]:
    """Kakao API 공통 요청 함수"""
    if not KAKAO_API_KEY:
        logging.warning("Kakao API 키가 .env 파일에 설정되지 않았습니다.")
        # 키가 없을 경우, 서비스 사용 불가 오류를 발생시킴
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서비스에 카카오 API 키가 설정되지 않았습니다."
        )

    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5.0)
        response.raise_for_status()  # 2xx 상태 코드가 아닐 경우 HTTPError 발생
        
        return response.json()
            
    except requests.exceptions.HTTPError as e:
        logging.error(f"Kakao API 오류 - 상태코드: {e.response.status_code}, 응답: {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="카카오 API 서비스에 문제가 발생했습니다."
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Kakao API 요청 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="카카오 API 요청 중 네트워크 오류가 발생했습니다."
        )

def search_web(query: str, size: int = 5) -> List[Dict[str, Any]]:
    """Kakao 웹 검색 API를 사용하여 웹 문서를 검색합니다."""
    params = {
        "query": query,
        "size": size,
    }
    
    # _kakao_api_request가 이제 오류를 발생시키므로, 이 함수를 호출하는 상위 레벨에서
    # try-except 블록으로 감싸야 할 수 있습니다.
    result = _kakao_api_request(KAKAO_WEB_SEARCH_URL, params)
    
    if result and 'documents' in result:
        return result['documents']
    else:
        return []
