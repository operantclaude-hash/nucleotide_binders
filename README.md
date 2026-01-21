# Optogenetic Nucleotide Binders

De novo design of optogenetically-controlled nanobodies for nucleotide-specific binding and light-triggered release.

## Project Goal

Design four "nucleotide catchers" - nanobodies that:
1. **Bind** a specific dNTP (dATP, dGTP, dCTP, or dTTP) with high selectivity
2. **Release** the nucleotide upon light stimulation
3. **Work** with an optogenetic TdT as a coincidence detector for programmable DNA synthesis

## The Challenge

No nucleotide-specific nanobodies exist. This requires **de novo computational design** using RFdiffusion3 to create binding pockets custom-shaped for each nucleotide.

## Spectral Assignments

| Component | Opto Domain | Activation | Deactivation |
|-----------|-------------|------------|--------------|
| TdT | PhyB | 660nm | 730nm |
| A-Catcher | LOV2 | 450nm | Dark (~60s) |
| T-Catcher | CRY2 | 488nm | Dark (~30s) |
| G-Catcher | BICYCL-Green | 520nm | 580nm |
| C-Catcher | BphP1 | 750nm | 650nm |

## Pipeline

```
1. RFdiffusion3    →  Design CDR loops around nucleotide (framework fixed)
2. LigandMPNN      →  Design amino acid sequences
3. Boltz-2         →  Validate structure predictions
4. Specificity     →  Screen against all 4 nucleotides
5. Optogenetics    →  Insert LOV2/CRY2/BphP1 at Loop 6
6. Validation      →  Predict final chimera structures
```

## Repository Structure

```
nucleotide_binders/
├── README.md
├── configs/                    # Boltz-2 and RFdiffusion configs
├── scripts/                    # Pipeline scripts
├── scaffolds/                  # Nanobody scaffold PDBs
├── outputs/                    # Design outputs
└── results/                    # Final candidates and reports
```

## Quick Start

See [GPU_RFDIFFUSION_PIPELINE_PROMPT.md](GPU_RFDIFFUSION_PIPELINE_PROMPT.md) for the complete pipeline instructions.

## Key Documents

- [PROJECT_DESIGN_SUMMARY.md](PROJECT_DESIGN_SUMMARY.md) - Full design rationale
- [RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md) - Literature review
- [GPU_RFDIFFUSION_PIPELINE_PROMPT.md](GPU_RFDIFFUSION_PIPELINE_PROMPT.md) - GPU machine setup

## References

1. Watson JL et al. (2023) De novo design of protein structure and function with RFdiffusion. *Nature*
2. Gil AA et al. (2020) Optogenetic control of protein binding using light-switchable nanobodies. *Nature Communications*
3. Wohlwend J et al. (2024) Boltz-1: Democratizing Biomolecular Interaction Modeling. *bioRxiv*

## License

MIT
