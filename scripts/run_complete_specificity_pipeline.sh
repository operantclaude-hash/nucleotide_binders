#!/bin/bash
# Master script to run complete specificity screening pipeline

set -e

echo "================================================================================"
echo "NUCLEOTIDE-SPECIFIC BINDER DESIGN - COMPLETE PIPELINE"
echo "================================================================================"
echo ""

# Configuration
VARIANTS_PER_TARGET=20
SEED=42
LIBRARY_DIR="../specificity_library"
QUICK_MODE=false
TEST_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --test)
            TEST_MODE=true
            VARIANTS_PER_TARGET=5
            LIBRARY_DIR="../specificity_library_test"
            shift
            ;;
        --variants)
            VARIANTS_PER_TARGET=$2
            shift 2
            ;;
        --seed)
            SEED=$2
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--quick] [--test] [--variants N] [--seed N]"
            echo ""
            echo "Options:"
            echo "  --quick       Use faster prediction settings (lower quality)"
            echo "  --test        Test mode (5 variants, for pipeline validation)"
            echo "  --variants N  Number of variants per nucleotide (default: 20)"
            echo "  --seed N      Random seed for reproducibility (default: 42)"
            exit 1
            ;;
    esac
done

cd "$(dirname "$0")"

# Summary
echo "Configuration:"
echo "  Variants per nucleotide: $VARIANTS_PER_TARGET"
echo "  Total variants: $((VARIANTS_PER_TARGET * 4))"
echo "  Total predictions: $((VARIANTS_PER_TARGET * 4 * 4))"
echo "  Random seed: $SEED"
echo "  Mode: $([ "$QUICK_MODE" = true ] && echo "QUICK" || echo "PRODUCTION")"
echo "  Test mode: $([ "$TEST_MODE" = true ] && echo "YES" || echo "NO")"
echo "  Library directory: $LIBRARY_DIR"
echo ""

if [ "$TEST_MODE" = false ]; then
    TOTAL_PREDS=$((VARIANTS_PER_TARGET * 16))
    if [ "$QUICK_MODE" = true ]; then
        EST_TIME=$((TOTAL_PREDS * 3 / 60))
    else
        EST_TIME=$((TOTAL_PREDS * 8 / 60))
    fi
    echo "Estimated time: ~$EST_TIME hours"
    echo ""

    read -p "Continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
fi

START_TIME=$(date +%s)

echo ""
echo "================================================================================"
echo "STEP 1: Generate CDR Library"
echo "================================================================================"
echo ""

python generate_cdr_library.py \
    --variants-per-target $VARIANTS_PER_TARGET \
    --seed $SEED \
    --output-dir $LIBRARY_DIR

if [ $? -ne 0 ]; then
    echo "ERROR: Library generation failed"
    exit 1
fi

echo ""
echo "================================================================================"
echo "STEP 2: Generate MSAs"
echo "================================================================================"
echo ""

python generate_library_msas.py \
    --library-dir $LIBRARY_DIR \
    --msa-output-dir $LIBRARY_DIR/msas

if [ $? -ne 0 ]; then
    echo "ERROR: MSA generation failed"
    exit 1
fi

echo ""
echo "================================================================================"
echo "STEP 3: Run Batch Predictions"
echo "================================================================================"
echo ""

if [ "$TEST_MODE" = true ]; then
    python run_specificity_screen.py \
        --library-dir $LIBRARY_DIR \
        --results-dir $LIBRARY_DIR/screening_results \
        --quick \
        --limit 10
else
    if [ "$QUICK_MODE" = true ]; then
        python run_specificity_screen.py \
            --library-dir $LIBRARY_DIR \
            --results-dir $LIBRARY_DIR/screening_results \
            --quick
    else
        python run_specificity_screen.py \
            --library-dir $LIBRARY_DIR \
            --results-dir $LIBRARY_DIR/screening_results
    fi
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Batch predictions failed"
    exit 1
fi

echo ""
echo "================================================================================"
echo "STEP 4: Analyze Specificity"
echo "================================================================================"
echo ""

python analyze_specificity.py \
    --results-file $LIBRARY_DIR/screening_results/screening_results.json \
    --output-dir $LIBRARY_DIR/analysis

if [ $? -ne 0 ]; then
    echo "ERROR: Analysis failed"
    exit 1
fi

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_HOURS=$((ELAPSED / 3600))
ELAPSED_MINS=$(((ELAPSED % 3600) / 60))

echo ""
echo "================================================================================"
echo "PIPELINE COMPLETE!"
echo "================================================================================"
echo ""
echo "Total time: ${ELAPSED_HOURS}h ${ELAPSED_MINS}m"
echo ""
echo "Results:"
echo "  Library: $LIBRARY_DIR/"
echo "  Analysis: $LIBRARY_DIR/analysis/"
echo "  Report: $LIBRARY_DIR/analysis/specificity_report.txt"
echo ""
echo "Next steps:"
echo "1. Review top candidates:"
echo "   cat $LIBRARY_DIR/analysis/specificity_report.txt"
echo ""
echo "2. Extract best sequences and add optogenetic domains:"
echo "   python insert_custom_optogenetic.py --sequence YOUR_BEST_SEQ --domain LOV2"
echo ""
echo "3. Proceed to experimental validation"
echo ""
