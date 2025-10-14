import React from 'react';
import { Play, Square } from 'lucide-react';

interface VideoStreamProps {
  isStreaming: boolean;
  streamUrl: string;
}

const VideoStream: React.FC<VideoStreamProps> = ({ isStreaming, streamUrl }) => {
  return (
    <div className="relative">
      {/* Video Container */}
      <div className="aspect-video bg-gray-900 rounded-lg overflow-hidden">
        {isStreaming && streamUrl ? (
          <img
            src={streamUrl}
            alt="Live video stream"
            className="w-full h-full object-contain"
            style={{ imageRendering: 'auto' }}
            onError={(e) => {
              console.error('Stream error:', e);
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
                {isStreaming ? (
                  <Square className="h-full w-full" />
                ) : (
                  <Play className="h-full w-full" />
                )}
              </div>
              <h3 className="text-lg font-medium text-white mb-2">
                {isStreaming ? 'Starting stream...' : 'No active stream'}
              </h3>
              <p className="text-gray-400">
                {isStreaming
                  ? 'Please wait while the stream initializes'
                  : 'Configure your video source and click Start Stream'}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Stream Status Indicator */}
      {isStreaming && (
        <div className="absolute top-4 left-4">
          <div className="flex items-center space-x-2 bg-black bg-opacity-50 rounded-full px-3 py-1">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-white text-sm font-medium">LIVE</span>
          </div>
        </div>
      )}

      {/* Stream Info Overlay */}
      {isStreaming && streamUrl && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-black bg-opacity-50 rounded-lg p-3">
            <div className="text-white text-sm">
              <div className="flex justify-between items-center">
                <span>Status: Active</span>
                <span>Quality: Auto</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoStream;

