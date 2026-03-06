from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    mobile_number: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "user"  # default to user

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    class Config:
        from_attributes = True

# OTP Schemas
class OTPRequest(BaseModel):
    mobile_number: str

class OTPVerify(BaseModel):
    mobile_number: str
    otp: str
    new_password: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# Image Schemas
class ImageResponse(BaseModel):
    id: int
    person_id: int
    file_path: str
    uploaded_at: datetime
    class Config:
        from_attributes = True

# Missing Person Schemas
class MissingPersonBase(BaseModel):
    full_name: str
    age: int
    gender: str
    state: Optional[str] = None  # New field as per requirements, optional for legacy data
    district: Optional[str] = None
    last_seen_location: str
    description: Optional[str] = None
    parent_contact_number: Optional[str] = None
    station_name: Optional[str] = None
    station_address: Optional[str] = None
    station_contact_number: Optional[str] = None
    # contact_phone mapping will just be retained if requested or dropped. For now mapping parent_contact_number to it if needed.

class MissingPersonCreate(MissingPersonBase):
    pass

class MissingPersonUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    last_seen_location: Optional[str] = None
    description: Optional[str] = None
    parent_contact_number: Optional[str] = None
    station_name: Optional[str] = None
    station_address: Optional[str] = None
    station_contact_number: Optional[str] = None
    status: Optional[str] = None

class MissingPersonResponse(MissingPersonBase):
    id: int
    status: str
    officer_name: Optional[str] = None
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    last_seen_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    reporter_id: int
    images: List[ImageResponse] = []
    class Config:
        from_attributes = True

# Stats Schemas
class CaseStats(BaseModel):
    total_cases: int
    missing_count: int
    found_count: int
    gender_distribution: dict
    age_groups: dict
    monthly_cases: list

class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    case_id: Optional[int]
    recipient_id: Optional[int]
    is_read: int
    created_at: datetime
    class Config:
        from_attributes = True

class MatchReportResponse(BaseModel):
    id: int
    child_id: int
    similarity: float
    reporter_image_url: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True
