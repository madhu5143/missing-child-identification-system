import requests
import json

BASE_URL = "http://localhost:8000"

def test_match_review():
    # 1. Login
    print("Logging in...")
    login_res = requests.post(f"{BASE_URL}/auth/token", data={"username": "admin", "password": "admin123"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.text}")
        return
    
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Cases
    print("Fetching cases...")
    cases_res = requests.get(f"{BASE_URL}/cases/", headers=headers)
    cases = cases_res.json()
    if not cases:
        print("No cases found to test.")
        return
    
    case_id = cases[0]["id"]
    print(f"Testing with Case ID: {case_id}")
    
    # 3. Get Matches for Case
    print(f"Fetching matches for Case {case_id}...")
    matches_res = requests.get(f"{BASE_URL}/cases/{case_id}/matches", headers=headers)
    matches = matches_res.json()
    print(f"Found {len(matches)} matches.")
    
    if matches:
        match_id = matches[0]["id"]
        # 4. Review Match (Reject)
        print(f"Rejecting Match {match_id}...")
        rej_res = requests.post(f"{BASE_URL}/cases/matches/{match_id}/review", data={"status": "rejected"}, headers=headers)
        print(f"Reject Result: {rej_res.status_code} - {rej_res.json()}")
        
        # 5. Review Match (Verify) - This will resolve case
        print(f"Verifying Match {match_id}...")
        ver_res = requests.post(f"{BASE_URL}/cases/matches/{match_id}/review", data={"status": "verified"}, headers=headers)
        print(f"Verify Result: {ver_res.status_code} - {ver_res.json()}")
        
        # 6. Verify Case Status
        case_check = requests.get(f"{BASE_URL}/cases/{case_id}", headers=headers)
        print(f"Updated Case Status: {case_check.json()['status']}")
    else:
        print("No matches to review. Try running a search first to generate matches.")

if __name__ == "__main__":
    test_match_review()
