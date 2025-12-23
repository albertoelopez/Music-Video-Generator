export interface AudioAnalysis {
  tempo: number;
  mood: string;
  genre: string;
  segments: AudioSegment[];
  duration: number;
  energy: number;
  danceability: number;
}

export interface AudioSegment {
  start: number;
  end: number;
  intensity: number;
  description: string;
}

export interface StyleCustomization {
  theme: string;
  colorPalette: string[];
  visualStyle: string;
  effectsIntensity: number;
}

export interface GenerationProgress {
  status: 'idle' | 'analyzing' | 'generating' | 'complete' | 'error';
  currentStep: string;
  progress: number;
  message: string;
}

export interface VideoPrompt {
  segment: AudioSegment;
  prompt: string;
  visualDescription: string;
}

export interface GenerationRequest {
  audioFilePath: string;
  analysis: AudioAnalysis;
  style: StyleCustomization;
  prompts: VideoPrompt[];
}

export interface GenerationResponse {
  videoPath: string;
  duration: number;
  segments: number;
  message: string;
  jobId?: string;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
}
