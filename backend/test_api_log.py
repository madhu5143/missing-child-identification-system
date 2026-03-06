import sys
import traceback

with open('api_error_log.txt', 'w', encoding='utf-8') as f:
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        with open('../test_images/person_b.jpg', 'rb') as img:
            response = client.post('/search/', files={'file': ('person_b.jpg', img, 'image/jpeg')})
            f.write(f"STATUS: {response.status_code}\n")
            f.write(f"JSON: {response.json()}\n")
    except Exception as e:
        traceback.print_exc(file=f)
