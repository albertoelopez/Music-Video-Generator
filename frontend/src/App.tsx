import React, { useState } from 'react';
import { AudioUpload } from './components/AudioUpload';
import { AnalysisDisplay } from './components/AnalysisDisplay';
import { StyleCustomizer } from './components/StyleCustomizer';
import { GenerationProgress } from './components/GenerationProgress';
import { apiClient } from './services/api';
import {
  AudioAnalysis,
  StyleCustomization,
  GenerationProgress as GenerationProgressType,
  VideoPrompt,
} from './types';

type AppStep = 'upload' | 'analyze' | 'customize' | 'generate' | 'complete';

export const App: React.FC = () => {
  const [currentStep, setCurrentStep] = useState<AppStep>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedFilePath, setUploadedFilePath] = useState<string>('');
  const [analysis, setAnalysis] = useState<AudioAnalysis | null>(null);
  const [style, setStyle] = useState<StyleCustomization>({
    theme: 'cinematic',
    colorPalette: ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF'],
    visualStyle: 'realistic',
    effectsIntensity: 0.7,
  });
  const [progress, setProgress] = useState<GenerationProgressType>({
    status: 'idle',
    currentStep: '',
    progress: 0,
    message: '',
  });
  const [videoPath, setVideoPath] = useState<string>('');
  const [prompts, setPrompts] = useState<VideoPrompt[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setIsProcessing(true);

    try {
      const { filePath } = await apiClient.uploadAudio(file);
      setUploadedFilePath(filePath);
      setCurrentStep('analyze');
      await handleAnalyze(filePath);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload audio file. Please try again.');
      setIsProcessing(false);
    }
  };

  const handleAnalyze = async (filePath: string) => {
    setProgress({
      status: 'analyzing',
      currentStep: 'Analyzing Audio',
      progress: 25,
      message: 'Extracting audio features and characteristics...',
    });

    try {
      const analysisResult = await apiClient.analyzeAudio(filePath);
      setAnalysis(analysisResult);

      const generatedPrompts: VideoPrompt[] = analysisResult.segments.map((segment) => ({
        segment,
        prompt: `${style.theme} ${style.visualStyle} scene, ${segment.description}`,
        visualDescription: `A ${style.visualStyle} ${style.theme} visual representing ${segment.description}`,
      }));
      setPrompts(generatedPrompts);

      setProgress({
        status: 'complete',
        currentStep: 'Analysis Complete',
        progress: 100,
        message: 'Audio analysis finished successfully',
      });

      setCurrentStep('customize');
    } catch (error) {
      console.error('Analysis failed:', error);
      setProgress({
        status: 'error',
        currentStep: 'Analysis Failed',
        progress: 0,
        message: 'Failed to analyze audio. Please try again.',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleStyleChange = (newStyle: StyleCustomization) => {
    setStyle(newStyle);

    if (analysis) {
      const updatedPrompts: VideoPrompt[] = analysis.segments.map((segment) => ({
        segment,
        prompt: `${newStyle.theme} ${newStyle.visualStyle} scene, ${segment.description}`,
        visualDescription: `A ${newStyle.visualStyle} ${newStyle.theme} visual representing ${segment.description}`,
      }));
      setPrompts(updatedPrompts);
    }
  };

  const handleGenerate = async () => {
    if (!analysis || !uploadedFilePath) return;

    setCurrentStep('generate');
    setIsProcessing(true);
    setProgress({
      status: 'generating',
      currentStep: 'Generating Video',
      progress: 0,
      message: 'Starting video generation...',
    });

    try {
      const response = await apiClient.generateVideo({
        audioFilePath: uploadedFilePath,
        analysis,
        style,
        prompts,
      });

      if (!response.jobId) {
        throw new Error('No job ID received from server');
      }

      const pollJobStatus = async (jobId: string): Promise<void> => {
        const maxAttempts = 9000;
        let attempts = 0;

        while (attempts < maxAttempts) {
          const jobStatus = await apiClient.getJobStatus(jobId);

          if (jobStatus.status === 'complete') {
            setVideoPath(response.videoPath || '');
            setProgress({
              status: 'complete',
              currentStep: 'Generation Complete',
              progress: 100,
              message: 'Your music video is ready!',
            });
            setCurrentStep('complete');
            return;
          }

          if (jobStatus.status === 'error') {
            setProgress({
              status: 'error',
              currentStep: 'Generation Failed',
              progress: 0,
              message: jobStatus.message || 'Video generation failed.',
            });
            return;
          }

          setProgress({
            status: 'generating',
            currentStep: jobStatus.currentStep || 'Generating Video',
            progress: jobStatus.progress || 0,
            message: jobStatus.message || 'Processing...',
          });

          await new Promise((resolve) => setTimeout(resolve, 2000));
          attempts++;
        }

        setProgress({
          status: 'error',
          currentStep: 'Generation Timeout',
          progress: 0,
          message: 'Video generation timed out. Please try again.',
        });
      };

      await pollJobStatus(response.jobId);
    } catch (error) {
      console.error('Generation failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate video. Please try again.';
      setProgress({
        status: 'error',
        currentStep: 'Generation Failed',
        progress: 0,
        message: errorMessage,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!videoPath) return;

    try {
      const blob = await apiClient.downloadVideo(videoPath);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'music-video.mp4';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download video. Please try again.');
    }
  };

  const handleReset = () => {
    setCurrentStep('upload');
    setSelectedFile(null);
    setUploadedFilePath('');
    setAnalysis(null);
    setVideoPath('');
    setPrompts([]);
    setProgress({
      status: 'idle',
      currentStep: '',
      progress: 0,
      message: '',
    });
    setIsProcessing(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Audio to Music Video
          </h1>
          <p className="text-lg text-gray-600">
            Transform your audio into stunning AI-generated music videos
          </p>
        </header>

        <div className="mb-8">
          <div className="flex justify-center">
            <div className="flex items-center space-x-4">
              {['upload', 'analyze', 'customize', 'generate', 'complete'].map((step, index) => {
                const stepIndex = ['upload', 'analyze', 'customize', 'generate', 'complete'].indexOf(currentStep);
                const currentIndex = ['upload', 'analyze', 'customize', 'generate', 'complete'].indexOf(step);
                const isActive = currentIndex === stepIndex;
                const isCompleted = currentIndex < stepIndex;

                return (
                  <React.Fragment key={step}>
                    {index > 0 && (
                      <div className={`h-1 w-16 ${isCompleted ? 'bg-primary-500' : 'bg-gray-300'}`}></div>
                    )}
                    <div className="flex flex-col items-center">
                      <div
                        className={`
                          w-10 h-10 rounded-full flex items-center justify-center font-semibold
                          ${isActive ? 'bg-primary-500 text-white' : ''}
                          ${isCompleted ? 'bg-green-500 text-white' : ''}
                          ${!isActive && !isCompleted ? 'bg-gray-300 text-gray-600' : ''}
                        `}
                      >
                        {isCompleted ? '✓' : index + 1}
                      </div>
                      <span className="text-xs mt-1 capitalize text-gray-600">{step}</span>
                    </div>
                  </React.Fragment>
                );
              })}
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {currentStep === 'upload' && (
            <AudioUpload onFileSelect={handleFileSelect} isProcessing={isProcessing} />
          )}

          {(currentStep === 'analyze' || currentStep === 'customize' || currentStep === 'generate' || currentStep === 'complete') && (
            <AnalysisDisplay analysis={analysis} isLoading={currentStep === 'analyze' && isProcessing} />
          )}

          {(currentStep === 'customize' || currentStep === 'generate' || currentStep === 'complete') && analysis && (
            <>
              <StyleCustomizer onStyleChange={handleStyleChange} initialStyle={style} />

              <div className="w-full max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Generated Prompts Preview
                </h2>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {prompts.map((prompt, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-4">
                      <div className="text-sm font-medium text-gray-700 mb-1">
                        Segment {index + 1}
                      </div>
                      <p className="text-sm text-gray-900">{prompt.prompt}</p>
                    </div>
                  ))}
                </div>
              </div>

              {currentStep === 'customize' && !isProcessing && (
                <div className="w-full max-w-4xl mx-auto text-center">
                  <button
                    onClick={handleGenerate}
                    className="px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-lg"
                  >
                    Generate Music Video
                  </button>
                </div>
              )}
            </>
          )}

          {(currentStep === 'generate' || currentStep === 'complete') && (
            <GenerationProgress progress={progress} />
          )}

          {currentStep === 'complete' && videoPath && (
            <div className="w-full max-w-4xl mx-auto text-center space-y-4">
              <button
                onClick={handleDownload}
                className="px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-lg hover:bg-green-700 transition-colors shadow-lg"
              >
                Download Video
              </button>
              <button
                onClick={handleReset}
                className="ml-4 px-8 py-4 bg-gray-600 text-white text-lg font-semibold rounded-lg hover:bg-gray-700 transition-colors shadow-lg"
              >
                Create Another Video
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
