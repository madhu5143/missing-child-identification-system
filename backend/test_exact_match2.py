import sys
import os
import certifi
import urllib.request
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models import Image
from app.embedding_engine import generate_normalized_embedding
from app.vector_index import search_database_top_k
import uuid

os.environ['SSL_CERT_FILE'] = certifi.where()

def test_remote_exact():
    db = SessionLocal()
    images = db.query(Image).filter(Image.embedding_vector.isnot(None)).all()
    if not images:
        print("No images with vectors in DB")
        return
    
    img = images[-1] # Let's test the LAST one just in case
    print(f"Testing against DB image ID {img.id}, url: {img.file_path}")
    
    temp_path = f"test_temp_{uuid.uuid4().hex[:6]}.jpg"
    try:
        urllib.request.urlretrieve(img.file_path, temp_path)
        print(f"Downloaded to {temp_path}")
        
        query_vector = generate_normalized_embedding(temp_path)
        print(f"Generated query vector length: {len(query_vector)}")
        
        matches = search_database_top_k(db, query_vector, k=3)
        print(f"Pgvector matches for EXACT same downloaded file:")
        for m in matches:
            print(f"  Child ID: {m['child_id']}, Similarity: {m['similarity']}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    test_remote_exact()
