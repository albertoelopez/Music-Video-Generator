import axios, { AxiosInstance } from 'axios';
import {
  AudioAnalysis,
  GenerationRequest,
  GenerationResponse,
  GenerationProgress,
  ApiError,
} from '../types';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:5000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      timeout: 300000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const apiError: ApiError = {
          message: error.response?.data?.message || error.message,
          code: error.response?.status?.toString(),
          details: error.response?.data,
        };
        return Promise.reject(apiError);
      }
    );
  }

  async uploadAudio(file: File): Promise<{ filePath: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return { filePath: response.data.filepath };
  }

  async analyzeAudio(filePath: string): Promise<AudioAnalysis> {
    const response = await this.client.post('/api/analyze', { filepath: filePath });
    const data = response.data;

    const segments = (data.segments || []).map((seg: {
      start_time: number;
      end_time: number;
      energy: number;
      mood: string;
      lyrics?: string;
    }) => ({
      start: seg.start_time,
      end: seg.end_time,
      intensity: seg.energy,
      description: seg.mood || 'Instrumental section',
    }));

    const avgEnergy = segments.length > 0
      ? segments.reduce((sum: number, s: { intensity: number }) => sum + s.intensity, 0) / segments.length
      : 0.5;

    return {
      tempo: data.tempo,
      mood: data.mood,
      genre: data.genre,
      segments,
      duration: data.duration,
      energy: avgEnergy,
      danceability: data.tempo > 100 ? Math.min(avgEnergy * 1.2, 1) : avgEnergy * 0.8,
    };
  }

  async generateVideo(request: GenerationRequest): Promise<GenerationResponse> {
    const backendRequest = {
      filepath: request.audioFilePath,
      style: request.style.visualStyle,
      theme: request.style.theme,
      use_mock: false,
    };
    const response = await this.client.post('/api/generate', backendRequest);
    return {
      videoPath: response.data.result?.output_path || '',
      duration: response.data.result?.duration || 0,
      segments: response.data.result?.segments_generated || 0,
      message: 'Generation started',
      jobId: response.data.job_id,
    };
  }

  async getJobStatus(jobId: string): Promise<GenerationProgress> {
    const response = await this.client.get(`/api/job/${jobId}`);
    const data = response.data;
    return {
      status: data.status === 'completed' ? 'complete' : data.status === 'error' ? 'error' : 'generating',
      currentStep: data.current_step || data.message || '',
      progress: data.progress || 0,
      message: data.message || '',
    };
  }

  async getGenerationProgress(jobId: string): Promise<GenerationProgress> {
    const response = await this.client.get(`/api/progress/${jobId}`);
    return response.data;
  }

  async downloadVideo(videoPath: string): Promise<Blob> {
    const response = await this.client.get(`/api/download`, {
      params: { path: videoPath },
      responseType: 'blob',
    });
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/api/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
