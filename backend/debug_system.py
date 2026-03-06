import httpx
import os

BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGE = r"c:\Users\MadhuSudhan\.gemini\antigravity\scratch\missing_child_id_system\test_images\person_a.jpg"

TIMEOUT = 60.0 # Increase timeout for AI processing

def test_flow():
    with httpx.Client() as client:
        # 1. Login
        print("Logging in...")
        resp = client.post(f"{BASE_URL}/auth/token", data={"username": "admin", "password": "admin123"}, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")

        # 2. Create Case
        print("Creating case...")
        case_data = {
            "full_name": "Test Child",
            "age": 10,
            "gender": "Male",
            "last_seen_location": "Test Park",
            "contact_phone": "1234567890",
            "description": "Test description",
            "status": "missing"
        }
        # Note: backend/app/routers/cases.py uses Form(...) for these fields
        resp = client.post(f"{BASE_URL}/cases/", data=case_data, headers=headers, timeout=TIMEOUT)
        if resp.status_code != 200:
            print(f"Create case failed: {resp.text}")
            return
        
        case_id = resp.json()["id"]
        print(f"Case created with ID: {case_id}")

        # 3. Upload Image
        print(f"Uploading image for case {case_id}...")
        with open(TEST_IMAGE, "rb") as f:
            files = {"file": ("person_a.jpg", f, "image/jpeg")}
            resp = client.post(f"{BASE_URL}/cases/{case_id}/images", files=files, headers=headers, timeout=TIMEOUT)
        
        if resp.status_code != 200:
            print(f"Upload image failed: {resp.text}")
            return
        
        print("Image uploaded successfully.")

        # 4. Search
        print("Performing search...")
        with open(TEST_IMAGE, "rb") as f:
            files = {"file": ("person_a.jpg", f, "image/jpeg")}
            resp = client.post(f"{BASE_URL}/search/", files=files, headers=headers, timeout=TIMEOUT)
        
        if resp.status_code != 200:
            print(f"Search failed: {resp.text}")
            return
        
        results = resp.json()
        print(f"Search results: {len(results)} matches found.")
        for res in results:
            print(f"- {res['full_name']} (Similarity: {res['similarity_score']:.4f}, Path: {res['image_path']})")

if __name__ == "__main__":
    test_flow()
