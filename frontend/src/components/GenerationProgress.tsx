import React from 'react';
import { GenerationProgress as GenerationProgressType } from '../types';

interface GenerationProgressProps {
  progress: GenerationProgressType;
}

export const GenerationProgress: React.FC<GenerationProgressProps> = ({
  progress,
}) => {
  const getStatusColor = (status: GenerationProgressType['status']): string => {
    switch (status) {
      case 'analyzing':
        return 'text-blue-600';
      case 'generating':
        return 'text-purple-600';
      case 'complete':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getProgressBarColor = (status: GenerationProgressType['status']): string => {
    switch (status) {
      case 'analyzing':
        return 'bg-blue-500';
      case 'generating':
        return 'bg-purple-500';
      case 'complete':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: GenerationProgressType['status']) => {
    switch (status) {
      case 'analyzing':
      case 'generating':
        return (
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-current"></div>
        );
      case 'complete':
        return (
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'error':
        return (
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      default:
        return null;
    }
  };

  if (progress.status === 'idle') {
    return null;
  }

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={getStatusColor(progress.status)}>
              {getStatusIcon(progress.status)}
            </div>
            <div>
              <h3 className={`text-lg font-semibold ${getStatusColor(progress.status)}`}>
                {progress.currentStep}
              </h3>
              <p className="text-sm text-gray-600">{progress.message}</p>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {Math.round(progress.progress)}%
          </div>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className={`h-4 rounded-full transition-all duration-300 ${getProgressBarColor(progress.status)}`}
            style={{ width: `${progress.progress}%` }}
          >
            <div className="h-full w-full bg-white opacity-20 animate-pulse"></div>
          </div>
        </div>

        {progress.status === 'generating' && (
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-xs text-gray-600 uppercase tracking-wide">
                Processing
              </div>
              <div className="text-lg font-semibold text-gray-900 mt-1">
                Video Frames
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-xs text-gray-600 uppercase tracking-wide">
                Syncing
              </div>
              <div className="text-lg font-semibold text-gray-900 mt-1">
                Audio Track
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-xs text-gray-600 uppercase tracking-wide">
                Rendering
              </div>
              <div className="text-lg font-semibold text-gray-900 mt-1">
                Final Output
              </div>
            </div>
          </div>
        )}

        {progress.status === 'complete' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-medium text-green-900">
                  Video generation complete!
                </p>
                <p className="text-sm text-green-700">
                  Your music video is ready to download.
                </p>
              </div>
            </div>
          </div>
        )}

        {progress.status === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="font-medium text-red-900">
                  Generation failed
                </p>
                <p className="text-sm text-red-700">
                  {progress.message}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
