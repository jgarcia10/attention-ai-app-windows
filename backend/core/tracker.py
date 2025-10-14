"""
Simple IoU-based person tracker for maintaining consistent IDs across frames
"""
import numpy as np
from typing import List, Dict, Any, Tuple


class PersonTracker:
    def __init__(self, iou_threshold: float = 0.3, max_disappeared: int = 15):
        """
        Initialize person tracker
        
        Args:
            iou_threshold: Minimum IoU for matching detections to tracks (reduced for better matching)
            max_disappeared: Maximum frames a track can be missing before removal (reduced for responsiveness)
        """
        self.iou_threshold = iou_threshold
        self.max_disappeared = max_disappeared
        
        self.tracks = {}  # {track_id: track_info}
        self.next_id = 1
        self.frame_count = 0
    
    def calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bounding boxes
        
        Args:
            box1: [x1, y1, x2, y2]
            box2: [x1, y1, x2, y2]
            
        Returns:
            IoU value between 0 and 1
        """
        # Calculate intersection area
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        
        # Calculate union area
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        if union <= 0:
            return 0.0
        
        return intersection / union
    
    def _get_center(self, bbox: List[int]) -> Tuple[float, float]:
        """Get center point of bounding box"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update tracker with new detections and assign IDs
        
        Args:
            detections: List of detection dictionaries with 'bbox' key
            
        Returns:
            List of detections with assigned 'id' field
        """
        self.frame_count += 1
        
        if not detections:
            # Mark all tracks as disappeared
            for track_id in self.tracks:
                self.tracks[track_id]['disappeared'] += 1
            
            # Remove tracks that have been missing too long
            self._cleanup_tracks()
            return []
        
        # If no existing tracks, assign new IDs to all detections
        if not self.tracks:
            for detection in detections:
                detection['id'] = self.next_id
                self.tracks[self.next_id] = {
                    'bbox': detection['bbox'],
                    'disappeared': 0,
                    'last_seen': self.frame_count
                }
                self.next_id += 1
            return detections
        
        # Match detections to existing tracks using improved algorithm
        matched_tracks = set()
        matched_detections = set()
        
        # Create a list of (detection_idx, track_id, score) tuples for all possible matches
        match_candidates = []
        
        for i, detection in enumerate(detections):
            for track_id, track in self.tracks.items():
                if track_id in matched_tracks:
                    continue
                
                iou = self.calculate_iou(detection['bbox'], track['bbox'])
                if iou > self.iou_threshold:
                    # Calculate center distance as additional metric
                    det_center = self._get_center(detection['bbox'])
                    track_center = self._get_center(track['bbox'])
                    distance = np.sqrt((det_center[0] - track_center[0])**2 + (det_center[1] - track_center[1])**2)
                    
                    # Combined score: IoU weighted more heavily, but distance also considered
                    # Normalize distance (assuming max reasonable distance is 200 pixels)
                    normalized_distance = min(distance / 200.0, 1.0)
                    score = iou * 0.8 + (1.0 - normalized_distance) * 0.2
                    
                    match_candidates.append((i, track_id, score))
        
        # Sort by score (highest first) and assign matches greedily
        match_candidates.sort(key=lambda x: x[2], reverse=True)
        
        for detection_idx, track_id, score in match_candidates:
            if detection_idx not in matched_detections and track_id not in matched_tracks:
                # Match found
                detection = detections[detection_idx]
                detection['id'] = track_id
                self.tracks[track_id]['bbox'] = detection['bbox']
                self.tracks[track_id]['disappeared'] = 0
                self.tracks[track_id]['last_seen'] = self.frame_count
                
                matched_tracks.add(track_id)
                matched_detections.add(detection_idx)
        
        # Create new tracks for unmatched detections
        for i, detection in enumerate(detections):
            if i not in matched_detections:
                detection['id'] = self.next_id
                self.tracks[self.next_id] = {
                    'bbox': detection['bbox'],
                    'disappeared': 0,
                    'last_seen': self.frame_count
                }
                self.next_id += 1
        
        # Mark unmatched tracks as disappeared
        for track_id in self.tracks:
            if track_id not in matched_tracks:
                self.tracks[track_id]['disappeared'] += 1
        
        # Remove tracks that have been missing too long
        self._cleanup_tracks()
        
        return detections
    
    def _cleanup_tracks(self):
        """Remove tracks that have been missing for too long"""
        tracks_to_remove = []
        
        for track_id, track in self.tracks.items():
            if track['disappeared'] > self.max_disappeared:
                tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.tracks[track_id]
    
    def get_disappeared_track_ids(self) -> List[int]:
        """Get list of track IDs that have disappeared (for cleanup purposes)"""
        return [track_id for track_id, track in self.tracks.items() 
                if track['disappeared'] > self.max_disappeared]
    
    def get_active_track_count(self) -> int:
        """Get number of currently active tracks"""
        return len([track for track in self.tracks.values() if track['disappeared'] == 0])
    
    def reset(self):
        """Reset tracker state"""
        self.tracks = {}
        self.next_id = 1
        self.frame_count = 0

