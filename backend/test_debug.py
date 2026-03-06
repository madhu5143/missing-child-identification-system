import os
import sys
import numpy as np
os.environ["SSL_CERT_FILE"] = __import__("certifi").where()

from sqlalchemy import text
from app.database import SessionLocal
from app.models import Image
from app.vector_index import search_database_top_k
from app.embedding_engine import get_embedding_engine
from app.alignment_engine import align_face
import urllib.request
import tempfile

def test_pipeline():
    print("--- Starting Debug Pipeline ---")
    db = SessionLocal()
    
    # 1. Get an existing image URL from the database
    img_record = db.query(Image).filter(Image.embedding_vector.isnot(None)).first()
    if not img_record:
        print("No images found in the database.")
        sys.exit(1)
        
    db_vector = np.array(img_record.embedding_vector)
    print(f"Db vector extracted from database, length {len(db_vector)}. Example values: {db_vector[:3]}")

    image_url = img_record.file_path
    print(f"Testing with image: {image_url}")

    # 2. Download the image locally to simulate an upload
    fd, local_path = tempfile.mkstemp(suffix=".jpg")
    os.close(fd)
    try:
        urllib.request.urlretrieve(image_url, local_path)
    except Exception as e:
        print(f"Failed to download image: {e}")
        # Use first image in test_images if available
        test_dir = 'test_images'
        if os.path.exists(test_dir):
             test_images = [f for f in os.listdir(test_dir) if f.endswith('.jpg')]
             if test_images:
                 local_path = os.path.join(test_dir, test_images[0])
                 print(f"Using local test image: {local_path}")
             else:
                 sys.exit(1)
        else:
             sys.exit(1)
             
    # 3. Process the image using exactly the pipeline in matcher.py
    print("\n--- Pipeline Execution ---")
    aligned_path = align_face(local_path)
    
    engine = get_embedding_engine()
    # Inside this get_embedding, the `norm` will be printed by the debug statement we added
    query_vector = engine.get_embedding(aligned_path)
    query_vector_list = query_vector.tolist()
    
    # 4. Search Database using Vector Index (SQL)
    print("\n--- Vector Search ---")
    candidates = search_database_top_k(db, query_vector_list, k=5)
    
    if not candidates:
        print("No candidates found.")
    else:
        top1_data = candidates[0]
        top1_sim = top1_data.get("similarity", 0.0)
        
        # Determine top2 similarity for the gap delta check
        top2_sim = 0.0
        if len(candidates) > 1:
            top2_sim = candidates[1].get("similarity", 0.0)
            
        print(f"\n--- Output Logs ---")
        print(f"DEBUG: top1_sim = {top1_sim}, top2_sim = {top2_sim}")

    # 5. Manual Python Dot Product against the actual matching record
    # Let's find the exact child id that matched
    matched_child_id = top1_data["child_id"]
    # Get that child's images to manually calculate
    matched_img_records = db.query(Image).filter(Image.person_id == matched_child_id, Image.embedding_vector.isnot(None)).all()
    
    print("\n--- Manual Dot Product Validation ---")
    best_manual_sim = -1.0
    for m in matched_img_records:
        m_vec = np.array(m.embedding_vector)
        # Inner product mathematically equals Cosine Similarity if L2 norm == 1
        dot_product = np.dot(query_vector, m_vec)
        if dot_product > best_manual_sim:
            best_manual_sim = dot_product
            
    print(f"SQL Calculated top1_sim:  {top1_sim}")
    print(f"Python calculated dot product: {best_manual_sim}")
    print(f"Difference: {abs(top1_sim - best_manual_sim)}")
    
    if abs(top1_sim - best_manual_sim) < 0.0001:
        print("MATCH! The manual Python dot product matches the SQL result.")
    else:
        print("MISMATCH! The Python dot product does NOT match the SQL result.")

if __name__ == '__main__':
    test_pipeline()
