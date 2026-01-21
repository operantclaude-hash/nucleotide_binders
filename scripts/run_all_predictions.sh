#!/bin/bash
# Batch script to run Boltz predictions for all nucleotide binders

set -e

cd "$(dirname "$0")/.."

echo "============================================"
echo "Nucleotide Binder Design Pipeline"
echo "Running Boltz predictions for all dNTPs"
echo "============================================"
echo ""

# Configuration
DEVICES=1
ACCELERATOR="gpu"
DIFFUSION_SAMPLES=5
SAMPLING_STEPS=200
RECYCLING_STEPS=3
USE_MSA_SERVER="--use_msa_server"

# Parse command line arguments
QUICK_MODE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            DIFFUSION_SAMPLES=1
            SAMPLING_STEPS=50
            shift
            ;;
        --no-msa-server)
            USE_MSA_SERVER=""
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--quick] [--no-msa-server]"
            exit 1
            ;;
    esac
done

if [ "$QUICK_MODE" = true ]; then
    echo "Running in QUICK mode (fewer samples)"
    echo ""
fi

# Array of nucleotides
NUCLEOTIDES=("dATP" "dGTP" "dCTP" "dTTP")

# Run predictions for each nucleotide
for NUC in "${NUCLEOTIDES[@]}"; do
    echo "----------------------------------------"
    echo "Processing: ${NUC}"
    echo "----------------------------------------"

    CONFIG="configs/${NUC}_binder.yaml"
    OUTPUT="results/${NUC}_predictions"

    if [ ! -f "$CONFIG" ]; then
        echo "ERROR: Config file not found: $CONFIG"
        continue
    fi

    echo "Config: $CONFIG"
    echo "Output: $OUTPUT"
    echo ""

    # Run Boltz
    boltz predict "$CONFIG" \
        --out_dir "$OUTPUT" \
        --devices $DEVICES \
        --accelerator $ACCELERATOR \
        --diffusion_samples $DIFFUSION_SAMPLES \
        --sampling_steps $SAMPLING_STEPS \
        --recycling_steps $RECYCLING_STEPS \
        $USE_MSA_SERVER \
        --write_full_pae

    echo "✓ Completed: ${NUC}"
    echo ""
done

echo "============================================"
echo "All predictions completed!"
echo "Results saved in: results/"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Review predicted structures in results/"
echo "2. Select best candidates"
echo "3. Insert optogenetic domains using scripts/insert_custom_optogenetic.py"
echo ""
