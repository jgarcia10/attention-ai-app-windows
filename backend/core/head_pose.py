"""
MediaPipe-based head pose estimation using facial landmarks
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import Tuple, Optional, List
import os


class HeadPoseEstimator:
    def __init__(self, yaw_threshold: float = 25.0, pitch_threshold: float = 20.0):
        """Initialize MediaPipe face mesh and head pose estimator"""
        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold
        
        # Temporal smoothing for head pose
        self.pose_history = {}  # {person_id: [recent_poses]}
        self.max_history = 12  # Keep last 12 poses for smoothing (increased for maximum stability)
        
        # Attention confidence tracking
        self.attention_confidence = {}  # {person_id: confidence_score}
        self.min_attention_confidence = 0.7  # Minimum confidence to classify as "Atencion"
        
        # Initialize MediaPipe Face Mesh with higher confidence thresholds
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=10,  # Allow up to 10 faces for multi-person scenarios
            refine_landmarks=True,
            min_detection_confidence=0.7,  # Increased for better face detection quality
            min_tracking_confidence=0.7    # Increased for better tracking quality
        )
        
        # 3D model points for key facial landmarks (in mm)
        # These are standard facial model points used in head pose estimation
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip (1)
            (0.0, -330.0, -65.0),        # Chin (152)
            (-225.0, 170.0, -135.0),     # Left eye left corner (33)
            (225.0, 170.0, -135.0),      # Right eye right corner (263)
            (-150.0, -150.0, -125.0),    # Left Mouth corner (61)
            (150.0, -150.0, -125.0)      # Right mouth corner (291)
        ], dtype=np.float64)
        
        # Landmark indices for the 6 key points
        self.landmark_indices = [1, 152, 33, 263, 61, 291]
    
    def get_face_landmarks(self, roi: np.ndarray) -> Optional[List]:
        """Extract facial landmarks from ROI using MediaPipe"""
        try:
            # Convert BGR to RGB
            rgb_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            
            # Process the image
            results = self.face_mesh.process(rgb_roi)
            
            if results.multi_face_landmarks:
                # For single ROI, return the first (and likely only) face detected
                # The multi-face capability is used when processing the full frame
                return results.multi_face_landmarks[0].landmark
            
            return None
            
        except Exception as e:
            print(f"Error in face landmark detection: {e}")
            return None
    
    def estimate_head_pose(self, face_landmarks, roi_shape: Tuple[int, int]) -> Tuple[float, float]:
        """
        Estimate head pose (yaw, pitch) from facial landmarks using SolvePnP
        
        Args:
            face_landmarks: MediaPipe face landmarks
            roi_shape: Shape of the ROI (height, width)
            
        Returns:
            Tuple of (yaw_degrees, pitch_degrees)
        """
        if face_landmarks is None:
            return 0.0, 0.0
        
        try:
            height, width = roi_shape[:2]
            
            # Extract 2D points for the 6 key landmarks
            image_points = []
            for idx in self.landmark_indices:
                landmark = face_landmarks[idx]
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                image_points.append([x, y])
            
            image_points = np.array(image_points, dtype=np.float64)
            
            # Camera matrix (assuming no lens distortion for simplicity)
            focal_length = width
            center = (width / 2, height / 2)
            camera_matrix = np.array([
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)
            
            # Distortion coefficients (assuming no distortion)
            dist_coeffs = np.zeros((4, 1))
            
            # Solve PnP to get rotation and translation vectors
            success, rotation_vector, translation_vector = cv2.solvePnP(
                self.model_points,
                image_points,
                camera_matrix,
                dist_coeffs
            )
            
            if not success:
                return 0.0, 0.0
            
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            
            # Extract Euler angles from rotation matrix
            # This is a simplified extraction - in practice, you might want more robust angle extraction
            yaw = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
            pitch = np.arctan2(-rotation_matrix[2, 0], 
                             np.sqrt(rotation_matrix[2, 1]**2 + rotation_matrix[2, 2]**2))
            
            # Convert from radians to degrees
            yaw_degrees = np.degrees(yaw)
            pitch_degrees = np.degrees(pitch)
            
            return float(yaw_degrees), float(pitch_degrees)
            
        except Exception as e:
            print(f"Error in head pose estimation: {e}")
            return 0.0, 0.0
    
    def classify_attention(self, yaw: float, pitch: float, person_id: int = None) -> str:
        """
        Classify attention status based on head pose angles with confidence scoring
        
        Args:
            yaw: Yaw angle in degrees
            pitch: Pitch angle in degrees
            person_id: Person ID for confidence tracking
            
        Returns:
            Status string: "Looking at camera", "Not looking at camera", or "No face detected"
        """
        # Calculate attention confidence based on how close to center the head is
        yaw_confidence = max(0, 1.0 - abs(yaw) / 90.0)  # 1.0 when yaw=0, 0.0 when yaw=±90
        pitch_confidence = max(0, 1.0 - abs(pitch) / 90.0)  # 1.0 when pitch=0, 0.0 when pitch=±90
        
        # Combined confidence (weighted average)
        attention_confidence = (yaw_confidence * 0.6 + pitch_confidence * 0.4)
        
        # Update confidence history for this person
        if person_id is not None:
            if person_id not in self.attention_confidence:
                self.attention_confidence[person_id] = []
            
            self.attention_confidence[person_id].append(attention_confidence)
            
            # Keep only recent confidence scores (last 10 frames)
            if len(self.attention_confidence[person_id]) > 10:
                self.attention_confidence[person_id].pop(0)
            
            # Use average confidence over recent frames
            avg_confidence = sum(self.attention_confidence[person_id]) / len(self.attention_confidence[person_id])
        else:
            avg_confidence = attention_confidence
        
        # Classify based on both angle thresholds and confidence
        if (abs(yaw) <= self.yaw_threshold and 
            abs(pitch) <= self.pitch_threshold and 
            avg_confidence >= self.min_attention_confidence):
            return "Looking at camera"  # Green - looking at camera/front with high confidence
        else:
            return "Not looking at camera"  # Yellow - face visible but head turned away
    
    def get_direction_vector(self, yaw: float, pitch: float) -> Tuple[float, float]:
        """
        Get direction vector for drawing arrow overlay
        
        Args:
            yaw: Yaw angle in degrees
            pitch: Pitch angle in degrees
            
        Returns:
            Normalized direction vector (dx, dy)
        """
        # Convert to radians
        yaw_rad = np.radians(yaw)
        pitch_rad = np.radians(pitch)
        
        # Calculate direction vector
        dx = np.sin(yaw_rad)
        dy = -np.sin(pitch_rad)  # Negative because image Y axis is inverted
        
        # Normalize
        magnitude = np.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
        
        return float(dx), float(dy)
    
    def smooth_pose(self, person_id: int, yaw: float, pitch: float) -> Tuple[float, float]:
        """
        Apply temporal smoothing to head pose angles
        
        Args:
            person_id: Unique identifier for the person
            yaw: Current yaw angle
            pitch: Current pitch angle
            
        Returns:
            Smoothed (yaw, pitch) angles
        """
        if person_id not in self.pose_history:
            self.pose_history[person_id] = []
        
        # Add current pose to history
        self.pose_history[person_id].append((yaw, pitch))
        
        # Keep only recent poses
        if len(self.pose_history[person_id]) > self.max_history:
            self.pose_history[person_id].pop(0)
        
        # Calculate smoothed pose (simple moving average)
        poses = self.pose_history[person_id]
        if len(poses) == 1:
            return yaw, pitch
        
        # Use weighted average (more weight to recent poses)
        weights = list(range(1, len(poses) + 1))
        total_weight = sum(weights)
        
        smoothed_yaw = sum(pose[0] * weight for pose, weight in zip(poses, weights)) / total_weight
        smoothed_pitch = sum(pose[1] * weight for pose, weight in zip(poses, weights)) / total_weight
        
        return smoothed_yaw, smoothed_pitch
    
    def clear_history(self, person_id: int = None):
        """Clear pose history and attention confidence for a specific person or all persons"""
        if person_id is not None:
            if person_id in self.pose_history:
                del self.pose_history[person_id]
            if person_id in self.attention_confidence:
                del self.attention_confidence[person_id]
        else:
            self.pose_history.clear()
            self.attention_confidence.clear()
    
    def get_last_known_pose(self, person_id: int) -> Tuple[float, float]:
        """Get the last known pose for a person (useful when face detection fails temporarily)"""
        if person_id in self.pose_history and self.pose_history[person_id]:
            return self.pose_history[person_id][-1]
        return 0.0, 0.0
    
    def get_attention_confidence(self, person_id: int) -> float:
        """Get the current attention confidence for a person"""
        if person_id in self.attention_confidence and self.attention_confidence[person_id]:
            return sum(self.attention_confidence[person_id]) / len(self.attention_confidence[person_id])
        return 0.0

