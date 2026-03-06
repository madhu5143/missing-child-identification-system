import cv2
import os
import uuid
from deepface import DeepFace

class AlignmentEngine:
    def __init__(self):
        # We rely on mtcnn for high-accuracy eye alignment
        self.detector_backend = "mtcnn"

    def align_and_crop(self, image_path: str) -> str:
        """
        Takes raw image, detects the face, applies horizontal eye alignment,
        crops tightly around the face, and saves it as a temporary aligned file.
        "Avoid aggressive histogram equalization or over-enhancement."
        """
        try:
            # 1. Detect and Align. Deepface has an internal extract_faces function
            # which does exactly what we need for alignment and tight crop.
            
            # extract_faces returns a list of dictionaries. Each has: 
            # - 'face': numpy array of the aligned/cropped face
            # - 'facial_area': dict containing x, y, w, h
            results = DeepFace.extract_faces(
                img_path=image_path,
                detector_backend=self.detector_backend,
                enforce_detection=False,
                align=True,
                grayscale=False
            )
            
            if not results or len(results) == 0:
                print("Warning: No face detected during tight crop phase.")
                return image_path
                
            # Grab the best face (assumed to be the first/largest one by default in deepface if multiple present)
            # The 'face' array given by extract_faces is typically already normalized to [0,1].
            # However, for writing to disk with cv2 or passing back into Deepface later,
            # we need it back in 0-255 format.
            aligned_face_arr = results[0]["face"]
            
            if aligned_face_arr.max() <= 1.0:
                aligned_face_arr = (aligned_face_arr * 255.0).astype(int)
            
            # Deepface returns RGB. cv2 expects BGR for writing.
            if len(aligned_face_arr.shape) == 3 and aligned_face_arr.shape[2] == 3:
                aligned_face_bgr = cv2.cvtColor(aligned_face_arr.astype("uint8"), cv2.COLOR_RGB2BGR)
            else:
                aligned_face_bgr = aligned_face_arr

            # Secure temp directory
            dir_name = os.path.dirname(image_path)
            file_name_clean = os.path.basename(image_path)
            temp_path = os.path.join(dir_name, f"aligned_{uuid.uuid4().hex[:6]}_{file_name_clean}")
            
            success = cv2.imwrite(temp_path, aligned_face_bgr)
            if not success:
               return image_path
               
            return temp_path
            
        except Exception as e:
            # e.g., MTCNN crashes or no face found. Bubble this up or fallback?
            # We log it but just return original. The embedding engine will catch failure.
            print(f"Alignment engine warning (fallback to original): {str(e)}")
            return image_path

_engine = None

def get_alignment_engine():
    global _engine
    if _engine is None:
        _engine = AlignmentEngine()
    return _engine

def align_face(image_path: str) -> str:
    engine = get_alignment_engine()
    return engine.align_and_crop(image_path)
