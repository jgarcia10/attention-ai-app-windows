#!/usr/bin/env python3
"""
Simple script to download YOLO model using requests
This doesn't require ultralytics to be installed first
"""

import os
import sys
from pathlib import Path
import requests
from tqdm import tqdm

def download_file(url, destination):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as file, tqdm(
        desc=destination.name,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=8192):
            size = file.write(chunk)
            progress_bar.update(size)

def download_yolo_model():
    """Download YOLOv8n model."""
    # Create models directory
    script_dir = Path(__file__).parent.absolute()
    models_dir = script_dir / "backend" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / "yolov8n.pt"
    
    if model_path.exists():
        print(f"✅ YOLO model already exists at {model_path}")
        return str(model_path)
    
    # YOLOv8n model URL from Ultralytics
    model_url = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
    
    print("📥 Downloading YOLOv8n model...")
    print(f"📁 Target: {model_path}")
    print(f"🌐 URL: {model_url}")
    
    try:
        download_file(model_url, model_path)
        print(f"✅ YOLO model downloaded successfully!")
        print(f"📁 Location: {model_path}")
        return str(model_path)
    except Exception as e:
        print(f"❌ Error downloading YOLO model: {e}")
        print("💡 Make sure you have internet connection")
        sys.exit(1)

if __name__ == "__main__":
    try:
        model_path = download_yolo_model()
        print(f"\n🎯 Model ready at: {model_path}")
        print("🚀 You can now run the Attention App!")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Install required packages with: pip install requests tqdm")
        sys.exit(1)
