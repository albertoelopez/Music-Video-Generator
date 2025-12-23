import React, { useState, useRef } from 'react';

interface AudioUploadProps {
  onFileSelect: (file: File) => void;
  isProcessing: boolean;
}

export const AudioUpload: React.FC<AudioUploadProps> = ({
  onFileSelect,
  isProcessing,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file: File) => {
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3'];
    const validExtensions = ['.mp3', '.wav'];

    const hasValidType = validTypes.includes(file.type);
    const hasValidExtension = validExtensions.some(ext =>
      file.name.toLowerCase().endsWith(ext)
    );

    if (hasValidType || hasValidExtension) {
      setSelectedFileName(file.name);
      onFileSelect(file);
    } else {
      alert('Please select a valid audio file (MP3 or WAV)');
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`
          border-2 border-dashed rounded-lg p-12 text-center
          transition-all duration-200 cursor-pointer
          ${isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
          }
          ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={!isProcessing ? handleButtonClick : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".mp3,.wav,audio/mpeg,audio/wav"
          onChange={handleFileInput}
          className="hidden"
          disabled={isProcessing}
          data-testid="file-input"
        />

        <div className="space-y-4">
          <svg
            className="mx-auto h-16 w-16 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
            />
          </svg>

          <div>
            <p className="text-lg font-medium text-gray-900">
              {selectedFileName || 'Drop your audio file here'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              or click to browse
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Supports MP3 and WAV files
            </p>
          </div>

          {!isProcessing && (
            <button
              type="button"
              className="
                inline-flex items-center px-6 py-3
                border border-transparent text-base font-medium rounded-md
                text-white bg-primary-600 hover:bg-primary-700
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                transition-colors duration-200
              "
              onClick={(e) => {
                e.stopPropagation();
                handleButtonClick();
              }}
            >
              Select Audio File
            </button>
          )}

          {isProcessing && (
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              <span className="text-sm text-gray-600">Processing...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
