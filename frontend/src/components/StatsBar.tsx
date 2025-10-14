import React from 'react';
import { Users, Eye, EyeOff, UserX, Camera } from 'lucide-react';
import { type Stats, type MultiCameraStats } from '../lib/api';

interface StatsBarProps {
  stats: Stats | null;
  multiCameraStats?: MultiCameraStats | null;
}

const StatsBar: React.FC<StatsBarProps> = ({ stats, multiCameraStats }) => {
  const getPercentage = (value: number, total: number): number => {
    return total > 0 ? Math.round((value / total) * 100) : 0;
  };

  if (!stats) return null;

  const isMultiCamera = multiCameraStats !== null;
  const displayStats = isMultiCamera ? (multiCameraStats?.aggregated_stats || stats) : stats;

  return (
    <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-indigo-200/50 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent flex items-center">
          {isMultiCamera ? (
            <Camera className="h-6 w-6 mr-3 text-indigo-600" />
          ) : (
            <Users className="h-6 w-6 mr-3 text-indigo-600" />
          )}
          {isMultiCamera ? 'Multi-Camera Statistics' : 'Live Audience Statistics'}
        </h2>
        <div className="text-sm text-gray-600 bg-indigo-50 rounded-lg px-3 py-2 border border-indigo-200">
          <span className="text-indigo-600">●</span> Last updated: {new Date(stats.timestamp * 1000).toLocaleTimeString()}
        </div>
      </div>

      {/* Multi-Camera Info */}
      {isMultiCamera && multiCameraStats && (
        <div className="mb-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Camera className="h-5 w-5 mr-2 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">
                Active Cameras: {multiCameraStats.camera_count}
              </span>
            </div>
            <div className="text-xs text-blue-600">
              Cameras: {multiCameraStats.active_cameras.join(', ')}
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="text-center bg-blue-50 rounded-xl p-4 border border-blue-200 hover:bg-blue-100 transition-all duration-300">
          <div className="text-3xl font-bold text-gray-800 mb-2">{displayStats.total}</div>
          <div className="text-sm text-gray-600 flex items-center justify-center">
            <Users className="h-4 w-4 mr-1 text-blue-600" />
            Total Personas
          </div>
        </div>
        
        <div className="text-center bg-green-50 rounded-xl p-4 border border-green-200 hover:bg-green-100 transition-all duration-300">
          <div className="text-3xl font-bold text-green-600 mb-2">{displayStats.green}</div>
          <div className="text-sm text-gray-600 flex items-center justify-center">
            <Eye className="h-4 w-4 mr-1 text-green-600" />
            Looking at Camera
          </div>
        </div>
        
        <div className="text-center bg-yellow-50 rounded-xl p-4 border border-yellow-200 hover:bg-yellow-100 transition-all duration-300">
          <div className="text-3xl font-bold text-yellow-600 mb-2">{displayStats.yellow}</div>
          <div className="text-sm text-gray-600 flex items-center justify-center">
            <EyeOff className="h-4 w-4 mr-1 text-yellow-600" />
            Not Looking
          </div>
        </div>
        
        <div className="text-center bg-red-50 rounded-xl p-4 border border-red-200 hover:bg-red-100 transition-all duration-300">
          <div className="text-3xl font-bold text-red-600 mb-2">{displayStats.red}</div>
          <div className="text-sm text-gray-600 flex items-center justify-center">
            <UserX className="h-4 w-4 mr-1 text-red-600" />
            No Face Detected
          </div>
        </div>
      </div>

      {/* Progress Bars */}
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-700 font-medium">Looking at Camera (Green)</span>
            <span className="font-bold text-green-600">
              {getPercentage(displayStats.green, displayStats.total)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-green-500 to-emerald-400 h-3 rounded-full transition-all duration-500 shadow-lg shadow-green-500/25"
              style={{ width: `${getPercentage(displayStats.green, displayStats.total)}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-700 font-medium">Not Looking (Yellow)</span>
            <span className="font-bold text-yellow-600">
              {getPercentage(displayStats.yellow, displayStats.total)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-yellow-500 to-orange-400 h-3 rounded-full transition-all duration-500 shadow-lg shadow-yellow-500/25"
              style={{ width: `${getPercentage(displayStats.yellow, displayStats.total)}%` }}
            ></div>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-700 font-medium">No Face Detected (Red)</span>
            <span className="font-bold text-red-600">
              {getPercentage(displayStats.red, displayStats.total)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-red-500 to-pink-400 h-3 rounded-full transition-all duration-500 shadow-lg shadow-red-500/25"
              style={{ width: `${getPercentage(displayStats.red, displayStats.total)}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Attention Score */}
      {displayStats.total > 0 && (
        <div className="mt-8 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-200">
          <div className="flex justify-between items-center mb-4">
            <span className="text-lg font-bold text-gray-800">
              {isMultiCamera ? 'Overall Attention Score (All Cameras)' : 'Overall Attention Score'}
            </span>
            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {getPercentage(displayStats.green, displayStats.total)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className={`h-4 rounded-full transition-all duration-500 shadow-lg ${
                getPercentage(displayStats.green, displayStats.total) >= 70
                  ? 'bg-gradient-to-r from-green-500 to-emerald-400 shadow-green-500/25'
                  : getPercentage(displayStats.green, displayStats.total) >= 40
                  ? 'bg-gradient-to-r from-yellow-500 to-orange-400 shadow-yellow-500/25'
                  : 'bg-gradient-to-r from-red-500 to-pink-400 shadow-red-500/25'
              }`}
              style={{ width: `${getPercentage(displayStats.green, displayStats.total)}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsBar;

