# Manual Model Download Instructions

If `python download_models.py` fails due to network/firewall issues, download models manually:

## Step 1: Create Models Directory

```bash
cd backend
mkdir -p app\models
```

Or create the folder manually:
- Path: `backend\app\models\`

## Step 2: Download YuNet Face Detector

**File:** `face_detection_yunet_2023mar.onnx` (~1.5 MB)

**Option A - Direct Download:**
1. Visit: https://github.com/opencv/opencv_zoo/tree/master/models/face_detection_yunet
2. Click on `face_detection_yunet_2023mar.onnx`
3. Click "Download" or "Raw" button
4. Save to: `backend\app\models\face_detection_yunet_2023mar.onnx`

**Option B - Hugging Face:**
1. Visit: https://huggingface.co/opencv/face_detection_yunet
2. Download `face_detection_yunet_2023mar.onnx`
3. Save to: `backend\app\models\face_detection_yunet_2023mar.onnx`

## Step 3: Download Face Recognition Model

**File:** `mobilefacenet.onnx` (can use ArcFace ResNet100, ~250 MB)

**Option A - ArcFace ResNet100 (Recommended):**
1. Visit: https://github.com/onnx/models/tree/main/validated/vision/body_analysis/arcface/model
2. Download `arcface-resnet100.onnx`
3. Rename it to `mobilefacenet.onnx`
4. Save to: `backend\app\models\mobilefacenet.onnx`

**Option B - MobileFaceNet (Smaller, ~4 MB):**
1. Visit: https://github.com/nizhib/pytorch-insightface/tree/master/models
2. Download `mobilefacenet.onnx`
3. Save to: `backend\app\models\mobilefacenet.onnx`

## Step 4: Verify Files

After downloading, verify:
```
backend\app\models\
├── face_detection_yunet_2023mar.onnx  (~1.5 MB)
└── mobilefacenet.onnx                 (~4-250 MB depending on model)
```

## Step 5: Restart Backend

Restart your backend server. Check console output for:
- ✓ YuNet face detector loaded (CNN-based)
- ✓ Face recognition CNN loaded

## Quick Check

Run: `python check_models.py` to verify models are loaded.
