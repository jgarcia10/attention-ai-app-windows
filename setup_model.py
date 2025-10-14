#!/usr/bin/env python3
"""
Setup script to download the YOLO model required for the Attention App.
This script downloads the YOLOv8n model to the models directory.
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO

def download_yolo_model():
    """Download YOLOv8n model to the models directory."""
    models_dir = Path("backend/models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / "yolov8n.pt"
    
    if model_path.exists():
        print(f"✅ YOLO model already exists at {model_path}")
        return str(model_path)
    
    print("📥 Downloading YOLOv8n model...")
    try:
        # Download the model
        model = YOLO("yolov8n.pt")
        # Save it to our models directory
        model.save(str(model_path))
        print(f"✅ YOLO model downloaded successfully to {model_path}")
        return str(model_path)
    except Exception as e:
        print(f"❌ Error downloading YOLO model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    model_path = download_yolo_model()
    print(f"\n🎯 Model ready at: {model_path}")
    print("🚀 You can now run the Attention App!")
