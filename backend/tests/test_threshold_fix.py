"""
Simple test to verify the threshold parameter fix in ai_engine.py
This test ensures that find_matches() now respects the threshold parameter.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai_engine import find_matches
import numpy as np

def test_threshold_parameter():
    """Test that find_matches respects the threshold parameter"""
    
    # Create a query embedding (normalized)
    query_emb = [1.0, 0.0, 0.0, 0.0]
    
    # Create database embeddings with known similarities
    # Perfect match (similarity = 1.0)
    perfect_match = [1.0, 0.0, 0.0, 0.0]
    
    # Good match (similarity ≈ 0.7)
    good_match = [0.7, 0.71, 0.0, 0.0]
    
    # Moderate match (similarity ≈ 0.5)
    moderate_match = [0.5, 0.866, 0.0, 0.0]
    
    # Poor match (similarity ≈ 0.3)
    poor_match = [0.3, 0.95, 0.0, 0.0]
    
    db_embeddings = [
        (1, perfect_match),
        (2, good_match),
        (3, moderate_match),
        (4, poor_match)
    ]
    
    print("=" * 60)
    print("Testing Threshold Parameter Fix")
    print("=" * 60)
    
    # Test 1: Threshold 0.3 (should match all except maybe the poorest)
    print("\n[TEST 1] Threshold = 0.3 (Liberal)")
    matches = find_matches(query_emb, db_embeddings, threshold=0.3)
    print(f"  Expected: 3-4 matches")
    print(f"  Actual: {len(matches)} matches")
    for person_id, score in matches:
        print(f"    Person {person_id}: {score:.3f}")
    
    # Test 2: Threshold 0.5 (should match perfect and good)
    print("\n[TEST 2] Threshold = 0.5 (Moderate)")
    matches = find_matches(query_emb, db_embeddings, threshold=0.5)
    print(f"  Expected: 2-3 matches")
    print(f"  Actual: {len(matches)} matches")
    for person_id, score in matches:
        print(f"    Person {person_id}: {score:.3f}")
    
    # Test 3: Threshold 0.7 (should match only perfect and good)
    print("\n[TEST 3] Threshold = 0.7 (Strict)")
    matches = find_matches(query_emb, db_embeddings, threshold=0.7)
    print(f"  Expected: 1-2 matches")
    print(f"  Actual: {len(matches)} matches")
    for person_id, score in matches:
        print(f"    Person {person_id}: {score:.3f}")
    
    # Test 4: Threshold 0.9 (should match only perfect)
    print("\n[TEST 4] Threshold = 0.9 (Very Strict)")
    matches = find_matches(query_emb, db_embeddings, threshold=0.9)
    print(f"  Expected: 1 match")
    print(f"  Actual: {len(matches)} matches")
    for person_id, score in matches:
        print(f"    Person {person_id}: {score:.3f}")
    
    # Verification
    print("\n" + "=" * 60)
    print("VERIFICATION:")
    print("=" * 60)
    
    # Critical test: threshold 0.5 should NOT return the poor match
    matches_05 = find_matches(query_emb, db_embeddings, threshold=0.5)
    poor_match_found = any(person_id == 4 for person_id, _ in matches_05)
    
    if poor_match_found:
        print("[FAIL] Threshold parameter is being IGNORED!")
        print("       (Poor match with ~0.3 similarity found when threshold=0.5)")
        return False
    else:
        print("[PASS] Threshold parameter is working correctly!")
        print("       (Poor match correctly filtered out when threshold=0.5)")
        return True

if __name__ == "__main__":
    success = test_threshold_parameter()
    sys.exit(0 if success else 1)
