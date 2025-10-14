"""
Pydantic models for request/response DTOs
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class StreamSource(str, Enum):
    WEBCAM = "webcam"
    RTSP = "rtsp"
    FILE = "file"


class JobState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: float
    version: str = "1.0.0"


class StreamRequest(BaseModel):
    source: StreamSource
    path: Optional[str] = None
    width: int = Field(default=1280, ge=320, le=1920)
    height: int = Field(default=720, ge=240, le=1080)
    fps: int = Field(default=20, ge=1, le=60)


class StatsResponse(BaseModel):
    green: int = 0
    yellow: int = 0
    red: int = 0
    total: int = 0
    timestamp: float
    green_pct: Optional[float] = None
    yellow_pct: Optional[float] = None
    red_pct: Optional[float] = None


class JobCreateResponse(BaseModel):
    job_id: str
    message: str = "Job created successfully"


class JobStatusResponse(BaseModel):
    job_id: str
    state: JobState
    progress: int = Field(ge=0, le=100)
    error: Optional[str] = None
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


class ConfigResponse(BaseModel):
    yolo_model_path: str
    conf_threshold: float
    yaw_threshold: float
    pitch_threshold: float
    stream_width: int
    stream_height: int
    stream_fps: int


class ConfigUpdateRequest(BaseModel):
    conf_threshold: Optional[float] = Field(None, ge=0.1, le=1.0)
    yaw_threshold: Optional[float] = Field(None, ge=5.0, le=90.0)
    pitch_threshold: Optional[float] = Field(None, ge=5.0, le=90.0)
    stream_width: Optional[int] = Field(None, ge=320, le=1920)
    stream_height: Optional[int] = Field(None, ge=240, le=1080)
    stream_fps: Optional[int] = Field(None, ge=1, le=60)


class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: float

