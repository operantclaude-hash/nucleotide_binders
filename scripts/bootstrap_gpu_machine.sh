#!/bin/bash
# Bootstrap script for GPU machine
# Run this first, then use Claude Code for the rest

set -e

echo "=== Nucleotide Catcher Pipeline Bootstrap ==="
echo ""

# Create directory structure
echo "Creating directory structure..."
mkdir -p ~/nucleotide_catchers/{structures,configs,scripts,outputs/{rfdiffusion,ligandmpnn,boltz,chimeras,figures}}
cd ~/nucleotide_catchers

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Create conda environment
echo ""
echo "Creating conda environment..."
conda create -n nucleotide_design python=3.11 -y
source $(conda info --base)/etc/profile.d/conda.sh
conda activate nucleotide_design

# Install PyTorch with CUDA
echo ""
echo "Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Check GPU
echo ""
echo "Checking GPU availability..."
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
else:
    print('WARNING: No GPU detected. Pipeline will be slow.')
"

# Install Boltz
echo ""
echo "Installing Boltz-2..."
pip install boltz[cuda] -U

# Verify Boltz
echo ""
echo "Verifying Boltz installation..."
python -c "import boltz; print('Boltz installed successfully')" 2>/dev/null || echo "Boltz import check failed (may still work)"

# Install other dependencies
echo ""
echo "Installing additional dependencies..."
pip install biopython requests pyyaml pandas numpy

# Download PDB structures
echo ""
echo "Downloading reference PDB structures..."
cd structures
for pdb in 2V0U 3G9A 3T04 6IR1; do
    if [ ! -f "${pdb}.pdb" ]; then
        echo "  Downloading ${pdb}..."
        curl -sO "https://files.rcsb.org/download/${pdb}.pdb"
    else
        echo "  ${pdb}.pdb already exists"
    fi
done
cd ..

# Create placeholder configs
echo ""
echo "Creating Boltz config files..."

cat > configs/dATP_binder.yaml << 'EOF'
version: 1
sequences:
  - protein:
      id: A
      sequence: QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGLDVWGQGTLVTVSS
  - ligand:
      id: B
      smiles: 'Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3'
EOF

cat > configs/dGTP_binder.yaml << 'EOF'
version: 1
sequences:
  - protein:
      id: A
      sequence: QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGLDVWGQGTLVTVSS
  - ligand:
      id: B
      smiles: 'Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1'
EOF

cat > configs/dCTP_binder.yaml << 'EOF'
version: 1
sequences:
  - protein:
      id: A
      sequence: QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGLDVWGQGTLVTVSS
  - ligand:
      id: B
      smiles: 'Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1'
EOF

cat > configs/dTTP_binder.yaml << 'EOF'
version: 1
sequences:
  - protein:
      id: A
      sequence: QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGLDVWGQGTLVTVSS
  - ligand:
      id: B
      smiles: 'Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O'
EOF

echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "Directory structure created at: ~/nucleotide_catchers"
echo "Conda environment: nucleotide_design"
echo ""
echo "Next steps:"
echo "1. Activate environment: conda activate nucleotide_design"
echo "2. Test Boltz: boltz predict configs/dATP_binder.yaml --use_msa_server --out_dir outputs/boltz/test"
echo "3. Run Claude Code with the QUICK_START_PROMPT.txt for full pipeline"
echo ""
echo "For RFdiffusion installation (optional, requires more setup):"
echo "  git clone https://github.com/RosettaCommons/RFdiffusion.git"
echo "  cd RFdiffusion && pip install -e ."
echo ""
