import requests

BASE_URL = "http://localhost:8000"

def test_stats():
    print("Testing GET /cases/stats...")
    try:
        response = requests.get(f"{BASE_URL}/cases/stats")
        if response.status_code == 200:
            print("Success: ", response.json())
        else:
            print(f"Failed: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_cases_list():
    print("\nTesting GET /cases/ (checking for images)...")
    try:
        response = requests.get(f"{BASE_URL}/cases/")
        if response.status_code == 200:
            cases = response.json()
            print(f"Found {len(cases)} cases.")
            for c in cases[:2]: # Show first 2
                print(f"Case: {c['full_name']}, Images: {len(c.get('images', []))}")
                if c.get('images'):
                    print(f"  First image path: {c['images'][0]['file_path']}")
        else:
            print(f"Failed: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stats()
    test_cases_list()
