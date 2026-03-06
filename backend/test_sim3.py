import os, sys, json
sys.path.append('.')
from app.ai_engine import get_embedding, compute_similarity

dir_path = '../test_images'
if not os.path.exists(dir_path):
    print(f'No test_images dir at {dir_path}')
    sys.exit()

images = [f for f in os.listdir(dir_path) if f.endswith('.jpg')][:4]
print(f"Testing images: {images}")

embeddings = {}
for img in images:
    path = os.path.join(dir_path, img)
    try:
        embeddings[img] = get_embedding(path)
        print(f'Generated embedding for {img}')
    except Exception as e:
        print(f'Failed on {img}: {e}')

for i in range(len(images)):
    for j in range(i+1, len(images)):
        img1 = images[i]
        img2 = images[j]
        if img1 in embeddings and img2 in embeddings:
            sim = compute_similarity(embeddings[img1], embeddings[img2])
            # Reverse map
            raw_sim = 0.32 + ((sim - 0.5) / 0.5) * (1.0 - 0.32) if sim >= 0.5 else '< 0.32'
            print(f"Comparison: {img1} vs {img2} -> Mapped Score: {sim:.3f}, Raw Cosine Sim: {raw_sim}")
