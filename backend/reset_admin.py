"""
Reset admin password to admin123. Run from backend folder when login fails:
    cd backend
    python reset_admin.py
"""
import sys
import os

# Run from backend directory; ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def reset_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role="admin",
            )
            db.add(admin)
            print("Admin user created: admin / admin123")
        else:
            admin.hashed_password = get_password_hash("admin123")
            admin.role = "admin"  # ensure string role
            print("Admin password reset: admin / admin123")
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
