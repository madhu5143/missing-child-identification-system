from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

# Default local PostgreSQL connection (can be overridden by environment variable)
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/missing_child_db"
)

# Render/Heroku compatibility (some providers use postgres:// instead of postgresql://)
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"DATABASE: Using DB at {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Migration helper: Automatically add embedding_json column if it's missing
def run_migrations():
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            # Check if column exists
            conn.execute(text("SELECT embedding_json FROM images LIMIT 1"))
        except Exception:
            print("DATABASE: Column 'embedding_json' missing. Attempting to add it...")
            try:
                # Add the column
                conn.execute(text("ALTER TABLE images ADD COLUMN embedding_json TEXT"))
                conn.commit()
                print("DATABASE: Successfully added 'embedding_json' column.")
            except Exception as e:
                print(f"DATABASE: Migration failed: {e}")
        try:
            conn.execute(text("SELECT content_hash FROM images LIMIT 1"))
        except Exception:
            print("DATABASE: Column 'content_hash' missing. Adding it...")
            try:
                conn.execute(text("ALTER TABLE images ADD COLUMN content_hash VARCHAR(64)"))
                conn.commit()
                print("DATABASE: Added 'content_hash' column.")
            except Exception as e:
                print(f"DATABASE: content_hash migration failed: {e}")

run_migrations()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
