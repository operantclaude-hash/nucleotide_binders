# Complete Workflow: Nucleotide Binder Design Pipeline

This document describes the complete workflow from design to optogenetic insertion.

## Overview

The pipeline has **TWO INDEPENDENT STAGES**:

1. **Design Stage**: Use Boltz to predict nanobody-nucleotide binding
2. **Engineering Stage**: Insert optogenetic domains into designed nanobodies

These stages are completely separate - optogenetic domains are added AFTER you've identified good nucleotide binders.

---

## Stage 1: Design Nucleotide-Binding Nanobodies

### Step 1A: Generate MSAs (One-time setup)

```bash
cd ~/nucleotide_catchers/scripts

# Generate minimal MSAs (query-only, fast)
python generate_msas.py

# Update configs to include MSA paths
python update_configs_with_msas.py
```

**Output**: MSAs saved in `~/nucleotide_catchers/msas/`

### Step 1B: Run Boltz Predictions

#### Quick Test (verify pipeline works)
```bash
cd ~/nucleotide_catchers
./scripts/run_all_with_msas.sh --test
```
- Takes ~5-10 minutes per nucleotide
- Generates low-quality predictions (for testing only)

#### Production Run (high quality)
```bash
cd ~/nucleotide_catchers
./scripts/run_all_with_msas.sh
```
- Takes several hours per nucleotide
- Generates high-quality predictions
- Uses 5 diffusion samples, 200 sampling steps

#### Single Nucleotide
```bash
cd ~/nucleotide_catchers

boltz predict configs_with_msas/dATP_binder.yaml \
    --out_dir results/dATP_production \
    --devices 1 \
    --diffusion_samples 5 \
    --sampling_steps 200 \
    --recycling_steps 3
```

### Step 1C: Analyze Predictions

**View confidence scores:**
```bash
cat results/dATP_predictions/boltz_results_dATP_binder/predictions/dATP_binder/confidence_*.json
```

**Key metrics:**
- `confidence_score`: Overall quality (higher is better, >0.7 is good)
- `complex_plddt`: Structure confidence
- `ligand_iptm`: Interface quality with ligand

**Visualize structures:**
```bash
# Structure files are in .cif format
ls results/dATP_predictions/boltz_results_dATP_binder/predictions/dATP_binder/*.cif

# Open in PyMOL, ChimeraX, or other molecular viewers
```

### Step 1D: Extract Best Sequences

From the predicted structures:
1. Identify best-performing nanobody (highest confidence, good binding interface)
2. Extract the nanobody sequence from the structure
3. Proceed to Stage 2

---

## Stage 2: Add Optogenetic Control

This stage is **COMPLETELY INDEPENDENT** of Stage 1.

### Step 2A: Generate All Optogenetic Variants

For the default nanobody scaffold:
```bash
cd ~/nucleotide_catchers/scripts
python insert_optogenetic_domains.py
```

**Output:**
- `results/optogenetic_chimeras/optogenetic_nanobody_chimeras.fasta`
- `results/optogenetic_chimeras/chimera_report.txt`

**Generated variants:**
- LOV2 chimera (500 aa) - Blue light responsive
- CRY2 chimera (472 aa) - Blue light, oligomerization
- BphP1 chimera (793 aa) - Red/far-red light

### Step 2B: Insert Into Custom Sequence

For YOUR designed nanobody from Stage 1:

```bash
cd ~/nucleotide_catchers/scripts

python insert_custom_optogenetic.py \
    --sequence "YOUR_NANOBODY_SEQUENCE_FROM_BOLTZ" \
    --domain LOV2 \
    --position 74 \
    --output my_datp_binder_lov2.fasta \
    --name dATP_LOV2_nanobody
```

**Options:**
- `--domain`: LOV2, CRY2, or BphP1
- `--position`: Insertion site (default: 74, in FR3 region)
- `--linker`: Linker sequence (default: GSGSGSG)

### Step 2C: Generate All Combinations

For each nucleotide binder, create all 3 optogenetic variants:

```bash
# dATP binder variants
python insert_custom_optogenetic.py -s "DATP_NANOBODY_SEQ" -d LOV2 -o datp_lov2.fasta
python insert_custom_optogenetic.py -s "DATP_NANOBODY_SEQ" -d CRY2 -o datp_cry2.fasta
python insert_custom_optogenetic.py -s "DATP_NANOBODY_SEQ" -d BphP1 -o datp_bphp1.fasta

# Repeat for dGTP, dCTP, dTTP...
```

---

## Complete Example Workflow

```bash
# ====================
# STAGE 1: DESIGN
# ====================

cd ~/nucleotide_catchers

# 1. Generate MSAs (one-time)
cd scripts
python generate_msas.py
python update_configs_with_msas.py

# 2. Test the pipeline
cd ..
./scripts/run_all_with_msas.sh --test

# 3. Review test results
cat results/dATP_predictions/boltz_results_dATP_binder/predictions/dATP_binder/confidence_*.json

# 4. Run production predictions
./scripts/run_all_with_msas.sh

# 5. Analyze results (takes several hours)
# Open structures in PyMOL/ChimeraX
# Identify best nanobodies for each nucleotide

# ====================
# STAGE 2: ENGINEERING
# ====================

cd ~/nucleotide_catchers/scripts

# 6. Insert optogenetic domains into best candidates
python insert_custom_optogenetic.py \
    --sequence "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS" \
    --domain LOV2 \
    --output ../results/final_designs/dATP_binder_LOV2.fasta

# 7. Generate all variants for all nucleotides
# Repeat for each nucleotide × each optogenetic domain combination

# 8. Final designs ready for synthesis/testing
ls -lh ../results/final_designs/
```

---

## Understanding the Separation

### Why are these stages independent?

**Stage 1 (Boltz Prediction):**
- Input: Nanobody + Nucleotide
- Process: Predict 3D structure of complex
- Output: Nanobody sequences that bind nucleotides
- Purpose: Design the binding function

**Stage 2 (Optogenetic Insertion):**
- Input: Any nanobody sequence (from Stage 1 or elsewhere)
- Process: Insert light-responsive domain at position 74
- Output: Light-controlled nanobody
- Purpose: Add optogenetic control

The **optogenetic domain does NOT participate in nucleotide binding**. It's inserted in a framework region away from the binding site, allowing independent light control of the nanobody's activity/localization.

---

## Output Files

### From Stage 1 (Boltz)
```
results/
├── dATP_predictions/
│   └── boltz_results_dATP_binder/
│       └── predictions/
│           └── dATP_binder/
│               ├── dATP_binder_model_0.cif        # Structure
│               ├── confidence_*.json               # Quality metrics
│               ├── pae_*.npz                       # Error estimates
│               └── plddt_*.npz                     # Confidence scores
├── dGTP_predictions/
├── dCTP_predictions/
└── dTTP_predictions/
```

### From Stage 2 (Optogenetics)
```
results/
├── optogenetic_chimeras/
│   ├── optogenetic_nanobody_chimeras.fasta  # All 3 variants
│   └── chimera_report.txt                    # Detailed info
└── final_designs/
    ├── dATP_binder_LOV2.fasta
    ├── dATP_binder_CRY2.fasta
    ├── dATP_binder_BphP1.fasta
    └── ...
```

---

## Tips & Best Practices

### Stage 1 Tips
1. **Start with --test mode** to verify everything works
2. **Run production mode overnight** (takes several hours)
3. **Compare multiple samples** - diffusion sampling gives different results
4. **Check confidence scores** - aim for >0.7 for reliable structures
5. **Visualize binding interface** - ensure ligand is properly coordinated

### Stage 2 Tips
1. **Position 74 is optimal** - tested for structural tolerance
2. **GSGSGSG linker is flexible** - prevents domain interference
3. **LOV2 is smallest** (142 aa) - best for minimal perturbation
4. **BphP1 uses red light** - better tissue penetration
5. **Test different positions** if needed - try 50-80 range

### General Tips
1. **Keep stages separate** - don't try to predict optogenetic chimeras with Boltz
2. **Document your choices** - track which nanobody + which domain
3. **Test experimentally** - computational predictions need validation
4. **Iterate if needed** - modify based on experimental results

---

## Troubleshooting

### Stage 1 Issues

**"Low confidence scores"**
- Increase sampling steps (200+)
- Use full MSAs (see Advanced MSA section in README)
- Try different random seeds

**"Poor binding interface"**
- Modify nanobody CDR regions
- Adjust input sequence
- Try different starting structures

### Stage 2 Issues

**"Chimera too large"**
- Use LOV2 instead of BphP1
- Try shorter linker (GSGS)

**"Expression problems"**
- Check for codon optimization
- Verify no internal stop codons
- Consider adding tags/signal sequences

---

## Next Steps After This Pipeline

1. **Sequence optimization**: Codon optimization for expression
2. **Plasmid design**: Clone into expression vectors
3. **Protein expression**: Test in E. coli, mammalian cells, etc.
4. **Functional assays**: Verify nucleotide binding
5. **Optogenetic validation**: Confirm light responsiveness
6. **Characterization**: Measure binding affinity, response kinetics
7. **Application**: Use in your biological system

---

## Questions?

- See `README.md` for detailed documentation
- See `QUICKSTART.md` for a 5-minute introduction
- Check script help: `python SCRIPT.py --help`

---

**Pipeline Version**: 1.0.0
**Last Updated**: 2026-01-08
