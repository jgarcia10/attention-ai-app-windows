import React, { useState, useRef } from 'react';
import { Upload, FileVideo, Download, Clock, CheckCircle, XCircle } from 'lucide-react';
import { apiService, type JobStatus } from '../lib/api';

interface UploadProcessorProps {
  onError: (error: string) => void;
}

const UploadProcessor: React.FC<UploadProcessorProps> = ({ onError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [currentJob, setCurrentJob] = useState<JobStatus | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo'];

  const handleFileSelect = (file: File) => {
    if (!allowedTypes.includes(file.type)) {
      onError('Please select a valid video file (MP4, AVI, MOV)');
      return;
    }

    if (file.size > 500 * 1024 * 1024) { // 500MB limit
      onError('File size must be less than 500MB');
      return;
    }

    uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    
    try {
      const response = await apiService.uploadVideo(file);
      const jobId = response.job_id;
      
      // Start polling for job status
      pollJobStatus(jobId);
      
    } catch (error) {
      onError('Failed to upload video file');
      setIsUploading(false);
      console.error('Upload error:', error);
    }
  };

  const pollJobStatus = async (jobId: string) => {
    try {
      const status = await apiService.getJobStatus(jobId);
      setCurrentJob(status);
      
      if (status.state === 'running' || status.state === 'pending') {
        // Continue polling
        setTimeout(() => pollJobStatus(jobId), 2000);
      } else {
        setIsUploading(false);
      }
    } catch (error) {
      onError('Failed to get job status');
      setIsUploading(false);
      console.error('Job status error:', error);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const downloadResult = () => {
    if (currentJob && currentJob.state === 'done') {
      const downloadUrl = apiService.getJobResultUrl(currentJob.job_id);
      window.open(downloadUrl, '_blank');
    }
  };

  const resetJob = () => {
    setCurrentJob(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusIcon = (state: string) => {
    switch (state) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'running':
        return <Clock className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'done':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = (state: string) => {
    switch (state) {
      case 'pending':
        return 'Queued for processing';
      case 'running':
        return 'Processing video';
      case 'done':
        return 'Processing complete';
      case 'error':
        return 'Processing failed';
      default:
        return '';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-2">
          Process Video File
        </h2>
        <p className="text-sm text-gray-600">
          Upload a video file to analyze audience attention patterns. 
          Supported formats: MP4, AVI, MOV (max 500MB)
        </p>
      </div>

      {!currentJob && (
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <FileVideo className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-900">
              Drop your video file here
            </p>
            <p className="text-sm text-gray-600">or</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <Upload className="h-4 w-4 mr-2" />
              Browse Files
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".mp4,.avi,.mov"
            onChange={handleFileInputChange}
            className="hidden"
          />
        </div>
      )}

      {currentJob && (
        <div className="bg-gray-50 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              {getStatusIcon(currentJob.state)}
              <div>
                <h3 className="text-sm font-medium text-gray-900">
                  Job ID: {currentJob.job_id.substring(0, 8)}...
                </h3>
                <p className="text-sm text-gray-600">
                  {getStatusText(currentJob.state)}
                </p>
              </div>
            </div>
            
            {currentJob.state === 'done' && (
              <button
                onClick={downloadResult}
                className="inline-flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </button>
            )}
          </div>

          {/* Progress Bar */}
          {(currentJob.state === 'running' || currentJob.state === 'pending') && (
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Progress</span>
                <span>{currentJob.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${currentJob.progress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Job Details */}
          <div className="text-xs text-gray-500 space-y-1">
            <div>Created: {new Date(currentJob.created_at * 1000).toLocaleString()}</div>
            {currentJob.started_at && (
              <div>Started: {new Date(currentJob.started_at * 1000).toLocaleString()}</div>
            )}
            {currentJob.completed_at && (
              <div>Completed: {new Date(currentJob.completed_at * 1000).toLocaleString()}</div>
            )}
            {currentJob.error && (
              <div className="text-red-600">Error: {currentJob.error}</div>
            )}
          </div>

          {/* Reset Button */}
          {(currentJob.state === 'done' || currentJob.state === 'error') && (
            <div className="mt-4">
              <button
                onClick={resetJob}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Process another video
              </button>
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          How it works:
        </h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Upload your video file (MP4, AVI, or MOV format)</li>
          <li>• The system will detect people and analyze their attention patterns</li>
          <li>• Each person gets a colored bounding box indicating their attention level</li>
          <li>• Download the processed video with overlays when complete</li>
        </ul>
      </div>
    </div>
  );
};

export default UploadProcessor;

