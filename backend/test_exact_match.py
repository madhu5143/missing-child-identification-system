import sys
import os
from sqlalchemy import text
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models import Image
from app.embedding_engine import generate_normalized_embedding
from app.vector_index import search_database_top_k

def test():
    db = SessionLocal()
    images = db.query(Image).filter(Image.embedding_vector.isnot(None)).all()
    if not images:
        print("No images with vectors in DB")
        return
    
    # Let's take the first image from DB and test it against itself
    img = images[0]
    print(f"Testing against DB image ID {img.id}, path: {img.file_path}")
    
    # We will compute the embedding of the exact same local file if it exists, otherwise skip
    local_path = img.file_path
    if local_path.startswith("http"):
        print("Image is a URL, we need a local file to test exact match.")
    elif not os.path.exists(local_path):
        print(f"Local file {local_path} does not exist.")
    else:
        query_vector = generate_normalized_embedding(local_path)
        print(f"Generated query vector length: {len(query_vector)}")
        
        # Test pgvector similarity
        matches = search_database_top_k(db, query_vector, k=3)
        print(f"Pgvector matches for SAME local file:")
        for m in matches:
            print(f"  Child ID: {m['child_id']}, Similarity: {m['similarity']}")

if __name__ == '__main__':
    test()
