import requests

# 1. Login to get token
login_url = "http://localhost:8000/auth/token"
login_data = {
    'username': 'admin@example.com',
    'password': 'password123'
}
response = requests.post(login_url, data=login_data)
token = response.json().get('access_token')
headers = {
    'Authorization': f'Bearer {token}'
}

# 2. Create case
url = "http://localhost:8000/cases/"
data = {
    'full_name': 'Test3',
    'age': 6,
    'gender': 'Female',
    'state': 'AP',
    'district': 'Vizag',
    'last_seen_location': 'Mall',
    'parent_contact_number': '1234567890',
    'station_name': 'Vizag PS',
    'station_address': 'Vizag',
    'station_contact_number': '1234567890'
}

print("Creating case...")
response = requests.post(url, headers=headers, data=data)
print(response.status_code)

case_id = response.json().get('id')
print(f"Created case ID: {case_id}")

# 3. Upload images
url = f"http://localhost:8000/cases/{case_id}/images"
files = [
    ('files', ('person_a.jpg', open('../test_images/person_a.jpg', 'rb'), 'image/jpeg')),
    ('files', ('person_b.jpg', open('../test_images/person_b.jpg', 'rb'), 'image/jpeg')),
    ('files', ('person_a.jpg', open('../test_images/person_a.jpg', 'rb'), 'image/jpeg')),
]

print(f"Uploading images to case {case_id}...")
response = requests.post(url, headers=headers, files=files)
print(response.status_code)
print(response.json())
