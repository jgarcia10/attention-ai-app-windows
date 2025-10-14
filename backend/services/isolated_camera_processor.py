"""
Isolated camera processor for smooth, independent attention estimation per camera
"""
import cv2
import numpy as np
import time
import threading
from typing import Dict, List, Any, Tuple, Optional
from core.pipeline import AttentionPipeline


class IsolatedCameraProcessor:
    def __init__(self, camera_id: int, model_path: str, conf_threshold: float, 
                 yaw_threshold: float, pitch_threshold: float):
        """
        Initialize isolated processor for a single camera
        
        Args:
            camera_id: Camera identifier
            model_path: Path to YOLO model
            conf_threshold: YOLO confidence threshold
            yaw_threshold: Head yaw threshold for attention classification
            pitch_threshold: Head pitch threshold for attention classification
        """
        self.camera_id = camera_id
        self.is_processing = False
        self.processing_thread = None
        self.frame_queue = []
        self.queue_lock = threading.Lock()
        self.result_lock = threading.Lock()
        self.latest_frame = None
        self.latest_stats = None
        
        # Create dedicated pipeline for this camera
        self.pipeline = AttentionPipeline(
            model_path=model_path,
            conf_threshold=conf_threshold,
            yaw_threshold=yaw_threshold,
            pitch_threshold=pitch_threshold
        )
        
        print(f"Created isolated processor for camera {camera_id}")
    
    def start_processing(self):
        """Start the isolated processing thread"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()
        print(f"Started isolated processing for camera {self.camera_id}")
    
    def stop_processing(self):
        """Stop the isolated processing thread"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        # Clear queue and results
        with self.queue_lock:
            self.frame_queue.clear()
        
        with self.result_lock:
            self.latest_frame = None
            self.latest_stats = None
        
        print(f"Stopped isolated processing for camera {self.camera_id}")
    
    def submit_frame(self, frame: np.ndarray, width: int, height: int):
        """
        Submit a frame for processing
        
        Args:
            frame: Input frame
            width: Target width
            height: Target height
        """
        with self.queue_lock:
            # Keep only the latest frame to avoid queue buildup
            self.frame_queue = [{
                'frame': frame.copy(),
                'width': width,
                'height': height,
                'timestamp': time.time()
            }]
    
    def get_latest_result(self) -> Tuple[Optional[np.ndarray], Optional[Dict[str, int]]]:
        """
        Get the latest processing result
        
        Returns:
            Tuple of (annotated_frame, stats) or (None, None) if not available
        """
        with self.result_lock:
            if self.latest_frame is not None and self.latest_stats is not None:
                return self.latest_frame.copy(), self.latest_stats.copy()
            return None, None
    
    def _processing_loop(self):
        """Main processing loop for this camera"""
        while self.is_processing:
            try:
                # Get frame to process
                frame_data = None
                with self.queue_lock:
                    if self.frame_queue:
                        frame_data = self.frame_queue.pop(0)
                
                if frame_data is None:
                    time.sleep(0.01)  # 10ms delay if no frame
                    continue
                
                # Process frame through dedicated pipeline
                annotated_frame, stats = self.pipeline.process_frame(
                    frame_data['frame'],
                    frame_data['width'],
                    frame_data['height']
                )
                
                # Update results
                with self.result_lock:
                    self.latest_frame = annotated_frame
                    self.latest_stats = stats
                
            except Exception as e:
                print(f"Error in camera {self.camera_id} processing loop: {e}")
                time.sleep(0.1)  # Longer delay on error
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics for this camera"""
        return {
            'camera_id': self.camera_id,
            'is_processing': self.is_processing,
            'queue_size': len(self.frame_queue),
            'has_latest_result': self.latest_frame is not None
        }
    
    def reset_pipeline(self):
        """Reset the pipeline state for this camera"""
        try:
            self.pipeline.reset()
            print(f"Reset pipeline for camera {self.camera_id}")
        except Exception as e:
            print(f"Error resetting pipeline for camera {self.camera_id}: {e}")


class IsolatedMultiCameraManager:
    def __init__(self, model_path: str, conf_threshold: float, 
                 yaw_threshold: float, pitch_threshold: float):
        """
        Manager for multiple isolated camera processors
        
        Args:
            model_path: Path to YOLO model
            conf_threshold: YOLO confidence threshold
            yaw_threshold: Head yaw threshold for attention classification
            pitch_threshold: Head pitch threshold for attention classification
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        
        self.camera_processors = {}  # {camera_id: IsolatedCameraProcessor}
        self.aggregated_stats = {"green": 0, "yellow": 0, "red": 0, "total": 0}
        self.stats_lock = threading.Lock()
    
    def create_camera_processor(self, camera_id: int) -> IsolatedCameraProcessor:
        """
        Create a new isolated processor for a camera
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            IsolatedCameraProcessor instance
        """
        if camera_id in self.camera_processors:
            return self.camera_processors[camera_id]
        
        processor = IsolatedCameraProcessor(
            camera_id=camera_id,
            model_path=self.model_path,
            conf_threshold=self.conf_threshold,
            yaw_threshold=self.yaw_threshold,
            pitch_threshold=self.pitch_threshold
        )
        
        self.camera_processors[camera_id] = processor
        return processor
    
    def start_camera_processing(self, camera_id: int):
        """Start processing for a specific camera"""
        if camera_id in self.camera_processors:
            self.camera_processors[camera_id].start_processing()
    
    def stop_camera_processing(self, camera_id: int):
        """Stop processing for a specific camera"""
        if camera_id in self.camera_processors:
            self.camera_processors[camera_id].stop_processing()
    
    def submit_frame(self, camera_id: int, frame: np.ndarray, width: int, height: int):
        """Submit a frame for processing by a specific camera"""
        if camera_id in self.camera_processors:
            self.camera_processors[camera_id].submit_frame(frame, width, height)
    
    def get_camera_result(self, camera_id: int) -> Tuple[Optional[np.ndarray], Optional[Dict[str, int]]]:
        """Get the latest result for a specific camera"""
        if camera_id in self.camera_processors:
            return self.camera_processors[camera_id].get_latest_result()
        return None, None
    
    def get_aggregated_stats(self) -> Dict[str, int]:
        """Get aggregated statistics from all active cameras"""
        with self.stats_lock:
            # Reset aggregated stats
            self.aggregated_stats = {"green": 0, "yellow": 0, "red": 0, "total": 0}
            
            # Sum stats from all active cameras
            for camera_id, processor in self.camera_processors.items():
                if processor.is_processing:
                    _, stats = processor.get_latest_result()
                    if stats:
                        self.aggregated_stats['green'] += stats.get('green', 0)
                        self.aggregated_stats['yellow'] += stats.get('yellow', 0)
                        self.aggregated_stats['red'] += stats.get('red', 0)
                        self.aggregated_stats['total'] += stats.get('total', 0)
            
            return self.aggregated_stats.copy()
    
    def get_active_cameras(self) -> List[int]:
        """Get list of active camera IDs"""
        return [camera_id for camera_id, processor in self.camera_processors.items() 
                if processor.is_processing]
    
    def stop_all_processing(self):
        """Stop processing for all cameras"""
        for camera_id in list(self.camera_processors.keys()):
            self.stop_camera_processing(camera_id)
    
    def remove_camera_processor(self, camera_id: int):
        """Remove a camera processor"""
        if camera_id in self.camera_processors:
            self.camera_processors[camera_id].stop_processing()
            del self.camera_processors[camera_id]
    
    def reset_all_pipelines(self):
        """Reset all camera pipelines"""
        for processor in self.camera_processors.values():
            processor.reset_pipeline()
    
    def get_all_stats(self) -> Dict[int, Dict[str, Any]]:
        """Get statistics for all cameras"""
        stats = {}
        for camera_id, processor in self.camera_processors.items():
            stats[camera_id] = processor.get_pipeline_stats()
        return stats
