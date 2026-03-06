import os
import sys

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from database import engine, SessionLocal
from models import User
from auth import get_password_hash

def reset_password(username, new_password):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        print(f"Password for user '{username}' has been reset successfully.")
    else:
        print(f"User '{username}' not found.")
    db.close()

if __name__ == "__main__":
    reset_password("madhu", "madhu123")
