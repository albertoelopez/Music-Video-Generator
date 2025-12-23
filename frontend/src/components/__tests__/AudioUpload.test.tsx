import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AudioUpload } from '../AudioUpload';

describe('AudioUpload', () => {
  const mockOnFileSelect = jest.fn();

  beforeEach(() => {
    mockOnFileSelect.mockClear();
  });

  it('renders upload area with correct text', () => {
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    expect(screen.getByText('Drop your audio file here')).toBeInTheDocument();
    expect(screen.getByText('or click to browse')).toBeInTheDocument();
    expect(screen.getByText('Supports MP3 and WAV files')).toBeInTheDocument();
  });

  it('handles valid file selection via input', async () => {
    const user = userEvent.setup();
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    const file = new File(['audio content'], 'test.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    });
  });

  it('handles valid WAV file selection', async () => {
    const user = userEvent.setup();
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    const file = new File(['audio content'], 'test.wav', { type: 'audio/wav' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    });
  });

  it('shows selected file name after selection', async () => {
    const user = userEvent.setup();
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    const file = new File(['audio content'], 'my-song.mp3', { type: 'audio/mpeg' });
    const input = screen.getByTestId('file-input') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText('my-song.mp3')).toBeInTheDocument();
    });
  });

  it('shows processing state when isProcessing is true', () => {
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={true} />);

    expect(screen.getByText('Processing...')).toBeInTheDocument();
    expect(screen.queryByText('Select Audio File')).not.toBeInTheDocument();
  });

  it('disables input when processing', () => {
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={true} />);

    const input = screen.getByTestId('file-input') as HTMLInputElement;
    expect(input).toBeDisabled();
  });

  it('handles drag and drop', async () => {
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    const file = new File(['audio content'], 'dropped.mp3', { type: 'audio/mpeg' });
    const dropZone = screen.getByText('Drop your audio file here').closest('div');

    fireEvent.dragEnter(dropZone!);
    fireEvent.dragOver(dropZone!);
    fireEvent.drop(dropZone!, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(mockOnFileSelect).toHaveBeenCalledWith(file);
    });
  });

  it('highlights drop zone on drag enter', () => {
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    const dropZone = screen.getByText('Drop your audio file here').closest('div');

    fireEvent.dragEnter(dropZone!);

    expect(dropZone).toHaveClass('border-primary-500');
  });

  it('removes highlight on drag leave', () => {
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    const dropZone = screen.getByText('Drop your audio file here').closest('div');

    fireEvent.dragEnter(dropZone!);
    fireEvent.dragLeave(dropZone!);

    expect(dropZone).not.toHaveClass('border-primary-500');
  });

  it('opens file picker when clicking select button', async () => {
    const user = userEvent.setup();
    render(<AudioUpload onFileSelect={mockOnFileSelect} isProcessing={false} />);

    const input = screen.getByTestId('file-input') as HTMLInputElement;
    const clickSpy = jest.spyOn(input, 'click');

    const button = screen.getByText('Select Audio File');
    await user.click(button);

    expect(clickSpy).toHaveBeenCalled();
  });
});
