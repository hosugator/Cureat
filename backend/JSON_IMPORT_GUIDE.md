# 🍽️ 음식점 JSON 데이터 Import 가이드

## 📋 JSON 파일 형식

### 방법 1: 음식점 배열 형식
```json
[
  {
    "name": "맛있는 파스타집",
    "address": "서울시 강남구 테헤란로 123",
    "phone": "02-1234-5678",
    "operating_hours": "11:00-22:00 (월~일)",
    "signature_dishes": ["크림 파스타", "토마토 파스타"],
    "price_range": "15,000~25,000원",
    "pros": ["맛있는 파스타", "친절한 서비스", "깔끔한 인테리어"],
    "cons": ["대기시간 김", "주차 어려움"],
    "keywords": ["파스타", "이탈리안", "데이트", "강남"],
    "category": "이탈리안",
    "atmosphere": "로맨틱"
  },
  {
    "name": "한국식 BBQ",
    "address": "서울시 서초구 강남대로 456",
    "phone": "02-9876-5432",
    "operating_hours": "17:00-02:00 (화~일), 월요일 휴무",
    "signature_dishes": ["갈비살", "삼겹살"],
    "price_range": "20,000~35,000원",
    "pros": ["신선한 고기", "넓은 공간", "좋은 환기"],
    "cons": ["가격 비쌈", "시끄러움"],
    "keywords": ["고기", "한식", "회식", "서초"],
    "category": "한식",
    "atmosphere": "활기찬"
  }
]
```

### 방법 2: 객체 형식
```json
{
  "restaurants": [
    {
      "name": "맛있는 파스타집",
      "address": "서울시 강남구 테헤란로 123",
      ...
    }
  ]
}
```

## 🔧 사용 방법

### 1. JSON 파일 준비
위 형식에 맞게 JSON 파일을 준비해주세요.

### 2. Import 실행
```bash
# backend 폴더에서 실행
cd backend
python import_restaurants.py your_data.json
```

### 3. 결과 확인
```
🎉 Import 완료!
📊 결과 통계:
   - 총 데이터: 50개
   - 새로 생성: 35개
   - 업데이트: 10개
   - 건너뜀: 3개
   - 오류: 2개
```

## 📝 필수 필드

- **name**: 음식점 이름 (필수)
- **address**: 주소 (필수)

## 🔄 선택 필드

- **phone**: 전화번호
- **operating_hours**: 운영시간
- **signature_dishes**: 대표메뉴 (배열)
- **price_range**: 가격대
- **pros**: 장점 (배열)
- **cons**: 단점 (배열)
- **keywords**: 키워드 (배열)
- **category**: 카테고리 (한식, 양식, 일식, 중식 등)
- **atmosphere**: 분위기

## ⚠️ 주의사항

1. **중복 처리**: 같은 이름 + 주소의 음식점은 자동으로 업데이트됩니다
2. **인코딩**: JSON 파일은 UTF-8 인코딩으로 저장해주세요
3. **데이터 검증**: 필수 필드가 없는 데이터는 자동으로 건너뜁니다
4. **에러 처리**: 개별 음식점 처리 중 오류가 발생해도 전체 과정은 계속됩니다

## 🛠️ 문제 해결

### JSON 형식 오류
```
JSON 파일 형식 오류: Expecting ',' delimiter: line 5 column 3 (char 123)
```
→ JSON 파일의 문법을 확인하세요 (쉼표, 따옴표 등)

### 파일을 찾을 수 없음
```
JSON 파일을 찾을 수 없습니다: data.json
```
→ 파일 경로를 확인하세요

### DB 연결 오류
→ backend/app/database.py의 DB 설정을 확인하세요

## 📞 지원

문제가 발생하면 로그를 확인하거나 개발자에게 문의하세요!