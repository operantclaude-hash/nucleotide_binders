# Nucleotide Binder Design Pipeline

A comprehensive pipeline for designing nanobodies that bind specific nucleotides (dATP, dGTP, dCTP, dTTP) using Boltz-2 structure prediction, with optogenetic domain insertion capabilities.

## Features

- **Nucleotide-specific binder design**: Pre-configured for all four dNTPs
- **Boltz-2 integration**: State-of-the-art protein structure prediction
- **Optogenetic control**: Insert LOV2, CRY2, or BphP1 domains for light-responsive control
- **Flexible linker design**: GSGSGSG linkers for domain mobility

## Directory Structure

```
nucleotide_catchers/
├── pdbs/                    # Reference PDB structures
│   ├── 2V0U.pdb            # DNA polymerase + dATP
│   ├── 3G9A.pdb            # DNA polymerase + dGTP
│   ├── 3T04.pdb            # DNA polymerase + dCTP
│   └── 6IR1.pdb            # DNA polymerase + dTTP
├── configs/                 # Boltz-2 configuration files
│   ├── dATP_binder.yaml
│   ├── dGTP_binder.yaml
│   ├── dCTP_binder.yaml
│   └── dTTP_binder.yaml
├── scripts/                 # Python scripts
│   ├── insert_optogenetic_domains.py
│   └── insert_custom_optogenetic.py
└── results/                 # Output directory
    └── optogenetic_chimeras/

```

## Installation

### Prerequisites
- Python 3.8+
- CUDA-compatible GPU (recommended)
- 24GB GPU memory (Quadro RTX 6000 or similar)

### Setup

Boltz-2 is already installed and configured. Dependencies include:
- torch >= 2.2
- rdkit
- biopython
- pytorch-lightning
- gemmi
- fairscale

## Usage

### 1. Nucleotide Binder Design with Boltz-2

Each nucleotide has a pre-configured YAML file specifying:
- **Nanobody scaffold**: Standard VHH framework
- **Target ligand**: Nucleotide with SMILES representation

#### Running Predictions

**Basic prediction** (requires MSA generation):
```bash
cd ~/nucleotide_catchers

# Generate MSAs locally or use MSA server
boltz predict configs/dATP_binder.yaml \
    --out_dir results/dATP \
    --use_msa_server \
    --devices 1 \
    --accelerator gpu
```

**Quick test** (fewer sampling steps):
```bash
boltz predict configs/dATP_binder.yaml \
    --out_dir results/dATP_test \
    --use_msa_server \
    --diffusion_samples 1 \
    --sampling_steps 50
```

**Production run** (high quality):
```bash
boltz predict configs/dATP_binder.yaml \
    --out_dir results/dATP_production \
    --use_msa_server \
    --diffusion_samples 5 \
    --sampling_steps 200 \
    --recycling_steps 3
```

#### Nucleotide SMILES Strings

The configs use these SMILES representations:

- **dATP**: `Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3`
- **dGTP**: `Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1`
- **dCTP**: `Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1`
- **dTTP**: `Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O`

### 2. Optogenetic Domain Insertion

#### Generate All Chimeras

Generate all three optogenetic variants for the default nanobody:

```bash
cd ~/nucleotide_catchers/scripts
python insert_optogenetic_domains.py
```

Output:
- `results/optogenetic_chimeras/optogenetic_nanobody_chimeras.fasta`
- `results/optogenetic_chimeras/chimera_report.txt`

#### Insert into Custom Sequence

```bash
python insert_custom_optogenetic.py \
    --sequence "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS" \
    --domain LOV2 \
    --position 74 \
    --output my_lov2_chimera.fasta \
    --name my_nanobody
```

**Options**:
- `--sequence, -s`: Your nanobody sequence (required)
- `--domain, -d`: LOV2, CRY2, or BphP1 (required)
- `--position, -p`: Insertion position (default: 74)
- `--linker, -l`: Linker sequence (default: GSGSGSG)
- `--output, -o`: Output FASTA file
- `--name, -n`: Construct name

## Optogenetic Domains

### LOV2 (Light-Oxygen-Voltage)
- **Length**: 142 aa
- **Activation**: Blue light (450-480 nm)
- **Response**: Conformational change, Jα helix unfolding
- **Application**: Rapid, reversible control

### CRY2 (Cryptochrome 2)
- **Length**: 351 aa
- **Activation**: Blue light (450-480 nm)
- **Response**: Oligomerization
- **Application**: Clustering, signal amplification

### BphP1 (Bacteriophytochrome)
- **Length**: 672 aa
- **Activation**: Red/far-red light (650/750 nm)
- **Response**: Conformational change
- **Application**: Deep tissue penetration, orthogonal control

## Design Parameters

### Insertion Position
- **Position 74**: Located in framework region 3 (FR3)
- Chosen for structural tolerance and surface accessibility
- Between CDR2 and CDR3 loops

### Linker Design
- **GSGSGSG** (7 residues)
- Flexible, non-structured
- Maintains domain independence
- Prevents steric clashes

### Chimera Architecture
```
N-term (1-74) → GSGSGSG → Optogenetic Domain → GSGSGSG → C-term (75-121)
```

## Example Workflow

Complete workflow for dATP binder with LOV2 control:

```bash
# 1. Design nanobody that binds dATP
cd ~/nucleotide_catchers
boltz predict configs/dATP_binder.yaml \
    --out_dir results/dATP_binder \
    --use_msa_server

# 2. Extract best nanobody sequence from results
# (manually inspect predictions in results/dATP_binder/)

# 3. Insert LOV2 domain
cd scripts
python insert_custom_optogenetic.py \
    --sequence "YOUR_DESIGNED_NANOBODY_SEQUENCE" \
    --domain LOV2 \
    --position 74 \
    --output ../results/dATP_LOV2_final.fasta

# 4. Validate structure with Boltz
# Create new config with chimeric sequence and run prediction
```

## Troubleshooting

### MSA Server Timeout
If the MSA server times out:
1. Generate MSAs locally using MMseqs2 or HHblits
2. Add MSA paths to your YAML config
3. Run without `--use_msa_server` flag

### GPU Memory Issues
Reduce memory usage:
```bash
--diffusion_samples 1 \
--max_parallel_samples 1
```

### Dependency Conflicts
Boltz has strict version requirements. If you encounter issues:
```bash
pip install --no-deps boltz
# Then manually install compatible versions
```

## Reference Structures

The PDB structures provide templates for nucleotide binding:

- **2V0U**: DNA polymerase β with dATP
- **3G9A**: DNA polymerase η with dGTP
- **3T04**: DNA polymerase λ with dCTP
- **6IR1**: DNA polymerase κ with dTTP

## Output Files

### Boltz Predictions
- `*.cif`: mmCIF structure files
- `*_pae.npz`: Predicted Aligned Error matrices
- `*_pde.npz`: Predicted Distance Error (if enabled)

### Optogenetic Chimeras
- `*.fasta`: Chimeric sequences
- `chimera_report.txt`: Detailed construct information

## Citation

If you use this pipeline, please cite:

**Boltz-2**:
- Wohlwend et al. (2024). "Boltz-2: Ultra-fast protein structure prediction"

**Optogenetic Domains**:
- LOV2: Harper et al. (2003), Christie et al. (2012)
- CRY2: Kennedy et al. (2010), Liu et al. (2008)
- BphP1: Takala et al. (2014), Bellini et al. (2014)

## License

This pipeline is for research use only.

## Contact

For issues or questions, please open an issue on GitHub.

---

**Last Updated**: 2026-01-08
**Pipeline Version**: 1.0.0
