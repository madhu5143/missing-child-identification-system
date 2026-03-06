from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import User, UserRole
from .auth import get_password_hash
# We'll import routers later

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Missing Child Identification System", version="1.0.0")

# CORS Setup (Allow Frontend)
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:5174", # Vite alternative port
    "http://localhost:3000",
    "http://[::1]:5173",
    "http://[::1]:5174",
    "http://[::1]:3000",
]

from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.get("/api/")
def read_root():
    return {"message": "Welcome to the Missing Child Identification System API"}

@app.get("/")
async def serve_index():
    # Serve index.html for root URL
    frontend_path = os.path.join(os.getcwd(), "static")
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend not found. Please run build."}

@app.get("/api/status")
def get_system_status():
    """Check if CNN/SVM models are loaded."""
    from .ai_engine import get_engine
    import os
    
    engine = get_engine()
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    detector_path = os.path.join(models_dir, "face_detection_yunet_2023mar.onnx")
    cnn_path = os.path.join(models_dir, "mobilefacenet.onnx")
    svm_path = os.path.join(models_dir, "face_matcher_svm.pkl")
    
    return {
        "face_detector": {
            "loaded": getattr(engine, 'face_detector', None) is not None,
            "model_path": detector_path,
            "exists": os.path.exists(detector_path),
            "type": "YuNet (CNN)" if getattr(engine, 'face_detector', None) else "Haar Cascade (fallback)"
        },
        "face_recognizer": {
            "loaded": getattr(engine, 'face_recognizer', None) is not None,
            "model_path": cnn_path,
            "exists": os.path.exists(cnn_path),
            "type": "CNN (ArcFace/MobileFaceNet)" if getattr(engine, 'face_recognizer', None) else "Deterministic fallback"
        },
        "svm_matcher": {
            "loaded": getattr(engine, 'svm_matcher', None) is not None,
            "model_path": svm_path,
            "exists": os.path.exists(svm_path),
            "type": "SVM" if getattr(engine, 'svm_matcher', None) else "Cosine similarity"
        },
        "recommendation": "Run 'python download_models.py' in backend/ to download CNN models" if not getattr(engine, 'face_recognizer', None) else "All models loaded - using CNN/SVM for face recognition"
    }

# Initial Admin setup (Quick hack for demo purposes)
@app.on_event("startup")
def create_initial_admin():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        # Compare with string so we find admin whether DB stores "admin" or enum
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            hashed_pwd = get_password_hash("admin123")
            new_admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hashed_pwd,
                role="admin",  # store string so auth comparisons always work
            )
            db.add(new_admin)
            db.commit()
            print("Admin user created: admin / admin123")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Admin setup error: {e}")
        db.rollback()
    finally:
        db.close()

from .routers import auth, cases, search, notifications
from fastapi.staticfiles import StaticFiles
import os

# Create uploads directory if not exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(search.router)
app.include_router(notifications.router)

# --- Unified Frontend Support ---
# This allows the backend to serve the frontend as a single application
frontend_path = os.path.join(os.getcwd(), "static")

if os.path.exists(frontend_path):
    # Mount the static directory for and files like JS/CSS/Images
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Catch-all route to serve index.html for React Router (Single Page Application)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If the request matches an existing file in static, though usually /assets/ handles most
        # but for index.html or other root files:
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fallback to index.html for React Router
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    print(f"Warning: Frontend static folder not found at {frontend_path}. Frontend will not be served by backend.")
