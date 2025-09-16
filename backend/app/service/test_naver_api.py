import logging
from .naverMapService import search_local_places, search_restaurant_reviews, _naver_api_request, NAVER_IMAGE_URL

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # 1) 지역 검색
    places = search_local_places("강남역 맛집", display=5)
    print("local items:", len(places))
    if places:
        print(places[0])
    # 2) 블로그 리뷰
    reviews = search_restaurant_reviews("을밀대", count=5)
    print("blog items:", len(reviews))
    if reviews:
        print(reviews[0])
    # 3) 이미지 검색
    imgs = _naver_api_request(
        NAVER_IMAGE_URL,
        {"query": "강아지", "display": 5, "start": 1, "sort": "sim"}
    )
    print("image keys:", imgs.keys())