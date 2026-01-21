# File Transfer Guide for Mac

## Required Directory Structure on Mac:

Create these directories on your Mac:
```bash
mkdir -p /Users/jeremylinsley/Documents/protein_modeling/structures
mkdir -p /Users/jeremylinsley/Documents/protein_modeling/visualizations
mkdir -p /Users/jeremylinsley/Documents/protein_modeling/scripts
```

## Files to Transfer from Linux:

### 1. Structure Files (CIF format)
Copy these CIF files from Linux to Mac:

From: ~/nucleotide_catchers/specificity_library/screening_results/
To:   /Users/jeremylinsley/Documents/protein_modeling/structures/

Files needed:
- dATP_variant_039_vs_dATP/boltz_results_*/predictions/*/dATP_variant_039_vs_dATP_model_0.cif
  → /Users/jeremylinsley/Documents/protein_modeling/structures/dATP_variant_039_vs_dATP_model_0.cif

- dTTP_variant_016_vs_dTTP/boltz_results_*/predictions/*/dTTP_variant_016_vs_dTTP_model_0.cif
  → /Users/jeremylinsley/Documents/protein_modeling/structures/dTTP_variant_016_vs_dTTP_model_0.cif

- dGTP_variant_019_vs_dGTP/boltz_results_*/predictions/*/dGTP_variant_019_vs_dGTP_model_0.cif
  → /Users/jeremylinsley/Documents/protein_modeling/structures/dGTP_variant_019_vs_dGTP_model_0.cif

- dCTP_variant_048_vs_dCTP/boltz_results_*/predictions/*/dCTP_variant_048_vs_dCTP_model_0.cif
  → /Users/jeremylinsley/Documents/protein_modeling/structures/dCTP_variant_048_vs_dCTP_model_0.cif

### 2. ChimeraX Scripts
Copy these scripts from Linux to Mac:

From: ~/nucleotide_catchers/specificity_library/visualizations/chimerax_scripts_mac/
To:   /Users/jeremylinsley/Documents/protein_modeling/scripts/

All *_mac.cxc files

## Transfer Methods:

### Option 1: SCP (from your Mac)
```bash
# Create directories
mkdir -p /Users/jeremylinsley/Documents/protein_modeling/{structures,visualizations,scripts}

# Transfer structure files (run from Mac terminal)
scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dATP_variant_039_vs_dATP/boltz_results_*/predictions/*/dATP_variant_039_vs_dATP_model_0.cif /Users/jeremylinsley/Documents/protein_modeling/structures/

scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dTTP_variant_016_vs_dTTP/boltz_results_*/predictions/*/dTTP_variant_016_vs_dTTP_model_0.cif /Users/jeremylinsley/Documents/protein_modeling/structures/

scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dGTP_variant_019_vs_dGTP/boltz_results_*/predictions/*/dGTP_variant_019_vs_dGTP_model_0.cif /Users/jeremylinsley/Documents/protein_modeling/structures/

scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dCTP_variant_048_vs_dCTP/boltz_results_*/predictions/*/dCTP_variant_048_vs_dCTP_model_0.cif /Users/jeremylinsley/Documents/protein_modeling/structures/

# Transfer scripts
scp -r thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/visualizations/chimerax_scripts_mac/* /Users/jeremylinsley/Documents/protein_modeling/scripts/
```

### Option 2: Rsync (more efficient)
```bash
# From Mac terminal
rsync -avz --progress thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/*/boltz_results_*/predictions/*/*_model_0.cif /Users/jeremylinsley/Documents/protein_modeling/structures/

rsync -avz --progress thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/visualizations/chimerax_scripts_mac/ /Users/jeremylinsley/Documents/protein_modeling/scripts/
```

## After Transfer:

1. Verify files are in place:
```bash
ls -lh /Users/jeremylinsley/Documents/protein_modeling/structures/*.cif
ls -lh /Users/jeremylinsley/Documents/protein_modeling/scripts/*.cxc
```

2. Run ChimeraX:
```bash
# View single structure
chimerax /Users/jeremylinsley/Documents/protein_modeling/scripts/dTTP_variant_016_dTTP_simple_mac.cxc

# View all 4 at once
chimerax /Users/jeremylinsley/Documents/protein_modeling/scripts/view_all_binders_mac.cxc
```

## Quick Test:

Try this first to make sure ChimeraX works:
```bash
cd /Users/jeremylinsley/Documents/protein_modeling/scripts
chimerax dTTP_variant_016_dTTP_simple_mac.cxc
```

This will open the best binder (dTTP) in ChimeraX with proper coloring and labels.
