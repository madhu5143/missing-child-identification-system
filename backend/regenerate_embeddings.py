import os
import sys
import json
from sqlalchemy.orm import Session

# Add current dir to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Image
from app.ai_engine import get_embedding, get_engine

def regenerate_embeddings():
    db = SessionLocal()
    engine = get_engine()
    
    if not engine.face_recognizer:
        print("Error: CNN model is not loaded. Cannot regenerate embeddings properly.")
        sys.exit(1)
        
    images = db.query(Image).all()
    updated = 0
    failed = 0
    
    for img in images:
        if img.file_path and os.path.exists(img.file_path):
            try:
                print(f"Processing image {img.id} at {img.file_path}...")
                emb = get_embedding(img.file_path)
                img.embedding_json = json.dumps(emb)
                
                # Check what the old length was
                old_len = "None"
                if img.embedding_json:
                    try:
                        old_len = str(len(json.loads(img.embedding_json)))
                    except:
                        pass
                
                print(f"  Success: embedding length {old_len} -> {len(emb)}")
                updated += 1
            except Exception as e:
                print(f"  Failed to process image {img.id}: {e}")
                failed += 1
        else:
            print(f"Image {img.id} file not found: {img.file_path}")
            failed += 1
            
    db.commit()
    print(f"\nDone. Updated {updated} embeddings, {failed} failed.")

if __name__ == "__main__":
    regenerate_embeddings()
