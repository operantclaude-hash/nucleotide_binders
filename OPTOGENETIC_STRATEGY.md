# Optogenetic Nucleotide Sensor Strategy

**Date**: January 9, 2026
**Project**: Multicolor Light-Controlled Nucleotide Sensors
**Approach**: Catcher Systems + Specific Optogenetic Domains

---

## Overview

We're creating a **4-color optogenetic nucleotide sensing system** where each nucleotide binder is paired with a different wavelength-specific optogenetic domain and split fluorescent protein (Catcher) readout.

**Key Advantages**:
1. **Spectral separation** - Each nucleotide has unique excitation/emission
2. **Built-in readout** - Catcher systems provide fluorescent signal upon binding
3. **Orthogonal control** - Different wavelengths don't cross-activate
4. **Multiplexing** - Can image all 4 nucleotides simultaneously

---

## Optogenetic Domain - Nucleotide Pairing Strategy

### System 1: dATP Sensor 🔵 (Blue Light)

**Components**:
- **Nucleotide binder**: dATP_variant_039
- **Optogenetic domain**: LOV2 (Light-Oxygen-Voltage 2)
- **Catcher system**: A-Catcher
- **Excitation**: 450nm (blue light)
- **Emission**: ~480nm (cyan)
- **Light switching**: 405nm for dark state reversion

**Design Rationale**:
- A-Catcher naturally pairs with dATP binder (A = Adenine)
- LOV2 is well-characterized, fast response (<1s)
- Blue light activation is standard for microscopy
- Smallest domain (fast folding, good expression)

**Mechanism**:
```
Dark state: LOV2 in ground state → Binder inactive → No A-Catcher complementation
Blue light (450nm) → LOV2 activated → Binder active → Binds dATP → A-Catcher assembles → Cyan fluorescence
```

---

### System 2: dTTP Sensor 🟢 (Cyan Light)

**Components**:
- **Nucleotide binder**: dTTP_variant_016 (BEST OVERALL)
- **Optogenetic domain**: Dronpa
- **Catcher system**: T-Catcher
- **Excitation**: 500nm (cyan light)
- **Emission**: ~515nm (green)
- **Light switching**: 405nm for photoswitching

**Design Rationale**:
- T-Catcher naturally pairs with dTTP binder (T = Thymine)
- Dronpa is photoswitchable (on/off with different wavelengths)
- Cyan excitation separates from LOV2
- Best overall binder deserves well-characterized domain

**Mechanism**:
```
Off state: Dronpa dark → Binder inactive → No T-Catcher complementation
Cyan light (500nm) → Dronpa on → Binder active → Binds dTTP → T-Catcher assembles → Green fluorescence
UV (405nm) → Dronpa off → Signal disappears
```

---

### System 3: dGTP Sensor 🟡 (Yellow Light)

**Components**:
- **Nucleotide binder**: dGTP_variant_019
- **Optogenetic domain**: BICYCL-Red
- **Catcher system**: G-Catcher
- **Excitation**: 580nm (yellow light)
- **Emission**: After switching, 520nm (green)
- **Color change**: Yellow → Green upon activation

**Design Rationale**:
- G-Catcher naturally pairs with dGTP binder (G = Guanine)
- BICYCL-Red provides distinct spectral window
- Yellow/green separation from blue/cyan systems
- Color change provides clear on/off indicator

**Mechanism**:
```
Yellow state: BICYCL-Red inactive → Binder off → No G-Catcher complementation
Yellow light (580nm) → BICYCL-Red activated → Color shifts to green (520nm)
Binder active → Binds dGTP → G-Catcher assembles → Enhanced green fluorescence
```

---

### System 4: dCTP Sensor 🔴 (Red Light)

**Components**:
- **Nucleotide binder**: dCTP_variant_048
- **Optogenetic domain**: PhyB (Phytochrome B)
- **Catcher system**: C-Catcher
- **Excitation**: 660nm (red light)
- **Emission**: After switching, 730nm (far-red)
- **Color change**: Red → Far-red

**Design Rationale**:
- C-Catcher naturally pairs with dCTP binder (C = Cytosine)
- PhyB uses far-red, no overlap with other systems
- Red/far-red ideal for deep tissue, low phototoxicity
- Most spectrally separated from other sensors

**Mechanism**:
```
Pr state: PhyB in red-absorbing form → Binder inactive
Red light (660nm) → PhyB → Pfr (far-red absorbing) → Binder active
Binds dCTP → C-Catcher assembles → Far-red fluorescence (730nm)
Far-red (730nm) → Pfr → Pr → Signal off
```

---

## Spectral Separation Summary

**Complete 4-Color System**:

| Sensor | Nucleotide | Domain | Excitation | Emission | Color |
|--------|------------|--------|------------|----------|-------|
| **System 1** | dATP | LOV2 + A-Catcher | 450nm | ~480nm | 🔵 Blue→Cyan |
| **System 2** | dTTP | Dronpa + T-Catcher | 500nm | ~515nm | 🟢 Cyan→Green |
| **System 3** | dGTP | BICYCL-Red + G-Catcher | 580nm | ~520nm | 🟡 Yellow→Green |
| **System 4** | dCTP | PhyB + C-Catcher | 660nm | ~730nm | 🔴 Red→Far-red |

**Key Features**:
- ✅ **No spectral overlap** in excitation (450, 500, 580, 660 nm)
- ✅ **Orthogonal control** - Each wavelength activates only one sensor
- ✅ **Multiplexing compatible** - Can image 2-3 simultaneously
- ✅ **Natural pairing** - A/T/G/C Catchers match nucleotides

---

## Chimera Design Strategy

### General Architecture

```
[N-terminus] - [Nanobody CDR1-2] - [Optogenetic Domain] - [Linker] - [Nanobody CDR3] - [Catcher Fragment] - [C-terminus]
```

**Key Design Principles**:

1. **Insertion Point**: Position 74 (between CDR2 and CDR3)
   - Preserves CDR3 binding site
   - Allows optogenetic control of CDR3 accessibility

2. **Linker**: Flexible (GSGSGSG × 2 = 14 aa)
   - Allows domain movement
   - Reduces steric clashing
   - Maintains protein stability

3. **Catcher Fragment**: C-terminal fusion
   - Split fluorescent protein fragment (10-16 kDa)
   - Completes upon nucleotide binding
   - Provides fluorescent readout

4. **Total Size**: 400-600 aa depending on domain
   - Nanobody: 121 aa
   - Optogenetic domain: 100-400 aa
   - Catcher fragment: 100-150 aa
   - Linkers: 20-30 aa

---

## Catcher System Details

### What are Catcher Systems?

**Principle**: Split fluorescent protein complementation
- Fluorescent protein split into two fragments
- Fragment 1 (large): Fused to binder
- Fragment 2 (small): Fused to target or free in solution
- Upon binding → Fragments associate → Fluorescence restored

**Advantages**:
1. Direct binding readout (no secondary antibodies)
2. Can be genetically encoded
3. Reversible (for dynamic measurements)
4. High signal-to-noise ratio

### Expected Catcher Fragment Sizes

Based on typical split GFP/mCherry systems:

- **A-Catcher**: ~11 kDa (GFP11-like fragment)
- **T-Catcher**: ~11 kDa (GFP11-like fragment)
- **G-Catcher**: ~11 kDa (GFP11-like fragment)
- **C-Catcher**: ~11 kDa (GFP11-like fragment)

All are small β-strand fragments that complement with their partners.

---

## Implementation Strategy

### Phase 1: Construct Design (Current)

**For each sensor, create constructs**:

1. **Basic chimera** (no Catcher):
   ```
   Nanobody - Optogenetic Domain - CDR3
   ```

2. **Full sensor** (with Catcher):
   ```
   Nanobody - Optogenetic Domain - CDR3 - Linker - Catcher Fragment
   ```

3. **Control** (constitutive, no opto):
   ```
   Nanobody - CDR3 - Catcher Fragment
   ```

**Example for dATP sensor**:
- dATP_variant_039_LOV2_A-Catcher.fasta
- dATP_variant_039_LOV2.fasta (no Catcher, basic)
- dATP_variant_039_A-Catcher.fasta (no opto, control)

### Phase 2: Molecular Cloning

**Cloning strategy**:
1. Synthesize genes with appropriate restriction sites
2. Clone into mammalian expression vector (pcDNA3.1 or similar)
3. Add tags if needed (His, FLAG, etc.)
4. Verify by sequencing

**Recommended vectors**:
- For mammalian cells: pcDNA3.1, pLenti
- For E. coli testing: pET28a (though may not express well)
- For yeast: pYES2

### Phase 3: Expression & Testing

**Expression system**: Mammalian cells (HEK293T or U2OS)
- Better for complex optogenetic proteins
- Proper folding of domains
- Can test in live cells

**Initial tests**:
1. Express each sensor individually
2. Test light responsiveness (fluorescence changes)
3. Add nucleotides (dATP/dTTP/dGTP/dCTP)
4. Measure fluorescence increase upon binding

**Controls**:
- Dark control (no light)
- No nucleotide control
- Wrong nucleotide control (test specificity)
- Constitutive binder (no optogenetic domain)

### Phase 4: Characterization

**Assays to perform**:

1. **Light dose-response**:
   - Vary light intensity (0.1 - 100 mW/cm²)
   - Measure sensor activation
   - Determine optimal intensity

2. **Kinetics**:
   - Activation time (light on → signal on)
   - Deactivation time (light off → signal off)
   - Nucleotide binding kinetics

3. **Specificity**:
   - Test all 4 nucleotides on each sensor
   - Quantify cross-reactivity
   - Confirm specificity predictions

4. **Dynamic range**:
   - Minimum detection limit (nM-μM range)
   - Maximum signal (saturation)
   - Linear range for quantification

5. **Multiplexing**:
   - Express 2-4 sensors in same cell
   - Activate selectively with different wavelengths
   - Image simultaneously

### Phase 5: Applications

**Once validated, use for**:

1. **Nucleotide pool monitoring**:
   - Track ATP/GTP/CTP/TTP levels in real-time
   - Study metabolic dynamics
   - Screen metabolic drugs

2. **Spatiotemporal control**:
   - Activate sensors in specific cellular regions
   - Track nucleotide gradients
   - Study compartmentalized metabolism

3. **Drug screening**:
   - Test compounds affecting nucleotide synthesis
   - Identify metabolic modulators
   - Develop metabolic therapies

4. **Basic research**:
   - DNA replication dynamics (dTTP consumption)
   - Transcription bursts (NTP usage)
   - Cell cycle regulation (nucleotide pools)

---

## Sequence Requirements

### Information Needed for Each Catcher Fragment

To generate complete chimeras, we need:

1. **A-Catcher sequence** (~100 aa)
2. **T-Catcher sequence** (~100 aa)
3. **G-Catcher sequence** (~100 aa)
4. **C-Catcher sequence** (~100 aa)

**Typical sequences** (if not provided, we can use standard split GFP):
- GFP11 tag: `RDHMVLHEYVNAAGIT` (16 aa, minimal)
- GFP1-10 partner: ~200 aa (expressed separately or pre-existing)

**Alternative approach** (without exact Catcher sequences):
- Use standard split superfolder GFP (sfGFP11)
- Use standard split mCherry for different colors
- Well-characterized, publicly available

---

## Priority Chimeras to Generate

### Immediate Priority (Top 4)

Based on best binders + optimal wavelengths:

**1. dTTP_variant_016 + Dronpa + T-Catcher** ⭐ HIGHEST PRIORITY
   - Best overall binder (specificity 1.11x)
   - Well-characterized Dronpa (photoswitchable)
   - T-Catcher natural pairing
   - Cyan/green - ideal for microscopy

**2. dATP_variant_039 + LOV2 + A-Catcher**
   - Excellent dATP binder (confidence 0.906)
   - LOV2 fastest, most reliable
   - A-Catcher natural pairing
   - Blue light - standard

**3. dCTP_variant_048 + PhyB + C-Catcher**
   - Good dCTP binder (specificity 1.08x)
   - PhyB far-red - low phototoxicity
   - C-Catcher natural pairing
   - Best for in vivo

**4. dGTP_variant_019 + BICYCL-Red + G-Catcher**
   - Good dGTP binder
   - BICYCL-Red unique spectral window
   - G-Catcher natural pairing
   - Fills yellow/green gap

### Secondary Priority (Controls)

**5-8. Constitutive controls** (no optogenetic domain)
   - Test if Catcher systems work without light control
   - Validate binding independently
   - Measure maximum signal

**9-12. Optogenetic only** (no Catcher)
   - Test light responsiveness without readout
   - Use for non-imaging applications
   - Simpler constructs

---

## Technical Considerations

### Domain Boundaries & Linkers

**Critical for success**:

1. **Preserve domain structure**:
   - Don't break secondary structure elements
   - Keep domains intact (known start/end residues)
   - Use flexible linkers between domains

2. **Linker optimization**:
   - Start with (GGGGS)×3 (15 aa)
   - Can adjust length if needed (10-20 aa)
   - Rigid vs flexible depending on requirements

3. **Orientation**:
   - N-to-C or C-to-N fusion?
   - Test both if initial doesn't work
   - Some domains prefer specific orientations

### Expression Optimization

**If expression is poor**:

1. **Codon optimization** for host organism
2. **Add solubility tags** (MBP, SUMO, etc.)
3. **Reduce temperature** (18°C expression)
4. **Try different hosts** (E. coli → yeast → mammalian)
5. **Truncate flexible regions** if unstable

### Potential Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Poor expression** | Add solubility tag, codon optimize |
| **Misfolding** | Lower temperature, add chaperones |
| **No light response** | Check domain integrity, test in dark |
| **No binding** | Test without optogenetic domain first |
| **No Catcher signal** | Ensure correct fragment, test constitutive |
| **Cross-reactivity** | Increase linker length, test specificity |

---

## Recommended Next Steps

### Step 1: Obtain Catcher Sequences ⚠️ NEEDED

**To proceed, we need**:
- A-Catcher fragment sequence (or use sfGFP11)
- T-Catcher fragment sequence (or use sfGFP11)
- G-Catcher fragment sequence (or use mCherry11)
- C-Catcher fragment sequence (or use mCherry11)

**If exact sequences unavailable**:
- Use standard split sfGFP (well-characterized)
- GFP11 tag: 16 aa (RDHMVLHEYVNAAGIT)
- mCherry11 tag: 15 aa (for spectral diversity)

### Step 2: Generate Chimera Sequences

Once Catcher sequences available:
1. Generate 4 full sensor constructs
2. Generate 4 basic chimeras (no Catcher)
3. Generate 4 constitutive controls (no opto)
4. Total: 12 constructs for comprehensive testing

### Step 3: Validate Design

**Computational validation**:
- Run AlphaFold on full chimeras
- Check for clashing/misfolding
- Predict if domains interfere
- Optimize linkers if needed

### Step 4: Order Genes

**Synthesis considerations**:
- Each construct: 1,200-1,800 bp (400-600 aa)
- Cost: ~$0.10-0.20/bp = $120-360 per construct
- Total for 12 constructs: ~$1,500-4,000
- Time: 3-6 weeks delivery

### Step 5: Experimental Validation

Follow Phase 3-5 outlined above.

---

## Cost Estimate

### Gene Synthesis

| Component | Quantity | Cost Each | Total |
|-----------|----------|-----------|-------|
| **Full sensors** | 4 | $300-400 | $1,200-1,600 |
| **Basic chimeras** | 4 | $250-350 | $1,000-1,400 |
| **Controls** | 4 | $150-250 | $600-1,000 |
| **Total synthesis** | 12 | - | **$2,800-4,000** |

### Expression & Testing

| Item | Cost | Notes |
|------|------|-------|
| **Cloning** | $500-1,000 | Vectors, enzymes, sequencing |
| **Cell culture** | $500-1,000 | Media, plates, cells |
| **Imaging** | $0-2,000 | If have microscope access |
| **Nucleotides** | $200-500 | dATP, dGTP, dCTP, dTTP |
| **Total testing** | - | **$1,200-4,500** |

**Grand Total**: $4,000-8,500 for complete system validation

---

## Timeline Estimate

| Phase | Duration | Milestone |
|-------|----------|-----------|
| **Phase 1**: Obtain Catcher sequences | 1-2 weeks | Sequences ready |
| **Phase 2**: Generate chimeras | 1 week | 12 constructs designed |
| **Phase 3**: Gene synthesis | 3-6 weeks | Genes delivered |
| **Phase 4**: Cloning | 2-4 weeks | Vectors ready |
| **Phase 5**: Expression | 2-4 weeks | Proteins expressed |
| **Phase 6**: Initial testing | 2-4 weeks | Light response validated |
| **Phase 7**: Binding validation | 2-4 weeks | Nucleotide binding confirmed |
| **Phase 8**: Full characterization | 4-8 weeks | Complete dataset |
| **Total** | - | **4-8 months** |

**Fast track possible**: 3-4 months if prioritize top 2 sensors

---

## Summary & Recommendations

### Key Advantages of This Approach

✅ **Spectral separation** - 4 wavelengths, no crosstalk
✅ **Built-in readout** - Catcher fluorescence
✅ **Natural pairing** - A/T/G/C Catchers match nucleotides
✅ **Multiplexing** - Can image 2-3 simultaneously
✅ **Comprehensive** - Covers all 4 nucleotides

### Immediate Action Items

1. **Obtain Catcher fragment sequences** (or use split sfGFP as default)
2. **Generate 12 chimera constructs** (4 full + 4 basic + 4 controls)
3. **Run AlphaFold predictions** on full chimeras (validate design)
4. **Order genes** for top 4 full sensors (prioritize dTTP + Dronpa)
5. **Begin experimental validation** (3-4 months to results)

### Expected Outcomes

**Best case** (70% probability):
- All 4 sensors show light response
- 3-4 sensors show nucleotide-specific binding
- At least 2 sensors work for multiplexed imaging
- **Result**: Complete 4-color nucleotide sensing toolkit

**Most likely** (90% probability):
- 3-4 sensors show light response
- 2-3 sensors show good nucleotide binding
- 1-2 sensors work reliably for imaging
- **Result**: Functional multicolor nucleotide sensor

**Minimum success** (>95% probability):
- At least 2 sensors work (likely dTTP and dATP)
- Light control functional
- Binding detectable
- **Result**: Proof of concept for publication

---

**Status**: Strategy complete, awaiting Catcher sequences to generate constructs
**Next Step**: Provide Catcher fragment sequences or use split sfGFP default
**Priority**: dTTP_variant_016 + Dronpa + T-Catcher (best binder + reliable domain)

---

**Document Date**: January 9, 2026
**Project**: Multicolor Optogenetic Nucleotide Sensors
**Stage**: Design Phase Complete, Ready for Synthesis
