"""
Utility functions for drawing overlays and processing
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple


def draw_overlays(frame: np.ndarray, detections: List[Dict[str, Any]]) -> np.ndarray:
    """
    Draw bounding boxes, labels, and direction arrows on frame
    
    Args:
        frame: Input frame
        detections: List of detection results with bbox, status, id, and optional head_vector
        
    Returns:
        Annotated frame
    """
    annotated = frame.copy()
    
    # Color mapping for status
    colors = {
        "Looking at camera": (0, 255, 0),    # Green - looking at camera
        "Not looking at camera": (0, 255, 255), # Yellow - not looking at camera
        "No face detected": (0, 0, 255)  # Red - no face detected
    }
    
    for detection in detections:
        bbox = detection['bbox']
        status = detection.get('status', 'UNKNOWN')
        person_id = detection.get('id', 0)
        head_vector = detection.get('head_vector')
        
        x1, y1, x2, y2 = bbox
        color = colors.get(status, (128, 128, 128))
        
        # Draw bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Draw label with confidence if available
        confidence = detection.get('attention_confidence', 0.0)
        if confidence > 0:
            label = f"#{person_id} {status} ({confidence:.2f})"
        else:
            label = f"#{person_id} {status}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        
        # Background for label
        cv2.rectangle(annotated, 
                     (x1, y1 - label_size[1] - 10), 
                     (x1 + label_size[0], y1), 
                     color, -1)
        
        # Label text
        cv2.putText(annotated, label, 
                   (x1, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                   (255, 255, 255), 2)
        
        # Draw direction arrow if available
        if head_vector and len(head_vector) == 2:
            center_x = (x1 + x2) // 2
            center_y = y1 + 20  # Slightly below the top of the box
            
            dx, dy = head_vector
            arrow_length = 30
            
            end_x = int(center_x + dx * arrow_length)
            end_y = int(center_y + dy * arrow_length)
            
            # Draw arrow
            cv2.arrowedLine(annotated, 
                          (center_x, center_y), 
                          (end_x, end_y), 
                          color, 2, tipLength=0.3)
    
    return annotated


def count_statuses(detections: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count detections by status
    
    Args:
        detections: List of detection results
        
    Returns:
        Dictionary with counts for each status
    """
    counts = {"green": 0, "yellow": 0, "red": 0, "total": 0}
    
    for detection in detections:
        status = detection.get('status', '')
        
        # Map status labels to color keys for API compatibility
        if status == "Looking at camera":
            counts["green"] += 1
        elif status == "Not looking at camera":
            counts["yellow"] += 1
        elif status == "No face detected":
            counts["red"] += 1
        
        counts['total'] += 1
    
    return counts


def add_stats_overlay(frame: np.ndarray, counts: Dict[str, int]) -> np.ndarray:
    """
    Add statistics overlay to frame
    
    Args:
        frame: Input frame
        counts: Status counts dictionary
        
    Returns:
        Frame with stats overlay
    """
    annotated = frame.copy()
    height, width = frame.shape[:2]
    
    # Create stats text with new labels
    stats_text = f"Looking at camera: {counts['green']} | Not looking: {counts['yellow']} | No face: {counts['red']} | Total: {counts['total']}"
    
    # Get text size
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    text_size = cv2.getTextSize(stats_text, font, font_scale, thickness)[0]
    
    # Position at top-right
    text_x = width - text_size[0] - 10
    text_y = 30
    
    # Background rectangle
    cv2.rectangle(annotated, 
                 (text_x - 10, text_y - text_size[1] - 10), 
                 (width, text_y + 10), 
                 (0, 0, 0), -1)
    
    # Text
    cv2.putText(annotated, stats_text, 
               (text_x, text_y), 
               font, font_scale, 
               (255, 255, 255), thickness)
    
    return annotated


def resize_frame(frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
    """
    Resize frame while maintaining aspect ratio
    
    Args:
        frame: Input frame
        target_width: Target width
        target_height: Target height
        
    Returns:
        Resized frame
    """
    height, width = frame.shape[:2]
    
    # Calculate scaling factor
    scale_w = target_width / width
    scale_h = target_height / height
    scale = min(scale_w, scale_h)
    
    # Calculate new dimensions
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize frame
    resized = cv2.resize(frame, (new_width, new_height))
    
    # Create canvas with target size
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    
    # Center the resized frame
    start_x = (target_width - new_width) // 2
    start_y = (target_height - new_height) // 2
    
    canvas[start_y:start_y + new_height, start_x:start_x + new_width] = resized
    
    return canvas

