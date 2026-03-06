import os
import requests
import json
import uuid

print("=== Downloading Face Dataset for Testing ===")
os.makedirs("dummy_dataset", exist_ok=True)

# Dataset of 10 distinct, identifiable faces (mostly public domain/CC Wikimedia portraits)
dataset = [
    {"name": "Barack Obama", "age": 62, "gender": "Male", "location": "Washington DC", "phone": "1234567890", "url": "https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg"},
    {"name": "Joe Biden", "age": 81, "gender": "Male", "location": "Washington DC", "phone": "1234567891", "url": "https://upload.wikimedia.org/wikipedia/commons/6/68/Joe_Biden_presidential_portrait.jpg"},
    {"name": "Kamala Harris", "age": 59, "gender": "Female", "location": "Washington DC", "phone": "1234567892", "url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Kamala_Harris_Vice_Presidential_Portrait.jpg"},
    {"name": "Albert Einstein", "age": 76, "gender": "Male", "location": "Princeton", "phone": "1234567893", "url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Albert_Einstein_Head.jpg"},
    {"name": "Marie Curie", "age": 66, "gender": "Female", "location": "Paris", "phone": "1234567894", "url": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Marie_Curie_c._1920s.jpg"},
    {"name": "Nelson Mandela", "age": 95, "gender": "Male", "location": "Johannesburg", "phone": "1234567895", "url": "https://upload.wikimedia.org/wikipedia/commons/0/02/Nelson_Mandela_1994.jpg"},
    {"name": "Malala Yousafzai", "age": 26, "gender": "Female", "location": "London", "phone": "1234567896", "url": "https://upload.wikimedia.org/wikipedia/commons/f/fe/Malala_Yousafzai_2015_%28cropped%29.jpg"},
    {"name": "Elon Musk", "age": 52, "gender": "Male", "location": "Boca Chica", "phone": "1234567897", "url": "https://upload.wikimedia.org/wikipedia/commons/3/34/Elon_Musk_Royal_Society_%28crop2%29.jpg"},
    {"name": "Neil Armstrong", "age": 82, "gender": "Male", "location": "Houston", "phone": "1234567898", "url": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Neil_Armstrong_pose.jpg"},
    {"name": "Jane Goodall", "age": 90, "gender": "Female", "location": "London", "phone": "1234567899", "url": "https://upload.wikimedia.org/wikipedia/commons/2/23/Jane_Goodall_%282015%29.jpg"}
]

print("Downloading images...")
for person in dataset:
    filename = person["name"].replace(" ", "_").lower() + ".jpg"
    filepath = os.path.join("dummy_dataset", filename)
    person["local_path"] = filepath
    
    if not os.path.exists(filepath):
        try:
            r = requests.get(person["url"], headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                print(f"✅ Downloaded {person['name']}")
            else:
                print(f"❌ Failed to download {person['name']} - HTTP {r.status_code}")
        except Exception as e:
            print(f"❌ Error downloading {person['name']}: {e}")
    else:
        print(f"⚡ {person['name']} already exists.")

# Save metadata for easy uploading
with open("dummy_dataset/metadata.json", "w") as f:
    json.dump(dataset, f, indent=4)

print("\nDataset successfully downloaded to the 'dummy_dataset' folder!")
print("You can now use these images to manually register cases in the system.")
print("To automatically upload them to your database to 'train' the Face Recognition DB, run `python upload_dataset.py` (if provided).")
