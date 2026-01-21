#!/usr/bin/env python3
"""
Generate ChimeraX visualization scripts for Mac.
Uses Mac-specific paths.
"""

from pathlib import Path
import json

def create_chimerax_script_mac(variant_id, target_nucleotide, output_dir, mac_base_path):
    """
    Create a ChimeraX command script for Mac with custom paths.

    Args:
        variant_id: e.g., "dATP_variant_039"
        target_nucleotide: e.g., "dATP"
        output_dir: Where to save the script
        mac_base_path: Base path on Mac (e.g., "/Users/jeremylinsley/Documents/protein_modeling")
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Construct Mac paths
    cif_file = f"{mac_base_path}/structures/{variant_id}_vs_{target_nucleotide}_model_0.cif"
    output_path = f"{mac_base_path}/visualizations"

    # ChimeraX commands
    script = f"""# ChimeraX Visualization Script (Mac Version)
# Variant: {variant_id}
# Target: {target_nucleotide}
# Run with: chimerax {variant_id}_{target_nucleotide}_mac.cxc

# Open structure
open {cif_file}

# Basic setup
preset "Overall Look" "publication 1"
lighting soft
set bgColor white

# Color protein and ligand
color /A tan
color /B green

# Show protein as cartoon
hide /A atoms
cartoon /A

# Show ligand as ball-and-stick
show /B atoms
style /B ball

# Highlight CDR3 region (residues 95-101)
color /A:95-101 orange
show /A:95-101 atoms
style /A:95-101 stick

# Find and display binding site residues (within 5Å of ligand)
select /A & <5 /B
color sel cyan
show sel atoms
style sel stick
~select

# Show hydrogen bonds
hbonds /A to /B
hbonds style dashed
hbonds color yellow

# Orient for best view
view

# Save session
save {output_path}/{variant_id}_{target_nucleotide}_session.cxs

# Save images
turn y 1 120
wait 120
# Front view
save {output_path}/{variant_id}_{target_nucleotide}_front.png width 1200 height 900 supersample 3
# Rotate for side view
turn y 90
wait 60
save {output_path}/{variant_id}_{target_nucleotide}_side.png width 1200 height 900 supersample 3
# Rotate for top view
turn x 90
wait 60
save {output_path}/{variant_id}_{target_nucleotide}_top.png width 1200 height 900 supersample 3

# Focus on binding site
view /B
cofr /B
zoom 0.5
save {output_path}/{variant_id}_{target_nucleotide}_binding_site.png width 1200 height 900 supersample 3

# Close-up of CDR3 and ligand interaction
view /A:95-101 | /B
zoom 0.7
save {output_path}/{variant_id}_{target_nucleotide}_CDR3_closeup.png width 1200 height 900 supersample 3

log save {output_path}/{variant_id}_{target_nucleotide}_log.txt

# Keep session open for interactive exploration
# Or uncomment to close automatically:
# exit
"""

    script_file = output_dir / f"{variant_id}_{target_nucleotide}_mac.cxc"
    with open(script_file, 'w') as f:
        f.write(script)

    print(f"✓ Generated Mac ChimeraX script: {script_file.name}")

    # Also create a simplified version for quick viewing
    simple_script = f"""# Quick ChimeraX Viewer (Mac)
# Run with: chimerax {variant_id}_{target_nucleotide}_simple_mac.cxc

open {cif_file}
preset "Overall Look" "publication 1"
color /A wheat
color /B green
show /B atoms
style /B ball
select /A & <5 /B
color sel cyan
show sel atoms
style sel stick
hbonds /A to /B
view
"""

    simple_file = output_dir / f"{variant_id}_{target_nucleotide}_simple_mac.cxc"
    with open(simple_file, 'w') as f:
        f.write(simple_script)

    print(f"✓ Generated simple script: {simple_file.name}")

    return script_file, simple_file


def create_master_chimerax_script_mac(output_dir, mac_base_path):
    """Create a master script that opens all 4 top binders in separate windows."""

    output_dir = Path(output_dir)

    variants = [
        ("dATP_variant_039", "dATP"),
        ("dTTP_variant_016", "dTTP"),
        ("dGTP_variant_019", "dGTP"),
        ("dCTP_variant_048", "dCTP")
    ]

    # Create master script
    master_script = f"""# ChimeraX Master Script (Mac Version)
# Opens all 4 top binders in tile view for comparison
# Run with: chimerax view_all_binders_mac.cxc

# Set up tiled viewing
windowsize 1920 1080
tile

"""

    for idx, (variant_id, target) in enumerate(variants, 1):
        cif_file = f"{mac_base_path}/structures/{variant_id}_vs_{target}_model_0.cif"
        master_script += f"""
# Open variant {idx}: {variant_id}
open {cif_file} name model{idx}
color model{idx}/A tan
color model{idx}/B green
show model{idx}/B atoms
style model{idx}/B ball
select model{idx}/A & <5 model{idx}/B
color sel cyan
show sel atoms
style sel stick
~select
view model{idx}

"""

    master_script += """
# Adjust view
tile
lighting soft
set bgColor white
"""

    master_file = output_dir / "view_all_binders_mac.cxc"
    with open(master_file, 'w') as f:
        f.write(master_script)

    print(f"\n✓ Generated master script: {master_file.name}")
    print(f"   Opens all 4 binders in tiled view")

    return master_file


def create_file_transfer_guide(output_dir, mac_base_path):
    """Create a guide for transferring files to Mac."""

    output_dir = Path(output_dir)

    guide = f"""# File Transfer Guide for Mac

## Required Directory Structure on Mac:

Create these directories on your Mac:
```bash
mkdir -p {mac_base_path}/structures
mkdir -p {mac_base_path}/visualizations
mkdir -p {mac_base_path}/scripts
```

## Files to Transfer from Linux:

### 1. Structure Files (CIF format)
Copy these CIF files from Linux to Mac:

From: ~/nucleotide_catchers/specificity_library/screening_results/
To:   {mac_base_path}/structures/

Files needed:
- dATP_variant_039_vs_dATP/boltz_results_*/predictions/*/dATP_variant_039_vs_dATP_model_0.cif
  → {mac_base_path}/structures/dATP_variant_039_vs_dATP_model_0.cif

- dTTP_variant_016_vs_dTTP/boltz_results_*/predictions/*/dTTP_variant_016_vs_dTTP_model_0.cif
  → {mac_base_path}/structures/dTTP_variant_016_vs_dTTP_model_0.cif

- dGTP_variant_019_vs_dGTP/boltz_results_*/predictions/*/dGTP_variant_019_vs_dGTP_model_0.cif
  → {mac_base_path}/structures/dGTP_variant_019_vs_dGTP_model_0.cif

- dCTP_variant_048_vs_dCTP/boltz_results_*/predictions/*/dCTP_variant_048_vs_dCTP_model_0.cif
  → {mac_base_path}/structures/dCTP_variant_048_vs_dCTP_model_0.cif

### 2. ChimeraX Scripts
Copy these scripts from Linux to Mac:

From: ~/nucleotide_catchers/specificity_library/visualizations/chimerax_scripts_mac/
To:   {mac_base_path}/scripts/

All *_mac.cxc files

## Transfer Methods:

### Option 1: SCP (from your Mac)
```bash
# Create directories
mkdir -p {mac_base_path}/{{structures,visualizations,scripts}}

# Transfer structure files (run from Mac terminal)
scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dATP_variant_039_vs_dATP/boltz_results_*/predictions/*/dATP_variant_039_vs_dATP_model_0.cif {mac_base_path}/structures/

scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dTTP_variant_016_vs_dTTP/boltz_results_*/predictions/*/dTTP_variant_016_vs_dTTP_model_0.cif {mac_base_path}/structures/

scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dGTP_variant_019_vs_dGTP/boltz_results_*/predictions/*/dGTP_variant_019_vs_dGTP_model_0.cif {mac_base_path}/structures/

scp thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/dCTP_variant_048_vs_dCTP/boltz_results_*/predictions/*/dCTP_variant_048_vs_dCTP_model_0.cif {mac_base_path}/structures/

# Transfer scripts
scp -r thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/visualizations/chimerax_scripts_mac/* {mac_base_path}/scripts/
```

### Option 2: Rsync (more efficient)
```bash
# From Mac terminal
rsync -avz --progress thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/screening_results/*/boltz_results_*/predictions/*/*_model_0.cif {mac_base_path}/structures/

rsync -avz --progress thinkingscopeanalysis@your-linux-server:~/nucleotide_catchers/specificity_library/visualizations/chimerax_scripts_mac/ {mac_base_path}/scripts/
```

## After Transfer:

1. Verify files are in place:
```bash
ls -lh {mac_base_path}/structures/*.cif
ls -lh {mac_base_path}/scripts/*.cxc
```

2. Run ChimeraX:
```bash
# View single structure
chimerax {mac_base_path}/scripts/dTTP_variant_016_dTTP_simple_mac.cxc

# View all 4 at once
chimerax {mac_base_path}/scripts/view_all_binders_mac.cxc
```

## Quick Test:

Try this first to make sure ChimeraX works:
```bash
cd {mac_base_path}/scripts
chimerax dTTP_variant_016_dTTP_simple_mac.cxc
```

This will open the best binder (dTTP) in ChimeraX with proper coloring and labels.
"""

    guide_file = output_dir / "MAC_TRANSFER_GUIDE.md"
    with open(guide_file, 'w') as f:
        f.write(guide)

    print(f"\n✓ Generated transfer guide: {guide_file.name}")

    return guide_file


def main():
    """Generate all Mac ChimeraX scripts."""

    print("="*80)
    print("GENERATING MAC CHIMERAX VISUALIZATION SCRIPTS")
    print("="*80)
    print()

    # Mac base path (user can customize this)
    mac_base_path = "/Users/jeremylinsley/Documents/protein_modeling"

    output_dir = Path.home() / "nucleotide_catchers/specificity_library/visualizations/chimerax_scripts_mac"
    output_dir.mkdir(exist_ok=True, parents=True)

    print(f"Mac base path: {mac_base_path}")
    print(f"Output directory: {output_dir}")
    print()

    # Top 4 variants
    variants_info = [
        {
            'variant_id': 'dATP_variant_039',
            'target': 'dATP',
            'mutations': 'A97W,K98R,S100T,Y101D'
        },
        {
            'variant_id': 'dTTP_variant_016',
            'target': 'dTTP',
            'mutations': 'C96N,K98R,S100A'
        },
        {
            'variant_id': 'dGTP_variant_019',
            'target': 'dGTP',
            'mutations': 'C96T,K98R,V99I'
        },
        {
            'variant_id': 'dCTP_variant_048',
            'target': 'dCTP',
            'mutations': 'C96S,A97F,S100Q,Y101E'
        }
    ]

    generated_scripts = []

    for var_info in variants_info:
        variant_id = var_info['variant_id']
        target = var_info['target']

        print(f"\nGenerating Mac scripts for {variant_id}:")
        print(f"  Target: {target}")
        print(f"  Mutations: {var_info['mutations']}")

        script_file, simple_file = create_chimerax_script_mac(
            variant_id, target, output_dir, mac_base_path
        )
        generated_scripts.append((variant_id, target, script_file, simple_file))
        print()

    # Create master script
    master_file = create_master_chimerax_script_mac(output_dir, mac_base_path)

    # Create transfer guide
    guide_file = create_file_transfer_guide(output_dir, mac_base_path)

    print()
    print("="*80)
    print("MAC CHIMERAX SCRIPTS GENERATED")
    print("="*80)
    print()
    print(f"Output directory: {output_dir}/")
    print()
    print("Generated files:")
    print("  • 4 full scripts (detailed views + multiple images)")
    print("  • 4 simple scripts (quick viewing)")
    print("  • 1 master script (view all 4 at once)")
    print("  • 1 transfer guide (instructions for moving files)")
    print(f"  Total: {len(generated_scripts) * 2 + 2} files")
    print()
    print("Next steps:")
    print(f"  1. Read: {guide_file}")
    print(f"  2. Transfer CIF files and scripts to your Mac")
    print(f"  3. Run on Mac: chimerax {mac_base_path}/scripts/view_all_binders_mac.cxc")
    print()


if __name__ == "__main__":
    main()
