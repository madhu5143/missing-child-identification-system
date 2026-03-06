import os
import sys
import json
from sqlalchemy import create_engine
from dotenv import load_dotenv

sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models import Image
from app.alignment_engine import align_face
from app.embedding_engine import generate_normalized_embedding
from app.ai_engine import get_embedding as get_dual_embedding

load_dotenv()

def regenerate_all_embeddings():
    db = SessionLocal()
    images = db.query(Image).all()
    
    updated = 0
    failed = 0
    
    for img in images:
        path = img.file_path
        
        # In a real deployed app, path might be a URL. 
        # But this is a local debugging fix. If it's a URL we need to download it.
        # Luckily, most of the dev database are local files or we can download them.
        temp_path = None
        if path.startswith("http"):
            # download it locally
            import urllib.request
            import uuid
            temp_path = f"target_{uuid.uuid4().hex[:6]}.jpg"
            try:
                urllib.request.urlretrieve(path, temp_path)
                process_path = temp_path
            except Exception as e:
                print(f"Failed to download {path}: {e}")
                failed += 1
                continue
        else:
            process_path = path

        if not os.path.exists(process_path):
            print(f"Skipping Image ID {img.id}: File not found at {process_path}")
            failed += 1
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            continue
            
        try:
            print(f"Processing Image ID {img.id}...")
            
            # 1. Regenerate vector for pgvector (Standardized RetinaFace Pipeline)
            # We no longer align externally. The engine handles it.
            embedding_list = generate_normalized_embedding(process_path)
            img.embedding_vector = embedding_list
            
            # 2. Regenerate dual-model JSON (Consistent with RetinaFace)
            # AIEngine will also be updated to ensure consistency
            dual_emb = get_dual_embedding(process_path)
            img.embedding_json = json.dumps(dual_emb)
            
            updated += 1
            print(f"  Successfully updated embeddings for image {img.id}")
            
        except Exception as e:
            print(f"  Failed for Image ID {img.id}: {e}")
            failed += 1
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                
    db.commit()
    db.close()
    print(f"\nRegeneration complete. Updated: {updated}, Failed: {failed}")

if __name__ == "__main__":
    regenerate_all_embeddings()
