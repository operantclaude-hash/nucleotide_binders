# Claude Code Prompt for GPU Machine Setup

Copy and paste the entire prompt below into Claude Code on your GPU machine.

---

## PROMPT START

I need you to set up and run a nucleotide binder design pipeline on this GPU machine. This is for designing optogenetically-controlled nanobodies that bind specific nucleotides (dATP, dGTP, dCTP, dTTP) and release them upon light stimulation.

### Project Overview

We're designing "nucleotide catchers" - nanobodies with optogenetic domains inserted that:
1. Bind a specific nucleotide (A, T, G, or C) but NOT the others
2. Release the nucleotide when stimulated with a specific wavelength of light
3. Work as part of a coincidence detector with an optogenetic TdT

### Spectral Assignments (from prior work)

| Catcher | Opto Domain | Activation | Deactivation |
|---------|-------------|------------|--------------|
| TdT | PhyB | 660nm | 730nm |
| A-Catcher | LOV2 | 450nm | Dark (~60s) |
| T-Catcher | CRY2 | 488nm | Dark (~30s) |
| G-Catcher | BICYCL-Green | 520nm | 580nm |
| C-Catcher | BphP1 | 750nm | 650nm |

### Tasks to Complete

#### 1. Environment Setup

Create a new conda environment and install all required tools:

```bash
# Create project directory
mkdir -p ~/nucleotide_catchers/{structures,configs,scripts,outputs/{rfdiffusion,ligandmpnn,boltz,alphafold,figures}}
cd ~/nucleotide_catchers

# Create conda environment
conda create -n nucleotide_design python=3.11 -y
conda activate nucleotide_design
```

Install the following tools (check GPU compatibility):
- **Boltz-2**: `pip install boltz[cuda] -U`
- **RFdiffusion3** (if available) or **RFdiffusionAA**: Clone from https://github.com/RosettaCommons/RFdiffusion
- **LigandMPNN**: Clone from https://github.com/dauparas/LigandMPNN
- **ColabFold** (local): `pip install colabfold[alphafold]`

Verify GPU is accessible:
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

#### 2. Download Required PDB Structures

Download these structures for reference and figure generation:
- **2V0U** - AsLOV2 crystal structure (the optogenetic switch)
- **3G9A** - Anti-GFP nanobody (general VHH scaffold)
- **3T04** - Anti-SH2Abl monobody (moonbody reference)
- **6IR1** - LaM4 nanobody-mCherry complex

Save to `structures/` directory.

#### 3. Create Boltz Configuration Files

Create YAML configs for each nucleotide in `configs/`:

**dATP_binder.yaml:**
```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGLDVWGQGTLVTVSS
  - ligand:
      id: B
      smiles: 'Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3'
```

Create similar files for dGTP, dCTP, dTTP with these SMILES:
- **dGTP**: `Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1`
- **dCTP**: `Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1`
- **dTTP**: `Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O`

#### 4. Create Design Pipeline Scripts

Create a Python script `scripts/design_pipeline.py` that:

1. **Generates backbones with RFdiffusion** (if installed) around each nucleotide ligand
   - Target protein length: ~120 residues (nanobody-sized)
   - Generate 100 designs per nucleotide
   - Use pocket constraints to ensure ligand binding

2. **Designs sequences with LigandMPNN**
   - 8 sequences per backbone
   - Use ligand context for sequence optimization

3. **Validates with Boltz-2**
   - Predict structure of each designed sequence
   - Predict binding affinity

4. **Screens for selectivity**
   - Test each design against ALL FOUR nucleotides
   - Filter for >10-fold selectivity for target over off-targets

5. **Inserts optogenetic domains**
   - Insert LOV2/CRY2/BphP1/BICYCL at Loop 6 (position ~74)
   - Use GSGSGSG linkers
   - Generate final chimera sequences

#### 5. Optogenetic Domain Sequences

Use these sequences for domain insertion:

**AsLOV2 (short, residues 408-543):**
```
GLTELLNALLPGHQDGAAFRRVTELLSQLVNFTQSRVLGAAIAASDALALGEATGGAAAE
GVVAPTETSPAFMQGVLKGGANATASILDLRDIAGQLVVGNDDGTEIPGPWGRCNPFSSR
LFVELEGVPDHQQPNFRATLA
```

**CRY2 PHR domain (residues 1-498):**
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

**BphP1 photosensory module:**
```
MSDTLPLRSIELGSRWGEPLSPAEVRRRLRQVLHELGCRVICGVFYGKEGPFPVGETRYD
GTHFWGKNHPVLAPGAPALYAVSVFEHHHRYRGTLDLRQVGIDVNFPIAPRPHRAGCGQV
IQYAPTLFELLRGELAASVSHQRVGIDVFVPGVNTSAELRALVRQLADLSVGTLTDRLGL
LESFFARQTEVIVRPDDGPVLVSNPVLSPDVLRCFEAVLPGQPLHLDAFSAELFPRQVDP
AGIPAHAGGVQTVLYPGDEVRIIRAGDALRVR
```

#### 6. Run the Pipeline

Execute in this order:

```bash
# Step 1: Test Boltz installation
boltz predict configs/dATP_binder.yaml --use_msa_server --out_dir outputs/boltz/test

# Step 2: If RFdiffusion is installed, generate backbones
# python scripts/run_rfdiffusion.py --target dATP --num_designs 100

# Step 3: Design sequences
# python scripts/run_ligandmpnn.py --input outputs/rfdiffusion/

# Step 4: Validate and screen
# python scripts/validate_designs.py --input outputs/ligandmpnn/

# Step 5: Generate chimeras with optogenetic domains
# python scripts/insert_optodomain.py --input outputs/validated/

# Step 6: Predict chimera structures
# boltz predict outputs/chimeras/ --use_msa_server
```

#### 7. Alternative: Use Online Tools

If RFdiffusion is not installed locally:

1. **Tamarind.bio** for RFdiffusion3: https://www.tamarind.bio/tools/rfdiffusion3
   - Upload nucleotide SMILES
   - Generate ~20-50 designs per nucleotide
   - Download PDB backbones

2. **ColabFold** for structure prediction:
   - https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb

#### 8. Output Organization

Organize outputs as:
```
outputs/
├── rfdiffusion/
│   ├── dATP/
│   ├── dGTP/
│   ├── dCTP/
│   └── dTTP/
├── ligandmpnn/
├── boltz/
│   ├── validation/
│   └── selectivity/
├── chimeras/
│   ├── A_catcher_LOV2/
│   ├── T_catcher_CRY2/
│   ├── G_catcher_BICYCL/
│   └── C_catcher_BphP1/
└── figures/
```

#### 9. Generate Figures

Create PyMOL scripts to visualize:
1. Reference optogenetic nanobody structure (LOV2 inserted in VHH)
2. Designed nucleotide binding pockets
3. Chimera structures with optogenetic domains
4. Comparison of all four catchers

### Key Constraints

- Each catcher must bind its target nucleotide with Kd in 1-100 μM range
- Selectivity must be >10-fold over off-target nucleotides
- Optogenetic domain insertion should not disrupt the binding pocket in dark state
- Light activation should cause >5-fold reduction in binding affinity

### Success Criteria

1. ✅ Environment set up with all tools working
2. ✅ PDB structures downloaded
3. ✅ Boltz configs created and tested
4. ✅ Design pipeline scripts created
5. ✅ Initial designs generated (at least 10 per nucleotide)
6. ✅ Selectivity screening completed
7. ✅ Chimera sequences with optogenetic domains generated
8. ✅ Structure predictions for chimeras completed
9. ✅ Figures generated

Please set this up step by step, verifying each component works before moving to the next. Start by checking GPU availability and installing Boltz-2, then proceed from there.

---

## PROMPT END

---

## Notes for Running

1. **Copy everything between "PROMPT START" and "PROMPT END"**
2. **Paste into Claude Code on your GPU machine**
3. **Claude will execute each step and verify**
4. **If any tool fails to install, Claude will find alternatives**

## Expected Timeline

- Environment setup: ~30 min (depending on downloads)
- Boltz installation and test: ~10 min
- RFdiffusion/LigandMPNN setup: ~1-2 hours (large model downloads)
- Running design pipeline: ~4-8 hours (depending on GPU and num_designs)
- Structure predictions: ~1-2 hours

## GPU Requirements

- Minimum: 16GB VRAM (RTX 3090, A5000, etc.)
- Recommended: 24GB+ VRAM (A6000, RTX 4090, A100)
- For RFdiffusion3: 40GB+ recommended

## Fallback Options

If GPU memory is limited:
1. Use Tamarind.bio for RFdiffusion (free tier available)
2. Use Google Colab for ColabFold
3. Run Boltz with `--cpu` flag (slower but works)
