import axios from 'axios';
import { apiClient } from '../api';
import { AudioAnalysis, GenerationRequest } from '../../types';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedAxios.create.mockReturnValue(mockedAxios as any);
  });

  describe('uploadAudio', () => {
    it('uploads audio file with correct form data', async () => {
      const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
      const mockResponse = { data: { filePath: '/uploads/test.mp3' } };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const result = await apiClient.uploadAudio(file);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
        })
      );
      expect(result).toEqual({ filePath: '/uploads/test.mp3' });
    });

    it('throws error when upload fails', async () => {
      const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });

      mockedAxios.post.mockRejectedValueOnce(new Error('Upload failed'));

      await expect(apiClient.uploadAudio(file)).rejects.toThrow();
    });
  });

  describe('analyzeAudio', () => {
    it('sends analyze request with file path', async () => {
      const mockAnalysis: AudioAnalysis = {
        tempo: 120,
        mood: 'energetic',
        genre: 'electronic',
        duration: 180,
        energy: 0.8,
        danceability: 0.7,
        segments: [],
      };

      mockedAxios.post.mockResolvedValueOnce({ data: mockAnalysis });

      const result = await apiClient.analyzeAudio('/uploads/test.mp3');

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/analyze', {
        filePath: '/uploads/test.mp3',
      });
      expect(result).toEqual(mockAnalysis);
    });

    it('throws error when analysis fails', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Analysis failed'));

      await expect(apiClient.analyzeAudio('/uploads/test.mp3')).rejects.toThrow();
    });
  });

  describe('generateVideo', () => {
    it('sends generation request with all parameters', async () => {
      const request: GenerationRequest = {
        audioFilePath: '/uploads/test.mp3',
        analysis: {
          tempo: 120,
          mood: 'energetic',
          genre: 'electronic',
          duration: 180,
          energy: 0.8,
          danceability: 0.7,
          segments: [],
        },
        style: {
          theme: 'cinematic',
          colorPalette: ['#FF0000'],
          visualStyle: 'realistic',
          effectsIntensity: 0.7,
        },
        prompts: [],
      };

      const mockResponse = {
        data: {
          videoPath: '/videos/output.mp4',
          duration: 180,
          segments: 3,
          message: 'Success',
        },
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const result = await apiClient.generateVideo(request);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/generate', request);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getGenerationProgress', () => {
    it('fetches progress with job id', async () => {
      const mockProgress = {
        status: 'generating',
        currentStep: 'Processing',
        progress: 50,
        message: 'Halfway done',
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockProgress });

      const result = await apiClient.getGenerationProgress('job-123');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/progress/job-123');
      expect(result).toEqual(mockProgress);
    });
  });

  describe('downloadVideo', () => {
    it('downloads video as blob', async () => {
      const mockBlob = new Blob(['video data'], { type: 'video/mp4' });

      mockedAxios.get.mockResolvedValueOnce({ data: mockBlob });

      const result = await apiClient.downloadVideo('/videos/output.mp4');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        '/api/download',
        expect.objectContaining({
          params: { path: '/videos/output.mp4' },
          responseType: 'blob',
        })
      );
      expect(result).toEqual(mockBlob);
    });
  });

  describe('healthCheck', () => {
    it('checks API health status', async () => {
      const mockHealth = { status: 'healthy' };

      mockedAxios.get.mockResolvedValueOnce({ data: mockHealth });

      const result = await apiClient.healthCheck();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/health');
      expect(result).toEqual(mockHealth);
    });
  });
});
