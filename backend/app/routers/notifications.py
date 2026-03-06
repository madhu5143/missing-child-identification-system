from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Notification, User, UserRole
from ..schemas import NotificationResponse
from ..auth import get_current_user, get_current_active_admin

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "admin":
        return db.query(Notification).order_by(Notification.created_at.desc()).all()
    else:
        # Regular users only see their own notifications or global ones (though we don't have global yet)
        return db.query(Notification).filter(Notification.recipient_id == current_user.id).order_by(Notification.created_at.desc()).all()

@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if current_user.role != "admin" and notif.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to mark this notification as read")
    
    notif.is_read = 1
    db.commit()
    db.refresh(notif)
    return notif
