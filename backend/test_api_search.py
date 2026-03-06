import requests

url = "http://localhost:8000/search/"
files = {
    'file': ('person_b.jpg', open('../test_images/person_b.jpg', 'rb'), 'image/jpeg')
}

print("Searching for child...")
response = requests.post(url, files=files)
print(response.status_code)

try:
    print(response.json())
except:
    print(response.text)
