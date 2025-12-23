import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StyleCustomizer } from '../StyleCustomizer';
import { StyleCustomization } from '../../types';

describe('StyleCustomizer', () => {
  const mockOnStyleChange = jest.fn();

  beforeEach(() => {
    mockOnStyleChange.mockClear();
  });

  it('renders all theme options', () => {
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    expect(screen.getByText('Cinematic')).toBeInTheDocument();
    expect(screen.getByText('Abstract')).toBeInTheDocument();
    expect(screen.getByText('Nature')).toBeInTheDocument();
    expect(screen.getByText('Cosmic')).toBeInTheDocument();
    expect(screen.getByText('Urban')).toBeInTheDocument();
  });

  it('renders all visual style options', () => {
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    expect(screen.getByText('Realistic')).toBeInTheDocument();
    expect(screen.getByText('Anime')).toBeInTheDocument();
    expect(screen.getByText('Oil Painting')).toBeInTheDocument();
    expect(screen.getByText('Watercolor')).toBeInTheDocument();
    expect(screen.getByText('Digital Art')).toBeInTheDocument();
  });

  it('renders all color palette options', () => {
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    expect(screen.getByText('Vibrant')).toBeInTheDocument();
    expect(screen.getByText('Monochrome')).toBeInTheDocument();
    expect(screen.getByText('Sunset')).toBeInTheDocument();
    expect(screen.getByText('Ocean')).toBeInTheDocument();
    expect(screen.getByText('Forest')).toBeInTheDocument();
  });

  it('calls onStyleChange when theme is selected', async () => {
    const user = userEvent.setup();
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const abstractButton = screen.getByTestId('theme-abstract');
    await user.click(abstractButton);

    expect(mockOnStyleChange).toHaveBeenCalledWith(
      expect.objectContaining({ theme: 'abstract' })
    );
  });

  it('calls onStyleChange when visual style is selected', async () => {
    const user = userEvent.setup();
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const animeButton = screen.getByTestId('visual-style-anime');
    await user.click(animeButton);

    expect(mockOnStyleChange).toHaveBeenCalledWith(
      expect.objectContaining({ visualStyle: 'anime' })
    );
  });

  it('calls onStyleChange when color palette is selected', async () => {
    const user = userEvent.setup();
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const sunsetButton = screen.getByTestId('palette-sunset');
    await user.click(sunsetButton);

    expect(mockOnStyleChange).toHaveBeenCalledWith(
      expect.objectContaining({
        colorPalette: ['#FF6B35', '#F7931E', '#FDC830', '#F37335'],
      })
    );
  });

  it('updates intensity when slider changes', async () => {
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const slider = screen.getByTestId('intensity-slider');
    fireEvent.change(slider, { target: { value: '50' } });

    expect(mockOnStyleChange).toHaveBeenCalledWith(
      expect.objectContaining({ effectsIntensity: 0.5 })
    );
  });

  it('displays current intensity percentage', () => {
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    expect(screen.getByText('Effects Intensity: 70%')).toBeInTheDocument();
  });

  it('updates intensity display when slider changes', () => {
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const slider = screen.getByTestId('intensity-slider');
    fireEvent.change(slider, { target: { value: '90' } });

    expect(screen.getByText('Effects Intensity: 90%')).toBeInTheDocument();
  });

  it('uses initial style when provided', () => {
    const initialStyle: StyleCustomization = {
      theme: 'cosmic',
      colorPalette: ['#000000', '#404040', '#808080', '#C0C0C0'],
      visualStyle: 'digital-art',
      effectsIntensity: 0.5,
    };

    render(
      <StyleCustomizer
        onStyleChange={mockOnStyleChange}
        initialStyle={initialStyle}
      />
    );

    expect(screen.getByText('Effects Intensity: 50%')).toBeInTheDocument();
  });

  it('highlights selected theme', async () => {
    const user = userEvent.setup();
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const natureButton = screen.getByTestId('theme-nature');
    await user.click(natureButton);

    expect(natureButton).toHaveClass('border-primary-500');
  });

  it('highlights selected visual style', async () => {
    const user = userEvent.setup();
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const watercolorButton = screen.getByTestId('visual-style-watercolor');
    await user.click(watercolorButton);

    expect(watercolorButton).toHaveClass('border-primary-500');
  });

  it('displays current selection summary', () => {
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    expect(screen.getByText('Current Selection')).toBeInTheDocument();
    expect(screen.getByText('cinematic')).toBeInTheDocument();
    expect(screen.getByText('realistic')).toBeInTheDocument();
  });

  it('updates current selection summary when style changes', async () => {
    const user = userEvent.setup();
    render(<StyleCustomizer onStyleChange={mockOnStyleChange} />);

    const urbanButton = screen.getByTestId('theme-urban');
    await user.click(urbanButton);

    expect(screen.getByText('urban')).toBeInTheDocument();
  });
});
