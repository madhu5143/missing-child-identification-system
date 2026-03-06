import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_login():
    try:
        with httpx.Client() as client:
            print(f"Testing login at {BASE_URL}/auth/token...")
            resp = client.post(
                f"{BASE_URL}/auth/token", 
                data={"username": "admin", "password": "admin123"},
                timeout=10.0
            )
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
