# Audio to Music Video - Frontend

Desktop application built with Electron, React, and TypeScript for converting audio files into AI-generated music videos.

## Features

- Audio file upload with drag & drop support
- Real-time audio analysis (tempo, mood, genre, segments)
- Customizable visual styles and themes
- Live generation progress tracking
- Video download functionality

## Tech Stack

- Electron - Desktop app framework
- React 18 - UI framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Vite - Build tool
- Jest + React Testing Library - Unit testing
- Playwright - E2E testing

## Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on http://localhost:5000

## Installation

```bash
npm install
```

## Development

Start the development server:

```bash
npm run dev
```

This will start both the React dev server and Electron app.

## Testing

Run unit tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm test:watch
```

Run E2E tests:

```bash
npm run test:e2e
```

## Building

Build for production:

```bash
npm run build
```

Build Electron app:

```bash
npm run build:electron
```

## Project Structure

```
frontend/
├── electron/           # Electron main and preload scripts
├── src/
│   ├── components/    # React components
│   ├── services/      # API client
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main application component
│   └── index.tsx      # Application entry point
├── tests/
│   ├── e2e/          # Playwright E2E tests
│   └── setup.ts      # Test configuration
└── public/           # Static assets
```

## API Integration

The frontend communicates with the Flask backend at `http://localhost:5000`. Ensure the backend is running before starting the frontend.

API endpoints:
- POST `/api/upload` - Upload audio file
- POST `/api/analyze` - Analyze audio
- POST `/api/generate` - Generate video
- GET `/api/progress/:jobId` - Get generation progress
- GET `/api/download` - Download video

## License

MIT
