import { useState, useEffect } from 'react';
import { Monitor, Upload, Settings, Activity, Camera } from 'lucide-react';
import VideoStream from './components/VideoStream';
import UploadProcessor from './components/UploadProcessor';
import Controls from './components/Controls';
import MultiCameraControls from './components/MultiCameraControls';
import RecordingControls from './components/RecordingControls';
import StatsBar from './components/StatsBar';
import { apiService, type Config, type Stats, type MultiCameraStats } from './lib/api';

type ViewMode = 'stream' | 'multi-camera' | 'upload' | 'settings';

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('stream');
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamUrl, setStreamUrl] = useState<string>('');
  const [config, setConfig] = useState<Config | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [multiCameraStats, setMultiCameraStats] = useState<MultiCameraStats | null>(null);
  const [error, setError] = useState<string>('');

  // Load initial configuration
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const configData = await apiService.getConfig();
        setConfig(configData);
      } catch (err) {
        setError('Failed to load configuration');
        console.error('Config load error:', err);
      }
    };

    loadConfig();
  }, []);

  // Poll for live stats when streaming
  useEffect(() => {
    if (!isStreaming) return;

    const interval = setInterval(async () => {
      try {
        if (viewMode === 'multi-camera') {
          const multiStats = await apiService.getMultiCameraStatus();
          setMultiCameraStats(multiStats);
        } else {
          const statsData = await apiService.getLiveStats();
          setStats(statsData);
        }
      } catch (err) {
        console.error('Stats polling error:', err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isStreaming, viewMode]);

  const handleStartStream = (url: string) => {
    setStreamUrl(url);
    setIsStreaming(true);
    setError('');
  };

  const handleStopStream = async () => {
    try {
      if (viewMode === 'multi-camera') {
        await apiService.stopMultiCamera();
      } else {
        await apiService.stopStream();
      }
      setIsStreaming(false);
      setStreamUrl('');
      setStats(null);
      setMultiCameraStats(null);
    } catch (err) {
      setError('Failed to stop stream');
      console.error('Stop stream error:', err);
    }
  };

  const handleConfigUpdate = (newConfig: Config) => {
    setConfig(newConfig);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg shadow-xl border-b border-indigo-200/50">
        <div className="max-w-full mx-auto px-2 sm:px-4 lg:px-6">
          <div className="flex justify-between items-center h-24">
            {/* Left side - Logos */}
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-6">
                <img 
                  src="/g2clogo.png" 
                  alt="GoToCloud" 
                  className="h-10 w-auto filter brightness-110"
                />
                <div className="h-16 w-px bg-gradient-to-b from-transparent via-indigo-300 to-transparent"></div>
                <img 
                  src="/ccblogo.png" 
                  alt="Cámara de Comercio de Barranquilla" 
                  className="h-20 w-auto filter brightness-110"
                />
              </div>
            </div>

            {/* Center - Title */}
            <div className="flex items-center">
              <div className="h-16 w-px bg-gradient-to-b from-transparent via-indigo-300 to-transparent mr-8"></div>
              <div className="relative">
                <Activity className="h-12 w-12 text-indigo-600 mr-4 animate-pulse" />
                <div className="absolute -top-1 -right-1 h-3 w-3 bg-emerald-500 rounded-full animate-ping"></div>
              </div>
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Audience Attention Detector
                </h1>
                <p className="text-base text-gray-700 mt-2 font-medium">AI-Powered Real-Time Analytics</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex space-x-2">
              <button
                onClick={() => setViewMode('stream')}
                className={`group flex items-center px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  viewMode === 'stream'
                    ? 'bg-gradient-to-r from-indigo-500 to-blue-600 text-white shadow-lg shadow-indigo-500/25'
                    : 'text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 backdrop-blur-sm'
                }`}
              >
                <Monitor className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />
                Single Camera
              </button>
              <button
                onClick={() => setViewMode('multi-camera')}
                className={`group flex items-center px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  viewMode === 'multi-camera'
                    ? 'bg-gradient-to-r from-blue-500 to-cyan-600 text-white shadow-lg shadow-blue-500/25'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50 backdrop-blur-sm'
                }`}
              >
                <Camera className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />
                Multi-Camera
              </button>
              <button
                onClick={() => setViewMode('upload')}
                className={`group flex items-center px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  viewMode === 'upload'
                    ? 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg shadow-purple-500/25'
                    : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50 backdrop-blur-sm'
                }`}
              >
                <Upload className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />
                Process Video
              </button>
              <button
                onClick={() => setViewMode('settings')}
                className={`group flex items-center px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  viewMode === 'settings'
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/25'
                    : 'text-gray-600 hover:text-emerald-600 hover:bg-emerald-50 backdrop-blur-sm'
                }`}
              >
                <Settings className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />
                Settings
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div className="bg-gradient-to-r from-red-50 to-pink-50 backdrop-blur-sm border-l-4 border-red-400 p-4 shadow-lg">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-red-800 font-medium">{error}</p>
            </div>
            <button
              onClick={() => setError('')}
              className="ml-auto text-red-600 hover:text-red-800 transition-colors p-1 rounded-full hover:bg-red-100"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-full mx-auto py-2 sm:py-4 px-2 sm:px-4 lg:px-6">
        <div className="py-2 sm:py-4">
          {/* Live Stats Bar */}
          {isStreaming && (stats || multiCameraStats) && (
            <div className="mb-6">
              <StatsBar 
                stats={viewMode === 'multi-camera' ? (multiCameraStats?.aggregated_stats || null) : stats} 
                multiCameraStats={viewMode === 'multi-camera' ? multiCameraStats : null}
              />
            </div>
          )}

          <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:gap-6">
            {/* Controls Sidebar */}
            <div className="xl:col-span-2">
              <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-indigo-200/50 p-4 xl:p-6">
                {viewMode === 'multi-camera' ? (
                  <MultiCameraControls
                    config={config}
                    isStreaming={isStreaming}
                    onStartStream={handleStartStream}
                    onStopStream={handleStopStream}
                    onConfigUpdate={handleConfigUpdate}
                    onError={setError}
                  />
                ) : (
                  <Controls
                    config={config}
                    isStreaming={isStreaming}
                    viewMode={viewMode}
                    onStartStream={handleStartStream}
                    onStopStream={handleStopStream}
                    onConfigUpdate={handleConfigUpdate}
                    onError={setError}
                  />
                )}
              </div>
            </div>

            {/* Recording Controls */}
            {(viewMode === 'stream' || viewMode === 'multi-camera') && (
              <div className="xl:col-span-2">
                <RecordingControls
                  streamType={viewMode === 'stream' ? 'single' : 'multi'}
                  isStreaming={isStreaming}
                  onError={setError}
                />
              </div>
            )}

            {/* Main Content Area - Larger and Centered */}
            <div className={`${(viewMode === 'stream' || viewMode === 'multi-camera') ? 'xl:col-span-8' : 'xl:col-span-10'}`}>
              {viewMode === 'stream' && (
                <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-indigo-200/50 overflow-hidden">
                  <VideoStream
                    isStreaming={isStreaming}
                    streamUrl={streamUrl}
                  />
                </div>
              )}

              {viewMode === 'multi-camera' && (
                <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-indigo-200/50 overflow-hidden">
                  <VideoStream
                    isStreaming={isStreaming}
                    streamUrl={streamUrl}
                  />
                </div>
              )}

              {viewMode === 'upload' && (
                <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-indigo-200/50 p-6">
                  <UploadProcessor onError={setError} />
                </div>
              )}

              {viewMode === 'settings' && config && (
                <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-indigo-200/50 p-6">
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-6">
                    System Configuration
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-indigo-50 rounded-xl p-4 border border-indigo-200">
                      <label className="block text-sm font-semibold text-indigo-700 mb-2">
                        YOLO Model Path
                      </label>
                      <p className="text-sm text-gray-700 font-mono bg-white rounded-lg p-2 border">
                        {config.yolo_model_path}
                      </p>
                    </div>
                    <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
                      <label className="block text-sm font-semibold text-purple-700 mb-2">
                        Confidence Threshold
                      </label>
                      <p className="text-lg font-bold text-gray-800">
                        {config.conf_threshold}
                      </p>
                    </div>
                    <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-200">
                      <label className="block text-sm font-semibold text-emerald-700 mb-2">
                        Yaw Threshold (°)
                      </label>
                      <p className="text-lg font-bold text-gray-800">
                        {config.yaw_threshold}°
                      </p>
                    </div>
                    <div className="bg-pink-50 rounded-xl p-4 border border-pink-200">
                      <label className="block text-sm font-semibold text-pink-700 mb-2">
                        Pitch Threshold (°)
                      </label>
                      <p className="text-lg font-bold text-gray-800">
                        {config.pitch_threshold}°
                      </p>
                    </div>
                    <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
                      <label className="block text-sm font-semibold text-yellow-700 mb-2">
                        Stream Resolution
                      </label>
                      <p className="text-lg font-bold text-gray-800">
                        {config.stream_width} × {config.stream_height}
                      </p>
                    </div>
                    <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                      <label className="block text-sm font-semibold text-blue-700 mb-2">
                        Stream FPS
                      </label>
                      <p className="text-lg font-bold text-gray-800">
                        {config.stream_fps} FPS
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

