import sys
import os
import json

# Add parent dir to path to import app
sys.path.append(os.getcwd())

# Mock models before importing to avoid complex dependencies if needed, 
# but let's try direct import first.
try:
    from backend.app.database import SessionLocal
    from backend.app.models import Image, MissingPerson
except ImportError:
    print("Direct import failed, attempting relative adjustment")
    # Add backend/app to path
    sys.path.append(os.path.join(os.getcwd(), "backend", "app"))
    from database import SessionLocal
    from models import Image, MissingPerson

def check_db():
    db = SessionLocal()
    try:
        persons = db.query(MissingPerson).all()
        print(f"--- DB STATUS ---")
        print(f"Total Cases: {len(persons)}")
        for p in persons:
            print(f"ID: {p.id}, Name: {p.full_name}, Status: {p.status}")
        
        images = db.query(Image).all()
        print(f"\nTotal Images: {len(images)}")
        for img in images:
            has_embedding = img.embedding_json is not None
            emb_len = 0
            if has_embedding:
                try:
                    emb = json.loads(img.embedding_json)
                    emb_len = len(emb)
                except:
                    emb_len = "ERROR"
            
            print(f"Img ID: {img.id}, Person ID: {img.person_id}, Has Emb: {has_embedding}, Size: {emb_len}, Path: {img.file_path}")
            
    except Exception as e:
        print(f"Error checking DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
