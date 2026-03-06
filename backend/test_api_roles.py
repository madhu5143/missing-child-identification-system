import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("1. Logging in as Admin")
    res = requests.post(f"{BASE_URL}/auth/token", data={"username": "admin", "password": "admin123"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("2. Creating Sub-Admin")
    # append timestamp to avoid unique constraints if ran multiple times
    ts = str(int(time.time()))
    sub_user = {"username": f"sub_{ts}", "email": f"sub_{ts}@test.com", "mobile_number": f"123456{ts[-4:]}", "password": "subpassword"}
    res = requests.post(f"{BASE_URL}/auth/create-subadmin", json=sub_user, headers=headers)
    assert res.status_code == 200, f"Sub-admin creation failed: {res.text}"
    print("   Sub-admin created successfully.")

    print("3. Logging in as Sub-admin")
    res = requests.post(f"{BASE_URL}/auth/token", data={"username": sub_user['username'], "password": sub_user['password']})
    assert res.status_code == 200, f"Sub-admin login failed: {res.text}"
    sub_token = res.json()["access_token"]
    print("   Sub-admin logged in successfully.")

    print("4. Requesting OTP")
    res = requests.post(f"{BASE_URL}/auth/request-otp", json={"mobile_number": sub_user['mobile_number']})
    assert res.status_code == 200, f"OTP request failed: {res.text}"
    print("   OTP requested successfully (check backend console for the print).")

    # To fully test OTP we would need to read the backend logs or DB, but we can verify the DB record using sqlalchemy directly
    from sqlalchemy import text, create_engine
    engine = create_engine("postgresql://postgres:Madhu%40Naidu@db.wcdafauvjfrfxgcgcuni.supabase.co:5432/postgres")
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT reset_otp FROM users WHERE username='{sub_user['username']}'")).fetchone()
        otp = result[0]
        print(f"   Retrieved OTP from DB: {otp}")

    print("5. Resetting Password")
    res = requests.post(f"{BASE_URL}/auth/reset-password", json={
        "mobile_number": sub_user["mobile_number"],
        "otp": otp,
        "new_password": "newsubpassword"
    })
    assert res.status_code == 200, f"Password reset failed: {res.text}"
    print("   Password reset successfully.")

    print("6. Logging in with new password")
    res = requests.post(f"{BASE_URL}/auth/token", data={"username": sub_user['username'], "password": "newsubpassword"})
    assert res.status_code == 200, f"Sub-admin login with new password failed: {res.text}"
    print("   Sub-admin logged in with new password successfully.")

if __name__ == "__main__":
    run_tests()
    print("ALL TESTS PASSED!")
