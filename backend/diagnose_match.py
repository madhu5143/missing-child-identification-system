import os
import sys

# Add current directory (backend) to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.embedding_engine import generate_normalized_embedding
from app.alignment_engine import align_face
from app.vector_index import search_database_top_k

IMAGE_PATH = "../test_images/person_b.jpg"

def diagnose():
    db = SessionLocal()
    try:
        print(f"Running identification for image: {IMAGE_PATH}")
        if not os.path.exists(IMAGE_PATH):
            print(f"ERROR: Image file not found at {IMAGE_PATH}")
            return
            
        print("\nGenerating embedding and searching manually...")
        try:
            aligned = align_face(IMAGE_PATH)
            # Fix: Pass align=False because we already aligned it above
            query_vector = generate_normalized_embedding(aligned, align=False)
            candidates = search_database_top_k(db, query_vector, k=10)
            
            print("\nTop 10 Candidates Similarity Scores:")
            for i, c in enumerate(candidates):
                print(f"{i+1}. Child ID: {c['child_id']}, Name: {c['full_name']}, Similarity: {c['similarity']:.4f}")
                
            if not candidates:
                print("No candidates returned from vector search.")
        except Exception as e:
            print(f"Error during manual search: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
