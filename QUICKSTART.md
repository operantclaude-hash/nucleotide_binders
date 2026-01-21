# Quick Start Guide

Get started with the nucleotide binder design pipeline in 5 minutes.

## Step 1: Test the Installation

```bash
cd ~/nucleotide_catchers

# Verify Boltz is installed
boltz --help

# Check GPU availability
nvidia-smi
```

## Step 2: Generate Optogenetic Chimeras

Generate all three optogenetic nanobody variants:

```bash
cd scripts
python insert_optogenetic_domains.py
```

**Output:**
- `results/optogenetic_chimeras/optogenetic_nanobody_chimeras.fasta`
- `results/optogenetic_chimeras/chimera_report.txt`

View the chimeras:
```bash
cat ../results/optogenetic_chimeras/chimera_report.txt
```

## Step 3: Design Custom Optogenetic Variant

Insert LOV2 domain into your own nanobody:

```bash
python insert_custom_optogenetic.py \
    --sequence "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS" \
    --domain LOV2 \
    --position 74 \
    --output my_lov2_nanobody.fasta
```

## Step 4: Run Nucleotide Binder Prediction (Optional)

**Note**: Requires MSA generation (may take time or timeout on public server)

Quick test with dATP:
```bash
cd ~/nucleotide_catchers

boltz predict configs/dATP_binder.yaml \
    --out_dir results/dATP_quick_test \
    --use_msa_server \
    --diffusion_samples 1 \
    --sampling_steps 50 \
    --devices 1
```

Or run all nucleotides in batch:
```bash
cd scripts
./run_all_predictions.sh --quick
```

## Step 5: Examine Results

```bash
# View optogenetic chimeras
cat results/optogenetic_chimeras/optogenetic_nanobody_chimeras.fasta

# View detailed report
cat results/optogenetic_chimeras/chimera_report.txt

# If you ran Boltz predictions, check results
ls -lh results/dATP_quick_test/
```

## Common Tasks

### Insert a different optogenetic domain
```bash
cd scripts

# CRY2 variant
python insert_custom_optogenetic.py \
    --sequence "YOUR_SEQUENCE" \
    --domain CRY2 \
    --position 74

# BphP1 variant
python insert_custom_optogenetic.py \
    --sequence "YOUR_SEQUENCE" \
    --domain BphP1 \
    --position 74
```

### Use different insertion position
```bash
python insert_custom_optogenetic.py \
    --sequence "YOUR_SEQUENCE" \
    --domain LOV2 \
    --position 50  # Insert at position 50 instead
```

### Use custom linker
```bash
python insert_custom_optogenetic.py \
    --sequence "YOUR_SEQUENCE" \
    --domain LOV2 \
    --linker "GGGGS"  # Use different linker
```

## Troubleshooting

### "MSA server timeout"
This is expected if the public MSA server is busy. Options:
1. Wait and retry later
2. Generate MSAs locally (see README)
3. Skip Boltz predictions and focus on optogenetic insertion

### "No module named rdkit"
Reinstall dependencies:
```bash
pip install rdkit biopython
```

### Scripts not executable
```bash
chmod +x ~/nucleotide_catchers/scripts/*.py
chmod +x ~/nucleotide_catchers/scripts/*.sh
```

## Next Steps

1. **Read the full README**: `cat README.md`
2. **Customize configs**: Edit `configs/*.yaml` for your targets
3. **Design workflow**: Combine Boltz predictions with optogenetic domains
4. **Validate designs**: Use your preferred structure validation tools

## Available Optogenetic Domains

| Domain | Size | Light | Response | Best For |
|--------|------|-------|----------|----------|
| LOV2 | 142 aa | Blue (450nm) | Fast, reversible | Rapid control |
| CRY2 | 351 aa | Blue (450nm) | Oligomerization | Signal amplification |
| BphP1 | 672 aa | Red/Far-red (650/750nm) | Conformational | Deep tissue |

## Example Output Sizes

For the standard nanobody (121 aa) with GSGSGSG linkers:
- **LOV2 chimera**: 500 aa
- **CRY2 chimera**: 472 aa
- **BphP1 chimera**: 793 aa

## Questions?

See `README.md` for detailed documentation or check the scripts with `--help`:
```bash
python insert_custom_optogenetic.py --help
./run_all_predictions.sh --help
```
