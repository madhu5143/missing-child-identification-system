from fastapi.testclient import TestClient
from app.main import app
import traceback

client = TestClient(app)

try:
    with open('../test_images/person_b.jpg', 'rb') as f:
        # Simulate exactly what the frontend does
        response = client.post('/search/', files={'file': ('person_b.jpg', f, 'image/jpeg')})
    
    print("STATUS:", response.status_code)
    print("JSON:", response.json())
except Exception as e:
    print("CRASH IN TESTCLIENT:")
    traceback.print_exc()
