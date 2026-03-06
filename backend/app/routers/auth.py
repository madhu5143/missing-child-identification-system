from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List
from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserCreate, UserResponse, Token, OTPRequest, OTPVerify, UserUpdate, PasswordChange
from ..auth import authenticate_user, create_access_token, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_admin, get_current_user
import random

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Ensure role is string (ORM may return enum)
    role_str = getattr(user.role, "value", user.role) if user.role else "user"
    access_token = create_access_token(
        data={"sub": user.username, "role": role_str}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": role_str}

@router.post("/create-subadmin", response_model=UserResponse)
def create_subadmin(user: UserCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_active_admin)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_mobile = db.query(User).filter(User.mobile_number == user.mobile_number).first()
    if db_mobile and user.mobile_number:
        raise HTTPException(status_code=400, detail="Mobile number already registered")
        
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username, 
        email=user.email, 
        mobile_number=user.mobile_number,
        hashed_password=hashed_password, 
        role="sub_admin"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_update.email is not None:
        # Check if email is already used by another user
        existing_email = db.query(User).filter(User.email == user_update.email, User.id != current_user.id).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email
        
    if user_update.mobile_number is not None:
        existing_mobile = db.query(User).filter(User.mobile_number == user_update.mobile_number, User.id != current_user.id).first()
        if existing_mobile:
            raise HTTPException(status_code=400, detail="Mobile number already registered")
        current_user.mobile_number = user_update.mobile_number
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/request-otp")
def request_otp(otp_req: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile_number == otp_req.mobile_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found with this mobile number")
    
    # Generate 6 digit OTP
    otp = str(random.randint(100000, 999999))
    user.reset_otp = otp
    user.reset_otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    # In a real app we would send SMS here. For now we just print it to terminal for emulation.
    print(f"--- OTP for {user.username} ({user.mobile_number}) is: {otp} ---")
    
    return {"message": "OTP generated and sent successfully"}

@router.post("/reset-password")
def reset_password(otp_verify: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile_number == otp_verify.mobile_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.reset_otp or user.reset_otp != otp_verify.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    if user.reset_otp_expiry and user.reset_otp_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    user.hashed_password = get_password_hash(otp_verify.new_password)
    user.reset_otp = None
    user.reset_otp_expiry = None
    db.commit()
    
    return {"message": "Password reset successfully"}
@router.get("/sub-admins", response_model=List[UserResponse])
def get_sub_admins(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    sub_admins = db.query(User).filter(User.role == "sub_admin").all()
    return sub_admins

@router.post("/change-password")
def change_password(pass_change: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(pass_change.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
        
    current_user.hashed_password = get_password_hash(pass_change.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
