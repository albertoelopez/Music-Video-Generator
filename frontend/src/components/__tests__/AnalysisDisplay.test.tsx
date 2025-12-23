import React from 'react';
import { render, screen } from '@testing-library/react';
import { AnalysisDisplay } from '../AnalysisDisplay';
import { AudioAnalysis } from '../../types';

describe('AnalysisDisplay', () => {
  const mockAnalysis: AudioAnalysis = {
    tempo: 128.5,
    mood: 'energetic',
    genre: 'electronic',
    duration: 180,
    energy: 0.85,
    danceability: 0.75,
    segments: [
      {
        start: 0,
        end: 30,
        intensity: 0.6,
        description: 'Intro with soft synths',
      },
      {
        start: 30,
        end: 90,
        intensity: 0.9,
        description: 'High energy drop',
      },
      {
        start: 90,
        end: 180,
        intensity: 0.7,
        description: 'Melodic outro',
      },
    ],
  };

  it('renders loading state when isLoading is true', () => {
    render(<AnalysisDisplay analysis={null} isLoading={true} />);

    expect(screen.getByText('Analyzing audio...')).toBeInTheDocument();
  });

  it('renders nothing when not loading and no analysis', () => {
    const { container } = render(<AnalysisDisplay analysis={null} isLoading={false} />);

    expect(container.firstChild).toBeNull();
  });

  it('renders analysis data correctly', () => {
    render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    expect(screen.getByText('Audio Analysis')).toBeInTheDocument();
    expect(screen.getByText('129')).toBeInTheDocument();
    expect(screen.getByText('energetic')).toBeInTheDocument();
    expect(screen.getByText('electronic')).toBeInTheDocument();
    expect(screen.getByText('3:00')).toBeInTheDocument();
  });

  it('displays energy level as percentage', () => {
    render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('displays danceability as percentage', () => {
    render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('renders all segments', () => {
    render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    expect(screen.getByText('Segment 1')).toBeInTheDocument();
    expect(screen.getByText('Segment 2')).toBeInTheDocument();
    expect(screen.getByText('Segment 3')).toBeInTheDocument();
  });

  it('displays segment time ranges', () => {
    render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    expect(screen.getByText('0:00 - 0:30')).toBeInTheDocument();
    expect(screen.getByText('0:30 - 1:30')).toBeInTheDocument();
    expect(screen.getByText('1:30 - 3:00')).toBeInTheDocument();
  });

  it('displays segment descriptions', () => {
    render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    expect(screen.getByText('Intro with soft synths')).toBeInTheDocument();
    expect(screen.getByText('High energy drop')).toBeInTheDocument();
    expect(screen.getByText('Melodic outro')).toBeInTheDocument();
  });

  it('shows segment count in header', () => {
    render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    expect(screen.getByText('Audio Segments (3)')).toBeInTheDocument();
  });

  it('formats time correctly for minutes and seconds', () => {
    const analysis: AudioAnalysis = {
      ...mockAnalysis,
      duration: 65,
      segments: [
        {
          start: 5,
          end: 65,
          intensity: 0.5,
          description: 'Test segment',
        },
      ],
    };

    render(<AnalysisDisplay analysis={analysis} isLoading={false} />);

    expect(screen.getByText('1:05')).toBeInTheDocument();
    expect(screen.getByText('0:05 - 1:05')).toBeInTheDocument();
  });

  it('renders energy progress bar with correct width', () => {
    const { container } = render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    const energyBar = container.querySelector('[style*="width: 85%"]');
    expect(energyBar).toBeInTheDocument();
  });

  it('renders danceability progress bar with correct width', () => {
    const { container } = render(<AnalysisDisplay analysis={mockAnalysis} isLoading={false} />);

    const danceabilityBar = container.querySelector('[style*="width: 75%"]');
    expect(danceabilityBar).toBeInTheDocument();
  });
});
