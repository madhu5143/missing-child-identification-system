import os
# Disable TensorFlow logs and OneDNN warnings BEFORE importing anything else
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import logging
from typing import List, Tuple

# Suppress deepface and tensorflow python warnings
logging.getLogger("deepface").setLevel(logging.ERROR)
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from deepface import DeepFace

import cv2
import uuid

class AIEngine:
    def __init__(self):
        # High-accuracy verification models
        self.primary_model = "ArcFace"
        self.secondary_model = "Facenet512"
        # Standardizing on mtcnn as a robust fallback due to tf-keras conflicts
        self.detector_backend = "mtcnn" 
        print(f"AIEngine Initialized: Dual-Model Verification ({self.primary_model} & {self.secondary_model}) using mtcnn")

    def get_embedding(self, image_path: str) -> dict:
        """
        Generates embeddings for ArcFace and Facenet512 using unified RetinaFace detection.
        Standardized on internal alignment for absolute consistency.
        """
        try:
            # 1. Extract Primary (ArcFace) using unified pipeline (align=True)
            res_primary = DeepFace.represent(
                img_path=image_path, 
                model_name=self.primary_model, 
                detector_backend=self.detector_backend, 
                enforce_detection=False, 
                align=True
            )
            
            # 2. Extract Secondary (Facenet512) using unified pipeline (align=True)
            res_secondary = DeepFace.represent(
                img_path=image_path, 
                model_name=self.secondary_model, 
                detector_backend=self.detector_backend, 
                enforce_detection=False, 
                align=True
            )
            
            if not res_primary or not res_secondary:
                raise ValueError("No face detected in the image.")
                
            return {
                "arcface": list(res_primary[0]["embedding"]),
                "facenet512": list(res_secondary[0]["embedding"])
            }
            
        except Exception as e:
             import traceback
             traceback.print_exc() 
             raise ValueError(f"DeepFace (RetinaFace) error: {str(e)}")
            
        except Exception as e:
             import traceback
             traceback.print_exc() 
             raise ValueError(f"DeepFace internal error: {str(e)}")

    def compute_similarity(self, dict1: dict, dict2: dict) -> float:
        # Fallback for old database entries that are just a list of floats (ArcFace only)
        if isinstance(dict1, list) and isinstance(dict2, list):
            return self._compute_single_sim(dict1, dict2, 0.33)

        if not isinstance(dict1, dict) or not isinstance(dict2, dict):
            # One is a list (DB), one is a dict (New Upload)
            legacy_list = dict1 if isinstance(dict1, list) else dict2
            new_dict = dict2 if isinstance(dict2, dict) else dict1
            
            # We MUST use the raw (non-preprocessed) embedding from the new upload to 
            # match the raw legacy DB image mathematically
            if "arcface_raw" in new_dict:
                return self._compute_single_sim(legacy_list, new_dict["arcface_raw"], 0.33)
            elif "arcface" in new_dict:
                return self._compute_single_sim(legacy_list, new_dict["arcface"], 0.33)
            return 0.0

        if "arcface" not in dict1 or "arcface" not in dict2:
            return 0.0
            
        if "facenet512" not in dict1 or "facenet512" not in dict2:
            # Fallback if facenet failed to generate for some reason
            return self._compute_single_sim(dict1.get("arcface", []), dict2.get("arcface", []), 0.33)

        # 1. Compute Primary (ArcFace)
        arc_sim = self._compute_single_sim(dict1["arcface"], dict2["arcface"], 0.33)
        # 2. Compute Secondary (Facenet512)
        face_sim = self._compute_single_sim(dict1["facenet512"], dict2["facenet512"], 0.50)

        # 3. Multi-Model Verification
        if arc_sim > 0.0 and face_sim > 0.0:
            return (arc_sim + face_sim) / 2.0
        else:
            return 0.0

    def _compute_single_sim(self, e1: list, e2: list, strict_threshold: float) -> float:
        arr1 = np.array(e1)
        arr2 = np.array(e2)
        if len(arr1) == 0 or len(arr2) == 0 or len(arr1) != len(arr2):
            return 0.0
            
        dot_product = np.dot(arr1, arr2)
        norm_product = np.linalg.norm(arr1) * np.linalg.norm(arr2)
        raw_cosine = dot_product / norm_product
        
        if raw_cosine >= strict_threshold:
            # Map up to UI space (0.5 to 1.0)
            return 0.5 + ((raw_cosine - strict_threshold) / (1.0 - strict_threshold)) * 0.5
        return 0.0

# Global engine instance for lazy loading
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine

def get_embedding(image_path: str) -> dict:
    return get_engine().get_embedding(image_path)

def compute_similarity(embedding1: dict, embedding2: dict) -> float:
    return get_engine().compute_similarity(embedding1, embedding2)

def find_matches(query_embedding: dict, db_embeddings: List[Tuple[int, dict]], threshold: float = 0.5) -> List[Tuple[int, float]]:
    engine = get_engine()
    matches = []
    
    for person_id, db_emb in db_embeddings:
        # Now passing the dicts natively
        score = engine.compute_similarity(query_embedding, db_emb)
        if score >= threshold: 
            matches.append((person_id, score))
    
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
