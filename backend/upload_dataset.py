import os
import requests
import json
import time

BASE_URL = "http://localhost:8000"
METADATA_FILE = "dummy_dataset/metadata.json"

def login():
    """Login as admin to get the token"""
    print("Logging in as Admin...")
    response = requests.post(f"{BASE_URL}/auth/token", data={
        "username": "admin",
        "password": "adminpassword"
    })
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("❌ Login failed. Ensure backend is running and credentials are 'admin' / 'adminpassword'")
        return None

def register_case(token, person):
    """Register a new missing person case"""
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "full_name": person["name"],
        "age": person["age"],
        "gender": person["gender"],
        "last_seen_location": person["location"],
        "contact_phone": person["phone"],
        "description": f"Test case added from dummy dataset. URL reference: {person['url']}",
        "status": "missing"
    }
    
    response = requests.post(f"{BASE_URL}/cases/", headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print(f"❌ Failed to register {person['name']}: {response.text}")
        return None

def upload_image(token, case_id, filepath, person_name):
    """Upload the physical photo for the case to extract embeddings"""
    headers = {"Authorization": f"Bearer {token}"}
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
        
    with open(filepath, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/cases/{case_id}/images", headers=headers, files=files)
        
    if response.status_code == 200:
        print(f"✅ Successfully registered and extracted face embeddings for: {person_name}")
        return True
    else:
        print(f"❌ Failed to extract face for {person_name}: {response.text}")
        return False

def main():
    if not os.path.exists(METADATA_FILE):
        print(f"❌ Metadata file not found: {METADATA_FILE}. Run download_dataset.py first.")
        return
        
    with open(METADATA_FILE, "r") as f:
        dataset = json.load(f)
        
    token = login()
    if not token: return
    
    print("\n=== Populating Face Database ('Training' the System) ===")
    success_count = 0
    
    for i, person in enumerate(dataset):
        filename = person["name"].replace(" ", "_").lower() + ".jpg"
        filepath = os.path.join("dummy_dataset", filename)
        
        print(f"[{i+1}/{len(dataset)}] Registering {person['name']}...")
        
        case_id = register_case(token, person)
        if case_id:
            success = upload_image(token, case_id, filepath, person["name"])
            if success:
                success_count += 1
                
        time.sleep(0.5) # Slight delay to not overwhelm the server
        
    print(f"\n🎉 Finished populating database. Successfully added {success_count} / {len(dataset)} faces.")
    print("The system is now 'trained' to recognize these individuals in the frontend Search page!")

if __name__ == "__main__":
    main()
