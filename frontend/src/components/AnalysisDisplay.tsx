import React from 'react';
import { AudioAnalysis } from '../types';

interface AnalysisDisplayProps {
  analysis: AudioAnalysis | null;
  isLoading: boolean;
}

export const AnalysisDisplay: React.FC<AnalysisDisplayProps> = ({
  analysis,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="text-lg text-gray-700">Analyzing audio...</span>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return null;
  }

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8 space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 border-b pb-3">
        Audio Analysis
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg p-4">
          <div className="text-sm font-medium text-primary-700 uppercase tracking-wide">
            Tempo
          </div>
          <div className="text-3xl font-bold text-primary-900 mt-2">
            {Math.round(analysis.tempo)}
          </div>
          <div className="text-xs text-primary-600 mt-1">BPM</div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
          <div className="text-sm font-medium text-purple-700 uppercase tracking-wide">
            Mood
          </div>
          <div className="text-xl font-bold text-purple-900 mt-2 capitalize">
            {analysis.mood}
          </div>
        </div>

        <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-lg p-4">
          <div className="text-sm font-medium text-pink-700 uppercase tracking-wide">
            Genre
          </div>
          <div className="text-xl font-bold text-pink-900 mt-2 capitalize">
            {analysis.genre}
          </div>
        </div>

        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-4">
          <div className="text-sm font-medium text-indigo-700 uppercase tracking-wide">
            Duration
          </div>
          <div className="text-3xl font-bold text-indigo-900 mt-2">
            {formatTime(analysis.duration)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-2">
            Energy Level
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${analysis.energy * 100}%` }}
            ></div>
          </div>
          <div className="text-xs text-gray-600 mt-1 text-right">
            {Math.round(analysis.energy * 100)}%
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-2">
            Danceability
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-400 to-blue-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${analysis.danceability * 100}%` }}
            ></div>
          </div>
          <div className="text-xs text-gray-600 mt-1 text-right">
            {Math.round(analysis.danceability * 100)}%
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Audio Segments ({analysis.segments.length})
        </h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {analysis.segments.map((segment, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-gray-50 rounded-lg p-3 hover:bg-gray-100 transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium text-gray-700">
                    Segment {index + 1}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatTime(segment.start)} - {formatTime(segment.end)}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {segment.description}
                </p>
              </div>
              <div className="ml-4">
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Intensity:</span>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${segment.intensity * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
