// 이 파일은 실제 백엔드 서버 없이 검색 기능을 시뮬레이션합니다.

const mockSearchResults = [
  {
    id: '101',
    name: 'Italian Feast Pizza',
    rating: 4.7,
    reviews: '320+',
    image: 'https://placehold.co/100x100/F5F5DC/6A4545?text=Pizza',
    description: 'Freshly baked pizza with a variety of Italian meats and vegetables.',
    tags: ['pizza', 'italian']
  },
  {
    id: '102',
    name: 'Classic Burger Joint',
    rating: 4.4,
    reviews: '550+',
    image: 'https://placehold.co/100x100/A9A9A9/4B4B4B?text=Burger',
    description: 'A classic American burger with all the fixings, served with fries.',
    tags: ['burger', 'american']
  },
  {
    id: '103',
    name: 'Sushi Sashimi Set',
    rating: 4.9,
    reviews: '910+',
    image: 'https://placehold.co/100x100/C1C1CD/333333?text=Sushi',
    description: 'Finest cuts of salmon and tuna sashimi, with a side of authentic sushi.',
    tags: ['sushi', 'japanese', 'seafood']
  },
  {
    id: '104',
    name: 'Spicy Thai Noodles',
    rating: 4.5,
    reviews: '420+',
    image: 'https://placehold.co/100x100/E6E6FA/483D8B?text=Noodles',
    description: 'Spicy stir-fried noodles with chicken and fresh vegetables.',
    tags: ['noodles', 'thai', 'spicy']
  },
  {
    id: '105',
    name: 'Cozy Coffee Cafe',
    rating: 4.8,
    reviews: '1,500+',
    image: 'https://placehold.co/100x100/D3D3D3/696969?text=Coffee',
    description: 'A quiet cafe with fresh brewed coffee and pastries.',
    tags: ['cafe', 'coffee', 'pastry']
  },
  {
    id: '106',
    name: 'Mexican Tacos Fiesta',
    rating: 4.6,
    reviews: '780+',
    image: 'https://placehold.co/100x100/FFD700/000000?text=Tacos',
    description: 'A vibrant spot with authentic Mexican tacos and burritos.',
    tags: ['tacos', 'mexican', 'burrito']
  }
];

/**
 * 테스트용 검색 함수
 * @param {string[] | string} query 검색어 목록 또는 단일 검색어
 * @returns {Promise<object[]>} 검색 결과 목록
 */
export const search = async (query) => {
  // 네트워크 지연 시뮬레이션
  await new Promise(resolve => setTimeout(resolve, 500));

  // query가 null, undefined, 또는 빈 배열인 경우 빈 배열 반환
  if (!query || (Array.isArray(query) && query.length === 0)) {
    return [];
  }

  // query를 배열로 변환하고 소문자로 변환
  const searchQueries = Array.isArray(query)
    ? query.map(q => String(q).toLowerCase())
    : [String(query).toLowerCase()];

  console.log("Searching for:", searchQueries.join(', '));

  // AND 조건으로 필터링
  const filteredResults = mockSearchResults.filter(item => {
    const itemName = item.name.toLowerCase();
    const itemDescription = item.description.toLowerCase();
    const itemTags = item.tags.map(tag => tag.toLowerCase());

    return searchQueries.every(q =>
      itemName.includes(q) || itemDescription.includes(q) || itemTags.includes(q)
    );
  });

  return filteredResults;
};
