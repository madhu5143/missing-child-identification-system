"""
Standalone script to fix the login issue for 'madhu'.
Uses the same DB path logic as app/database.py and same hashing as app/auth.py.
"""
import os
import sqlite3
from passlib.context import CryptContext

# Replicate the DB path logic from app/database.py
# database.py is at: backend/app/database.py
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  -> backend/
# PROJECT_ROOT = os.path.dirname(BASE_DIR)  -> missing_child_id_system/
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)               # missing_child_id_system/
DB_PATH = os.path.join(PROJECT_ROOT, "missing_child.db")

print(f"Using DB at: {DB_PATH}")
print(f"DB exists: {os.path.exists(DB_PATH)}")

# Same hashing scheme as app/auth.py
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def fix_user(username, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id, username, hashed_password, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        print(f"Found user: id={row[0]}, username={row[1]}, role={row[3]}")
        print(f"Current hash: {row[2][:40]}...")

        # Reset password
        new_hash = pwd_context.hash(new_password)
        cursor.execute("UPDATE users SET hashed_password = ? WHERE username = ?", (new_hash, username))
        conn.commit()
        print(f"Password reset to '{new_password}' successfully!")

        # Verify it works
        cursor.execute("SELECT hashed_password FROM users WHERE username = ?", (username,))
        stored = cursor.fetchone()[0]
        ok = pwd_context.verify(new_password, stored)
        print(f"Verification check: {'PASS ✓' if ok else 'FAIL ✗'}")
    else:
        print(f"User '{username}' NOT FOUND in database.")
        print("Listing all users:")
        cursor.execute("SELECT id, username, role FROM users")
        for r in cursor.fetchall():
            print(f"  id={r[0]}, username={r[1]}, role={r[2]}")

    conn.close()

if __name__ == "__main__":
    fix_user("madhu", "madhu123")
