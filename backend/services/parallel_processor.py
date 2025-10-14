"""
Parallel processing service for concurrent attention estimation across multiple cameras
"""
import cv2
import numpy as np
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple, Optional
from core.pipeline import AttentionPipeline


class ParallelProcessor:
    def __init__(self, pipeline: AttentionPipeline, max_workers: int = 4):
        """
        Initialize parallel processor for multi-camera attention estimation
        
        Args:
            pipeline: Attention detection pipeline
            max_workers: Maximum number of parallel processing threads
        """
        self.pipeline = pipeline
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.processing_lock = threading.Lock()
        self.frame_queue = {}  # {camera_id: frame_data}
        self.results = {}  # {camera_id: (annotated_frame, stats)}
        self.queue_lock = threading.Lock()
        
    def process_frame_parallel(self, camera_id: int, frame: np.ndarray, 
                              width: int, height: int) -> Tuple[np.ndarray, Dict[str, int]]:
        """
        Process a single frame through the attention pipeline
        
        Args:
            camera_id: Camera identifier
            frame: Input frame
            width: Target width
            height: Target height
            
        Returns:
            Tuple of (annotated_frame, stats)
        """
        try:
            # Process frame through pipeline
            annotated_frame, stats = self.pipeline.process_frame(frame, width, height)
            return annotated_frame, stats
        except Exception as e:
            print(f"Error processing frame for camera {camera_id}: {e}")
            # Return original frame with empty stats on error
            return frame, {"green": 0, "yellow": 0, "red": 0, "total": 0}
    
    def submit_frame_for_processing(self, camera_id: int, frame: np.ndarray, 
                                   width: int, height: int) -> None:
        """
        Submit a frame for parallel processing
        
        Args:
            camera_id: Camera identifier
            frame: Input frame
            width: Target width
            height: Target height
        """
        with self.queue_lock:
            self.frame_queue[camera_id] = {
                'frame': frame.copy(),
                'width': width,
                'height': height,
                'timestamp': time.time()
            }
    
    def process_pending_frames(self) -> Dict[int, Tuple[np.ndarray, Dict[str, int]]]:
        """
        Process all pending frames in parallel
        
        Returns:
            Dictionary of {camera_id: (annotated_frame, stats)}
        """
        if not self.frame_queue:
            return {}
        
        # Get frames to process
        frames_to_process = {}
        with self.queue_lock:
            frames_to_process = self.frame_queue.copy()
            self.frame_queue.clear()
        
        if not frames_to_process:
            return {}
        
        # Submit all frames for parallel processing
        future_to_camera = {}
        for camera_id, frame_data in frames_to_process.items():
            future = self.executor.submit(
                self.process_frame_parallel,
                camera_id,
                frame_data['frame'],
                frame_data['width'],
                frame_data['height']
            )
            future_to_camera[future] = camera_id
        
        # Collect results as they complete
        results = {}
        for future in as_completed(future_to_camera):
            camera_id = future_to_camera[future]
            try:
                annotated_frame, stats = future.result()
                results[camera_id] = (annotated_frame, stats)
            except Exception as e:
                print(f"Error getting result for camera {camera_id}: {e}")
                # Use original frame with empty stats
                frame_data = frames_to_process[camera_id]
                results[camera_id] = (frame_data['frame'], {"green": 0, "yellow": 0, "red": 0, "total": 0})
        
        return results
    
    def get_latest_result(self, camera_id: int) -> Optional[Tuple[np.ndarray, Dict[str, int]]]:
        """
        Get the latest processing result for a specific camera
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Tuple of (annotated_frame, stats) or None if not available
        """
        with self.queue_lock:
            return self.results.get(camera_id)
    
    def update_result(self, camera_id: int, annotated_frame: np.ndarray, stats: Dict[str, int]):
        """
        Update the latest result for a specific camera
        
        Args:
            camera_id: Camera identifier
            annotated_frame: Processed frame
            stats: Processing statistics
        """
        with self.queue_lock:
            self.results[camera_id] = (annotated_frame, stats)
    
    def clear_camera_data(self, camera_id: int):
        """
        Clear all data for a specific camera
        
        Args:
            camera_id: Camera identifier
        """
        with self.queue_lock:
            if camera_id in self.frame_queue:
                del self.frame_queue[camera_id]
            if camera_id in self.results:
                del self.results[camera_id]
    
    def clear_all_data(self):
        """Clear all queued frames and results"""
        with self.queue_lock:
            self.frame_queue.clear()
            self.results.clear()
    
    def shutdown(self):
        """Shutdown the parallel processor"""
        self.executor.shutdown(wait=True)
        self.clear_all_data()
    
    def get_queue_size(self) -> int:
        """Get the number of frames currently in the processing queue"""
        with self.queue_lock:
            return len(self.frame_queue)
    
    def get_active_cameras(self) -> List[int]:
        """Get list of cameras with pending frames or results"""
        with self.queue_lock:
            cameras = set(self.frame_queue.keys()) | set(self.results.keys())
            return list(cameras)
