"""
Attention tracking service for recording analysis
"""
import time
import json
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class AttentionTracker:
    def __init__(self, recording_id: str, output_dir: str = "recordings", custom_name: Optional[str] = None):
        """
        Initialize attention tracker for a recording session
        
        Args:
            recording_id: Unique identifier for this recording
            output_dir: Directory to save tracking data
            custom_name: Custom name for the recording
        """
        self.recording_id = recording_id
        self.custom_name = custom_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.tracking_data = []
        self.start_time = None
        self.is_tracking = False
        self.lock = threading.Lock()
        
        # Statistics
        self.total_frames = 0
        self.total_attention_time = 0.0
        self.total_distracted_time = 0.0
        self.total_no_face_time = 0.0
        
    def start_tracking(self):
        """Start tracking attention data"""
        with self.lock:
            self.is_tracking = True
            self.start_time = time.time()
            self.tracking_data = []
            self.total_frames = 0
            self.total_attention_time = 0.0
            self.total_distracted_time = 0.0
            self.total_no_face_time = 0.0
            print(f"Started attention tracking for recording {self.recording_id}")
    
    def stop_tracking(self):
        """Stop tracking and save data"""
        with self.lock:
            self.is_tracking = False
            self._save_tracking_data()
            print(f"Stopped attention tracking for recording {self.recording_id}")
    
    def record_attention_data(self, stats: Dict[str, int], frame_timestamp: Optional[float] = None):
        """
        Record attention data for a frame
        
        Args:
            stats: Dictionary with 'green', 'yellow', 'red', 'total' counts
            frame_timestamp: Timestamp of the frame (defaults to current time)
        """
        if not self.is_tracking:
            return
        
        if frame_timestamp is None:
            frame_timestamp = time.time()
        
        # Calculate relative time from start
        relative_time = frame_timestamp - self.start_time if self.start_time else 0.0
        
        # Calculate percentages
        total = stats.get('total', 0)
        if total > 0:
            attention_pct = (stats.get('green', 0) / total) * 100
            distracted_pct = (stats.get('yellow', 0) / total) * 100
            no_face_pct = (stats.get('red', 0) / total) * 100
        else:
            attention_pct = 0.0
            distracted_pct = 0.0
            no_face_pct = 0.0
        
        # Record data point
        data_point = {
            'timestamp': frame_timestamp,
            'relative_time': relative_time,
            'total_people': total,
            'attention_count': stats.get('green', 0),
            'distracted_count': stats.get('yellow', 0),
            'no_face_count': stats.get('red', 0),
            'attention_percentage': attention_pct,
            'distracted_percentage': distracted_pct,
            'no_face_percentage': no_face_pct
        }
        
        with self.lock:
            self.tracking_data.append(data_point)
            self.total_frames += 1
            
            # Update cumulative time (assuming ~20 FPS)
            frame_duration = 1.0 / 20.0  # 50ms per frame
            self.total_attention_time += (attention_pct / 100.0) * frame_duration
            self.total_distracted_time += (distracted_pct / 100.0) * frame_duration
            self.total_no_face_time += (no_face_pct / 100.0) * frame_duration
    
    def _save_tracking_data(self):
        """Save tracking data to JSON file"""
        if not self.tracking_data:
            return
        
        # Create summary statistics
        summary = self._calculate_summary_statistics()
        
        # Prepare complete data
        complete_data = {
            'recording_id': self.recording_id,
            'custom_name': self.custom_name,
            'start_time': self.start_time,
            'end_time': time.time(),
            'total_duration': time.time() - self.start_time if self.start_time else 0.0,
            'total_frames': self.total_frames,
            'summary_statistics': summary,
            'tracking_data': self.tracking_data
        }
        
        # Save to file
        filename = f"{self.recording_id}_attention_data.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved attention tracking data to {filepath}")
    
    def _calculate_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics from tracking data"""
        if not self.tracking_data:
            return {}
        
        # Calculate averages
        avg_attention = sum(point['attention_percentage'] for point in self.tracking_data) / len(self.tracking_data)
        avg_distracted = sum(point['distracted_percentage'] for point in self.tracking_data) / len(self.tracking_data)
        avg_no_face = sum(point['no_face_percentage'] for point in self.tracking_data) / len(self.tracking_data)
        avg_total_people = sum(point['total_people'] for point in self.tracking_data) / len(self.tracking_data)
        
        # Find peaks and valleys
        attention_values = [point['attention_percentage'] for point in self.tracking_data]
        max_attention = max(attention_values) if attention_values else 0
        min_attention = min(attention_values) if attention_values else 0
        
        # Calculate attention levels
        high_attention_frames = sum(1 for pct in attention_values if pct >= 70)
        medium_attention_frames = sum(1 for pct in attention_values if 30 <= pct < 70)
        low_attention_frames = sum(1 for pct in attention_values if pct < 30)
        
        total_frames = len(self.tracking_data)
        
        return {
            'average_attention_percentage': round(avg_attention, 2),
            'average_distracted_percentage': round(avg_distracted, 2),
            'average_no_face_percentage': round(avg_no_face, 2),
            'average_total_people': round(avg_total_people, 1),
            'max_attention_percentage': round(max_attention, 2),
            'min_attention_percentage': round(min_attention, 2),
            'high_attention_frames': high_attention_frames,
            'medium_attention_frames': medium_attention_frames,
            'low_attention_frames': low_attention_frames,
            'high_attention_percentage': round((high_attention_frames / total_frames) * 100, 2) if total_frames > 0 else 0,
            'medium_attention_percentage': round((medium_attention_frames / total_frames) * 100, 2) if total_frames > 0 else 0,
            'low_attention_percentage': round((low_attention_frames / total_frames) * 100, 2) if total_frames > 0 else 0,
            'total_attention_time_seconds': round(self.total_attention_time, 2),
            'total_distracted_time_seconds': round(self.total_distracted_time, 2),
            'total_no_face_time_seconds': round(self.total_no_face_time, 2)
        }
    
    def get_tracking_data(self) -> List[Dict[str, Any]]:
        """Get current tracking data"""
        with self.lock:
            return self.tracking_data.copy()
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get current summary statistics"""
        return self._calculate_summary_statistics()
    
    def is_active(self) -> bool:
        """Check if tracking is active"""
        return self.is_tracking


class AttentionTrackerManager:
    """Manager for multiple attention trackers"""
    
    def __init__(self, output_dir: str = "recordings"):
        self.output_dir = output_dir
        self.active_trackers = {}  # {recording_id: AttentionTracker}
        self.lock = threading.Lock()
    
    def create_tracker(self, recording_id: str) -> AttentionTracker:
        """Create a new attention tracker"""
        with self.lock:
            if recording_id in self.active_trackers:
                return self.active_trackers[recording_id]
            
            tracker = AttentionTracker(recording_id, self.output_dir)
            self.active_trackers[recording_id] = tracker
            return tracker
    
    def start_tracking(self, recording_id: str):
        """Start tracking for a recording"""
        with self.lock:
            if recording_id in self.active_trackers:
                self.active_trackers[recording_id].start_tracking()
    
    def stop_tracking(self, recording_id: str):
        """Stop tracking for a recording"""
        with self.lock:
            if recording_id in self.active_trackers:
                self.active_trackers[recording_id].stop_tracking()
                del self.active_trackers[recording_id]
    
    def record_data(self, recording_id: str, stats: Dict[str, int], frame_timestamp: Optional[float] = None):
        """Record attention data for a recording"""
        with self.lock:
            if recording_id in self.active_trackers:
                self.active_trackers[recording_id].record_attention_data(stats, frame_timestamp)
    
    def get_tracker(self, recording_id: str) -> Optional[AttentionTracker]:
        """Get tracker for a recording"""
        with self.lock:
            return self.active_trackers.get(recording_id)
    
    def get_all_trackers(self) -> Dict[str, AttentionTracker]:
        """Get all active trackers"""
        with self.lock:
            return self.active_trackers.copy()
