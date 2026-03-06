import os
import sys
import numpy as np
import joblib
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from ai_engine import AIEngine

def train_svm():
    engine = AIEngine()
    test_image_dir = os.path.join("..", "test_images")
    
    # Check for test images
    images = [f for f in os.listdir(test_image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if len(images) < 2:
        print("Not enough test images to train SVM. Need at least 2.")
        return

    print(f"Found {len(images)} test images. Extracting embeddings...")
    
    embeddings = {}
    for img_name in images:
        img_path = os.path.join(test_image_dir, img_name)
        try:
            emb = engine.get_embedding(img_path)
            embeddings[img_name] = np.array(emb)
            print(f"Extracted embedding for {img_name}")
        except Exception as e:
            print(f"Failed to extract embedding for {img_name}: {e}")

    if len(embeddings) < 2:
        print("Failed to extract enough embeddings for training.")
        return

    # Create training data
    # X will be the absolute difference between embeddings
    # y will be 1 for same person, 0 for different person
    X = []
    y = []

    # Since we have limited data, we'll augment it slightly or use what we have.
    # In a real scenario, we'd have thousands of pairs.
    # For this system, we'll create a baseline SVM.
    
    img_list = list(embeddings.keys())
    
    # 1. Different person pairs (Negative samples)
    for i in range(len(img_list)):
        for j in range(i + 1, len(img_list)):
            diff = np.abs(embeddings[img_list[i]] - embeddings[img_list[j]])
            X.append(diff)
            y.append(0) # Different
            
    # 2. Same person pairs (Positive samples)
    # Since we only have one image per person in test_images, 
    # we'll simulate "same" by adding tiny noise to the embeddings or using the embedding themselves.
    # Realistically, this is a placeholder training.
    for i in range(len(img_list)):
        # Exact same (will have 0 diff)
        diff = np.zeros_like(embeddings[img_list[i]])
        X.append(diff)
        y.append(1) # Same
        
        # Slightly noisy version
        noise = np.random.normal(0, 0.01, embeddings[img_list[i]].shape)
        diff = np.abs(noise)
        X.append(diff)
        y.append(1) # Same

    X = np.array(X)
    y = np.array(y)

    print(f"Training SVM on {len(X)} samples...")
    # Using probability=True so we can get scores
    svm = SVC(kernel='linear', probability=True, random_state=42)
    svm.fit(X, y)

    # Save the model
    models_dir = os.path.join(os.path.dirname(__file__), "app", "models")
    os.makedirs(models_dir, exist_ok=True)
    svm_path = os.path.join(models_dir, "face_matcher_svm.pkl")
    joblib.dump(svm, svm_path)
    
    print(f"SVM model trained and saved to {svm_path}")

if __name__ == "__main__":
    train_svm()
