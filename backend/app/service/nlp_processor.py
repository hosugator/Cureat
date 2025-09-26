import re
import logging
from typing import Dict, Any, List, Optional
from .gemini_service import gemini_service

class NaturalLanguageProcessor:
    """자연어 프롬프트에서 핵심 키워드와 검색 파라미터를 추출하는 클래스"""
    
    def __init__(self):
        self.location_keywords = [
            '강남', '홍대', '신촌', '명동', '이태원', '압구정', '청담', '삼성동', '성수동',
            '건대', '왕십리', '신림', '사당', '교대', '역삼', '선릉', '잠실', '송파',
            '마포', '용산', '서초', '강서', '노원', '은평', '도봉', '관악', '동작'
        ]
        
        self.food_keywords = [
            '한식', '일식', '중식', '양식', '이탈리안', '프렌치', '멕시칸', '태국', '베트남',
            '스시', '초밥', '파스타', '피자', '햄버거', '치킨', '삼겹살', '갈비', '불고기',
            '냉면', '짜장면', '짬뽕', '라면', '김치찌개', '된장찌개', '부대찌개',
            '카페', '디저트', '아이스크림', '케이크', '빵'
        ]
        
        self.mood_keywords = [
            '데이트', '연인', '커플', '친구', '가족', '회식', '술', '소주', '맥주',
            '조용한', '분위기', '로맨틱', '캐주얼', '고급', '저렴한', '합리적',
            '혼밥', '혼술', '테이크아웃'
        ]
        
        self.weather_keywords = [
            '비오는', '추운', '더운', '선선한', '따뜻한', '겨울', '여름', '봄', '가을'
        ]

    def extract_keywords_with_llm(self, user_input: str) -> Dict[str, Any]:
        """
        LLM을 사용하여 자연어 입력에서 구조화된 검색 파라미터 추출
        """
        prompt = f"""
다음 사용자 입력을 분석하여 맛집 검색에 필요한 정보를 JSON 형태로 추출해주세요.

사용자 입력: "{user_input}"

다음 형식으로 응답해주세요:
{{
    "location": "지역명 (예: 강남, 홍대, 신촌 등)",
    "food_type": "음식 종류 (예: 한식, 일식, 파스타, 피자 등)",
    "mood": "분위기나 상황 (예: 데이트, 회식, 혼밥, 가족모임 등)",
    "weather": "날씨 관련 키워드 (예: 비오는날, 추운날 등, 없으면 null)",
    "price_range": "가격대 (예: 저렴한, 합리적인, 고급 등, 없으면 null)",
    "special_needs": "특별한 요구사항 (예: 주차가능, 테이크아웃, 24시간 등, 없으면 null)",
    "search_keywords": ["핵심 검색 키워드들을 배열로"]
}}

규칙:
1. 한국어 지역명을 우선 사용하세요
2. 구체적인 음식명이 있으면 그것을 우선하세요
3. 분위기나 상황을 정확히 파악하세요
4. 날씨 언급이 없으면 weather는 null로 하세요
5. 검색 키워드는 네이버/카카오 API 검색에 적합하게 조합하세요
"""

        try:
            response = gemini_service.generate_text(prompt)
            # JSON 응답에서 코드 블록 제거
            json_str = response.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            
            import json
            extracted_data = json.loads(json_str.strip())
            
            # 기본값 설정
            result = {
                'location': extracted_data.get('location', ''),
                'food_type': extracted_data.get('food_type', ''),
                'mood': extracted_data.get('mood', ''),
                'weather': extracted_data.get('weather'),
                'price_range': extracted_data.get('price_range'),
                'special_needs': extracted_data.get('special_needs'),
                'search_keywords': extracted_data.get('search_keywords', []),
                'original_query': user_input
            }
            
            logging.info(f"LLM 키워드 추출 결과: {result}")
            return result
            
        except Exception as e:
            logging.error(f"LLM 키워드 추출 실패: {e}")
            # 폴백: 기본 키워드 추출 사용
            return self.extract_keywords_basic(user_input)

    def extract_keywords_basic(self, user_input: str) -> Dict[str, Any]:
        """
        기본 규칙 기반 키워드 추출 (LLM 실패 시 폴백)
        """
        user_input_lower = user_input.lower()
        
        # 지역 추출
        location = ''
        for loc in self.location_keywords:
            if loc in user_input:
                location = loc
                break
        
        # 음식 종류 추출
        food_type = ''
        for food in self.food_keywords:
            if food in user_input:
                food_type = food
                break
        
        # 분위기/상황 추출
        mood = ''
        for m in self.mood_keywords:
            if m in user_input:
                mood = m
                break
        
        # 날씨 추출
        weather = None
        for w in self.weather_keywords:
            if w in user_input:
                weather = w
                break
        
        # 검색 키워드 생성
        search_keywords = []
        if location:
            search_keywords.append(location)
        if food_type:
            search_keywords.append(food_type)
        if mood and mood in ['데이트', '연인', '커플']:
            search_keywords.append('데이트')
        
        # 기본 맛집 키워드 추가
        search_keywords.append('맛집')
        
        return {
            'location': location,
            'food_type': food_type,
            'mood': mood,
            'weather': weather,
            'price_range': None,
            'special_needs': None,
            'search_keywords': search_keywords,
            'original_query': user_input
        }

    def generate_search_queries(self, extracted_data: Dict[str, Any]) -> List[str]:
        """
        추출된 키워드를 바탕으로 API 검색용 쿼리 생성
        """
        queries = []
        base_keywords = extracted_data['search_keywords'].copy()
        
        # 기본 쿼리
        if base_keywords:
            queries.append(' '.join(base_keywords))
        
        # 위치 + 음식 조합
        if extracted_data['location'] and extracted_data['food_type']:
            queries.append(f"{extracted_data['location']} {extracted_data['food_type']} 맛집")
        
        # 분위기 포함 쿼리
        if extracted_data['mood'] and extracted_data['location']:
            queries.append(f"{extracted_data['location']} {extracted_data['mood']} 맛집")
        
        # 날씨 고려 쿼리
        if extracted_data['weather'] and extracted_data['location']:
            queries.append(f"{extracted_data['location']} {extracted_data['weather']} 맛집")
        
        # 중복 제거 및 최대 3개 쿼리로 제한
        unique_queries = list(set(queries))[:3]
        
        logging.info(f"생성된 검색 쿼리: {unique_queries}")
        return unique_queries

# 싱글톤 인스턴스
nlp_processor = NaturalLanguageProcessor()