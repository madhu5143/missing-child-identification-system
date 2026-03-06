from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text, LargeBinary, Float, Boolean
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import enum
from datetime import datetime
from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SUB_ADMIN = "sub_admin"
    USER = "user"

class MissingStatus(str, enum.Enum):
    MISSING = "missing"
    FOUND = "found"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.USER)
    reset_otp = Column(String, nullable=True)
    reset_otp_expiry = Column(DateTime, nullable=True)
    
    reports = relationship("MissingPerson", primaryjoin="User.id == MissingPerson.reporter_id", back_populates="reporter")

class MissingPerson(Base):
    __tablename__ = "missing_persons"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    age = Column(Integer)
    gender = Column(String)
    last_seen_date = Column(DateTime, default=datetime.utcnow)
    last_seen_location = Column(String)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    status = Column(String, default=MissingStatus.MISSING)
    description = Column(Text)
    contact_phone = Column(String) # Keeping for backward compatibility if needed, though requirements ask for parent_contact_number
    parent_contact_number = Column(String, nullable=True) # Making nullable first for existing rows
    station_name = Column(String, nullable=True)
    station_address = Column(String, nullable=True)
    station_contact_number = Column(String, nullable=True)
    officer_name = Column(String, nullable=True)
    
    # Resolution Tracking
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    
    # Backref for resolver
    resolver = relationship("User", foreign_keys=[resolved_by])

    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports")
    images = relationship("Image", back_populates="person", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("missing_persons.id"))
    file_path = Column(String)
    original_filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    # Storing embedding as a JSON string or we can use a separate approach. 
    # For SQLite, retrieving all and computing cosine similarity in memory is okay for small scale.
    # We will store the path to a .npy file or similar if vectors are large, 
    # but for simplicity let's stick to file management or just re-compute/cache.
    # Actually, let's add a column for embedding_path to store the numpy file path.
    embedding_json = Column(Text, nullable=True)
    
    # New Vector column for pgvector scaling
    # Import Vector inline or top level (we will add to top level)
    embedding_vector = Column(Vector(512), nullable=True)
    
    content_hash = Column(String(64), nullable=True)

    person = relationship("MissingPerson", back_populates="images")

class MatchReport(Base):
    __tablename__ = "match_reports"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("missing_persons.id"), nullable=True)
    similarity = Column(Integer) # or Float, let's use Float
    reporter_image_url = Column(String)
    status = Column(String, default="pending_review") # pending_review, verified, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("MissingPerson")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String) # e.g. "match_found"
    message = Column(Text)
    case_id = Column(Integer, ForeignKey("missing_persons.id"), nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True) # If null, it's for all admins
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("MissingPerson")
    recipient = relationship("User")
