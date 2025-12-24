# Music Video Generator

Transform your audio files into AI-generated music videos using the Ovi model.

## Features

- **Audio Analysis**: Beat detection, mood classification, and lyrics extraction
- **Visual Prompt Generation**: Automatically creates scene descriptions based on audio characteristics
- **Style Customization**: Choose themes, color palettes, and visual styles
- **AI Video Generation**: Uses the Ovi model to generate synchronized video with audio
- **Desktop App**: Electron-based UI for easy interaction

## Requirements

- **GPU**: NVIDIA GPU with 24GB+ VRAM (tested on RTX 4090)
- **Python**: 3.10+
- **Node.js**: 18+
- **CUDA**: 11.8+ with cuDNN

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/albertoelopez/Music-Video-Generator.git
cd Music-Video-Generator
```

### 2. Clone and setup Ovi model

```bash
git clone https://github.com/character-ai/Ovi.git
cd Ovi
pip install -e .
```

Download the model weights (~22GB):
```bash
huggingface-cli download character-ai/Ovi --local-dir ./ckpts/Ovi
```

### 3. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3a. Setup MuseTalk Lip Sync (Optional)

For lip sync functionality, install the MMLab packages:

```bash
cd backend
./setup_mmlab.sh
```

This installs mmpose, mmcv (with CUDA), mmdet, and applies necessary compatibility patches for PyTorch 2.6.0.

Create symlinks to Ovi:
```bash
ln -s ../Ovi/ovi ovi
ln -s ../Ovi/ckpts ckpts
```

### 4. Setup Frontend

```bash
cd frontend
npm install
```

### 5. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` as needed:
```
OVI_PATH=../Ovi
OUTPUT_DIR=./output
TEMP_DIR=./temp
MODEL_NAME=960x960_10s
CPU_OFFLOAD=true
```

## Usage

### Start the Backend

```bash
cd backend
source venv/bin/activate
python run_server.py
```

The API will be available at `http://localhost:5000`

### Start the Frontend

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

### Generate a Video

1. Upload an audio file (MP3, WAV, FLAC)
2. Wait for audio analysis to complete
3. Customize the visual style (theme, colors, effects)
4. Click "Generate Music Video"
5. Download the result when complete

## Configuration

### Ovi Model Settings

Edit `Ovi/ovi/configs/inference/inference_fusion.yaml`:

| Setting | Description | Default |
|---------|-------------|---------|
| `model_name` | Model variant | `960x960_10s` |
| `cpu_offload` | Offload to RAM (required for 24GB VRAM) | `True` |
| `fp8` | FP8 quantization (only for 720x720_5s) | `False` |
| `mode` | Generation mode | `t2v` |
| `sample_steps` | Diffusion steps | `50` |

### Available Models

| Model | Resolution | Duration | VRAM (no offload) |
|-------|------------|----------|-------------------|
| `720x720_5s` | 720x720 | 5 sec | ~16GB |
| `960x960_5s` | 960x960 | 5 sec | ~20GB |
| `960x960_10s` | 960x960 | 10 sec | ~24GB+ |

## Architecture

```
audio_to_musicvideo/
├── backend/
│   ├── src/
│   │   ├── api.py                 # Flask REST API
│   │   ├── pipeline.py            # Main orchestration
│   │   ├── audio_analysis/        # Beat detection, mood, lyrics
│   │   ├── prompt_generation/     # Visual prompt creation
│   │   └── video_generation/      # Ovi integration
│   └── run_server.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main application
│   │   ├── components/            # React components
│   │   └── services/api.ts        # API client
│   └── electron/                  # Desktop app config
├── Ovi/                           # Ovi model (clone separately)
└── scripts/
    ├── setup.sh
    └── run.sh
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/upload` | POST | Upload audio file |
| `/api/analyze` | POST | Analyze uploaded audio |
| `/api/generate` | POST | Start video generation |
| `/api/job/<id>` | GET | Get job status |
| `/api/download/<path>` | GET | Download generated video |

## Troubleshooting

### CUDA Out of Memory

Ensure `cpu_offload: True` in `Ovi/ovi/configs/inference/inference_fusion.yaml`

Check for stuck processes:
```bash
nvidia-smi
kill -9 <PID>  # Kill any stuck Python processes
```

### FP8 Assertion Error

FP8 quantization only works with the `720x720_5s` model. For other models, set `fp8: False`.

### Model Not Loading

Verify symlinks in backend directory:
```bash
ls -la backend/ovi backend/ckpts
```

Should show:
```
backend/ovi -> ../Ovi/ovi
backend/ckpts -> ../Ovi/ckpts
```

### Lip Sync Not Working

If you see `ModuleNotFoundError: No module named 'mmpose'`, run the MMLab setup:
```bash
cd backend
./setup_mmlab.sh
```

If mmcv import fails with `No module named 'mmcv._ext'`, mmcv needs to be rebuilt with CUDA:
```bash
source venv/bin/activate
pip uninstall mmcv -y
export MMCV_WITH_OPS=1 FORCE_CUDA=1
pip install mmcv==2.2.0 --no-cache-dir --no-build-isolation
```

## License

MIT

## Acknowledgments

- [Ovi](https://github.com/character-ai/Ovi) - The AI model powering video generation
- [Character.AI](https://character.ai) - Creators of the Ovi model
