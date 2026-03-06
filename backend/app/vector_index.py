from sqlalchemy import text
from typing import List, Tuple, Dict, Any
from .database import get_db

class VectorIndex:
    def __init__(self):
        pass

    def search_top_k(self, db_session, query_vector: list, k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a high-speed pgvector search using the inner product `<#>` operator.
        Requires all vectors to be exactly L2 Normalized beforehand for
        inner product to mathematically equal Cosine Similarity.
        
        It groups by child_id and returns their maximum similarity photo score 
        so we don't accidentally return 5 photos of the exact same child if they
        are all very similar.
        """
        
        # Format list to postgres vector string
        vec_str = '[' + ','.join(map(str, query_vector)) + ']'
        
        # Let's break down the mathematical inner product operator.
        # In pgvector, `<#>` returns the NEAGATIVE inner product to allow ASC sorting.
        # e.g., if inner product is 0.95 (strong match), `<#>` is -0.95.
        # To get the positive similarity score back, we multiply by -1.
        
        query = text(f"""
            SELECT 
                r.child_id,
                MAX(r.similarity) as best_match_score,
                MAX(r.image_url) as matched_image,
                MAX(mp.full_name) as full_name,
                MAX(mp.status) as child_status,
                MAX(mp.age) as age,
                MAX(mp.gender) as gender,
                MAX(mp.last_seen_location) as last_seen_location,
                MAX(mp.station_name) as station_name,
                MAX(mp.station_address) as station_address,
                MAX(mp.station_contact_number) as station_contact_number
            FROM (
                -- Subselect: rank ALL images individually by cosine inner product
                SELECT 
                    person_id as child_id, 
                    file_path as image_url,
                    (embedding_vector <#> :qvec) * -1 as similarity
                FROM images
                WHERE embedding_vector IS NOT NULL
            ) r
            JOIN missing_persons mp ON r.child_id = mp.id
            WHERE mp.is_resolved = false
            GROUP BY r.child_id
            ORDER BY best_match_score DESC
            LIMIT :k;
        """)
        
        results = db_session.execute(query, {'qvec': vec_str, 'k': k})
        
        formatted_matches = []
        for row in results:
            formatted_matches.append({
                "child_id": row.child_id,
                "similarity": float(row.best_match_score),
                "image_url": row.matched_image,
                "full_name": row.full_name,
                "status": row.child_status,
                "age": row.age,
                "gender": row.gender,
                "last_seen_location": row.last_seen_location,
                "station_name": row.station_name,
                "station_address": row.station_address,
                "station_contact_number": row.station_contact_number
            })
            
        return formatted_matches

# Global instance
_index = None

def get_vector_index():
    global _index
    if _index is None:
        _index = VectorIndex()
    return _index

def search_database_top_k(db, query_vector: list, k: int = 5) -> List[Dict[str, Any]]:
    index = get_vector_index()
    return index.search_top_k(db, query_vector, k)
