import chromadb
from typing import List, Dict, Any

# ChromaDB 클라이언트 설정
client =chromadb.PersistentClient(path="./chroma_db")

# 'restaurants' 컬렉션 가져오기 (없으면 생성)
collection = client.get_or_create_collection(name="restaurants")

# 벡터 DB 
def upsert_restaurant_vector(restaurant_id: int, vector: List[float], metadata: Dict[str, Any]):
    """
    음식점의 벡터와 메타데이터 (요약 정보 등)를 ChromaDB에 저장하거나 업데이트합니다.
    """
    # ChromaDB에 데이터 저장
    # id는 고유 식별자, embedding은 벡터값, metadata는 부가 정보
    collection.upsert(
        ids=[str(restaurant_id)], # id는 문자열이어야 함.
        embeddings=[vector],
        metadatas=[metadata]
    )
    print(f"Restaurant ID {restaurant_id} 벡터 정보가 ChrromaDB에 업데이트 되었습니다.")

def query_similar_restaurant(vector: List[float], n_results: int = 3) -> List[Dict[str, Any]]:
    """
    입력된 벡터와 가장 유사한 맛집을 ChromaDB에서 검색
    """
    # 벡터 검색
    results = collection.query(
        query_embeddings=[vector],
        n_results=n_results
    )
    
    # 검색 결과에서 메타데이터만 추출하여 리스트로 반환
    return results.get('metadatas', [[]])[0]  # 첫 번째 쿼리의 메타데이터 반환

