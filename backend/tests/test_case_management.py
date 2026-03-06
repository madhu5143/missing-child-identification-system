import requests
import os
import time

BASE_URL = "http://localhost:8000"

def get_token(username, password):
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    return response.json()["access_token"]

def test_case_management():
    print("Starting Case Management Tests...")
    
    # 1. Login
    try:
        token = get_token("admin", "admin123")
    except Exception:
        print("Error: Could not login. Make sure server is running and admin user exists.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a test case
    print("Creating test case...")
    case_data = {
        "full_name": "Test Delete Me",
        "age": 10,
        "gender": "Male",
        "last_seen_location": "Test Lab",
        "contact_phone": "1234567890",
        "description": "To be deleted"
    }
    response = requests.post(f"{BASE_URL}/cases/", data=case_data, headers=headers)
    assert response.status_code == 200
    case_id = response.json()["id"]

    # 3. Upload an image
    print("Uploading test image...")
    with open("test_images/person_a.jpg", "rb") as f:
        img_response = requests.post(f"{BASE_URL}/cases/{case_id}/images", files={"file": f}, headers=headers)
    assert img_response.status_code == 200
    file_path = img_response.json()["file_path"]
    
    # Verify file exists
    assert os.path.exists(file_path)

    # 4. Update the case
    print("Updating test case...")
    update_data = {"full_name": "Updated Name", "status": "found"}
    update_response = requests.put(f"{BASE_URL}/cases/{case_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Updated Name"
    assert update_response.json()["status"] == "found"

    # 5. Delete the case
    print("Deleting test case...")
    delete_response = requests.delete(f"{BASE_URL}/cases/{case_id}", headers=headers)
    assert delete_response.status_code == 204

    # 6. Verify Deletion
    # Check DB
    get_response = requests.get(f"{BASE_URL}/cases/{case_id}", headers=headers)
    assert get_response.status_code == 404
    
    # Check File System
    if os.path.exists(file_path):
        print(f"FAILED: File {file_path} still exists after deletion!")
        assert False
    else:
        print("SUCCESS: File deleted from disk.")

    print("\n--- ALL CASE MANAGEMENT TESTS PASSED ---")

if __name__ == "__main__":
    # Ensure test image exists for the test script
    if not os.path.exists("test_images/person_a.jpg"):
        print("Please run backend/test_setup_v2.py first to download test images.")
    else:
        test_case_management()
