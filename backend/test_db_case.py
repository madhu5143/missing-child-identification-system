import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import MissingPerson, User, Image, MatchReport
from app.embedding_engine import generate_normalized_embedding
from app.alignment_engine import align_face
import json
import uuid
import shutil
import hashlib

def create_test_case():
    db = SessionLocal()
    try:
        # Get admin user
        admin = db.query(User).filter_by(role='admin').first()
        if not admin:
            print("No admin user found")
            return

        # Create case
        case = MissingPerson(
            full_name="Test Direct Case",
            age=7,
            gender="Male",
            state="AP",
            district="Test District",
            last_seen_location="Park",
            parent_contact_number="1234567890",
            contact_phone="1234567890",
            station_name="Test PS",
            station_address="Test Address",
            station_contact_number="0987654321",
            officer_name="Admin",
            status="missing",
            reporter_id=admin.id
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        print(f"Created case ID: {case.id}")

        # Process and upload images
        images = ['../test_images/person_a.jpg', '../test_images/person_b.jpg', '../test_images/person_a.jpg']
        
        for file_path in images:
            abs_path = os.path.abspath(file_path)
            content_hash = hashlib.sha256(open(abs_path, "rb").read()).hexdigest()
            
            try:
                aligned_path = align_face(abs_path)
                embedding_list = generate_normalized_embedding(aligned_path)
                embedding_json = json.dumps(embedding_list)
                
                if aligned_path != abs_path and os.path.exists(aligned_path):
                    os.remove(aligned_path)
                    
                # We'll just save it to local for now
                dest_path = f"uploads/{uuid.uuid4()}.jpg"
                if not os.path.exists("uploads"):
                    os.makedirs("uploads")
                shutil.copyfile(abs_path, dest_path)
                
                db_image = Image(
                    person_id=case.id,
                    file_path=os.path.abspath(dest_path),
                    original_filename=os.path.basename(file_path),
                    embedding_json=embedding_json,
                    embedding_vector=embedding_list,
                    content_hash=content_hash
                )
                db.add(db_image)
                print(f"Added image {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                
        db.commit()
        print("Test case creation complete!")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_case()
