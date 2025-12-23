import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../App';
import { apiClient } from '../services/api';

jest.mock('../services/api');
const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders app title and description', () => {
    render(<App />);

    expect(screen.getByText('Audio to Music Video')).toBeInTheDocument();
    expect(
      screen.getByText('Transform your audio into stunning AI-generated music videos')
    ).toBeInTheDocument();
  });

  it('renders all step indicators', () => {
    render(<App />);

    expect(screen.getByText('upload')).toBeInTheDocument();
    expect(screen.getByText('analyze')).toBeInTheDocument();
    expect(screen.getByText('customize')).toBeInTheDocument();
    expect(screen.getByText('generate')).toBeInTheDocument();
    expect(screen.getByText('complete')).toBeInTheDocument();
  });

  it('starts at upload step', () => {
    render(<App />);

    expect(screen.getByText('Drop your audio file here')).toBeInTheDocument();
    expect(screen.getByText('Select Audio File')).toBeInTheDocument();
  });

  it('uploads file and transitions to analyze step', async () => {
    const user = userEvent.setup();

    mockedApiClient.uploadAudio.mockResolvedValueOnce({
      filePath: '/uploads/test.mp3',
    });

    mockedApiClient.analyzeAudio.mockResolvedValueOnce({
      tempo: 120,
      mood: 'energetic',
      genre: 'electronic',
      duration: 180,
      energy: 0.8,
      danceability: 0.7,
      segments: [
        {
          start: 0,
          end: 60,
          intensity: 0.7,
          description: 'Intro section',
        },
      ],
    });

    render(<App />);

    const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(mockedApiClient.uploadAudio).toHaveBeenCalledWith(file);
    });

    await waitFor(
      () => {
        expect(screen.getByText('Audio Analysis')).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it('displays audio analysis results after upload', async () => {
    const user = userEvent.setup();

    mockedApiClient.uploadAudio.mockResolvedValueOnce({
      filePath: '/uploads/test.mp3',
    });

    mockedApiClient.analyzeAudio.mockResolvedValueOnce({
      tempo: 128,
      mood: 'happy',
      genre: 'pop',
      duration: 200,
      energy: 0.9,
      danceability: 0.8,
      segments: [],
    });

    render(<App />);

    const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(
      () => {
        expect(screen.getByText('128')).toBeInTheDocument();
        expect(screen.getByText('happy')).toBeInTheDocument();
        expect(screen.getByText('pop')).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it('shows style customizer after analysis', async () => {
    const user = userEvent.setup();

    mockedApiClient.uploadAudio.mockResolvedValueOnce({
      filePath: '/uploads/test.mp3',
    });

    mockedApiClient.analyzeAudio.mockResolvedValueOnce({
      tempo: 120,
      mood: 'energetic',
      genre: 'electronic',
      duration: 180,
      energy: 0.8,
      danceability: 0.7,
      segments: [],
    });

    render(<App />);

    const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(
      () => {
        expect(screen.getByText('Customize Video Style')).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it('shows generate button after customization', async () => {
    const user = userEvent.setup();

    mockedApiClient.uploadAudio.mockResolvedValueOnce({
      filePath: '/uploads/test.mp3',
    });

    mockedApiClient.analyzeAudio.mockResolvedValueOnce({
      tempo: 120,
      mood: 'energetic',
      genre: 'electronic',
      duration: 180,
      energy: 0.8,
      danceability: 0.7,
      segments: [],
    });

    render(<App />);

    const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(
      () => {
        expect(screen.getByText('Generate Music Video')).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it('handles upload error gracefully', async () => {
    const user = userEvent.setup();
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {});

    mockedApiClient.uploadAudio.mockRejectedValueOnce(
      new Error('Upload failed')
    );

    render(<App />);

    const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith(
        'Failed to upload audio file. Please try again.'
      );
    });

    alertSpy.mockRestore();
  });

  it('displays prompts preview', async () => {
    const user = userEvent.setup();

    mockedApiClient.uploadAudio.mockResolvedValueOnce({
      filePath: '/uploads/test.mp3',
    });

    mockedApiClient.analyzeAudio.mockResolvedValueOnce({
      tempo: 120,
      mood: 'energetic',
      genre: 'electronic',
      duration: 180,
      energy: 0.8,
      danceability: 0.7,
      segments: [
        {
          start: 0,
          end: 60,
          intensity: 0.7,
          description: 'Intro section',
        },
      ],
    });

    render(<App />);

    const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(
      () => {
        expect(screen.getByText('Generated Prompts Preview')).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });
});
