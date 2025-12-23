#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Audio to Music Video - Setup Script ==="
echo ""

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is not installed"
        exit 1
    fi
}

echo "Checking prerequisites..."
check_command python3
check_command pip3
check_command node
check_command npm

echo "Python version: $(python3 --version)"
echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"
echo ""

echo "Setting up Python backend..."
cd "$PROJECT_ROOT/backend"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ -f "tests/requirements-test.txt" ]; then
    echo "Installing test dependencies..."
    pip install -r tests/requirements-test.txt
fi

echo ""
echo "Setting up Electron/React frontend..."
cd "$PROJECT_ROOT/frontend"

echo "Installing npm dependencies..."
npm install

echo ""
echo "Cloning Ovi repository..."
cd "$PROJECT_ROOT"

if [ ! -d "Ovi" ]; then
    echo "Cloning Ovi from GitHub..."
    git clone https://github.com/character-ai/Ovi.git

    echo "Installing Ovi dependencies..."
    cd Ovi
    pip install torch==2.6.0 torchvision torchaudio
    pip install -r requirements.txt
    pip install flash_attn --no-build-isolation || echo "Flash Attention installation failed - optional"

    echo "Downloading Ovi model weights..."
    python3 download_weights.py --models 960x960_10s

    echo "Downloading FP8 quantized weights for 24GB VRAM..."
    mkdir -p ckpts/Ovi
    wget -O "./ckpts/Ovi/model_fp8_e4m3fn.safetensors" \
        "https://huggingface.co/rkfg/Ovi-fp8_quantized/resolve/main/model_fp8_e4m3fn.safetensors"
else
    echo "Ovi already cloned, skipping..."
fi

echo ""
echo "Creating output directories..."
mkdir -p "$PROJECT_ROOT/output"
mkdir -p "$PROJECT_ROOT/temp"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the application:"
echo "  1. Start the backend API:"
echo "     cd $PROJECT_ROOT/backend"
echo "     source venv/bin/activate"
echo "     python run_server.py"
echo ""
echo "  2. Start the frontend (in another terminal):"
echo "     cd $PROJECT_ROOT/frontend"
echo "     npm run dev"
echo ""
echo "  3. Or run the Electron desktop app:"
echo "     cd $PROJECT_ROOT/frontend"
echo "     npm run electron:dev"
