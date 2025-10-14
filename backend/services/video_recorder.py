"""
Video recording service for attention estimation streams
"""
import cv2
import numpy as np
import time
import threading
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from .attention_tracker import AttentionTracker


class VideoRecorder:
    def __init__(self, output_dir: str = "recordings"):
        """
        Initialize video recorder
        
        Args:
            output_dir: Directory to save recorded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.active_recordings = {}  # {recording_id: recording_info}
        self.recording_lock = threading.Lock()
        self.attention_trackers = {}  # {recording_id: AttentionTracker}
        
    def start_recording(self, recording_id: str, width: int, height: int, fps: int = 20, 
                       camera_ids: Optional[List[int]] = None, custom_name: Optional[str] = None) -> bool:
        """
        Start recording a video stream
        
        Args:
            recording_id: Unique identifier for this recording
            width: Video width
            height: Video height
            fps: Frames per second
            camera_ids: List of camera IDs (None for single camera)
            custom_name: Custom name for the recording file
            
        Returns:
            True if recording started successfully
        """
        with self.recording_lock:
            if recording_id in self.active_recordings:
                print(f"Recording {recording_id} is already active")
                return False
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if custom_name:
                # Use custom name if provided
                safe_name = custom_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                if camera_ids:
                    camera_suffix = "_".join(map(str, camera_ids))
                    filename = f"{safe_name}_multi_camera_{camera_suffix}_{timestamp}.mp4"
                else:
                    filename = f"{safe_name}_single_camera_{timestamp}.mp4"
            else:
                # Use default naming
                if camera_ids:
                    camera_suffix = "_".join(map(str, camera_ids))
                    filename = f"conference_multi_camera_{camera_suffix}_{timestamp}.mp4"
                else:
                    filename = f"conference_single_camera_{timestamp}.mp4"
            
            filepath = self.output_dir / filename
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                str(filepath), fourcc, fps, (width, height)
            )
            
            if not video_writer.isOpened():
                print(f"Failed to initialize video writer for {recording_id}")
                return False
            
            # Create recording info
            recording_info = {
                'recording_id': recording_id,
                'video_writer': video_writer,
                'filepath': filepath,
                'start_time': time.time(),
                'frame_count': 0,
                'width': width,
                'height': height,
                'fps': fps,
                'camera_ids': camera_ids,
                'custom_name': custom_name,
                'is_recording': True
            }
            
            self.active_recordings[recording_id] = recording_info
            
            # Start attention tracking
            attention_tracker = AttentionTracker(recording_id, str(self.output_dir), custom_name)
            attention_tracker.start_tracking()
            self.attention_trackers[recording_id] = attention_tracker
            
            print(f"Started recording {recording_id} to {filepath}")
            return True
    
    def stop_recording(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """
        Stop recording and return recording summary
        
        Args:
            recording_id: Recording identifier
            
        Returns:
            Recording summary or None if not found
        """
        with self.recording_lock:
            if recording_id not in self.active_recordings:
                print(f"Recording {recording_id} not found")
                return None
            
            recording_info = self.active_recordings[recording_id]
            recording_info['is_recording'] = False
            
            # Release video writer
            video_writer = recording_info['video_writer']
            video_writer.release()
            
            # Stop attention tracking
            if recording_id in self.attention_trackers:
                self.attention_trackers[recording_id].stop_tracking()
                del self.attention_trackers[recording_id]
            
            # Calculate recording duration
            duration = time.time() - recording_info['start_time']
            
            # Create summary
            summary = {
                'recording_id': recording_id,
                'filepath': str(recording_info['filepath']),
                'duration': duration,
                'frame_count': recording_info['frame_count'],
                'width': recording_info['width'],
                'height': recording_info['height'],
                'fps': recording_info['fps'],
                'camera_ids': recording_info['camera_ids'],
                'custom_name': recording_info.get('custom_name'),
                'file_size': recording_info['filepath'].stat().st_size if recording_info['filepath'].exists() else 0
            }
            
            del self.active_recordings[recording_id]
            print(f"Stopped recording {recording_id}. Duration: {duration:.2f}s, Frames: {recording_info['frame_count']}")
            return summary
    
    def write_frame(self, recording_id: str, frame: np.ndarray, stats: Optional[Dict[str, int]] = None) -> bool:
        """
        Write a frame to the recording and record attention data
        
        Args:
            recording_id: Recording identifier
            frame: Frame to write
            stats: Attention statistics for this frame
            
        Returns:
            True if frame was written successfully
        """
        with self.recording_lock:
            if recording_id not in self.active_recordings:
                return False
            
            recording_info = self.active_recordings[recording_id]
            if not recording_info['is_recording']:
                return False
            
            # Resize frame if necessary
            if frame.shape[:2] != (recording_info['height'], recording_info['width']):
                frame = cv2.resize(frame, (recording_info['width'], recording_info['height']))
            
            # Write frame
            recording_info['video_writer'].write(frame)
            recording_info['frame_count'] += 1
            
            # Record attention data if available
            if stats and recording_id in self.attention_trackers:
                self.attention_trackers[recording_id].record_attention_data(stats)
            
            return True
    
    def is_recording(self, recording_id: str) -> bool:
        """Check if a recording is active"""
        with self.recording_lock:
            return (recording_id in self.active_recordings and 
                   self.active_recordings[recording_id]['is_recording'])
    
    def get_active_recordings(self) -> List[str]:
        """Get list of active recording IDs"""
        with self.recording_lock:
            return [rid for rid, info in self.active_recordings.items() 
                   if info['is_recording']]
    
    def get_recording_info(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an active recording"""
        with self.recording_lock:
            if recording_id not in self.active_recordings:
                return None
            
            info = self.active_recordings[recording_id].copy()
            info['duration'] = time.time() - info['start_time']
            # Remove video_writer from the copy
            info.pop('video_writer', None)
            return info
    
    def stop_all_recordings(self) -> List[Dict[str, Any]]:
        """Stop all active recordings"""
        summaries = []
        active_ids = self.get_active_recordings()
        
        for recording_id in active_ids:
            summary = self.stop_recording(recording_id)
            if summary:
                summaries.append(summary)
        
        return summaries
    
    def get_attention_data(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """Get attention tracking data for a recording"""
        if recording_id in self.attention_trackers:
            tracker = self.attention_trackers[recording_id]
            return {
                'tracking_data': tracker.get_tracking_data(),
                'summary_statistics': tracker.get_summary_statistics()
            }
        return None
    
    def get_attention_data(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """Get attention tracking data for a recording"""
        if recording_id in self.attention_trackers:
            tracker = self.attention_trackers[recording_id]
            return {
                'tracking_data': tracker.get_tracking_data(),
                'summary_statistics': tracker.get_summary_statistics()
            }
        return None


class MultiCameraVideoRecorder:
    """Specialized recorder for multi-camera layouts"""
    
    def __init__(self, output_dir: str = "recordings"):
        """
        Initialize multi-camera video recorder
        
        Args:
            output_dir: Directory to save recorded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.active_recordings = {}  # {recording_id: recording_info}
        self.recording_lock = threading.Lock()
        self.attention_trackers = {}  # {recording_id: AttentionTracker}
    
    def start_multi_camera_recording(self, recording_id: str, camera_frames: Dict[int, np.ndarray], 
                                   fps: int = 20, custom_name: Optional[str] = None) -> bool:
        """
        Start recording multi-camera layout
        
        Args:
            recording_id: Unique identifier for this recording
            camera_frames: Dictionary of {camera_id: frame} to determine layout
            fps: Frames per second
            custom_name: Custom name for the recording file
            
        Returns:
            True if recording started successfully
        """
        with self.recording_lock:
            if recording_id in self.active_recordings:
                print(f"Multi-camera recording {recording_id} is already active")
                return False
            
            # Determine layout based on number of cameras
            camera_ids = list(camera_frames.keys())
            num_cameras = len(camera_ids)
            
            if num_cameras == 0:
                return False
            
            # Get frame dimensions from first camera
            first_frame = list(camera_frames.values())[0]
            frame_height, frame_width = first_frame.shape[:2]
            
            # Calculate layout dimensions
            if num_cameras == 1:
                layout_width, layout_height = frame_width, frame_height
            elif num_cameras == 2:
                layout_width, layout_height = frame_width * 2, frame_height
            elif num_cameras <= 4:
                layout_width, layout_height = frame_width * 2, frame_height * 2
            else:
                # For more than 4 cameras, use a grid layout
                cols = int(np.ceil(np.sqrt(num_cameras)))
                rows = int(np.ceil(num_cameras / cols))
                layout_width, layout_height = frame_width * cols, frame_height * rows
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            camera_suffix = "_".join(map(str, sorted(camera_ids)))
            if custom_name:
                safe_name = custom_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                filename = f"{safe_name}_multi_camera_{camera_suffix}_{timestamp}.mp4"
            else:
                filename = f"conference_multi_camera_{camera_suffix}_{timestamp}.mp4"
            filepath = self.output_dir / filename
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                str(filepath), fourcc, fps, (layout_width, layout_height)
            )
            
            if not video_writer.isOpened():
                print(f"Failed to initialize multi-camera video writer for {recording_id}")
                return False
            
            # Create recording info
            recording_info = {
                'recording_id': recording_id,
                'video_writer': video_writer,
                'filepath': filepath,
                'start_time': time.time(),
                'frame_count': 0,
                'layout_width': layout_width,
                'layout_height': layout_height,
                'frame_width': frame_width,
                'frame_height': frame_height,
                'fps': fps,
                'camera_ids': camera_ids,
                'num_cameras': num_cameras,
                'is_recording': True
            }
            
            self.active_recordings[recording_id] = recording_info
            
            # Start attention tracking
            attention_tracker = AttentionTracker(recording_id, str(self.output_dir), custom_name)
            attention_tracker.start_tracking()
            self.attention_trackers[recording_id] = attention_tracker
            
            print(f"Started multi-camera recording {recording_id} to {filepath}")
            return True
    
    def write_multi_camera_frame(self, recording_id: str, camera_frames: Dict[int, np.ndarray], stats: Optional[Dict[str, int]] = None) -> bool:
        """
        Write a multi-camera frame to the recording
        
        Args:
            recording_id: Recording identifier
            camera_frames: Dictionary of {camera_id: frame}
            stats: Attention statistics for this frame
            
        Returns:
            True if frame was written successfully
        """
        with self.recording_lock:
            if recording_id not in self.active_recordings:
                return False
            
            recording_info = self.active_recordings[recording_id]
            if not recording_info['is_recording']:
                return False
            
            # Create layout frame
            layout_frame = self._create_layout_frame(camera_frames, recording_info)
            
            # Write frame
            recording_info['video_writer'].write(layout_frame)
            recording_info['frame_count'] += 1
            
            # Record attention data if available
            if stats and recording_id in self.attention_trackers:
                self.attention_trackers[recording_id].record_attention_data(stats)
            
            return True
    
    def _create_layout_frame(self, camera_frames: Dict[int, np.ndarray], 
                           recording_info: Dict[str, Any]) -> np.ndarray:
        """Create a layout frame from multiple camera frames"""
        layout_width = recording_info['layout_width']
        layout_height = recording_info['layout_height']
        frame_width = recording_info['frame_width']
        frame_height = recording_info['frame_height']
        camera_ids = recording_info['camera_ids']
        num_cameras = recording_info['num_cameras']
        
        # Create blank layout frame
        layout_frame = np.zeros((layout_height, layout_width, 3), dtype=np.uint8)
        
        # Place frames in layout
        for i, camera_id in enumerate(camera_ids):
            if camera_id not in camera_frames:
                continue
            
            frame = camera_frames[camera_id]
            
            # Resize frame if necessary
            if frame.shape[:2] != (frame_height, frame_width):
                frame = cv2.resize(frame, (frame_width, frame_height))
            
            # Calculate position
            if num_cameras == 1:
                x, y = 0, 0
            elif num_cameras == 2:
                x, y = i * frame_width, 0
            elif num_cameras <= 4:
                x = (i % 2) * frame_width
                y = (i // 2) * frame_height
            else:
                cols = int(np.ceil(np.sqrt(num_cameras)))
                x = (i % cols) * frame_width
                y = (i // cols) * frame_height
            
            # Place frame in layout
            layout_frame[y:y+frame_height, x:x+frame_width] = frame
        
        return layout_frame
    
    def stop_recording(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """Stop recording and return summary"""
        with self.recording_lock:
            if recording_id not in self.active_recordings:
                return None
            
            recording_info = self.active_recordings[recording_id]
            recording_info['is_recording'] = False
            
            # Release video writer
            video_writer = recording_info['video_writer']
            video_writer.release()
            
            # Stop attention tracking
            if recording_id in self.attention_trackers:
                self.attention_trackers[recording_id].stop_tracking()
                del self.attention_trackers[recording_id]
            
            # Calculate recording duration
            duration = time.time() - recording_info['start_time']
            
            # Create summary
            summary = {
                'recording_id': recording_id,
                'filepath': str(recording_info['filepath']),
                'duration': duration,
                'frame_count': recording_info['frame_count'],
                'layout_width': recording_info['layout_width'],
                'layout_height': recording_info['layout_height'],
                'fps': recording_info['fps'],
                'camera_ids': recording_info['camera_ids'],
                'num_cameras': recording_info['num_cameras'],
                'file_size': recording_info['filepath'].stat().st_size if recording_info['filepath'].exists() else 0
            }
            
            del self.active_recordings[recording_id]
            print(f"Stopped multi-camera recording {recording_id}. Duration: {duration:.2f}s, Frames: {recording_info['frame_count']}")
            return summary
    
    def is_recording(self, recording_id: str) -> bool:
        """Check if a recording is active"""
        with self.recording_lock:
            return (recording_id in self.active_recordings and 
                   self.active_recordings[recording_id]['is_recording'])
    
    def get_active_recordings(self) -> List[str]:
        """Get list of active recording IDs"""
        with self.recording_lock:
            return [rid for rid, info in self.active_recordings.items() 
                   if info['is_recording']]
    
    def stop_all_recordings(self) -> List[Dict[str, Any]]:
        """Stop all active recordings"""
        summaries = []
        active_ids = self.get_active_recordings()
        
        for recording_id in active_ids:
            summary = self.stop_recording(recording_id)
            if summary:
                summaries.append(summary)
        
        return summaries
    
    def get_attention_data(self, recording_id: str) -> Optional[Dict[str, Any]]:
        """Get attention tracking data for a recording"""
        if recording_id in self.attention_trackers:
            tracker = self.attention_trackers[recording_id]
            return {
                'tracking_data': tracker.get_tracking_data(),
                'summary_statistics': tracker.get_summary_statistics()
            }
        return None
