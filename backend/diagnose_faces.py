import os
import sys
import cv2

sys.path.append('c:/Users/MadhuSudhan/.gemini/antigravity/scratch/missing_child_id_system/backend')
from app.ai_engine import get_engine

eng = get_engine()
uploads_dir = 'c:/Users/MadhuSudhan/.gemini/antigravity/scratch/missing_child_id_system/backend/uploads'
files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if f.endswith(('.jpg','.jpeg','.png'))]
files.sort(key=os.path.getmtime, reverse=True)

f1 = files[0]
f2 = files[1]

def draw_boxes(path, out):
    img = cv2.imread(path)
    if img is None: return
    h, w = img.shape[:2]
    max_dim = 800
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    
    img_dn = eng.denoise_image(img)
    
    if eng.face_detector:
        eng.face_detector.setInputSize((img_dn.shape[1], img_dn.shape[0]))
        _, faces = eng.face_detector.detect(img_dn)
        if faces is not None:
            for face in faces:
                box = face[:4].astype(int)
                # Raw box from model
                cv2.rectangle(img, (box[0], box[1]), (box[0]+box[2], box[1]+box[3]), (0, 0, 255), 2)
                print(f"Detected face at: {box}")

    cv2.imwrite(out, img)

draw_boxes(f1, 'boxes1.jpg')
draw_boxes(f2, 'boxes2.jpg')
print("Saved boxes to boxes1.jpg and boxes2.jpg")
