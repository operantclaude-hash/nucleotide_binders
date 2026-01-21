# Optogenetic Nucleotide Catchers: Research Summary & Implementation Plan

## Executive Summary

This document summarizes the literature research and provides an implementation roadmap for developing optogenetically-controlled nucleotide binders (A-Catcher, T-Catcher, G-Catcher, C-Catcher) that:
1. Bind specific dNTPs (dATP, dTTP, dGTP, dCTP) with high selectivity
2. Release nucleotides upon optogenetic stimulation
3. Function as a coincidence detector with the optogenetic TdT

---

## Part A: Optogenetic Nanobody Literature Deep Dive

### Key Publications

1. **OptoNanobodies (Gil et al., 2020)** - [Nature Communications](https://www.nature.com/articles/s41467-020-17836-8)
   - First systematic study of AsLOV2 insertion into nanobodies
   - Tested 8 surface-exposed loops
   - **Best sites**: Loop 1 (GG15) and Loop 6 (AK74)

2. **Sunbody/Moonbody (He et al., 2021)** - [PMC8295464](https://pmc.ncbi.nlm.nih.gov/articles/PMC8295464/)
   - "Sunbody" = light turns binding ON
   - "Moonbody" = light turns binding OFF
   - Dual LOV2 insertion (N-terminus + internal loop) enhances dynamic range

### Optimal Insertion Sites for LOV2 in Nanobodies

| Site | Location | Effect | Fold-Change | Notes |
|------|----------|--------|-------------|-------|
| GG15 | Loop 1 | Dark-binding | 3.9x | Distal from CDRs |
| AK74 | Loop 6 | Light-binding | 7x | Proximal to binding surface |
| DG62-66 | Loop 5 | Variable | >100% | Tested for anti-actin |
| S0 + S3 | N-term + internal | Enhanced | >80% | Dual insertion, synergistic |

### Mechanism of Action

The AsLOV2 domain (residues 408-543 of *Avena sativa* Phototropin 1) works via:
- **Dark state**: Jα helix packed against LOV core
- **Light state (450nm)**: Jα helix undocks, becomes disordered
- **Allosteric transmission**: Conformational change propagates through nanobody backbone
- **Key insight**: Changes primarily affect k_off (dissociation rate), not k_on

### PDB Structures to Use

| PDB ID | Description | Use Case |
|--------|-------------|----------|
| 2V0U | AsLOV2 crystal structure | LOV domain template |
| 3G9A | Anti-GFP minimizer nanobody | General nanobody scaffold |
| 6IR1 | LaM4-mCherry complex | Nanobody-target interaction |
| 3T04 | Anti-SH2Abl monobody | Moonbody template |

---

## Part B: Nanobody vs Antibody for Single Nucleotide Binding

### The Challenge

Single nucleotides (dNTPs) are **small molecules** (~330-500 Da):
- dATP: 491 Da
- dGTP: 507 Da
- dCTP: 467 Da
- dTTP: 482 Da

This is similar in size to caffeine (194 Da), methotrexate (454 Da), and other haptens.

### Key Findings

**Nanobodies CAN bind small molecules** - Evidence:
1. **Anti-caffeine VHH**: Binds caffeine (194 Da) with Kb = 7.1 × 10^7 via homodimerization
2. **Anti-methotrexate VHH**: Binds MTX (454 Da) in a tunnel under CDR1
3. **Anti-triclocarban VHH**: Near-nanomolar affinity for TCC in CDR1 tunnel

**Critical insight**: Small molecule binding often requires:
- **Tunnel/cavity binding mode** (not surface binding)
- **CDR1 involvement** (unlike protein targets that use CDR3)
- **Potential homodimerization** (as seen with caffeine VHH)

### Recommendation: Nanobody is FEASIBLE

| Factor | Nanobody | Full Antibody | Winner |
|--------|----------|---------------|--------|
| Size | 15 kDa | 150 kDa | Nanobody |
| Genetic encoding | Simple | Complex (2 chains) | Nanobody |
| Opto-switch insertion | Well-characterized | Unknown | Nanobody |
| Small molecule binding | Proven (caffeine, MTX) | Proven | Tie |
| Affinity for small molecules | μM-nM range | nM range | Antibody (slight) |
| Homodimerization | May be required | Not needed | Antibody |

**Verdict**: Start with nanobody design. The dNTPs are in the right size range for VHH binding (similar to methotrexate at 454 Da). The key will be achieving **base specificity** (A vs G vs C vs T) while maintaining enough affinity to bind but not so much that release is impossible.

### Target Affinity Range

For optogenetic release to work, we need:
- **Binding Kd**: 1-100 μM range (too tight = won't release)
- **Optogenetic fold-change**: >5-10x to achieve meaningful release
- **Base specificity**: >100-fold selectivity for target nucleotide

---

## Part C: Computational Binder Design Pipeline

### Recommended Tool Stack

1. **RFdiffusion3 / RFdiffusionAA** - De novo backbone generation around ligands
2. **LigandMPNN** - Sequence design for ligand-binding proteins
3. **Boltz-2** - Structure prediction and affinity estimation
4. **AlphaFold2** - Validation of designed sequences

### Option 1: Boltz-2 for Structure Prediction

**Installation:**
```bash
pip install boltz[cuda] -U
```

**Example YAML for dATP binder prediction:**
```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: [YOUR_DESIGNED_SEQUENCE]
  - ligand:
      id: B
      smiles: 'Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3'

# Or use CCD codes if available
```

**Run prediction:**
```bash
boltz predict dATP_binder.yaml --use_msa_server
```

### Option 2: RFdiffusion3 for De Novo Design (Preferred)

This is more powerful for generating novel binders:

1. **Prepare ligand structure** (dATP, dGTP, dCTP, dTTP)
2. **Run RFdiffusion3** to generate backbones around ligand
3. **Run LigandMPNN** to assign sequences
4. **Validate with Boltz-2 or AlphaFold2**
5. **Filter by predicted affinity and selectivity**

### SMILES for dNTPs

| Nucleotide | SMILES |
|------------|--------|
| dATP | `Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3` |
| dGTP | `Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1` |
| dCTP | `Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1` |
| dTTP | `Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O` |

### Negative Design Strategy

To achieve selectivity (bind A but NOT C, G, T), use **negative design**:

1. Generate designs for dATP
2. Score each design against ALL four nucleotides
3. Keep only designs with >10-100x selectivity
4. This requires running Boltz-2 affinity predictions for each design against all 4 nucleotides

---

## Part D: Optogenetic Switch Integration Strategy

### Your Spectral Assignments (from previous work)

| Component | Domain | Activation | Deactivation | Chromophore |
|-----------|--------|------------|--------------|-------------|
| TdT | PhyB | 660nm | 730nm | Phycocyanobilin (PCB) |
| A-Catcher | LOV2 | 450nm | Dark (~60s) | FMN (endogenous) |
| T-Catcher | CRY2 | 488nm | Dark (~30s) | FAD (endogenous) |
| G-Catcher | BICYCL-Green | 520nm | 580nm | Biliverdin (BV) |
| C-Catcher | BphP1 | 750nm | 650nm | Biliverdin (BV) |

### Domain Properties

| Domain | Size | Mechanism | Pros | Cons |
|--------|------|-----------|------|------|
| AsLOV2 | ~130 aa | Jα helix undocking | Small, well-characterized, endogenous chromophore | Blue light only |
| CRY2-CIBN | ~500 aa | Heterodimerization | Fast kinetics, tunable | Large, needs partner |
| CRY2 homo | ~500 aa | Homo-oligomerization | Auto-resets | Large |
| BphP1-QPAS1 | ~500+170 aa | Heterodimerization | NIR, endogenous BV | Two-component |
| PhyB-PIF | ~600 aa | Heterodimerization | Red/far-red, reversible | Needs PCB (exogenous) |

### Insertion Strategy for "Breaking" the Nanobody

**Goal**: Insert optogenetic domain such that light activation DISRUPTS binding

**Approach 1: Allosteric Disruption (Recommended)**
- Insert LOV2/other domain into Loop 1 or Loop 6 of nanobody
- Light-induced conformational change propagates to binding site
- This is the OptoNB approach - well characterized

**Approach 2: Steric Occlusion**
- Insert domain near CDR1 (where small molecules often bind)
- Light-induced domain expansion physically blocks binding pocket
- Riskier but potentially more dramatic effect

**Approach 3: Domain Splitting**
- Split nanobody into two fragments that only associate when optogenetic domains are in dark state
- Light causes domain dissociation → loss of binding
- Most complex but cleanest release mechanism

### Chimera Design Template

For A-Catcher (LOV2-based):
```
[Signal peptide (optional)] - [VHH N-terminus] - [FR1] - [CDR1] - [FR2] - [CDR2] -
[FR3-part1] - [Gly-Ser linker] - [AsLOV2(408-543)] - [Gly-Ser linker] -
[FR3-part2] - [CDR3] - [FR4] - [C-terminus tag]
```

Insertion at Loop 6 (around residue 74 in standard numbering):
- Original: ...A74K75...
- Modified: ...A74-GSGSGS-[AsLOV2]-GSGSGS-K75...

---

## Part E: AlphaFold/ColabFold Modeling Plan

### Option 1: ColabFold (Easiest)

Use the [ColabFold notebook](https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb):

1. Paste chimera sequence
2. Run prediction
3. Download PDB

**Limitations**:
- Cannot include ligands in standard AF2
- Need to dock dNTPs separately

### Option 2: Local AlphaFold3 / Boltz-2

For protein-ligand complexes:
```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: [CHIMERA_SEQUENCE]  # VHH + LOV2 fusion
  - ligand:
      id: B
      smiles: [dATP_SMILES]
```

### Modeling Workflow

1. **Design nanobody sequence** (RFdiffusion3 + LigandMPNN)
2. **Validate fold** (AlphaFold2 for protein only)
3. **Predict complex** (Boltz-2 for protein + dNTP)
4. **Insert optogenetic domain** (manual sequence insertion)
5. **Predict chimera fold** (AlphaFold2 or Boltz-2)
6. **Visualize** (PyMOL/ChimeraX)

---

## Implementation Roadmap

### Phase 1: Computational Design (Weeks 1-2)
- [ ] Install RFdiffusion3 or use Tamarind.bio online
- [ ] Generate dNTP binding pocket designs
- [ ] Run LigandMPNN for sequence design
- [ ] Score designs with Boltz-2

### Phase 2: Selectivity Screening (Week 3)
- [ ] Score each design against all 4 dNTPs
- [ ] Filter for >100x selectivity
- [ ] Cluster designs by structural similarity

### Phase 3: Optogenetic Integration (Week 4)
- [ ] Insert LOV2/CRY2/BphP1/BICYCL domains at optimal sites
- [ ] Predict chimera structures
- [ ] Assess whether binding pocket is maintained

### Phase 4: Experimental Validation
- [ ] Synthesize top 10-20 designs
- [ ] Express and purify
- [ ] Measure binding affinity (ITC, SPR, or MST)
- [ ] Test light-dependent release

---

## Key References

1. Gil AA et al. (2020) Optogenetic control of protein binding using light-switchable nanobodies. *Nat Commun* 11:4044. [Link](https://www.nature.com/articles/s41467-020-17836-8)

2. He L et al. (2021) Design of Smart Antibody Mimetics with Photosensitive Switches. *Adv Biol* 5:2000541. [PMC8295464](https://pmc.ncbi.nlm.nih.gov/articles/PMC8295464/)

3. Watson JL et al. (2023) De novo design of protein structure and function with RFdiffusion. *Nature* 620:1089-1100. [Link](https://www.nature.com/articles/s41586-023-06415-8)

4. Wohlwend J et al. (2024) Boltz-1: Democratizing Biomolecular Interaction Modeling. *bioRxiv*. [GitHub](https://github.com/jwohlwend/boltz)

5. Krishna R et al. (2024) Generalized biomolecular modeling and design with RoseTTAFold All-Atom. *Science* 384:eadl2528. [Link](https://www.science.org/doi/10.1126/science.adl2528)

6. Ladenson RC et al. (2006) Isolation and characterization of a thermally stable recombinant anti-caffeine heavy-chain antibody fragment. *Anal Chem* 78:4501-4508.

7. Spinelli S et al. (2000) Camelid heavy-chain variable domains provide efficient combining sites to haptens. *Biochemistry* 39:1217-1222.

---

## Files to Create Next

1. `configs/dATP_binder.yaml` - Boltz config for dATP
2. `configs/dGTP_binder.yaml` - Boltz config for dGTP
3. `configs/dCTP_binder.yaml` - Boltz config for dCTP
4. `configs/dTTP_binder.yaml` - Boltz config for dTTP
5. `scripts/run_boltz_design.py` - Automation script
6. `scripts/score_selectivity.py` - Cross-nucleotide scoring
7. `scripts/insert_optodomain.py` - Chimera sequence generator
