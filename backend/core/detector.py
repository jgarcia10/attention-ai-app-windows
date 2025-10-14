"""
YOLO person detection module
"""
import os
import numpy as np
import torch
from ultralytics import YOLO
from typing import List, Dict, Any


class PersonDetector:
    def __init__(self, model_path: str = "./models/yolov8n.pt", conf_threshold: float = 0.4):
        """Initialize YOLO detector for person detection"""
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model, download if not exists"""
        if not os.path.exists(self.model_path):
            # Create models directory if it doesn't exist
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            print(f"Model not found at {self.model_path}, downloading...")
        
        try:
            # Fix for PyTorch 2.6 compatibility - temporarily patch torch.load
            original_torch_load = torch.load
            
            def patched_torch_load(*args, **kwargs):
                # Force weights_only=False for YOLO model loading
                kwargs['weights_only'] = False
                return original_torch_load(*args, **kwargs)
            
            # Apply the patch
            torch.load = patched_torch_load
            
            self.model = YOLO(self.model_path)
            print(f"YOLO model loaded successfully from {self.model_path}")
            
            # Restore original torch.load
            torch.load = original_torch_load
            
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            # Restore original torch.load in case of error
            torch.load = original_torch_load
            
            # Fallback to default model name which will auto-download
            try:
                # Apply patch again for fallback
                torch.load = patched_torch_load
                self.model = YOLO('yolov8n.pt')
                print("Using default YOLOv8n model")
                # Restore original torch.load
                torch.load = original_torch_load
            except Exception as e2:
                print(f"Error loading default model: {e2}")
                # Restore original torch.load
                torch.load = original_torch_load
                raise e2
    
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect persons in frame
        
        Args:
            frame: Input image as numpy array
            
        Returns:
            List of detections with bbox and confidence
        """
        if self.model is None:
            return []
        
        try:
            # Run inference
            results = self.model(frame, conf=self.conf_threshold, classes=[0])  # class 0 is 'person' in COCO
            
            detections = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        
                        detections.append({
                            "bbox": [int(x1), int(y1), int(x2), int(y2)],
                            "conf": float(conf)
                        })
            
            return detections
        
        except Exception as e:
            print(f"Error in person detection: {e}")
            return []

