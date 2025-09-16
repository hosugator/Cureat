from typing import List, Dict, Any
from .database import get_vector_db_collection

# database.py에서 설정한 벡터 DB 컬렉션 가져오기
collection = get_vector_db_collection()

def upsert_restaurant(restaurant_id: str, vector: List[float], metadata: Dict[str, Any]):
    """맛집의 벡터와 메타데이터(요약 정보 등)를 ChromaDB에 저장하거나 업데이트"""
    # ChromaDB는 리스트 형태 메타데이터 지원하지 않음, 문자열로 변환 필요
    sanitized_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            sanitized_metadata[key] = '|'.join(str(v) for v in value)
        else:
            sanitized_metadata[key] = str(value) if value is not None else ''
            
    collection.upsert(
        ids=[restaurant_id],
        embeddings=[vector],
        metadatas=[sanitized_metadata]
    )
    print(f"Restaurant ID {restaurant_id} 벡터 정보가 ChromaDB에 업데이트 되었습니다.")
    
def query_similar_restaurants(vector: List[float], n_results: int = 3) -> List[Dict[str, Any]]:
    results = collection.query(
        query_embeddings=[vector],
        n_results=n_results
    )
    
    # DB에서 |로 구분된 문자열을 다시 리스트로 변환하여 반환합니다.
    final_results = []
    if results and results.get('metadatas'):
        for metadata in results['metadatas'][0]:
            if metadata.get('summary_pros'):
                metadata['summary_pros'] = metadata['summary_pros'].split('|')
            if metadata.get('summary_cons'):
                metadata['summary_cons'] = metadata['summary_cons'].split('|')
            if metadata.get('keywords'):
                metadata['keywords'] = metadata['keywords'].split('|')
            if metadata.get('nearby_attractions'):
                metadata['nearby_attractions'] = metadata['nearby_attractions'].split('|')
            # 단일 값 필드들은 문자열로 유지
            if metadata.get('signature_menu') and '|' in metadata['signature_menu']:
                metadata['signature_menu'] = metadata['signature_menu'].split('|')[0]
            if metadata.get('summary_parking') and '|' in metadata['summary_parking']:
                metadata['summary_parking'] = metadata['summary_parking'].split('|')[0]
            if metadata.get('summary_price') and '|' in metadata['summary_price']:
                metadata['summary_price'] = metadata['summary_price'].split('|')[0]
            if metadata.get('summary_opening_hours') and '|' in metadata['summary_opening_hours']:
                metadata['summary_opening_hours'] = metadata['summary_opening_hours'].split('|')[0]
            if metadata.get('summary_phone') and '|' in metadata['summary_phone']:
                metadata['summary_phone'] = metadata['summary_phone'].split('|')[0]
            final_results.append(metadata)
                        
    return final_results

def get_restaurant_by_id(restaurant_id: str) -> Dict[str, Any]:
    """벡터 DB에서 특정 맛집 정보를 가져옵니다."""
    try:
        result = collection.get(ids=[restaurant_id])
        if result and result.get('ids') and len(result['ids']) > 0:
            metadata = result['metadatas'][0]
            # 리스트 형태 데이터 복원
            if metadata.get('summary_pros'):
                metadata['summary_pros'] = metadata['summary_pros'].split('|')
            if metadata.get('summary_cons'):
                metadata['summary_cons'] = metadata['summary_cons'].split('|')
            if metadata.get('keywords'):
                metadata['keywords'] = metadata['keywords'].split('|')
            if metadata.get('nearby_attractions'):
                metadata['nearby_attractions'] = metadata['nearby_attractions'].split('|')
            return metadata
        return None
    except Exception as e:
        print(f"벡터 DB에서 맛집 정보 조회 중 오류: {e}")
        return None

def check_restaurant_exists(restaurant_id: str) -> bool:
    """벡터 DB에 해당 맛집 정보가 이미 있는지 확인합니다."""
    try:
        result = collection.get(ids=[restaurant_id])
        return bool(result['ids'])
    except Exception as e:
        print(f"벡터 DB 존재 확인 중 오류: {e}")
        return False