from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import uuid
import hashlib
from datetime import datetime
from ..database import get_db
from ..models import MissingPerson, User, Image, MissingStatus, Notification, MatchReport
from ..schemas import MissingPersonCreate, MissingPersonResponse, ImageResponse, CaseStats, MissingPersonUpdate, MatchReportResponse
from ..auth import get_current_user, get_current_active_admin
from ..ai_engine import get_embedding
from ..embedding_engine import generate_normalized_embedding
import json
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase_client: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(
    prefix="/cases",
    tags=["cases"]
)

@router.get("/stats", response_model=CaseStats)
def get_case_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(MissingPerson)
    
    # Apply role-based visibility
    if current_user.role != "admin":
        query = query.filter(MissingPerson.reporter_id == current_user.id)
        
    cases = query.all()
    total = len(cases)
    missing = sum(1 for c in cases if c.status == "missing")
    found = sum(1 for c in cases if c.status == "found")
    
    gender_dist = {"Male": 0, "Female": 0, "Other": 0}
    age_groups = {"0-5": 0, "6-12": 0, "13-18": 0, "19+": 0}
    
    MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_counts = {m: 0 for m in MONTHS}

    for c in cases:
        # Gender Distribution
        if c.gender:
            g = c.gender.capitalize()
            if g in gender_dist:
                gender_dist[g] += 1
            else:
                gender_dist["Other"] += 1
                
        # Age Groups
        if c.age is not None:
            if c.age <= 5:
                age_groups["0-5"] += 1
            elif c.age <= 12:
                age_groups["6-12"] += 1
            elif c.age <= 18:
                age_groups["13-18"] += 1
            else:
                age_groups["19+"] += 1
                
        # Monthly Trends
        if c.created_at:
            month_idx = c.created_at.month - 1
            if 0 <= month_idx < 12:
                monthly_counts[MONTHS[month_idx]] += 1

    monthly_cases = [{"month": m, "count": monthly_counts[m]} for m in MONTHS]

    return {
        "total_cases": total,
        "missing_count": missing,
        "found_count": found,
        "gender_distribution": gender_dist,
        "age_groups": age_groups,
        "monthly_cases": monthly_cases
    }
UPLOAD_DIR = "uploads"

@router.post("/", response_model=MissingPersonResponse)
def create_missing_person(
    full_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    last_seen_location: str = Form(...),
    parent_contact_number: str = Form(...),
    station_name: str = Form(...),
    station_address: str = Form(...),
    station_contact_number: str = Form(...),
    description: Optional[str] = Form(None),
    status: str = Form("missing"), # default
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Admin and Sub-admin can create cases
    if current_user.role not in ["admin", "sub_admin"]:
        raise HTTPException(status_code=403, detail="Public users cannot create cases.")

    # Validation rules
    if not parent_contact_number.isdigit() or not (10 <= len(parent_contact_number) <= 15):
        raise HTTPException(status_code=400, detail="Parent contact number must be numeric and 10-15 digits.")
    if not station_contact_number.isdigit() or not (10 <= len(station_contact_number) <= 15):
        raise HTTPException(status_code=400, detail="Station contact number must be numeric and 10-15 digits.")

    new_case = MissingPerson(
        full_name=full_name,
        age=age,
        gender=gender,
        state=state,
        district=district,
        last_seen_location=last_seen_location,
        parent_contact_number=parent_contact_number,
        contact_phone=parent_contact_number, # mapping for backward compatibility
        station_name=station_name,
        station_address=station_address,
        station_contact_number=station_contact_number,
        officer_name=current_user.username,
        description=description,
        status=status,
        reporter_id=current_user.id
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    # Notify admins if created by sub_admin
    if current_user.role == "sub_admin":
        notification = Notification(
            type="new_case",
            message=f"Sub-admin {current_user.username} registered a new case: {full_name}",
            case_id=new_case.id,
            recipient_id=None  # None means for all admins
        )
        db.add(notification)
        db.commit()

    return new_case

@router.post("/{case_id}/images", response_model=List[ImageResponse])
async def upload_case_images(
    case_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Any user can upload? Or only reporter/admin? Let's say reporter or admin.
):
    case = db.query(MissingPerson).filter(MissingPerson.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.role != "admin" and case.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this case")

    # Enforce minimum 3 photos
    if len(files) < 3:
        raise HTTPException(status_code=400, detail="Please provide at least 3 distinct photos of the child to ensure accurate AI matching.")

    uploaded_images = []

    for file in files:
        # Save file
        file_extension = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # File is closed here so get_embedding can read it reliably

        abs_path = os.path.abspath(file_path)
        content_hash = hashlib.sha256(open(abs_path, "rb").read()).hexdigest()

        try:
            # Step 1: Standardized detection and embedding using RetinaFace
            # We no longer align externally. The engine handles it via DeepFace.represent(align=True)
            embedding_list = generate_normalized_embedding(abs_path)
            embedding_json = json.dumps(embedding_list)
            
        except ValueError as ve:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract a clear face from {file.filename}. Please upload photos with a visible frontal face. Error: {str(ve)}"
            )
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Error processing image {file.filename}: {str(e)}")

        # Upload to Supabase Storage
        public_url = None
        if supabase_client:
            try:
                with open(abs_path, 'rb') as f:
                    res = supabase_client.storage.from_("missing-persons-images").upload(
                        path=filename,
                        file=f,
                        file_options={"content-type": file.content_type}
                    )
                
                # Get public URL
                public_url = supabase_client.storage.from_("missing-persons-images").get_public_url(filename)
            except Exception as e:
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=500, detail=f"Error uploading {file.filename} to Supabase: {str(e)}")
            
            # We can remove the local file since it's uploaded
            if os.path.exists(file_path):
                os.remove(file_path)
                
            file_path_to_save = public_url # Save the public URL
        else:
            # Fallback to local storage if Supabase is not configured
            file_path_to_save = file_path

        # Save to DB (with content_hash so same photo always matches in search)
        new_image = Image(
            person_id=case_id,
            file_path=file_path_to_save,
            original_filename=file.filename,
            embedding_json=embedding_json,
            embedding_vector=embedding_list,
            content_hash=content_hash,
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        uploaded_images.append(new_image)
        
    return uploaded_images

@router.get("/", response_model=List[MissingPersonResponse])
def read_cases(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(MissingPerson)
    
    # Apply role-based visibility
    if current_user.role != "admin":
        query = query.filter(MissingPerson.reporter_id == current_user.id)
    
    if search:
        # Case-insensitive search on full_name
        query = query.filter(MissingPerson.full_name.ilike(f"%{search}%"))
    
    if status and status.lower() != "all":
        query = query.filter(MissingPerson.status == status.lower())
        
    cases = query.order_by(MissingPerson.created_at.desc()).offset(skip).limit(limit).all()
    return cases

@router.get("/{case_id}", response_model=MissingPersonResponse)
def read_case(
    case_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(MissingPerson).filter(MissingPerson.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if current_user.role not in ["admin", "sub_admin"]:
        raise HTTPException(status_code=403, detail="Public users cannot view full case details.")
        
    if current_user.role == "sub_admin" and case.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this case.")
        
    return case

@router.put("/{case_id}", response_model=MissingPersonResponse)
def update_case(
    case_id: int,
    case_update: MissingPersonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(MissingPerson).filter(MissingPerson.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.role != "admin" and case.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this case")

    update_data = case_update.model_dump(exclude_unset=True)
    
    # Sync is_resolved flag if status was manually changed back to missing
    if "status" in update_data and update_data["status"] == "missing":
        case.is_resolved = False
        case.resolved_at = None
        case.resolved_by = None
    elif "status" in update_data and update_data["status"] == "found":
        case.is_resolved = True
        case.resolved_at = case.resolved_at or datetime.utcnow()
        case.resolved_by = case.resolved_by or current_user.id

    for key, value in update_data.items():
        setattr(case, key, value)
    
    db.commit()
    db.refresh(case)
    return case

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(MissingPerson).filter(MissingPerson.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.role != "admin" and case.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this case")

    # Delete physical files
    for image in case.images:
        try:
            if image.file_path:
                if image.file_path.startswith("http"):
                    # It's a Supabase URL, extract filename and delete from bucket
                    if supabase_client:
                        filename = image.file_path.split("/")[-1]
                        # Remove query params if any
                        filename = filename.split("?")[0]
                        supabase_client.storage.from_("missing-persons-images").remove([filename])
                elif os.path.exists(image.file_path):
                    # Local file path fallback
                    os.remove(image.file_path)
        except Exception as e:
            print(f"Error deleting file {image.file_path}: {e}")

    try:
        # Delete associated notifications and match reports first to prevent foreign key constraint failures
        db.query(Notification).filter(Notification.case_id == case.id).delete()
        db.query(MatchReport).filter(MatchReport.child_id == case.id).delete()
        
        db.delete(case)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error deleting case: {str(e)}")
        
    return None
@router.post("/{case_id}/resolve", response_model=MissingPersonResponse)
def resolve_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(MissingPerson).filter(MissingPerson.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.role not in ["admin", "sub_admin"]:
        raise HTTPException(status_code=403, detail="Public users cannot resolve cases.")
        
    if current_user.role == "sub_admin" and case.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to resolve this case.")

    case.status = "found"
    case.is_resolved = True
    case.resolved_at = datetime.utcnow()
    case.resolved_by = current_user.id
    
    db.commit()
    db.refresh(case)
    
    # Create notification for owner if admin marked it
    if current_user.id != case.reporter_id:
        db.add(Notification(
            type="case_update",
            message=f"Status update: '{case.full_name}' has been marked as RESOLVED.",
            case_id=case.id,
            recipient_id=case.reporter_id
        ))
        db.commit()

    return case

@router.get("/{case_id}/matches", response_model=List[MatchReportResponse])
def get_case_matches(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = db.query(MissingPerson).filter(MissingPerson.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    # Check authorization (Admin or Reporter)
    if current_user.role != "admin" and case.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view matches for this case")
        
    return db.query(MatchReport).filter(MatchReport.child_id == case_id).all()

@router.post("/matches/{match_id}/review")
def review_match(
    match_id: int,
    status: str = Form(...), # verified, rejected
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if status not in ["verified", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Use 'verified' or 'rejected'.")
        
    report = db.query(MatchReport).filter(MatchReport.id == match_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Match report not found")
        
    case = db.query(MissingPerson).filter(MissingPerson.id == report.child_id).first()
    
    # Check authorization
    if current_user.role != "admin" and case.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to review this match")
        
    report.status = status
    
    if status == "verified":
        # If verified, trigger resolution logic
        case.status = "found"
        case.is_resolved = True
        case.resolved_at = datetime.utcnow()
        case.resolved_by = current_user.id
        
        # Create notification for owner if admin marked it
        if current_user.id != case.reporter_id:
            db.add(Notification(
                type="case_update",
                message=f"Official verification: '{case.full_name}' has been verified and RESOLVED based on an AI match.",
                case_id=case.id,
                recipient_id=case.reporter_id
            ))
            
    db.commit()
    return {"message": f"Match {status} successfully", "case_status": case.status}
