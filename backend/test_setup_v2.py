import urllib.request
import os
import sys
import shutil
import ssl

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')

# Bypass SSL verification for legacy environments
ssl._create_default_https_context = ssl._create_unverified_context

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        print(f"Success: {dest_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def setup_test_data():
    if not os.path.exists("test_images"):
        os.makedirs("test_images")

    # Reliable images from Wikipedia
    # Obama (Person A)
    download_file("https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg", "test_images/person_a.jpg")
    # Michelle Obama (Person B)
    download_file("https://upload.wikimedia.org/wikipedia/commons/4/4b/Michelle_Obama_2013_official_portrait.jpg", "test_images/person_b.jpg")

    # Manual weight download
    home = os.path.expanduser("~")
    weights_dir = os.path.join(home, ".deepface", "weights")
    if not os.path.exists(weights_dir):
        os.makedirs(weights_dir)
    
    weights_file = os.path.join(weights_dir, "arcface_weights.h5")
    if not os.path.exists(weights_file) or os.path.getsize(weights_file) < 1000: # check if valid
        print("ArcFace weights missing or invalid. Downloading manually...")
        weights_url = "https://github.com/serengil/deepface_models/releases/download/v1.0/arcface_weights.h5"
        download_file(weights_url, weights_file)
    else:
        print(f"Weights exist at {weights_file}")

    print("Verifying DeepFace import...")
    try:
        # Suppress logging slightly
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
        from deepface import DeepFace
        DeepFace.build_model("ArcFace")
        print("DeepFace ArcFace loaded successfully!")
    except Exception as e:
        # print repr(e) safely
        print(f"Error loading DeepFace: {repr(e)}")

if __name__ == "__main__":
    setup_test_data()
