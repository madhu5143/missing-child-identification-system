import os
import sys

# Add current directory (backend) to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.alignment_engine import align_face
from app.embedding_engine import generate_normalized_embedding
from app.vector_index import search_database_top_k

IMAGE_PATH = "../test_images/person_b.jpg"

def verify():
    db = SessionLocal()
    try:
        print(f"Verifying similarity for image: {IMAGE_PATH}")
        aligned = align_face(IMAGE_PATH)
        # Using the fix: align=False
        query_vector = generate_normalized_embedding(aligned, align=False)
        candidates = search_database_top_k(db, query_vector, k=5)
        
        print("\nResults:")
        for i, c in enumerate(candidates):
            print(f"{i+1}. Child ID: {c['child_id']}, Name: {c['full_name']}, Similarity: {c['similarity']:.4f}")
            
        if os.path.exists(aligned):
            os.remove(aligned)
            
    finally:
        db.close()

if __name__ == "__main__":
    verify()
