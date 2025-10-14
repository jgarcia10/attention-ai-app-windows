# Multi-Person Attention Detection Improvements

## Issues Fixed

### 1. MediaPipe Face Detection Limit
**Problem**: The system was configured with `max_num_faces=1`, limiting face detection to only one person at a time.

**Solution**: 
- Increased `max_num_faces` to 10 to support multiple people
- Updated face landmark detection to handle multiple faces properly

### 2. Pose Smoothing ID Mismatch
**Problem**: Pose smoothing was using temporary detection indices instead of actual person IDs from the tracker, causing inconsistent smoothing across frames.

**Solution**:
- Restructured the pipeline to apply pose smoothing after person tracking
- Now uses actual person IDs from the tracker for consistent pose history
- Added cleanup for pose history when tracks disappear

### 3. Tracking Instability
**Problem**: Simple IoU-based tracking was not robust enough for complex multi-person scenarios.

**Solution**:
- Improved matching algorithm using combined IoU and distance metrics
- Reduced IoU threshold from 0.4 to 0.3 for better matching
- Reduced max_disappeared from 20 to 15 frames for more responsive tracking
- Added greedy matching with score-based prioritization

### 4. Face Detection Failures
**Problem**: When face detection failed temporarily, the system would lose track of attention status.

**Solution**:
- Added fallback to last known pose when face detection fails
- Maintains attention status continuity for tracked persons
- Prevents attention status from jumping between "No atencion" and other states

## Technical Improvements

### Enhanced Tracker (`core/tracker.py`)
- **Improved matching algorithm**: Combines IoU (80% weight) and distance (20% weight) for better person matching
- **Greedy assignment**: Sorts matches by score and assigns best matches first
- **Better thresholds**: Reduced IoU threshold and max_disappeared for more responsive tracking
- **Memory management**: Added method to get disappeared track IDs for cleanup

### Enhanced Head Pose Estimator (`core/head_pose.py`)
- **Multi-face support**: Increased max_num_faces to 10
- **Pose continuity**: Added method to get last known pose for fallback
- **Better memory management**: Improved cleanup of pose history

### Enhanced Pipeline (`core/pipeline.py`)
- **Proper ID usage**: Pose smoothing now uses actual person IDs from tracker
- **Fallback mechanism**: Uses last known pose when face detection fails
- **Memory cleanup**: Automatically cleans up pose history for disappeared tracks
- **Better processing order**: Tracking happens before pose smoothing for consistent IDs

## Configuration Changes

### Default Parameters
- `iou_threshold`: 0.4 → 0.3 (better matching)
- `max_disappeared`: 20 → 15 frames (more responsive)
- `max_num_faces`: 1 → 10 (multi-person support)

## Testing

A test script `test_multi_person.py` has been created to verify the improvements:
- Tests multi-person detection with webcam or video file
- Displays real-time statistics
- Allows pipeline reset during testing
- Shows frame-by-frame processing results

## Expected Results

With these improvements, the system should now:
1. **Detect multiple people simultaneously** without jumping between IDs
2. **Maintain consistent attention tracking** for each person across frames
3. **Provide smoother attention status transitions** with proper temporal smoothing
4. **Handle temporary face detection failures** gracefully
5. **Be more responsive** to people entering/leaving the scene

## Usage

The improvements are automatically applied when using the existing API endpoints. No changes to the frontend or API are required.

To test the improvements:
```bash
cd backend
python3 test_multi_person.py
```

Or use the existing API endpoints with multi-person videos to see the improved behavior.
