# Optogenetic Nucleotide Catchers: Project Design Summary

## Project Vision

Design a set of four optogenetically-controlled "nucleotide catchers" that work as a coincidence detector with an optogenetic Terminal deoxynucleotidyl Transferase (TdT) for programmable in-cell DNA synthesis.

### The Concept

Each nucleotide catcher:
1. **Binds** a specific dNTP (dATP, dTTP, dGTP, or dCTP) with high selectivity
2. **Holds** the nucleotide until activated by a specific wavelength of light
3. **Releases** the nucleotide upon optogenetic stimulation
4. **Works in concert** with the optogenetic TdT as a coincidence detector

When both the TdT AND the appropriate nucleotide catcher are activated simultaneously, the released nucleotide is incorporated into the growing DNA strand. This enables programmable, light-controlled DNA synthesis.

---

## Design Decisions

### Decision 1: Nanobody vs Full Antibody

**Question:** Can a nanobody (~15 kDa, single domain) bind a small molecule like a nucleotide (~500 Da), or do we need a full antibody (~150 kDa)?

**Research Findings:**
- Anti-caffeine VHH binds caffeine (194 Da) with Kb = 7.1 × 10⁷ via homodimerization
- Anti-methotrexate VHH binds MTX (454 Da) in a tunnel under CDR1
- dNTPs (467-507 Da) are in the same size range as proven VHH targets

**Decision:** Use **nanobodies (VHH)**
- Smaller, easier to engineer
- Genetically encodable as single chain
- Well-characterized optogenetic insertion sites
- May use homodimerization mechanism (advantageous for light-induced release)

### Decision 2: Optogenetic Domain Selection

**Constraint:** Need spectral separation between TdT and all four catchers to enable independent control.

**Previous Work:** We had already optimized five spectrally-separated optogenetic proteins:

| Component | Domain | Activation | Deactivation | Chromophore |
|-----------|--------|------------|--------------|-------------|
| TdT | PhyB | 660nm (red) | 730nm (far-red) | Phycocyanobilin |
| A-Catcher | LOV2 | 450nm (blue) | Dark (~60s) | FMN (endogenous) |
| T-Catcher | CRY2 | 488nm (cyan) | Dark (~30s) | FAD (endogenous) |
| G-Catcher | BICYCL-Green | 520nm (green) | 580nm | Biliverdin |
| C-Catcher | BphP1 | 750nm (NIR) | 650nm | Biliverdin (endogenous) |

**Key Features:**
- LOV2 and CRY2 auto-reset in the dark (no deactivation light needed)
- BphP1 uses endogenous biliverdin (no exogenous chromophore)
- PhyB requires phycocyanobilin (must be added or synthesized)
- Maximal spectral separation between all five components

### Decision 3: Optogenetic Insertion Strategy

**Question:** Where in the nanobody should we insert the optogenetic domain to achieve light-controlled release?

**Literature Review (OptoNB, Sunbody/Moonbody papers):**

| Insertion Site | Position | Effect | Fold-Change |
|----------------|----------|--------|-------------|
| Loop 1 (GG15) | ~Residue 15 | Dark-binding (light disrupts) | 3.9x |
| Loop 6 (AK74) | ~Residue 74 | Light-binding (dark disrupts) | 7x |
| Dual (N-term + S3) | 0 + internal | Enhanced dynamic range | >80% |

**Decision:** Insert at **Loop 6 (position ~74)**
- Gives "light breaks binding" phenotype (dark = bound, light = released)
- 7-fold change in affinity is sufficient for release
- Well-characterized, generalizable to different nanobodies

**Mechanism:**
- In dark: Optogenetic domain is compact, nanobody maintains binding conformation
- Upon light: Domain undergoes conformational change, propagates allosterically to binding site
- Result: Binding pocket disrupted, nucleotide released

### Decision 4: Linker Design

**Decision:** Use **GSGSGSG** (Gly-Ser) linkers on both sides of the optogenetic domain insertion

**Rationale:**
- Flexible, allows independent domain movement
- Glycine-serine linkers are standard in protein engineering
- Length (7 aa) provides enough flexibility without being too long

**Chimera Architecture:**
```
[VHH N-terminus] - [FR1-CDR1-FR2-CDR2-FR3(partial)] -
[GSGSGSG] - [Optogenetic Domain] - [GSGSGSG] -
[FR3(rest)-CDR3-FR4] - [C-terminus]
```

### Decision 5: Computational Design Strategy

**Challenge:** No natural nanobodies exist that bind free nucleotides with the required specificity.

**Solution:** De novo computational design using modern AI tools

**Pipeline:**
1. **RFdiffusion3/RFdiffusionAA** - Generate protein backbones with binding pockets around nucleotide ligands
2. **LigandMPNN** - Design amino acid sequences for the generated backbones
3. **Boltz-2** - Predict structures and binding affinities
4. **Selectivity screening** - Test each design against all four nucleotides
5. **Optogenetic insertion** - Add LOV2/CRY2/BphP1 domains at Loop 6
6. **Chimera validation** - Predict final structures with AlphaFold/Boltz

### Decision 6: Selectivity Requirements

**Target Specifications:**
- Binding affinity: Kd = 1-100 μM (tight enough to bind, loose enough to release)
- Selectivity: >10-fold preference for target over any off-target nucleotide
- Release: >5-fold reduction in affinity upon light activation

**Selectivity Strategy (Negative Design):**
- Score each designed binder against ALL FOUR nucleotides
- Only keep designs with >10-fold selectivity
- Leverage unique chemical features of each base:

| Nucleotide | Unique Features | Design Considerations |
|------------|-----------------|----------------------|
| dATP | 6-amino, no carbonyl, purine | H-bond donor at position 6 |
| dGTP | 2-amino, 6-oxo, purine | H-bond donor at 2, acceptor at 6 |
| dCTP | 4-amino, 2-oxo, pyrimidine | Smaller ring, different geometry |
| dTTP | 5-methyl, 2,4-dioxo, pyrimidine | Unique methyl group for recognition |

---

## Implementation Pipeline

### Phase 1: Environment Setup (GPU Machine)
```
├── Install Boltz-2 (structure prediction + affinity)
├── Install RFdiffusion3 or RFdiffusionAA (backbone generation)
├── Install LigandMPNN (sequence design)
├── Download reference PDB structures (2V0U, 3G9A, 3T04, 6IR1)
└── Create config files for each nucleotide
```

### Phase 2: De Novo Binder Design
```
For each nucleotide (dATP, dGTP, dCTP, dTTP):
├── Generate 100 backbone designs with RFdiffusion
├── Design 8 sequences per backbone with LigandMPNN
├── Validate structures with Boltz-2
├── Score affinity against target nucleotide
├── Score affinity against 3 off-target nucleotides
├── Filter for >10-fold selectivity
└── Rank by predicted affinity and selectivity
```

### Phase 3: Optogenetic Integration
```
For each top binder design:
├── Insert appropriate optogenetic domain at Loop 6
│   ├── A-binder → LOV2
│   ├── T-binder → CRY2
│   ├── G-binder → BICYCL-Green
│   └── C-binder → BphP1
├── Add GSGSGSG linkers
├── Predict chimera structure with Boltz-2/AlphaFold
├── Verify binding pocket is maintained
└── Model light-state conformation (if possible)
```

### Phase 4: Experimental Validation (Future)
```
├── Synthesize top 10-20 designs per nucleotide
├── Express and purify
├── Measure binding affinity (ITC, SPR, or MST)
├── Test nucleotide selectivity
├── Verify light-dependent release
├── Optimize kinetics if needed
└── Test in cellular context with optogenetic TdT
```

---

## Key Reference Structures

| PDB ID | Description | Use |
|--------|-------------|-----|
| 2V0U | AsLOV2 crystal structure | Optogenetic domain template |
| 3G9A | Anti-GFP minimizer nanobody | General VHH scaffold |
| 3T04 | Anti-SH2Abl monobody | Moonbody reference |
| 6IR1 | LaM4-mCherry complex | Nanobody-target interaction |

---

## Nucleotide Ligand Specifications

### SMILES Representations (for Boltz input)

```
dATP: Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3
dGTP: Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1
dCTP: Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1
dTTP: Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O
```

### Molecular Properties

| Nucleotide | MW (Da) | Base Type | Ring System |
|------------|---------|-----------|-------------|
| dATP | 491.18 | Purine | Bicyclic (fused) |
| dGTP | 507.18 | Purine | Bicyclic (fused) |
| dCTP | 467.16 | Pyrimidine | Single ring |
| dTTP | 482.17 | Pyrimidine | Single ring |

---

## Files Generated

```
nucleotide_catchers/
├── PROJECT_DESIGN_SUMMARY.md      # This document
├── RESEARCH_SUMMARY.md            # Detailed literature review
├── GPU_MACHINE_SETUP_PROMPT.md    # Full Claude Code prompt for GPU
├── QUICK_START_PROMPT.txt         # Compact setup prompt
├── configs/
│   ├── dATP_binder.yaml          # Boltz config for dATP
│   ├── dGTP_binder.yaml          # Boltz config for dGTP
│   ├── dCTP_binder.yaml          # Boltz config for dCTP
│   └── dTTP_binder.yaml          # Boltz config for dTTP
├── scripts/
│   ├── bootstrap_gpu_machine.sh   # Initial GPU setup
│   ├── setup_boltz.sh            # Boltz installation
│   ├── design_nucleotide_binders.py  # RFdiffusion pipeline
│   ├── insert_optodomain.py      # Chimera sequence generator
│   └── run_colabfold.py          # ColabFold preparation
├── structures/                    # PDB files (to be downloaded)
└── outputs/                       # Design outputs (to be generated)
```

---

## Key Literature

1. **Gil AA et al. (2020)** - Optogenetic control of protein binding using light-switchable nanobodies. *Nature Communications* 11:4044
   - Established OptoNB methodology
   - Identified Loop 1 and Loop 6 as optimal insertion sites

2. **He L et al. (2021)** - Design of Smart Antibody Mimetics with Photosensitive Switches. *Advanced Biology* 5:2000541
   - Sunbody/Moonbody design
   - Dual LOV2 insertion for enhanced dynamic range

3. **Watson JL et al. (2023)** - De novo design of protein structure and function with RFdiffusion. *Nature* 620:1089-1100
   - Foundation for computational binder design

4. **Krishna R et al. (2024)** - Generalized biomolecular modeling and design with RoseTTAFold All-Atom. *Science* 384:eadl2528
   - RFdiffusionAA for small molecule binder design

5. **Wohlwend J et al. (2024)** - Boltz-1: Democratizing Biomolecular Interaction Modeling. *bioRxiv*
   - Open-source structure prediction with affinity estimation

---

## Next Steps

1. **Run GPU pipeline** - Execute the Boltz-based design workflow
2. **Generate initial binders** - Create 100+ designs per nucleotide
3. **Screen for selectivity** - Filter for >10-fold specificity
4. **Insert optogenetic domains** - Create chimera sequences
5. **Validate structures** - Predict chimera folds
6. **Select candidates** - Choose top 10-20 for synthesis
7. **Experimental validation** - Test binding and light-release

---

*Document generated: January 2025*
*Project: Optogenetic Nucleotide Catchers for Programmable DNA Synthesis*
