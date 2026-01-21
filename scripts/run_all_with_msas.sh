#!/bin/bash
# Batch script to run Boltz predictions for all nucleotide binders using local MSAs

set -e

cd "$(dirname "$0")/.."

echo "============================================"
echo "Nucleotide Binder Design Pipeline"
echo "Running Boltz with Local MSAs"
echo "============================================"
echo ""

# Configuration
DEVICES=1
ACCELERATOR="gpu"
DIFFUSION_SAMPLES=5
SAMPLING_STEPS=200
RECYCLING_STEPS=3

# Parse command line arguments
QUICK_MODE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            DIFFUSION_SAMPLES=1
            SAMPLING_STEPS=50
            RECYCLING_STEPS=1
            shift
            ;;
        --test)
            QUICK_MODE=true
            DIFFUSION_SAMPLES=1
            SAMPLING_STEPS=10
            RECYCLING_STEPS=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--quick|--test]"
            echo "  --quick: Faster predictions (50 steps)"
            echo "  --test:  Very fast test (10 steps)"
            exit 1
            ;;
    esac
done

if [ "$QUICK_MODE" = true ]; then
    echo "Running in REDUCED mode"
    echo "  Diffusion samples: $DIFFUSION_SAMPLES"
    echo "  Sampling steps: $SAMPLING_STEPS"
    echo "  Recycling steps: $RECYCLING_STEPS"
    echo ""
else
    echo "Running in PRODUCTION mode"
    echo "  Diffusion samples: $DIFFUSION_SAMPLES"
    echo "  Sampling steps: $SAMPLING_STEPS"
    echo "  Recycling steps: $RECYCLING_STEPS"
    echo "  (This may take several hours)"
    echo ""
fi

# Array of nucleotides
NUCLEOTIDES=("dATP" "dGTP" "dCTP" "dTTP")

# Run predictions for each nucleotide
for NUC in "${NUCLEOTIDES[@]}"; do
    echo "----------------------------------------"
    echo "Processing: ${NUC}"
    echo "----------------------------------------"

    CONFIG="configs_with_msas/${NUC}_binder.yaml"
    OUTPUT="results/${NUC}_predictions"

    if [ ! -f "$CONFIG" ]; then
        echo "ERROR: Config file not found: $CONFIG"
        echo "Run: cd scripts && python generate_msas.py && python update_configs_with_msas.py"
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
        --write_full_pae \
        --write_full_pde

    echo "✓ Completed: ${NUC}"
    echo ""
done

echo "============================================"
echo "All predictions completed!"
echo "============================================"
echo ""
echo "Results saved in: results/"
echo ""
echo "Next steps:"
echo "1. Review predicted structures:"
for NUC in "${NUCLEOTIDES[@]}"; do
    echo "   results/${NUC}_predictions/boltz_results_${NUC}_binder/predictions/${NUC}_binder/"
done
echo ""
echo "2. Examine confidence scores in confidence_*.json files"
echo "3. Visualize structures in PyMOL or ChimeraX"
echo "4. Select best nanobody sequences"
echo "5. Insert optogenetic domains:"
echo "   cd scripts"
echo "   python insert_custom_optogenetic.py --sequence YOUR_BEST_NANOBODY --domain LOV2"
echo ""
