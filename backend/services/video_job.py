"""
Video job processing service for offline video processing
"""
import cv2
import os
import uuid
import threading
import time
from typing import Dict, Any, Optional
from core.pipeline import AttentionPipeline


class VideoJobManager:
    def __init__(self, pipeline: AttentionPipeline, output_dir: str = "./output"):
        """Initialize video job manager"""
        self.pipeline = pipeline
        self.output_dir = output_dir
        self.jobs = {}  # {job_id: job_info}
        self.job_lock = threading.Lock()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def create_job(self, input_path: str) -> str:
        """
        Create a new video processing job
        
        Args:
            input_path: Path to input video file
            
        Returns:
            Job ID string
        """
        job_id = str(uuid.uuid4())
        
        with self.job_lock:
            self.jobs[job_id] = {
                'job_id': job_id,
                'input_path': input_path,
                'output_path': os.path.join(self.output_dir, f"{job_id}_processed.mp4"),
                'state': 'pending',
                'progress': 0,
                'error': None,
                'created_at': time.time(),
                'started_at': None,
                'completed_at': None
            }
        
        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_video,
            args=(job_id,),
            daemon=True
        )
        thread.start()
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and progress"""
        with self.job_lock:
            return self.jobs.get(job_id, {}).copy() if job_id in self.jobs else None
    
    def get_job_result_path(self, job_id: str) -> Optional[str]:
        """Get path to processed video result"""
        job = self.get_job_status(job_id)
        if job and job['state'] == 'done' and os.path.exists(job['output_path']):
            return job['output_path']
        return None
    
    def _process_video(self, job_id: str):
        """Process video file (runs in background thread)"""
        with self.job_lock:
            if job_id not in self.jobs:
                return
            
            job = self.jobs[job_id]
            job['state'] = 'running'
            job['started_at'] = time.time()
        
        try:
            input_path = job['input_path']
            output_path = job['output_path']
            
            # Open input video
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise Exception(f"Could not open video file: {input_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise Exception(f"Could not create output video: {output_path}")
            
            # Reset pipeline for clean processing
            self.pipeline.reset()
            
            frame_count = 0
            
            print(f"Processing video {job_id}: {total_frames} frames at {fps} FPS")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                annotated_frame, stats = self.pipeline.process_frame(frame, width, height)
                
                # Write processed frame
                out.write(annotated_frame)
                
                frame_count += 1
                
                # Update progress
                progress = int((frame_count / total_frames) * 100)
                with self.job_lock:
                    self.jobs[job_id]['progress'] = progress
                
                # Log progress periodically
                if frame_count % (fps * 10) == 0:  # Every 10 seconds
                    print(f"Job {job_id}: {progress}% complete ({frame_count}/{total_frames})")
            
            # Clean up
            cap.release()
            out.release()
            
            # Mark as completed
            with self.job_lock:
                self.jobs[job_id]['state'] = 'done'
                self.jobs[job_id]['progress'] = 100
                self.jobs[job_id]['completed_at'] = time.time()
            
            print(f"Job {job_id} completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing job {job_id}: {error_msg}")
            
            with self.job_lock:
                self.jobs[job_id]['state'] = 'error'
                self.jobs[job_id]['error'] = error_msg
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        jobs_to_remove = []
        
        with self.job_lock:
            for job_id, job in self.jobs.items():
                job_age = current_time - job['created_at']
                
                if (job_age > max_age_seconds and 
                    job['state'] in ['done', 'error']):
                    jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            self._remove_job(job_id)
    
    def _remove_job(self, job_id: str):
        """Remove job and clean up files"""
        with self.job_lock:
            if job_id in self.jobs:
                job = self.jobs[job_id]
                
                # Remove output file if it exists
                if os.path.exists(job['output_path']):
                    try:
                        os.remove(job['output_path'])
                    except Exception as e:
                        print(f"Error removing output file for job {job_id}: {e}")
                
                # Remove job from memory
                del self.jobs[job_id]

