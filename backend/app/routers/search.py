from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import json
import hashlib
from ..database import get_db
from ..models import Image, MissingPerson, Notification
from ..ai_engine import get_embedding, find_matches, compute_similarity
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

UPLOAD_DIR = "uploads"

class MatchResult(BaseModel):
    child_id: Optional[str] = None
    similarity: Optional[float] = None
    confidence_level: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    last_seen_location: Optional[str] = None
    station_name: Optional[str] = None
    station_address: Optional[str] = None
    station_contact_number: Optional[str] = None
    error: Optional[str] = None

@router.post("/", response_model=List[MatchResult])
def search_face(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Save temp file
    file_extension = file.filename.split(".")[-1]
    filename = f"search_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Initialize Supabase if available for query preservation
    from .cases import supabase_client
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    abs_path = os.path.abspath(file_path)

    try:
        # 2. Match Phase (10K-Scale Pipeline)
        try:
            from ..matcher import run_identification_pipeline
            # Initially we don't have the URL
            result = run_identification_pipeline(db, abs_path)
            
            # 3. Preservation & Notification Phase
            if result.get("confidence_level") in ["strong_match", "review_required"]:
                # Upload query image to Supabase for official verification
                query_image_url = "Uploaded_Directly"
                if supabase_client:
                    try:
                        with open(abs_path, 'rb') as f:
                            supabase_client.storage.from_("missing-persons-images").upload(
                                path=f"queries/{filename}",
                                file=f,
                                file_options={"content-type": file.content_type}
                            )
                        query_image_url = supabase_client.storage.from_("missing-persons-images").get_public_url(f"queries/{filename}")
                    except Exception as upload_err:
                        print(f"Query image preservation failed: {upload_err}")

                # Re-run or update MatchReport with the real URL
                # Actually, let's just update the most recent MatchReport for this child
                if query_image_url != "Uploaded_Directly":
                    from ..models import MatchReport
                    report = db.query(MatchReport).filter(
                        MatchReport.child_id == int(result["child_id"])
                    ).order_by(MatchReport.created_at.desc()).first()
                    if report:
                        report.reporter_image_url = query_image_url
                        db.commit()

                child_id = int(result["child_id"])
                person = db.query(MissingPerson).filter(MissingPerson.id == child_id).first()
                if person:
                    # Notify admins
                    db.add(Notification(
                        type="match_found",
                        message=f"A potential match for '{person.full_name}' was found and is awaiting official verification.",
                        case_id=person.id,
                        recipient_id=None
                    ))
                    # DO NOT set person.status = "found" automatically!
                    
                    if person.reporter_id:
                        db.add(Notification(
                            type="match_found",
                            message=f"A match was found for '{person.full_name}'. Official verification is required. Check your dashboard.",
                            case_id=person.id,
                            recipient_id=person.reporter_id
                        ))
                    db.commit()
            
            return [result]

        except Exception as e:
            import traceback
            print("--- SEARCH ROUTER EXCEPTION ---")
            traceback.print_exc()
            print("-------------------------------")
            raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error during search: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)
