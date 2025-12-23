import React from 'react';
import { render, screen } from '@testing-library/react';
import { GenerationProgress } from '../GenerationProgress';
import { GenerationProgress as GenerationProgressType } from '../../types';

describe('GenerationProgress', () => {
  it('renders nothing when status is idle', () => {
    const progress: GenerationProgressType = {
      status: 'idle',
      currentStep: '',
      progress: 0,
      message: '',
    };

    const { container } = render(<GenerationProgress progress={progress} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders analyzing status correctly', () => {
    const progress: GenerationProgressType = {
      status: 'analyzing',
      currentStep: 'Analyzing Audio',
      progress: 25,
      message: 'Extracting audio features',
    };

    render(<GenerationProgress progress={progress} />);

    expect(screen.getByText('Analyzing Audio')).toBeInTheDocument();
    expect(screen.getByText('Extracting audio features')).toBeInTheDocument();
    expect(screen.getByText('25%')).toBeInTheDocument();
  });

  it('renders generating status correctly', () => {
    const progress: GenerationProgressType = {
      status: 'generating',
      currentStep: 'Generating Video',
      progress: 60,
      message: 'Creating video frames',
    };

    render(<GenerationProgress progress={progress} />);

    expect(screen.getByText('Generating Video')).toBeInTheDocument();
    expect(screen.getByText('Creating video frames')).toBeInTheDocument();
    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('shows generation substeps when generating', () => {
    const progress: GenerationProgressType = {
      status: 'generating',
      currentStep: 'Generating Video',
      progress: 50,
      message: 'Processing',
    };

    render(<GenerationProgress progress={progress} />);

    expect(screen.getByText('Video Frames')).toBeInTheDocument();
    expect(screen.getByText('Audio Track')).toBeInTheDocument();
    expect(screen.getByText('Final Output')).toBeInTheDocument();
  });

  it('renders complete status with success message', () => {
    const progress: GenerationProgressType = {
      status: 'complete',
      currentStep: 'Complete',
      progress: 100,
      message: 'Video ready',
    };

    render(<GenerationProgress progress={progress} />);

    expect(screen.getByText('Video generation complete!')).toBeInTheDocument();
    expect(screen.getByText('Your music video is ready to download.')).toBeInTheDocument();
  });

  it('renders error status with error message', () => {
    const progress: GenerationProgressType = {
      status: 'error',
      currentStep: 'Failed',
      progress: 0,
      message: 'Network connection lost',
    };

    render(<GenerationProgress progress={progress} />);

    expect(screen.getByText('Generation failed')).toBeInTheDocument();
    expect(screen.getByText('Network connection lost')).toBeInTheDocument();
  });

  it('displays correct progress bar width', () => {
    const progress: GenerationProgressType = {
      status: 'generating',
      currentStep: 'Generating',
      progress: 75,
      message: 'Processing',
    };

    const { container } = render(<GenerationProgress progress={progress} />);
    const progressBar = container.querySelector('[style*="width: 75%"]');

    expect(progressBar).toBeInTheDocument();
  });

  it('applies correct color for analyzing status', () => {
    const progress: GenerationProgressType = {
      status: 'analyzing',
      currentStep: 'Analyzing',
      progress: 25,
      message: 'Processing',
    };

    render(<GenerationProgress progress={progress} />);

    const stepElement = screen.getByText('Analyzing');
    expect(stepElement).toHaveClass('text-blue-600');
  });

  it('applies correct color for generating status', () => {
    const progress: GenerationProgressType = {
      status: 'generating',
      currentStep: 'Generating',
      progress: 50,
      message: 'Processing',
    };

    render(<GenerationProgress progress={progress} />);

    const stepElement = screen.getByText('Generating');
    expect(stepElement).toHaveClass('text-purple-600');
  });

  it('applies correct color for complete status', () => {
    const progress: GenerationProgressType = {
      status: 'complete',
      currentStep: 'Complete',
      progress: 100,
      message: 'Done',
    };

    render(<GenerationProgress progress={progress} />);

    const stepElement = screen.getByText('Complete');
    expect(stepElement).toHaveClass('text-green-600');
  });

  it('applies correct color for error status', () => {
    const progress: GenerationProgressType = {
      status: 'error',
      currentStep: 'Error',
      progress: 0,
      message: 'Failed',
    };

    render(<GenerationProgress progress={progress} />);

    const stepElement = screen.getByText('Error');
    expect(stepElement).toHaveClass('text-red-600');
  });

  it('shows spinner icon for analyzing status', () => {
    const progress: GenerationProgressType = {
      status: 'analyzing',
      currentStep: 'Analyzing',
      progress: 25,
      message: 'Processing',
    };

    const { container } = render(<GenerationProgress progress={progress} />);
    const spinner = container.querySelector('.animate-spin');

    expect(spinner).toBeInTheDocument();
  });

  it('shows checkmark icon for complete status', () => {
    const progress: GenerationProgressType = {
      status: 'complete',
      currentStep: 'Complete',
      progress: 100,
      message: 'Done',
    };

    const { container } = render(<GenerationProgress progress={progress} />);
    const checkmark = container.querySelector('path[d*="M5 13l4 4L19 7"]');

    expect(checkmark).toBeInTheDocument();
  });
});
