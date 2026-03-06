import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from app.models import Base

# Load environment variables
load_dotenv()

# Get DB URL
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("Error: DATABASE_URL environment variable is missing!")
    exit(1)

print(f"Connecting to: {db_url}")

# Create engine
try:
    engine = create_engine(db_url)
    print("Engine created successfully.")
except Exception as e:
    print(f"Error creating engine: {e}")
    exit(1)

# Create tables
try:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")
    exit(1)
