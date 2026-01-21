#!/bin/bash
# Setup script for Boltz-2 installation
# Run this on a machine with GPU support for best performance

set -e

echo "=== Boltz-2 Installation Script ==="
echo ""

# Check if conda/mamba is available
if command -v mamba &> /dev/null; then
    PKG_MANAGER="mamba"
elif command -v conda &> /dev/null; then
    PKG_MANAGER="conda"
else
    echo "Neither conda nor mamba found. Using pip directly."
    PKG_MANAGER="pip"
fi

# Create environment
if [ "$PKG_MANAGER" != "pip" ]; then
    echo "Creating boltz environment..."
    $PKG_MANAGER create -n boltz python=3.11 -y

    echo "Activating environment..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate boltz
fi

# Check for CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "CUDA GPU detected. Installing with CUDA support..."
    pip install boltz[cuda] -U
else
    echo "No CUDA GPU detected. Installing CPU version (will be slower)..."
    pip install boltz -U
fi

# Verify installation
echo ""
echo "Verifying installation..."
python -c "import boltz; print(f'Boltz version: {boltz.__version__}')" 2>/dev/null || echo "Boltz installed but version check failed"

# Test prediction capability
echo ""
echo "Testing Boltz prediction capability..."
boltz predict --help > /dev/null && echo "Boltz predict command available!" || echo "Warning: boltz predict not working"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To run predictions:"
echo "  boltz predict <input.yaml> --use_msa_server"
echo ""
echo "Example configs are in: configs/"
echo "  - dATP_binder.yaml"
echo "  - dGTP_binder.yaml"
echo "  - dCTP_binder.yaml"
echo "  - dTTP_binder.yaml"
