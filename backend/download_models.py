"""
Download face recognition models for CNN/SVM-based matching.
Run this script to download required ONNX models:
    cd backend
    python download_models.py
"""
import os
import urllib.request
import sys
import ssl

# Allow unverified SSL (some GitHub mirrors need this)
ssl._create_default_https_context = ssl._create_unverified_context

def download_file(urls, destination, description=""):
    """Download a file with multiple fallback URLs."""
    print(f"\n{'='*60}")
    print(f"Downloading {description or os.path.basename(destination)}...")
    print(f"Destination: {destination}")
    print(f"{'='*60}")
    
    if not isinstance(urls, list):
        urls = [urls]
    
    for i, url in enumerate(urls, 1):
        print(f"\nTrying URL {i}/{len(urls)}: {url}")
        try:
            def show_progress(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    print(f"\rProgress: {percent}%", end='', flush=True)
            
            urllib.request.urlretrieve(url, destination, show_progress)
            file_size = os.path.getsize(destination) / (1024 * 1024)  # MB
            print(f"\n✓ Successfully downloaded ({file_size:.2f} MB)")
            return True
        except Exception as e:
            print(f"\n✗ Failed: {e}")
            if i < len(urls):
                print("Trying next URL...")
            continue
    
    print(f"\n✗ All URLs failed for {description}")
    return False

def main():
    models_dir = os.path.join(os.path.dirname(__file__), "app", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("Face Recognition Model Downloader")
    print("="*60)
    print("\nThis script downloads ONNX models for:")
    print("  1. Face Detection (YuNet)")
    print("  2. Face Recognition (ArcFace/MobileFaceNet)")
    print("\nModels will be saved to:", models_dir)
    
    success_count = 0
    total_count = 2

    # 1. Download YuNet Face Detector (OpenCV)
    yunet_urls = [
        "https://github.com/opencv/opencv_zoo/raw/master/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "https://raw.githubusercontent.com/opencv/opencv_zoo/master/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx",
    ]
    yunet_dest = os.path.join(models_dir, "face_detection_yunet_2023mar.onnx")
    
    if os.path.exists(yunet_dest):
        file_size = os.path.getsize(yunet_dest) / (1024 * 1024)
        print(f"\n✓ YuNet detector already exists: {yunet_dest} ({file_size:.2f} MB)")
        success_count += 1
    else:
        if download_file(yunet_urls, yunet_dest, "YuNet Face Detector"):
            success_count += 1

    # 2. Download ArcFace ResNet100 (Face Recognition CNN)
    # Multiple fallback URLs for reliability
    arcface_urls = [
        "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/arcface/model/arcface-resnet100.onnx",
        "https://raw.githubusercontent.com/onnx/models/main/validated/vision/body_analysis/arcface/model/arcface-resnet100.onnx",
        # Alternative: Smaller MobileFaceNet model (if ArcFace fails)
        "https://github.com/nizhib/pytorch-insightface/raw/master/models/mobilefacenet.onnx",
    ]
    arcface_dest = os.path.join(models_dir, "mobilefacenet.onnx")  # Keep name for compatibility
    
    if os.path.exists(arcface_dest):
        file_size = os.path.getsize(arcface_dest) / (1024 * 1024)
        print(f"\n✓ Face recognition model already exists: {arcface_dest} ({file_size:.2f} MB)")
        success_count += 1
    else:
        if download_file(arcface_urls, arcface_dest, "ArcFace ResNet100 (Face Recognition)"):
            success_count += 1

    print("\n" + "="*60)
    print("Download Summary")
    print("="*60)
    print(f"Successfully downloaded: {success_count}/{total_count} models")
    
    if success_count == total_count:
        print("\n✓ All models downloaded successfully!")
        print("\nNext steps:")
        print("  1. Restart your backend server")
        print("  2. The system will now use CNN-based face recognition")
        print("  3. SVM matcher can be trained later if needed")
    elif success_count > 0:
        print("\n⚠ Some models failed to download.")
        print("\nTroubleshooting:")
        print("  1. Check your internet connection")
        print("  2. Try running the script again (may be temporary network issue)")
        print("  3. Check firewall/proxy settings")
        print("  4. Ensure you have enough disk space (~300 MB needed)")
        print("\nAlternative: Download models manually:")
        print("  - YuNet: https://github.com/opencv/opencv_zoo/tree/master/models/face_detection_yunet")
        print("  - ArcFace: https://github.com/onnx/models/tree/main/validated/vision/body_analysis/arcface")
    else:
        print("\n✗ No models were downloaded.")
        print("\nPossible causes:")
        print("  1. No internet connection")
        print("  2. Firewall/proxy blocking GitHub")
        print("  3. Insufficient disk space")
        print("  4. SSL certificate issues")
        print("\nManual download option:")
        print("  1. Visit: https://github.com/opencv/opencv_zoo/tree/master/models/face_detection_yunet")
        print("  2. Download: face_detection_yunet_2023mar.onnx")
        print("  3. Visit: https://github.com/onnx/models/tree/main/validated/vision/body_analysis/arcface")
        print("  4. Download: arcface-resnet100.onnx")
        print("  5. Rename arcface-resnet100.onnx to mobilefacenet.onnx")
        print(f"  6. Place both files in: {models_dir}")
    
    print(f"\nModel files location: {models_dir}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
