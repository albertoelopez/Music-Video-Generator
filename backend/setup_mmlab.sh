#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
SITE_PACKAGES="${VENV_DIR}/lib/python3.11/site-packages"

echo "Installing MMLab packages for MuseTalk lip sync..."

source "${VENV_DIR}/bin/activate"

pip install --no-cache-dir -U openmim
mim install mmengine

pip install chumpy --no-build-isolation

echo "Building mmcv with CUDA extensions (this may take a few minutes)..."
export MMCV_WITH_OPS=1
export FORCE_CUDA=1
pip install mmcv==2.2.0 --no-cache-dir --no-build-isolation

mim install "mmdet>=3.3.0"
mim install "mmpose>=1.3.0"

echo "Applying compatibility patches..."

MMDET_INIT="${SITE_PACKAGES}/mmdet/__init__.py"
if [ -f "$MMDET_INIT" ]; then
    sed -i "s/mmcv_maximum_version = '2.2.0'/mmcv_maximum_version = '2.3.0'/" "$MMDET_INIT"
    echo "Patched mmdet to allow mmcv 2.2.0"
fi

MMENGINE_CHECKPOINT="${SITE_PACKAGES}/mmengine/runner/checkpoint.py"
if [ -f "$MMENGINE_CHECKPOINT" ]; then
    sed -i 's/torch\.load(filename, map_location=map_location)/torch.load(filename, map_location=map_location, weights_only=False)/g' "$MMENGINE_CHECKPOINT"
    sed -i 's/torch\.load(downloaded_file, map_location=map_location)/torch.load(downloaded_file, map_location=map_location, weights_only=False)/g' "$MMENGINE_CHECKPOINT"
    sed -i 's/torch\.load(buffer, map_location=map_location)/torch.load(buffer, map_location=map_location, weights_only=False)/g' "$MMENGINE_CHECKPOINT"
    echo "Patched mmengine for PyTorch 2.6.0 compatibility"
fi

echo "MMLab setup complete!"
echo "Installed versions:"
pip list | grep -E "mmcv|mmdet|mmpose|mmengine"
