# Edited Proposal Text for Nucleotide Catchers

## Your Original Text:
> We generated ~3000 CDR3 loop variants and screened them using Boltz-1 structure prediction against all four nucleotides. Selection criteria included confidence score >0.85, ligand interface score (ipTM) >0.75, and specificity ratio >1.05 for target versus off-target nucleotides. Our top four binders achieved confidence scores of 0.885-0.906 and ligand ipTM of 0.80-0.88, significantly exceeding typical AlphaFold 3 performance (Abramson et al., Nature 2024) and indicating high probability of experimental validation. For optogenetic control, we will insert photoswitchable domains at loop 6 (position ~74) of validated binders, following previously reported optogenetic switching success for nano-bodies (citation).

---

## Corrected Version (reflects your actual pipeline):

> We generated CDR loop variants from a nanobody scaffold and screened them using Boltz-2 structure prediction against all four nucleotides (dATP, dGTP, dCTP, dTTP). Each variant was tested for binding to all four nucleotides to calculate specificity ratios. Selection criteria included confidence score >0.85, ligand interface score (ipTM) >0.75, and specificity ratio >1.05 for target versus off-target nucleotides. Our top four binders achieved confidence scores of 0.885-0.906 and ligand ipTM of 0.80-0.88, indicating high probability of experimental validation. For optogenetic control, we will insert photoswitchable domains at loop 6 (position ~74) of validated binders, following previously reported optogenetic switching success for nanobodies (Gil et al., 2020).

---

## Alternative Shorter Version:

> We screened CDR loop variants using Boltz-2 structure prediction, testing each against all four nucleotides to identify specific binders. Selection criteria included confidence score >0.85, ipTM >0.75, and specificity ratio >1.05. Our top binders achieved confidence scores of 0.885-0.906 and ipTM of 0.80-0.88. For optogenetic control, we will insert photoswitchable domains at loop 6 (~position 74) following established protocols (Gil et al., 2020).

---

## Key Changes Made:

1. **Changed Boltz-1 → Boltz-2** - You used Boltz-2
2. **Kept CDR variant approach** - This is what you actually did (not RFdiffusion)
3. **Added specificity screening description** - Each variant tested vs all 4 nucleotides
4. **Added citation** - Gil et al., 2020 for optogenetic nanobody insertion
5. **Removed "~3000"** - Unless you actually ran 3000 variants (your pipeline shows 80 for production run)

## Note on Numbers:

Your pipeline shows:
- Test mode: 20 variants (5 per nucleotide)
- Production: 80 variants (20 per nucleotide)
- Each tested against 4 nucleotides = 320 predictions

If you want to claim ~3000, you'd need to run with higher variant counts. Otherwise, adjust the number or remove it.

## Citation to Add:

Gil AA, et al. (2020) Optogenetic control of protein binding using light-switchable nanobodies. *Nature Communications* 11:4044.
