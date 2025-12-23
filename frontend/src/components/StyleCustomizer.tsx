import React, { useState } from 'react';
import { StyleCustomization } from '../types';

interface StyleCustomizerProps {
  onStyleChange: (style: StyleCustomization) => void;
  initialStyle?: StyleCustomization;
}

const THEME_OPTIONS = [
  { value: 'cinematic', label: 'Cinematic', description: 'Movie-like visuals' },
  { value: 'abstract', label: 'Abstract', description: 'Artistic patterns' },
  { value: 'nature', label: 'Nature', description: 'Natural landscapes' },
  { value: 'cosmic', label: 'Cosmic', description: 'Space and stars' },
  { value: 'urban', label: 'Urban', description: 'City and architecture' },
];

const VISUAL_STYLE_OPTIONS = [
  { value: 'realistic', label: 'Realistic' },
  { value: 'anime', label: 'Anime' },
  { value: 'oil-painting', label: 'Oil Painting' },
  { value: 'watercolor', label: 'Watercolor' },
  { value: 'digital-art', label: 'Digital Art' },
];

const COLOR_PALETTE_OPTIONS = [
  { value: 'vibrant', label: 'Vibrant', colors: ['#FF6B6B', '#4ECDC4', '#FFE66D', '#A8E6CF'] },
  { value: 'monochrome', label: 'Monochrome', colors: ['#000000', '#404040', '#808080', '#C0C0C0'] },
  { value: 'sunset', label: 'Sunset', colors: ['#FF6B35', '#F7931E', '#FDC830', '#F37335'] },
  { value: 'ocean', label: 'Ocean', colors: ['#006BA6', '#0496FF', '#00A8E8', '#7FC8F8'] },
  { value: 'forest', label: 'Forest', colors: ['#2D5016', '#50723C', '#789461', '#A2B592'] },
];

export const StyleCustomizer: React.FC<StyleCustomizerProps> = ({
  onStyleChange,
  initialStyle,
}) => {
  const [style, setStyle] = useState<StyleCustomization>(
    initialStyle || {
      theme: 'cinematic',
      colorPalette: COLOR_PALETTE_OPTIONS[0].colors,
      visualStyle: 'realistic',
      effectsIntensity: 0.7,
    }
  );

  const updateStyle = (updates: Partial<StyleCustomization>) => {
    const newStyle = { ...style, ...updates };
    setStyle(newStyle);
    onStyleChange(newStyle);
  };

  const handleThemeChange = (theme: string) => {
    updateStyle({ theme });
  };

  const handleVisualStyleChange = (visualStyle: string) => {
    updateStyle({ visualStyle });
  };

  const handleColorPaletteChange = (colors: string[]) => {
    updateStyle({ colorPalette: colors });
  };

  const handleIntensityChange = (intensity: number) => {
    updateStyle({ effectsIntensity: intensity });
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-lg shadow-md p-8 space-y-8">
      <h2 className="text-2xl font-bold text-gray-900 border-b pb-3">
        Customize Video Style
      </h2>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Theme
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {THEME_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => handleThemeChange(option.value)}
              className={`
                p-4 rounded-lg border-2 transition-all text-left
                ${style.theme === option.value
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300'
                }
              `}
              data-testid={`theme-${option.value}`}
            >
              <div className="font-medium text-gray-900">{option.label}</div>
              <div className="text-xs text-gray-500 mt-1">
                {option.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Visual Style
        </label>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {VISUAL_STYLE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => handleVisualStyleChange(option.value)}
              className={`
                p-3 rounded-lg border-2 transition-all
                ${style.visualStyle === option.value
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-primary-300'
                }
              `}
              data-testid={`visual-style-${option.value}`}
            >
              <div className="text-sm font-medium text-gray-900 text-center">
                {option.label}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Color Palette
        </label>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {COLOR_PALETTE_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => handleColorPaletteChange(option.colors)}
              className={`
                p-3 rounded-lg border-2 transition-all
                ${JSON.stringify(style.colorPalette) === JSON.stringify(option.colors)
                  ? 'border-primary-500'
                  : 'border-gray-200 hover:border-primary-300'
                }
              `}
              data-testid={`palette-${option.value}`}
            >
              <div className="text-xs font-medium text-gray-900 text-center mb-2">
                {option.label}
              </div>
              <div className="flex space-x-1">
                {option.colors.map((color, index) => (
                  <div
                    key={index}
                    className="flex-1 h-6 rounded"
                    style={{ backgroundColor: color }}
                  ></div>
                ))}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Effects Intensity: {Math.round(style.effectsIntensity * 100)}%
        </label>
        <input
          type="range"
          min="0"
          max="100"
          value={style.effectsIntensity * 100}
          onChange={(e) => handleIntensityChange(parseInt(e.target.value) / 100)}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          data-testid="intensity-slider"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>Subtle</span>
          <span>Moderate</span>
          <span>Intense</span>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-primary-500">
        <h3 className="font-medium text-gray-900 mb-2">Current Selection</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Theme:</span>
            <span className="ml-2 font-medium text-gray-900 capitalize">
              {style.theme}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Style:</span>
            <span className="ml-2 font-medium text-gray-900 capitalize">
              {style.visualStyle.replace('-', ' ')}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
