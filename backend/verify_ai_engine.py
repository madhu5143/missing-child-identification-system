import os
import sys

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from ai_engine import AIEngine

def test_ai_engine():
    engine = AIEngine()
    
    test_image_dir = os.path.join("..", "test_images")
    image_a = os.path.join(test_image_dir, "person_a.jpg")
    image_b = os.path.join(test_image_dir, "person_b.jpg")
    
    if not os.path.exists(image_a) or not os.path.exists(image_b):
        print("Test images not found. Skipping engine test.")
        return

    print("Testing Embedding Generation for person_a.jpg...")
    try:
        emb_a = engine.get_embedding(image_a)
        print(f"Embedding A (truncated): {emb_a[:5]}... (length: {len(emb_a)})")
    except Exception as e:
        print(f"Failed to get embedding for image A: {e}")
        return

    print("Testing Embedding Generation for person_b.jpg...")
    try:
        emb_b = engine.get_embedding(image_b)
        print(f"Embedding B (truncated): {emb_b[:5]}... (length: {len(emb_b)})")
    except Exception as e:
        print(f"Failed to get embedding for image B: {e}")
        return

    print(f"Similarity Calculation Mode: {'SVM' if engine.svm_matcher else 'Cosine Fallback'}")
    
    print("Testing Similarity Computation...")
    similarity = engine.compute_similarity(emb_a, emb_b)
    print(f"Similarity between A and B: {similarity:.4f}")
    
    print("Testing Self-Similarity (should be ~1.0)...")
    self_sim = engine.compute_similarity(emb_a, emb_a)
    print(f"Similarity between A and A: {self_sim:.4f}")

if __name__ == "__main__":
    test_ai_engine()
