import React, { useState } from 'react';
import { Play, Square, Camera, Wifi, FileVideo } from 'lucide-react';
import { apiService, type Config, type StreamSource } from '../lib/api';

interface ControlsProps {
  config: Config | null;
  isStreaming: boolean;
  viewMode: string;
  onStartStream: (url: string) => void;
  onStopStream: () => void;
  onConfigUpdate: (config: Config) => void;
  onError: (error: string) => void;
}

const Controls: React.FC<ControlsProps> = ({
  config,
  isStreaming,
  viewMode,
  onStartStream,
  onStopStream,
  onConfigUpdate,
  onError,
}) => {
  const [source, setSource] = useState<'webcam' | 'rtsp' | 'file'>('webcam');
  const [rtspUrl, setRtspUrl] = useState('');
  const [filePath, setFilePath] = useState('');
  const [streamConfig, setStreamConfig] = useState({
    width: config?.stream_width || 1280,
    height: config?.stream_height || 720,
    fps: config?.stream_fps || 20,
  });

  const handleStartStream = async () => {
    try {
      const streamParams: StreamSource = {
        source,
        width: streamConfig.width,
        height: streamConfig.height,
        fps: streamConfig.fps,
      };

      if (source === 'rtsp' && rtspUrl) {
        streamParams.path = rtspUrl;
      } else if (source === 'file' && filePath) {
        streamParams.path = filePath;
      }

      const url = apiService.getStreamUrl(streamParams);
      onStartStream(url);
    } catch (error) {
      onError('Failed to start stream');
      console.error('Start stream error:', error);
    }
  };

  const handleConfigUpdate = async (updates: Partial<Config>) => {
    if (!config) return;

    try {
      const updatedConfig = await apiService.updateConfig(updates);
      onConfigUpdate(updatedConfig);
    } catch (error) {
      onError('Failed to update configuration');
      console.error('Config update error:', error);
    }
  };

  if (viewMode !== 'stream') {
    return null;
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Stream Controls</h3>

        {/* Source Selection */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            Video Source
          </label>
          
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="source"
                value="webcam"
                checked={source === 'webcam'}
                onChange={(e) => setSource(e.target.value as any)}
                className="mr-2"
              />
              <Camera className="h-4 w-4 mr-2" />
              Webcam
            </label>
            
            <label className="flex items-center">
              <input
                type="radio"
                name="source"
                value="rtsp"
                checked={source === 'rtsp'}
                onChange={(e) => setSource(e.target.value as any)}
                className="mr-2"
              />
              <Wifi className="h-4 w-4 mr-2" />
              RTSP/IP Camera
            </label>
            
            <label className="flex items-center">
              <input
                type="radio"
                name="source"
                value="file"
                checked={source === 'file'}
                onChange={(e) => setSource(e.target.value as any)}
                className="mr-2"
              />
              <FileVideo className="h-4 w-4 mr-2" />
              Video File
            </label>
          </div>
        </div>

        {/* RTSP URL Input */}
        {source === 'rtsp' && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              RTSP URL
            </label>
            <input
              type="text"
              value={rtspUrl}
              onChange={(e) => setRtspUrl(e.target.value)}
              placeholder="rtsp://username:password@ip:port/stream"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        {/* File Path Input */}
        {source === 'file' && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              File Path
            </label>
            <input
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="/path/to/video.mp4"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        {/* Stream Settings */}
        <div className="mt-6 space-y-4">
          <h4 className="text-sm font-medium text-gray-900">Stream Settings</h4>
          
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Width
              </label>
              <input
                type="number"
                value={streamConfig.width}
                onChange={(e) =>
                  setStreamConfig({
                    ...streamConfig,
                    width: parseInt(e.target.value) || 1280,
                  })
                }
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Height
              </label>
              <input
                type="number"
                value={streamConfig.height}
                onChange={(e) =>
                  setStreamConfig({
                    ...streamConfig,
                    height: parseInt(e.target.value) || 720,
                  })
                }
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              FPS
            </label>
            <input
              type="number"
              value={streamConfig.fps}
              onChange={(e) =>
                setStreamConfig({
                  ...streamConfig,
                  fps: parseInt(e.target.value) || 20,
                })
              }
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Control Buttons */}
        <div className="mt-6">
          {!isStreaming ? (
            <button
              onClick={handleStartStream}
              className="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <Play className="h-4 w-4 mr-2" />
              Start Stream
            </button>
          ) : (
            <button
              onClick={onStopStream}
              className="w-full flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <Square className="h-4 w-4 mr-2" />
              Stop Stream
            </button>
          )}
        </div>
      </div>

      {/* Detection Thresholds */}
      {config && (
        <div className="pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-4">
            Detection Thresholds
          </h4>
          
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Yaw Threshold (°)
              </label>
              <input
                type="number"
                value={config.yaw_threshold}
                onChange={(e) =>
                  handleConfigUpdate({
                    yaw_threshold: parseFloat(e.target.value) || 20,
                  })
                }
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Pitch Threshold (°)
              </label>
              <input
                type="number"
                value={config.pitch_threshold}
                onChange={(e) =>
                  handleConfigUpdate({
                    pitch_threshold: parseFloat(e.target.value) || 15,
                  })
                }
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Confidence Threshold
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="1.0"
                value={config.conf_threshold}
                onChange={(e) =>
                  handleConfigUpdate({
                    conf_threshold: parseFloat(e.target.value) || 0.4,
                  })
                }
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Controls;

