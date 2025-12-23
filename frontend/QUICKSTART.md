# Quick Start Guide

## Installation

```bash
cd /home/darthvader/AI_Projects/audio_to_musicvideo/frontend
npm install
```

## Development

1. Make sure the Flask backend is running on `http://localhost:5000`

2. Start the development server:
```bash
npm run dev
```

This will start:
- React dev server on `http://localhost:3000`
- Electron desktop app

## Testing

Run unit tests:
```bash
npm test
```

Run E2E tests:
```bash
npm run test:e2e
```

## Building

Build for production:
```bash
npm run build
npm run build:electron
```

## Project Structure

```
/home/darthvader/AI_Projects/audio_to_musicvideo/frontend/
├── electron/
│   ├── main.ts              # Electron main process
│   └── preload.ts           # Preload script for IPC
├── src/
│   ├── components/
│   │   ├── AudioUpload.tsx           # File upload with drag & drop
│   │   ├── AnalysisDisplay.tsx       # Audio analysis results
│   │   ├── StyleCustomizer.tsx       # Theme/style customization
│   │   ├── GenerationProgress.tsx    # Progress tracking
│   │   └── __tests__/               # Component unit tests
│   ├── services/
│   │   ├── api.ts                   # API client
│   │   └── __tests__/               # Service tests
│   ├── types/
│   │   └── index.ts                 # TypeScript definitions
│   ├── App.tsx                      # Main application
│   ├── index.tsx                    # Entry point
│   └── index.css                    # Tailwind styles
├── tests/
│   ├── e2e/
│   │   └── app.spec.ts              # Playwright E2E tests
│   ├── fixtures/                    # Test fixtures
│   └── setup.ts                     # Test setup
└── public/
    └── index.html                   # HTML template
```

## Key Features

1. Audio Upload - Drag & drop or file picker for MP3/WAV files
2. Audio Analysis - Real-time analysis showing tempo, mood, genre, segments
3. Style Customization - Choose themes, visual styles, color palettes, effects intensity
4. Generation Progress - Live progress tracking with status updates
5. Video Download - Download generated music video

## API Endpoints Used

- POST `/api/upload` - Upload audio file
- POST `/api/analyze` - Analyze audio
- POST `/api/generate` - Generate video
- GET `/api/progress/:jobId` - Get generation progress
- GET `/api/download` - Download video

## Testing Coverage

- Unit Tests: All components and services
- E2E Tests: Complete user workflow
- Test Framework: Jest + React Testing Library + Playwright

## Code Standards

- No single-line or multi-line comments
- Self-documenting code with clear naming
- TDD approach: Tests written before implementation
- TypeScript strict mode enabled
- ESLint for code quality
