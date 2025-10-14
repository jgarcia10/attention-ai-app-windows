import React, { useState, useEffect } from 'react';
import { Video, Square, Clock, FileVideo, FileText, Download } from 'lucide-react';
import { apiService, type RecordingInfo, type RecordingSummary, type RecordingStatus } from '../lib/api';

interface RecordingControlsProps {
  streamType: 'single' | 'multi';
  isStreaming: boolean;
  onError: (error: string) => void;
}

const RecordingControls: React.FC<RecordingControlsProps> = ({ 
  streamType, 
  isStreaming, 
  onError 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingId, setRecordingId] = useState<string>('');
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordingStatus, setRecordingStatus] = useState<RecordingStatus | null>(null);
  const [recordingSummary, setRecordingSummary] = useState<RecordingSummary | null>(null);
  const [conferenceName, setConferenceName] = useState<string>('');
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportPath, setReportPath] = useState<string | null>(null);

  // Generate unique recording ID with conference name
  const generateRecordingId = () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const namePrefix = conferenceName.trim() 
      ? conferenceName.trim().replace(/[^a-zA-Z0-9\s-_]/g, '').replace(/\s+/g, '_')
      : 'conference';
    return `${namePrefix}_${streamType}_${timestamp}`;
  };

  // Start recording
  const handleStartRecording = async () => {
    if (!isStreaming) {
      onError('Cannot start recording: stream is not active');
      return;
    }

    try {
      const newRecordingId = generateRecordingId();
      const recordingInfo: RecordingInfo = await apiService.startRecording(
        newRecordingId,
        streamType,
        1280,
        720,
        20,
        conferenceName.trim() || undefined
      );

      setRecordingId(newRecordingId);
      setIsRecording(true);
      setRecordingDuration(0);
      setRecordingSummary(null);
      
      console.log('Recording started:', recordingInfo);
    } catch (error) {
      onError(`Failed to start recording: ${error}`);
      console.error('Start recording error:', error);
    }
  };

  // Stop recording
  const handleStopRecording = async () => {
    if (!recordingId) {
      onError('No active recording to stop');
      return;
    }

    try {
      const result = await apiService.stopRecording(recordingId, streamType);
      setRecordingSummary(result.summary);
      setIsRecording(false);
      setRecordingId('');
      setRecordingDuration(0);
      
      console.log('Recording stopped:', result);
    } catch (error) {
      onError(`Failed to stop recording: ${error}`);
      console.error('Stop recording error:', error);
    }
  };

  // Generate report
  const handleGenerateReport = async () => {
    if (!recordingSummary) return;

    setIsGeneratingReport(true);
    try {
      const result = await apiService.generateReport(recordingSummary.recording_id, streamType);
      setReportPath(result.report_path);
    } catch (error) {
      onError(`Error generating report: ${error}`);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // Download report
  const handleDownloadReport = () => {
    if (!reportPath) {
      console.error('No report path available for download');
      return;
    }
    
    const filename = reportPath.split('/').pop() || 'report.pdf';
    const downloadUrl = apiService.getReportDownloadUrl(filename);
    
    console.log('Downloading report:', { reportPath, filename, downloadUrl });
    
    // Create a temporary link to trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    link.target = '_blank'; // Open in new tab as fallback
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Also try window.open as fallback
    setTimeout(() => {
      window.open(downloadUrl, '_blank');
    }, 100);
  };

  // Update recording duration
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isRecording]);

  // Check recording status
  useEffect(() => {
    const checkRecordingStatus = async () => {
      try {
        const status = await apiService.getRecordingStatus(streamType);
        setRecordingStatus(status);
        
        // If we think we're recording but no active recordings, reset state
        if (isRecording && status.recording_count === 0) {
          setIsRecording(false);
          setRecordingId('');
          setRecordingDuration(0);
        }
      } catch (error) {
        console.error('Error checking recording status:', error);
      }
    };

    if (isStreaming) {
      checkRecordingStatus();
      const interval = setInterval(checkRecordingStatus, 5000); // Check every 5 seconds
      return () => clearInterval(interval);
    }
  }, [isStreaming, streamType, isRecording]);

  // Format duration
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-indigo-200/50 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent flex items-center">
          <FileVideo className="h-5 w-5 mr-2 text-red-600" />
          Conference Recording
        </h3>
        <div className="text-sm text-gray-600">
          {streamType === 'single' ? 'Single Camera' : 'Multi-Camera'}
        </div>
      </div>

      {/* Recording Status */}
      {isRecording && (
        <div className="mb-4 p-4 bg-red-50 rounded-xl border border-red-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-3"></div>
              <span className="text-sm font-medium text-red-800">
                Recording in progress...
              </span>
            </div>
            <div className="flex items-center text-red-600">
              <Clock className="h-4 w-4 mr-1" />
              <span className="text-sm font-mono">
                {formatDuration(recordingDuration)}
              </span>
            </div>
          </div>
          <div className="mt-2 text-xs text-red-600">
            {conferenceName && (
              <div>Conference: {conferenceName}</div>
            )}
            <div>Recording ID: {recordingId}</div>
          </div>
        </div>
      )}

      {/* Recording Summary */}
      {recordingSummary && (
        <div className="mb-4 p-4 bg-green-50 rounded-xl border border-green-200">
          <div className="flex items-center mb-2">
            <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <span className="text-sm font-medium text-green-800">
              Recording completed successfully
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-xs text-green-700">
            <div>
              <span className="font-medium">Duration:</span> {formatDuration(Math.floor(recordingSummary.duration))}
            </div>
            <div>
              <span className="font-medium">Frames:</span> {recordingSummary.frame_count}
            </div>
            <div>
              <span className="font-medium">Resolution:</span> {recordingSummary.width}x{recordingSummary.height}
            </div>
            <div>
              <span className="font-medium">File Size:</span> {formatFileSize(recordingSummary.file_size)}
            </div>
          </div>
          <div className="mt-2 text-xs text-green-600">
            Saved to: {recordingSummary.filepath}
          </div>
          
          {/* Report Generation */}
          <div className="mt-4 pt-4 border-t border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-medium text-green-800 mb-1">
                  Generate Attention Report
                </h4>
                <p className="text-xs text-green-600">
                  Create a detailed analysis report in Spanish
                </p>
              </div>
              <div className="flex space-x-2">
                {!reportPath ? (
                  <button
                    onClick={handleGenerateReport}
                    disabled={isGeneratingReport}
                    className={`flex items-center px-3 py-2 rounded-lg text-xs font-medium transition-all duration-300 ${
                      isGeneratingReport
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        : 'bg-blue-500 text-white hover:bg-blue-600 hover:scale-105'
                    }`}
                  >
                    <FileText className="h-4 w-4 mr-1" />
                    {isGeneratingReport ? 'Generating...' : 'Generate Report'}
                  </button>
                ) : (
                  <button
                    onClick={handleDownloadReport}
                    className="flex items-center px-3 py-2 rounded-lg text-xs font-medium bg-green-500 text-white hover:bg-green-600 hover:scale-105 transition-all duration-300"
                  >
                    <Download className="h-4 w-4 mr-1" />
                    Download Report
                  </button>
                )}
              </div>
            </div>
            {reportPath && (
              <div className="mt-2 text-xs text-green-600">
                Report generated successfully: {reportPath.split('/').pop()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Conference Name Input */}
      <div className="mb-4">
        <label htmlFor="conferenceName" className="block text-sm font-medium text-gray-700 mb-2">
          Conference Name
        </label>
        <input
          id="conferenceName"
          type="text"
          value={conferenceName}
          onChange={(e) => setConferenceName(e.target.value)}
          placeholder="Enter conference or presenter name..."
          disabled={isRecording}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        <p className="text-xs text-gray-500 mt-1">
          This will be included in the filename for easy identification
        </p>
      </div>

      {/* Recording Controls */}
      <div className="flex items-center justify-center space-x-4">
        {!isRecording ? (
          <button
            onClick={handleStartRecording}
            disabled={!isStreaming}
            className={`flex items-center px-6 py-3 rounded-xl font-semibold transition-all duration-300 ${
              isStreaming
                ? 'bg-gradient-to-r from-red-500 to-pink-600 text-white shadow-lg shadow-red-500/25 hover:shadow-red-500/40 hover:scale-105'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Video className="h-5 w-5 mr-2" />
            Start Recording
          </button>
        ) : (
          <button
            onClick={handleStopRecording}
            className="flex items-center px-6 py-3 rounded-xl font-semibold bg-gradient-to-r from-gray-600 to-gray-700 text-white shadow-lg shadow-gray-600/25 hover:shadow-gray-600/40 hover:scale-105 transition-all duration-300"
          >
            <Square className="h-5 w-5 mr-2" />
            Stop Recording
          </button>
        )}
      </div>

      {/* Recording Info */}
      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">
          {isStreaming 
            ? 'Ready to record your conference with attention estimation'
            : 'Start streaming to enable recording'
          }
        </p>
        {recordingStatus && recordingStatus.recording_count > 0 && (
          <p className="text-xs text-blue-600 mt-1">
            {recordingStatus.recording_count} active recording(s)
          </p>
        )}
      </div>
    </div>
  );
};

export default RecordingControls;
