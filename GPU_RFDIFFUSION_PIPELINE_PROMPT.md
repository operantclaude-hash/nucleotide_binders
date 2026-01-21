# Claude Code Prompt: Optogenetic Nucleotide Catcher Design Pipeline

## COPY EVERYTHING BELOW THIS LINE TO CLAUDE CODE ON YOUR GPU MACHINE

---

# PROMPT START

## Project Overview

I need you to set up and run a complete computational pipeline for designing optogenetically-controlled nucleotide-binding nanobodies ("nucleotide catchers"). This is a novel protein engineering challenge - no nucleotide-specific nanobodies exist, so we need de novo design.

### The Scientific Goal

We're building a system for programmable, light-controlled DNA synthesis:

1. **Optogenetic TdT** (Terminal deoxynucleotidyl Transferase) - activated by 660nm red light
2. **Four nucleotide catchers** - each binds ONE specific dNTP (dATP, dGTP, dCTP, or dTTP) and releases it upon light stimulation
3. **Coincidence detection** - DNA synthesis only occurs when BOTH TdT is active AND the correct nucleotide is released

This enables writing arbitrary DNA sequences by sequential light activation.

### Why This Is Hard

- **No existing nucleotide-binding nanobodies** - We can't just mutate an existing binder
- **Small molecule binding** - dNTPs are ~500 Da, at the lower limit of nanobody binding capability
- **Specificity required** - Each catcher must bind its target nucleotide but NOT the other three
- **Optogenetic compatibility** - Must preserve insertion sites for light-switchable domains

### The Solution: RFdiffusion3 + Constrained Nanobody Scaffold

We will use RFdiffusion3 to design NEW CDR loop conformations around each nucleotide ligand, while keeping the nanobody framework regions fixed. This:
- Creates binding pockets custom-shaped for each dNTP
- Preserves the nanobody fold (validated for optogenetic domain insertion)
- Maintains Loop 6 (~position 74) for photoswitchable domain insertion

---

## Spectral Assignments (Pre-determined)

| Component | Opto Domain | Activation | Deactivation | Chromophore |
|-----------|-------------|------------|--------------|-------------|
| TdT | PhyB | 660nm | 730nm | Phycocyanobilin |
| A-Catcher | LOV2 | 450nm | Dark (~60s) | FMN (endogenous) |
| T-Catcher | CRY2 | 488nm | Dark (~30s) | FAD (endogenous) |
| G-Catcher | BICYCL-Green | 520nm | 580nm | Biliverdin |
| C-Catcher | BphP1 | 750nm | 650nm | Biliverdin |

---

## Complete Pipeline (5 Steps + Validation)

```
Step 1: RFdiffusion3
├── Input: Nanobody scaffold PDB + nucleotide ligand
├── Constraint: Framework regions FIXED, CDR loops FLEXIBLE
├── Output: ~100 backbone designs per nucleotide (400 total)
└── Goal: Generate binding pocket geometries around each dNTP

Step 2: LigandMPNN
├── Input: RFdiffusion3 backbone outputs
├── Process: Design 8 sequences per backbone
├── Output: ~800 sequences per nucleotide (3200 total)
└── Goal: Assign amino acids that will bind the nucleotide

Step 3: Boltz-2 Structure Validation
├── Input: Designed sequences + target nucleotide
├── Process: Predict structure, assess fold quality
├── Metrics: Confidence score, pLDDT, ipTM
├── Filter: Keep confidence >0.80
└── Goal: Verify designed sequences fold correctly

Step 4: Specificity Screening
├── Input: Validated designs
├── Process: Test EACH design against ALL 4 nucleotides
├── Metrics: Confidence and ipTM for each nucleotide
├── Calculate: Specificity ratio = target_score / max(off_target_scores)
├── Filter: Keep specificity ratio >1.5 (ideally >2.0)
└── Goal: Ensure binders are SPECIFIC, not promiscuous

Step 5: Optogenetic Domain Insertion
├── Input: Top specific binders for each nucleotide
├── Process: Insert LOV2/CRY2/BphP1/BICYCL at Loop 6 (position ~74)
├── Linkers: GSGSGSG on both sides
├── Validate: Predict chimera structure with Boltz-2
└── Goal: Create light-switchable nucleotide catchers
```

---

## Validation Metrics & Benchmarks

### Quality Thresholds

| Metric | Minimum | Good | Excellent | What It Means |
|--------|---------|------|-----------|---------------|
| Confidence | >0.70 | >0.80 | >0.90 | Overall structure prediction quality |
| pLDDT | >70 | >80 | >90 | Per-residue confidence |
| ipTM | >0.60 | >0.75 | >0.85 | Interface quality (protein-ligand) |
| Specificity ratio | >1.2 | >1.5 | >2.0 | Target binding vs best off-target |

### Negative Controls (CRITICAL)

To validate that our pipeline isn't just producing false positives:

1. **Random sequence control**: Run Boltz-2 on random nanobody-like sequences + nucleotides
   - Expected: Low confidence, low ipTM
   - If high scores → pipeline is unreliable

2. **Scaffold-only control**: Run original scaffold (no design) against nucleotides
   - Expected: Moderate confidence (fold is good) but low ipTM (no real binding)
   - This is the baseline to beat

3. **Cross-nucleotide control**: Ensure A-binder doesn't bind G, C, T equally well
   - Expected: Target ipTM >> off-target ipTM
   - If similar → design isn't specific

4. **Known binder positive control**: Run Boltz-2 on a known small-molecule nanobody (anti-caffeine)
   - Expected: High confidence, high ipTM
   - Validates the pipeline works for real binders

### Unit Tests to Implement

```python
def test_rfdiffusion_produces_valid_backbones():
    """RFdiffusion output should have correct chain topology"""
    # Check: PDB has correct residue count
    # Check: Framework regions match input scaffold
    # Check: CDR regions are present and variable

def test_ligandmpnn_sequences_are_valid():
    """LigandMPNN should produce valid amino acid sequences"""
    # Check: Only standard amino acids
    # Check: Correct length
    # Check: Framework regions preserved

def test_boltz_scores_are_reasonable():
    """Boltz predictions should be within expected ranges"""
    # Check: Confidence between 0-1
    # Check: Random controls score lower than designs
    # Check: Known binders score high

def test_specificity_calculation():
    """Specificity ratios should be calculated correctly"""
    # Check: Ratio = target / max(off_targets)
    # Check: Specific binders have ratio > 1.5
    # Check: Promiscuous binders are filtered out

def test_optodomain_insertion():
    """Optogenetic domains should be inserted at correct position"""
    # Check: Insertion at Loop 6 (~position 74)
    # Check: Linkers are correct (GSGSGSG)
    # Check: Total sequence length is framework + CDRs + linkers + optodomain
```

---

## Directory Structure to Create

```
~/nucleotide_catchers/
├── README.md
├── requirements.txt
├── configs/
│   ├── rfdiffusion/
│   │   ├── dATP_design.yaml
│   │   ├── dGTP_design.yaml
│   │   ├── dCTP_design.yaml
│   │   └── dTTP_design.yaml
│   └── boltz/
│       └── validation_configs/
├── scaffolds/
│   ├── nanobody_scaffold.pdb          # Reference VHH structure
│   └── ligands/
│       ├── dATP.sdf
│       ├── dGTP.sdf
│       ├── dCTP.sdf
│       └── dTTP.sdf
├── scripts/
│   ├── 01_run_rfdiffusion.py
│   ├── 02_run_ligandmpnn.py
│   ├── 03_run_boltz_validation.py
│   ├── 04_run_specificity_screen.py
│   ├── 05_insert_optodomain.py
│   ├── 06_final_validation.py
│   ├── run_full_pipeline.sh
│   └── utils/
│       ├── metrics.py
│       ├── controls.py
│       └── visualization.py
├── tests/
│   ├── test_pipeline.py
│   ├── test_metrics.py
│   └── test_controls.py
├── outputs/
│   ├── step1_rfdiffusion/
│   ├── step2_ligandmpnn/
│   ├── step3_boltz_validation/
│   ├── step4_specificity/
│   ├── step5_optodomain/
│   ├── step6_final/
│   └── controls/
└── results/
    ├── summary_report.md
    ├── top_candidates.csv
    └── figures/
```

---

## Nucleotide Ligand Information

### SMILES (for Boltz-2)

```
dATP: Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3
dGTP: Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1
dCTP: Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1
dTTP: Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O
```

### Key Distinguishing Features

| Nucleotide | Base Type | Unique Features | Design Considerations |
|------------|-----------|-----------------|----------------------|
| dATP | Purine | 6-amino group, no carbonyl | H-bond donor at position 6 |
| dGTP | Purine | 2-amino, 6-oxo groups | H-bond donor at 2, acceptor at 6 |
| dCTP | Pyrimidine | 4-amino, 2-oxo, single ring | Smaller, different geometry |
| dTTP | Pyrimidine | 5-methyl (unique!), 2,4-dioxo | Methyl group for hydrophobic contact |

---

## Optogenetic Domain Sequences

### AsLOV2 (for A-Catcher, 131 aa)
```
GLTELLNALLPGHQDGAAFRRVTELLSQLVNFTQSRVLGAAIAASDALALGEATGGAAAE
GVVAPTETSPAFMQGVLKGGANATASILDLRDIAGQLVVGNDDGTEIPGPWGRCNPFSSR
LFVELEGVPDHQQPNFRATLA
```

### CRY2 PHR domain (for T-Catcher, 498 aa)
```
MKMDKKTIVWFRRDLRIEDNPALAAAAHEGSVFPVFIWCPEEEGQFYPGRASRWWMKQSL
FHLVKPSQEFWQAGFIHPQGDAPFTGCDLVKILSRCNFSQGLGCRGSSEKLTDSIHTAIA
KEPDKYHRGVSQRFDFKIDTSKRNPLLHIQPGAETVTKIISVLGNTYNRLRVTSDKVSTT
EDLNSGLTLSDLQKALEQGNELPLRCLVGVPSAISTKVSVFVNSPKTFHCAGSTVNGKQF
GSLVAPGCYGNSTWEDHQGLIPFLWGKADEFAVEKAQAEIQQAVKPLGKACPQCVLAWTR
WDADQQVQSVACYRGCVFVPRLRKRVLMTRYLLQAEQFLNNPILQGILTYSPVGNGCSPN
TLLLNLVFMHFLPVHWIQKGQEVVPQGWVQWYNPGKLYYHAGLPGDLIRLNQVGSVMPCS
YLFKLAGLWLTLTEPNVFVLSSTASAARTARFQTLRRMQATRLVDRLTQFLIRFCSSFPV
HQVYFAEQF
```

### BphP1 PSM (for C-Catcher, ~200 aa)
```
MSDTLPLRSIELGSRWGEPLSPAEVRRRLRQVLHELGCRVICGVFYGKEGPFPVGETRYD
GTHFWGKNHPVLAPGAPALYAVSVFEHHHRYRGTLDLRQVGIDVNFPIAPRPHRAGCGQV
IQYAPTLFELLRGELAASVSHQRVGIDVFVPGVNTSAELRALVRQLADLSVGTLTDRLGL
LESFFARQTEVIVRPDDGPVLVSNPVLSPDVLRCFEAVLPGQPLHLDAFSAELFPRQVDP
AGIPAHAGGVQTVLYPGDEVRIIRAGDALRVR
```

---

## Execution Instructions

### Phase 1: Environment Setup

```bash
# Create project directory
mkdir -p ~/nucleotide_catchers
cd ~/nucleotide_catchers

# Create conda environment
conda create -n nuc_design python=3.11 -y
conda activate nuc_design

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Check GPU
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}, VRAM: {torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB')"

# Install Boltz-2
pip install boltz[cuda] -U

# Install other dependencies
pip install biopython pandas numpy pyyaml pytest rdkit
```

### Phase 2: Install RFdiffusion3

```bash
# Clone RFdiffusion
git clone https://github.com/RosettaCommons/RFdiffusion.git
cd RFdiffusion

# Install
pip install -e .

# Download model weights (large, may take time)
# Follow instructions in RFdiffusion README
```

### Phase 3: Install LigandMPNN

```bash
cd ~/nucleotide_catchers
git clone https://github.com/dauparas/LigandMPNN.git
cd LigandMPNN
pip install -e .
```

### Phase 4: Download Scaffold and Prepare Ligands

```bash
# Download a nanobody scaffold structure
cd ~/nucleotide_catchers/scaffolds
curl -O https://files.rcsb.org/download/3G9A.pdb  # Anti-GFP nanobody

# Generate ligand SDF files from SMILES (script will do this)
```

### Phase 5: Run the Pipeline

You can either run the full pipeline:
```bash
bash scripts/run_full_pipeline.sh
```

Or run steps individually for debugging:
```bash
python scripts/01_run_rfdiffusion.py --target dATP --num_designs 100
python scripts/02_run_ligandmpnn.py --input outputs/step1_rfdiffusion/dATP/
python scripts/03_run_boltz_validation.py --input outputs/step2_ligandmpnn/dATP/
python scripts/04_run_specificity_screen.py --input outputs/step3_boltz_validation/dATP/
python scripts/05_insert_optodomain.py --input outputs/step4_specificity/dATP/ --domain LOV2
python scripts/06_final_validation.py --input outputs/step5_optodomain/dATP/
```

---

## Agent Workflow (Optional - For Parallel Execution)

If you want to use multiple agents to parallelize the workflow:

### Agent 1: RFdiffusion Runner
- Runs RFdiffusion3 for all four nucleotides in parallel
- Monitors GPU memory usage
- Reports completion status

### Agent 2: Sequence Designer
- Waits for RFdiffusion backbones
- Runs LigandMPNN on completed backbones
- Can start as soon as first backbone is ready

### Agent 3: Validator
- Runs Boltz-2 validation
- Calculates metrics
- Runs control experiments
- Generates reports

### Agent 4: Specificity Screener
- Tests each design against all 4 nucleotides
- Calculates specificity ratios
- Ranks candidates

To use agents, spawn them with the Task tool targeting specific steps of the pipeline.

---

## Expected Outputs

After running the full pipeline, you should have:

1. **`results/summary_report.md`** - Complete analysis
2. **`results/top_candidates.csv`** - Top 10 binders per nucleotide with scores
3. **`results/figures/`** - Visualizations of binding pockets
4. **`outputs/step6_final/`** - Final chimera PDB structures

### Success Criteria

The pipeline is successful if:
- [ ] At least 5 designs per nucleotide pass validation (confidence >0.80)
- [ ] At least 2 designs per nucleotide have specificity ratio >1.5
- [ ] Control experiments show expected behavior (random < scaffold < design)
- [ ] Final chimera structures are predicted to fold correctly
- [ ] Optogenetic insertion site (Loop 6) is preserved in chimera

---

## Troubleshooting

### GPU Memory Issues
- RFdiffusion3: Reduce batch size or use RFdiffusionAA (smaller model)
- Boltz-2: Use `--low-memory` flag if available
- Run nucleotides sequentially instead of in parallel

### RFdiffusion Not Producing Good Backbones
- Try different contig specifications
- Increase number of diffusion steps
- Adjust potentials/guide_scale

### Low Specificity
- Increase number of designs (more to choose from)
- Try different CDR length ranges
- Focus design on base-specific features (methyl group for T, etc.)

### Boltz-2 Giving Low Scores
- Check MSA quality (use --use_msa_server)
- Verify ligand SMILES is correct
- Compare to positive control (known binder)

---

## Key References

1. **RFdiffusion**: Watson JL et al. (2023) De novo design of protein structure and function with RFdiffusion. *Nature* 620:1089-1100

2. **LigandMPNN**: Dauparas J et al. (2023) Atomic context-conditioned protein sequence design using LigandMPNN. *bioRxiv*

3. **Boltz-2**: Wohlwend J et al. (2024) Boltz-1: Democratizing Biomolecular Interaction Modeling. *bioRxiv*

4. **Optogenetic Nanobodies**: Gil AA et al. (2020) Optogenetic control of protein binding using light-switchable nanobodies. *Nature Communications* 11:4044

5. **Small Molecule Nanobodies**: Ladenson RC et al. (2006) Isolation and characterization of a thermally stable recombinant anti-caffeine heavy-chain antibody fragment. *Analytical Chemistry* 78:4501-4508

---

## Start Here

Begin by:
1. Setting up the environment (Phase 1-3)
2. Running the control experiments first to validate the pipeline
3. Then running the full design pipeline for all four nucleotides
4. Generating the summary report with metrics and figures

Please create all necessary scripts, run the pipeline, and report results with validation metrics. Use agents to parallelize where appropriate.

If any step fails, diagnose the issue, fix it, and document the solution.

---

# PROMPT END

