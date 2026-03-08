import numpy as np
import concurrent.futures
import os

# Create exactly 1 persistent background OS process for all TF operations
_ml_executor = concurrent.futures.ProcessPoolExecutor(max_workers=1)

def _run_ml_process(image_path, model_name, detector_backend):
    """
    Runs completely outside of the FastAPI memory space.
    Imports TF and DeepFace strictly inside this isolated process.
    """
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    from deepface import DeepFace
    
    return DeepFace.represent(
        img_path=image_path,
        model_name=model_name,
        detector_backend=detector_backend,
        enforce_detection=False,
        align=True 
    )

class EmbeddingEngine:
    def __init__(self):
        # By strict instruction, we only use ArcFace for vector embeddings
        self.model_name = "ArcFace"
        # Standardizing on mtcnn as a robust fallback with no keras dependencies
        self.detector_backend = "mtcnn" 

    def get_embedding(self, image_path: str) -> np.ndarray:
        """
        Generates an embedding for the face, and STRICTLY L2 normalizes it
        before returning so that raw dot products equal cosine similarity.
        Standardized on RetinaFace with internal alignment.
        """
        try:
            # Dispatch to the isolated TF process
            future = _ml_executor.submit(_run_ml_process, image_path, self.model_name, self.detector_backend)
            result = future.result()
            
            if not result or len(result) == 0:
                raise ValueError("No face detected in the image.")
                
            raw_embedding = result[0]["embedding"]
            emb_array = np.array(raw_embedding, dtype=np.float32)
            
            # 1. mathematically L2 Normalize
            norm = np.linalg.norm(emb_array)
            if norm == 0:
                raise ValueError("Embedding calculation returned a zero-vector.")
                
            normalized_embedding = emb_array / norm
            return normalized_embedding
            
        except Exception as e:
            import traceback
            traceback.print_exc() 
            raise ValueError(f"Embedding Engine Error (RetinaFace): {str(e)}")

# Global instance
_engine = None

def get_embedding_engine():
    global _engine
    if _engine is None:
        _engine = EmbeddingEngine()
    return _engine

def generate_normalized_embedding(image_path: str) -> list:
    engine = get_embedding_engine()
    emb = engine.get_embedding(image_path)
    # Return as list for easier SQLAlchemy JSON fallback formatting/printing
    return emb.tolist()
