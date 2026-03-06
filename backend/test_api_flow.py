import requests
import os
import json

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("--- Starting API Integration Test ---")

    # 1. Register / Login Admin
    # Note: backend/main.py creates a default admin: admin / admin123 on startup if not exists
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("Logging in...")
    # The current auth.py might use form-data for login (standard for OAuth2 in FastAPI)
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        response.raise_for_status()
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Create a Missing Person Case
    case_data = {
        "full_name": "Barack Obama",
        "age": 60,
        "gender": "Male",
        "last_seen_location": "Washington D.C.",
        "contact_phone": "202-456-1111",
        "description": "Test entry for AI verification",
        "status": "missing"
    }
    
    print("Creating case...")
    try:
        case_res = requests.post(f"{BASE_URL}/cases/", data=case_data, headers=headers)
        case_res.raise_for_status()
        case_id = case_res.json()["id"]
        print(f"Case created with ID: {case_id}")
    except Exception as e:
        print(f"Case creation failed: {e}")
        return

    # 3. Upload Image for Case (Person A)
    img_a_path = os.path.join("test_images", "person_a.jpg")
    print(f"Uploading image {img_a_path}...")
    try:
        with open(img_a_path, "rb") as f:
            files = {"file": (os.path.basename(img_a_path), f, "image/jpeg")}
            upload_res = requests.post(f"{BASE_URL}/cases/{case_id}/images", files=files, headers=headers)
            upload_res.raise_for_status()
            print("Image uploaded and embedding generated.")
    except Exception as e:
        print(f"Image upload failed: {e}")
        # Note: This might fail if DeepFace initialization takes too long (timeout)
        return

    # 4. Search with same image (Should be 100% or very high)
    print("Searching with same image (Positive Match)...")
    try:
        with open(img_a_path, "rb") as f:
            files = {"file": (os.path.basename(img_a_path), f, "image/jpeg")}
            search_res = requests.post(f"{BASE_URL}/search/", files=files)
            search_res.raise_for_status()
            results = search_res.json()
            print(f"Found {len(results)} matches.")
            for r in results:
                print(f"- {r['full_name']}: Score {r['similarity_score']:.4f}")
    except Exception as e:
        print(f"Search failed: {e}")

    # 5. Search with different image (Person B - Michelle Obama)
    img_b_path = os.path.join("test_images", "person_b.jpg")
    print(f"Searching with different image {img_b_path} (Negative Match)...")
    try:
        with open(img_b_path, "rb") as f:
            files = {"file": (os.path.basename(img_b_path), f, "image/jpeg")}
            search_res = requests.post(f"{BASE_URL}/search/", files=files)
            search_res.raise_for_status()
            results = search_res.json()
            print(f"Found {len(results)} matches.")
            for r in results:
                # If similarity > 0.4 it might appear, but Obama vs Michelle should be low.
                print(f"- {r['full_name']}: Score {r['similarity_score']:.4f}")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    test_full_flow()
