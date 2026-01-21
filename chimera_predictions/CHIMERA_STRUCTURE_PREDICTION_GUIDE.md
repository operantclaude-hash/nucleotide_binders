# Optogenetic Chimera Structure Prediction Guide

## Chimera: dATP-Binding Nanobody + Dronpa + A-Catcher

**Total length**: 409 amino acids

**Domain architecture**:
- Nanobody N-term (1-74): dATP binder
- Linker 1 (75-81): GSGSGSG
- Dronpa (82-334): Optogenetic switch (253 aa)
- Linker 2 (335-341): GSGSGSG
- Nanobody C-term (342-388): dATP binder (includes CDR3)
- Linker 3 (389-393): GGGGS
- A-Catcher (394-409): Fluorescent readout tag

---

## Option 1: ESMFold Web Server ⭐ RECOMMENDED (Fastest, ~5 minutes)

**Website**: https://esmatlas.com/resources?action=fold

**Steps**:
1. Go to the ESMFold website
2. Paste the sequence below
3. Click "Fold"
4. Wait ~3-5 minutes
5. Download the PDB file

**Sequence to paste**:
```
QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNGSGSGSGMRGSHHHHHHGMASMASKGEELFTGVVPILVELDGDVNGHKFSVRGEGEGDATNGKLTLKFICTTGKLPVPWPTLVTTLTYGVQCFARYPDHMKQHDFFKSAMPEGYVQERTISFKDDGTYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNFNSHNVYITADKQKNGIKANFKIRHNVEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSVLSKDPNEKRDHMVLLEFVTAAGITHGMDELYKGSGSGSGSKNTLYLQMNSLRAEDTAVYYCWRVTDLSTASSLDYWGQGTLVTVSSGGGGSRDHMVLHEYVNAAGIT
```

**What you'll get**:
- Full 3D structure prediction
- Confidence scores (pLDDT per residue)
- Downloadable PDB file
- Can visualize directly in browser

---

## Option 2: AlphaFold 3 Server (Best quality, ~30 minutes)

**Website**: https://golgi.sandbox.google.com/about

**Steps**:
1. Create a free account (academic use)
2. Upload FASTA file: `dATP_Dronpa_A_Catcher_protein_only.fasta`
   (Located at: `/home/thinkingscopeanalysis/nucleotide_catchers/chimera_predictions/`)
3. Submit job
4. Wait ~20-30 minutes
5. Download CIF file

**Advantages**:
- Most accurate predictions
- Includes confidence metrics
- Can add dATP ligand if desired

---

## Option 3: Compare to Known Dronpa Structure

Since Dronpa has a known crystal structure, we can:

1. **Download Dronpa structure**: PDB ID 2IE2 (1.7Å resolution)
   - https://www.rcsb.org/structure/2IE2

2. **Predict just the nanobody parts separately** (much easier)

3. **Manually assemble** in ChimeraX:
   - Load Dronpa structure
   - Load predicted nanobody
   - Align based on linker positions

---

## Visualization Plan (After Getting Structure)

Once you have the predicted structure, we'll create a ChimeraX script to color it by domain:

**Colors**:
- **Nanobody (cyan)**: The dATP-binding regions
- **Dronpa (orange)**: The optogenetic switch
- **CDR3 (red)**: The specific binding loop (residues 363-369)
- **A-Catcher (green)**: The fluorescent readout tag
- **Linkers (gray)**: Flexible connectors

This will clearly show how the optogenetic domain is inserted into the nanobody!

---

## What to Look For in the Prediction

### Good signs:
- ✅ Dronpa region forms characteristic β-barrel (like GFP)
- ✅ Nanobody regions show typical immunoglobulin fold
- ✅ High confidence (pLDDT > 80) in Dronpa core
- ✅ CDR3 loops accessible for binding

### Potential issues:
- ⚠️ Low confidence at linker regions (expected - they're flexible)
- ⚠️ Unusual orientation of nanobody halves
- ⚠️ Dronpa barrel disrupted

---

## Next Steps After Prediction

1. **Download the structure** (PDB or CIF format)
2. **Transfer to your Mac** (put in protein_modeling/structures/)
3. **Create colored ChimeraX visualization** (I'll make you a script!)
4. **Compare Dronpa region to known structure** (PDB 2IE2)
5. **Identify the binding pocket** for dATP

---

## Files Ready for You

Located in: `/home/thinkingscopeanalysis/nucleotide_catchers/chimera_predictions/`

- `dATP_Dronpa_A_Catcher_protein_only.fasta` - Sequence file
- `dATP_Dronpa_A_Catcher_regions.json` - Domain boundaries for coloring
- This guide

---

**Estimated time**: 5-30 minutes depending on which service you use

**My recommendation**: Start with ESMFold - it's fast and free, no account needed!
