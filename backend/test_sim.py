import os, sys
sys.path.append('.')
from deepface import DeepFace

dir_path = 'test_images'
if not os.path.exists(dir_path):
    print('No test_images dir')
    sys.exit()

images = [f for f in os.listdir(dir_path) if f.endswith('.jpg')][:4]

for i in range(len(images)):
    for j in range(i+1, len(images)):
        p1 = os.path.join(dir_path, images[i])
        p2 = os.path.join(dir_path, images[j])
        res = DeepFace.verify(
            img1_path=p1,
            img2_path=p2,
            model_name='ArcFace',
            detector_backend='mtcnn',
            enforce_detection=False,
            align=True
        )
        print(f"{images[i]} vs {images[j]} -> Verified: {res.get('verified')}, Distance: {res.get('distance')}, Threshold: {res.get('threshold')}")
