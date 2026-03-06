import urllib.request
import os
import sys
import shutil

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

def download_file(url, dest_path):
    print(f"Downloading {url} to {dest_path}...")
    try:
        # User-Agent is often required
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(dest_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
        print(f"Success: {dest_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def setup_test_data():
    # 1. Create test_images dir
    if not os.path.exists("test_images"):
        os.makedirs("test_images")

    # 2. Download reliable test images (DeepFace examples)
    # img1 and img2 are usually the same person or used for testing. 
    # Let's download img1 and img2.
    img_base = "https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset"
    download_file(f"{img_base}/img1.jpg", "test_images/person_a.jpg")
    download_file(f"{img_base}/img2.jpg", "test_images/person_b.jpg") 
    # img2 is different? Let's assume so. If same, we test match.

    # 3. Manually download ArcFace weights
    home = os.path.expanduser("~")
    weights_dir = os.path.join(home, ".deepface", "weights")
    if not os.path.exists(weights_dir):
        os.makedirs(weights_dir)
    
    weights_file = os.path.join(weights_dir, "arcface_weights.h5")
    if not os.path.exists(weights_file):
        print("ArcFace weights not found. Downloading manually...")
        weights_url = "https://github.com/serengil/deepface_models/releases/download/v1.0/arcface_weights.h5"
        download_file(weights_url, weights_file)
    else:
        print(f"Weights already exist at {weights_file}")

    # 4. Verify Import
    print("Verifying DeepFace import...")
    try:
        from deepface import DeepFace
        # Build model to verify load (should be silent/fast if weights exist)
        DeepFace.build_model("ArcFace")
        print("DeepFace ArcFace model loaded successfully!")
    except Exception as e:
        print(f"Error loading DeepFace: {e}")

if __name__ == "__main__":
    setup_test_data()
