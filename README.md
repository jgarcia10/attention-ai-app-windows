# Audience Attention Detector

A production-ready system for real-time and offline analysis of audience attention patterns using computer vision. The system detects people in video streams and classifies their attention level based on head pose and gaze direction.

## 🎯 Features

- **Real-time Processing**: Live webcam, RTSP/IP camera, and file streaming
- **Offline Processing**: Upload video files for batch processing
- **Multi-person Detection**: Simultaneous tracking of multiple people with stable IDs
- **Attention Classification**:
  - 🟢 **GREEN**: Looking at camera/front (attention on stage)
  - 🟡 **YELLOW**: Face visible but head/gaze turned away
  - 🔴 **RED**: Back facing camera or no face detected
- **Live Statistics**: Real-time stats with visual progress bars
- **Modern UI**: Clean React frontend with responsive design
- **Docker Support**: Easy deployment with Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Flask Backend  │
│   (Port 5173)   │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
            ┌───────▼───┐ ┌───▼───┐ ┌───▼────┐
            │   YOLO    │ │MediaPipe│ │ OpenCV │
            │ Detection │ │Head Pose│ │Drawing │
            └───────────┘ └─────────┘ └────────┘
```

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd attention-app
   ```

2. **Quick setup (Linux/Mac):**
   ```bash
   chmod +x docker-setup.sh
   ./docker-setup.sh
   ```

   **Quick setup (Windows):**
   ```cmd
   docker-setup.bat
   ```

3. **Manual setup:**
   ```bash
   # Create necessary directories
   mkdir -p backend/uploads backend/output backend/recordings backend/reports
   
   # Build and start services
   docker-compose up --build -d
   ```

4. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - Health Check: http://localhost:8000/api/health

### Local Development

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the YOLO model:**
   ```bash
   # Option 1: Using the setup script (requires ultralytics)
   python3 setup_model.py
   
   # Option 2: Using the simple download script (only requires requests)
   python3 download_model.py
   ```

5. **Set environment variables:**
   ```bash
   # When running from backend directory:
   export YOLO_MODEL_PATH=./models/yolov8n.pt
   
   # When running from root directory:
   export YOLO_MODEL_PATH=backend/models/yolov8n.pt
   export CONF_THRESHOLD=0.4
   export YAW_T=20
   export PITCH_T=15
   export STREAM_WIDTH=1280
   export STREAM_HEIGHT=720
   export STREAM_FPS=20
   ```

6. **Run the backend:**
   ```bash
   python3 app.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

## 📖 Usage Guide

### Live Stream Analysis

1. **Select Video Source:**
   - **Webcam**: Uses default system camera
   - **RTSP/IP Camera**: Enter RTSP URL (e.g., `rtsp://username:password@ip:port/stream`)
   - **Video File**: Specify path to local video file

2. **Configure Stream Settings:**
   - Resolution (width × height)
   - Frame rate (FPS)
   - Detection thresholds

3. **Start Streaming:**
   - Click "Start Stream" button
   - View live annotated video with colored bounding boxes
   - Monitor real-time statistics

### Video File Processing

1. **Upload Video:**
   - Drag and drop or browse for video file
   - Supported formats: MP4, AVI, MOV (max 500MB)

2. **Monitor Progress:**
   - View processing status and progress bar
   - Get notified when processing is complete

3. **Download Results:**
   - Download processed video with annotations
   - Video includes all overlays and statistics

### Configuration

Adjust detection parameters in the Settings tab:

- **Confidence Threshold**: YOLO detection confidence (0.1-1.0)
- **Yaw Threshold**: Head rotation threshold for attention classification (5-90°)
- **Pitch Threshold**: Head tilt threshold for attention classification (5-90°)

## 🛠️ Technical Details

### Backend Components

#### Core Modules
- **`detector.py`**: YOLO-based person detection
- **`head_pose.py`**: MediaPipe facial landmark detection and head pose estimation
- **`tracker.py`**: IoU-based person tracking for stable IDs
- **`pipeline.py`**: Main processing pipeline coordinating all components
- **`utils.py`**: Drawing and utility functions

#### Services
- **`stream.py`**: MJPEG streaming service for real-time video
- **`video_job.py`**: Background job processing for uploaded videos

#### API Endpoints
- `GET /api/health` - Health check
- `GET /api/stream` - MJPEG video stream
- `POST /api/upload` - Upload video for processing
- `GET /api/job/{id}/status` - Get job processing status
- `GET /api/job/{id}/result` - Download processed video
- `GET /api/stats/live` - Get live statistics
- `GET /api/config` - Get/update configuration

### Head Pose Estimation

The system uses MediaPipe FaceMesh to extract facial landmarks and estimates head pose using the PnP algorithm:

1. **Landmark Extraction**: 6 key facial points (nose tip, chin, eye corners, mouth corners)
2. **3D Model Matching**: Maps 2D landmarks to 3D face model
3. **Pose Calculation**: Uses `cv2.solvePnP` to compute rotation angles
4. **Classification**: Compares yaw/pitch angles against thresholds

### Performance Characteristics

- **Real-time Processing**: ~20-30 FPS on modern hardware
- **Memory Usage**: ~2-4GB depending on video resolution
- **GPU Acceleration**: Automatic CUDA support if available
- **Scalability**: Handles multiple concurrent streams

## 🧪 Testing

### Demo Script

Run the included demo script to test the system:

```bash
cd backend

# Test with webcam
python3 -m _samples.run_demo --mode webcam

# Create sample video
python3 -m _samples.run_demo --mode create-sample --output sample.mp4

# Process video file
python3 -m _samples.run_demo --mode video --input sample.mp4 --output result.mp4
```

### Manual Testing

1. **Webcam Test**: Verify detection with different head positions
2. **Multiple People**: Test with multiple people in frame
3. **Lighting Conditions**: Test in various lighting scenarios
4. **Video Upload**: Test with different video formats and resolutions

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `YOLO_MODEL_PATH` | `./models/yolov8n.pt` | Path to YOLO model file |
| `CONF_THRESHOLD` | `0.4` | YOLO detection confidence threshold |
| `YAW_T` | `20` | Head yaw threshold for attention (degrees) |
| `PITCH_T` | `15` | Head pitch threshold for attention (degrees) |
| `STREAM_WIDTH` | `1280` | Default stream width |
| `STREAM_HEIGHT` | `720` | Default stream height |
| `STREAM_FPS` | `20` | Default stream frame rate |

### Model Files

The YOLOv8n model is required for person detection. To set it up:

1. **Download the model:**
   ```bash
   python3 setup_model.py
   ```

2. **For custom models:**
   - Place model file in `backend/models/` directory
   - Update `YOLO_MODEL_PATH` environment variable
   - Ensure model supports person detection (class 0 in COCO)

**Note:** The model file (~6MB) is not included in the repository to keep it lightweight. Run the setup script after cloning to download it automatically.

## 🚨 Known Limitations

### Current Limitations

1. **Low Light Performance**: Reduced accuracy in poor lighting conditions
2. **Occlusion Handling**: Partial face occlusions may cause misclassification
3. **Profile Views**: Side profiles may be classified as "not facing" 
4. **Distance Sensitivity**: Very small faces (distant people) may not be detected
5. **Motion Blur**: Fast head movements may affect pose estimation accuracy

### Planned Improvements

- [ ] MediaPipe Pose integration for better back detection
- [ ] WebRTC support for lower-latency streaming
- [ ] Session metrics persistence and CSV export
- [ ] Advanced tracking algorithms (DeepSORT)
- [ ] Multi-camera support
- [ ] Real-time alerting system

## 🔒 Privacy & Compliance

### Privacy Considerations

- **In-Memory Processing**: No permanent storage of video data by default
- **Local Processing**: All AI processing happens locally (no cloud dependencies)
- **Configurable Retention**: Uploaded files and results can be automatically cleaned up
- **No PII Storage**: System doesn't store personally identifiable information

### Compliance Notes

- Ensure compliance with local privacy regulations (GDPR, CCPA, etc.)
- Obtain appropriate consent when using in public venues
- Consider data retention policies for your use case
- Review local laws regarding video recording and analysis

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues

**YOLO Model Download Fails:**
```bash
# Manually download model
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O backend/models/yolov8n.pt
```

**MediaPipe Installation Issues:**
```bash
# Reinstall MediaPipe
pip uninstall mediapipe
pip install mediapipe==0.10.7
```

**OpenCV Camera Access:**
```bash
# Linux: Add user to video group
sudo usermod -a -G video $USER
# Logout and login again
```

**Docker Issues:**

**Docker Build Fails:**
```bash
# Clean Docker cache and rebuild
docker system prune -a
docker-compose build --no-cache
```

**Model Download Fails in Docker:**
```bash
# Check if the model download step completed
docker-compose logs backend | grep -i "yolo\|model"
```

**Frontend Not Loading:**
```bash
# Check if frontend container is running
docker-compose ps frontend
# View frontend logs
docker-compose logs frontend
```

**Port Already in Use:**
```bash
# Check what's using the ports
netstat -tulpn | grep :80
netstat -tulpn | grep :8000
# Stop conflicting services or change ports in docker-compose.yml
```

#### Frontend Issues

**CORS Errors:**
- Ensure backend is running on port 8000
- Check `VITE_API_URL` environment variable

**Stream Not Loading:**
- Verify backend stream endpoint is accessible
- Check browser console for errors
- Try different video source

### Performance Issues

**High CPU Usage:**
- Reduce stream resolution and FPS
- Lower YOLO confidence threshold
- Use GPU acceleration if available

**Memory Issues:**
- Reduce video resolution
- Limit concurrent processing jobs
- Increase system swap space

### Debug Mode

Enable debug logging:

```bash
export FLASK_DEBUG=True
export FLASK_ENV=development
```

## 📝 API Documentation

### Stream Endpoint

```http
GET /api/stream?source=webcam&w=1280&h=720&fps=20
```

**Parameters:**
- `source`: `webcam`, `rtsp`, or `file`
- `path`: RTSP URL or file path (required for rtsp/file)
- `w`: Stream width (default: 1280)
- `h`: Stream height (default: 720)
- `fps`: Frame rate (default: 20)

### Upload Endpoint

```http
POST /api/upload
Content-Type: multipart/form-data

file: <video-file>
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "message": "Job created successfully"
}
```

### Statistics Endpoint

```http
GET /api/stats/live
```

**Response:**
```json
{
  "green": 2,
  "yellow": 1,
  "red": 0,
  "total": 3,
  "timestamp": 1699123456.789
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) for person detection
- [MediaPipe](https://mediapipe.dev/) for facial landmark detection
- [OpenCV](https://opencv.org/) for computer vision utilities
- [React](https://reactjs.org/) and [Vite](https://vitejs.dev/) for the frontend
- [Flask](https://flask.palletsprojects.com/) for the backend API

---

For support, please open an issue on the GitHub repository.

