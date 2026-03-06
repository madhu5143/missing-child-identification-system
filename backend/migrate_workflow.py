import os
import sys

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine

def migrate():
    print("Starting database migration...")
    
    with engine.begin() as conn:
        # Check if columns exist first by trying to alter table, or just catching exceptions
        # PostgreSQL syntax:
        try:
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN parent_contact_number VARCHAR;"))
            print("Added parent_contact_number")
        except Exception as e:
            print(f"parent_contact_number might exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN station_name VARCHAR;"))
            print("Added station_name")
        except Exception as e:
            print(f"station_name might exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN station_address VARCHAR;"))
            print("Added station_address")
        except Exception as e:
            print(f"station_address might exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN station_contact_number VARCHAR;"))
            print("Added station_contact_number")
        except Exception as e:
            print(f"station_contact_number might exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN officer_name VARCHAR;"))
            print("Added officer_name")
        except Exception as e:
            print(f"officer_name might exist: {e}")
            
        try:
            # We'll use BOOLEAN since postgres supports it natively for integer mappings
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN is_resolved BOOLEAN DEFAULT FALSE;"))
            print("Added is_resolved")
        except Exception as e:
            print(f"is_resolved might exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN resolved_at TIMESTAMP;"))
            print("Added resolved_at")
        except Exception as e:
            print(f"resolved_at might exist: {e}")
            
        try:
            conn.execute(text("ALTER TABLE missing_persons ADD COLUMN resolved_by INTEGER;"))
            # Optionally add a foreign key constraint
            conn.execute(text("ALTER TABLE missing_persons ADD CONSTRAINT fk_missing_persons_resolved_by FOREIGN KEY (resolved_by) REFERENCES users (id);"))
            print("Added resolved_by")
        except Exception as e:
            print(f"resolved_by might exist: {e}")

    print("Migration finished!")

if __name__ == "__main__":
    migrate()
