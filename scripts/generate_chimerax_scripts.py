#!/usr/bin/env python3
"""
Generate ChimeraX visualization scripts for nucleotide binders.
ChimeraX is free and has excellent rendering capabilities.
"""

from pathlib import Path
import json

def create_chimerax_script(variant_id, target_nucleotide, cif_file, output_dir):
    """
    Create a ChimeraX command script to visualize binding.

    ChimeraX scripts use simple commands that can be run interactively
    or saved as .cxc files and run with: chimerax script.cxc
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Extract mutation info from variant_id if available
    mutations_file = Path(cif_file).parent.parent.parent.parent / "mutations.json"

    # ChimeraX commands
    script = f"""# ChimeraX Visualization Script
# Variant: {variant_id}
# Target: {target_nucleotide}
# Run with: chimerax {variant_id}_{target_nucleotide}_chimerax.cxc

# Open structure
open {cif_file}

# Basic setup
preset "Overall Look" publication
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
save {output_dir}/{variant_id}_{target_nucleotide}_session.cxs

# Save images
turn y 1 120
wait 120
# Front view
save {output_dir}/{variant_id}_{target_nucleotide}_front.png width 1200 height 900 supersample 3
# Rotate for side view
turn y 90
wait 60
save {output_dir}/{variant_id}_{target_nucleotide}_side.png width 1200 height 900 supersample 3
# Rotate for top view
turn x 90
wait 60
save {output_dir}/{variant_id}_{target_nucleotide}_top.png width 1200 height 900 supersample 3

# Focus on binding site
view /B
cofr /B
zoom 0.5
save {output_dir}/{variant_id}_{target_nucleotide}_binding_site.png width 1200 height 900 supersample 3

# Close-up of CDR3 and ligand interaction
view /A:95-101 | /B
zoom 0.7
save {output_dir}/{variant_id}_{target_nucleotide}_CDR3_closeup.png width 1200 height 900 supersample 3

# Optional: Create a spinning movie
# movie record
# turn y 2 180
# wait 180
# movie encode {output_dir}/{variant_id}_{target_nucleotide}_rotation.mp4

log save {output_dir}/{variant_id}_{target_nucleotide}_log.txt

# Keep session open for interactive exploration
# Or uncomment to close automatically:
# exit
"""

    script_file = output_dir / f"{variant_id}_{target_nucleotide}_chimerax.cxc"
    with open(script_file, 'w') as f:
        f.write(script)

    print(f"✓ Generated ChimeraX script: {script_file.name}")

    # Also create a simplified version for quick viewing
    simple_script = f"""# Quick ChimeraX Viewer
# Run with: chimerax {variant_id}_{target_nucleotide}_simple.cxc

open {cif_file}
preset publication
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

    simple_file = output_dir / f"{variant_id}_{target_nucleotide}_simple.cxc"
    with open(simple_file, 'w') as f:
        f.write(simple_script)

    print(f"✓ Generated simple script: {simple_file.name}")

    return script_file, simple_file


def create_master_chimerax_script(output_dir):
    """Create a master script that opens all 4 top binders in separate windows."""

    output_dir = Path(output_dir)

    # Find the top 4 variant CIF files
    base_dir = Path.home() / "nucleotide_catchers/specificity_library/screening_results"

    variants = [
        ("dATP_variant_039", "dATP"),
        ("dTTP_variant_016", "dTTP"),
        ("dGTP_variant_019", "dGTP"),
        ("dCTP_variant_048", "dCTP")
    ]

    cif_files = []
    for variant_id, target in variants:
        search_pattern = f"{variant_id}_vs_{target}"
        search_dir = base_dir / search_pattern / f"boltz_results_{search_pattern}" / "predictions" / search_pattern
        cif_path = search_dir / f"{search_pattern}_model_0.cif"

        if cif_path.exists():
            cif_files.append((variant_id, target, cif_path))
        else:
            print(f"⚠ Warning: CIF file not found: {cif_path}")

    # Create master script
    master_script = """# ChimeraX Master Script
# Opens all 4 top binders in tile view for comparison
# Run with: chimerax view_all_binders.cxc

# Set up tiled viewing
windowsize 1920 1080
tile

"""

    for idx, (variant_id, target, cif_path) in enumerate(cif_files, 1):
        master_script += f"""
# Open variant {idx}: {variant_id}
open {cif_path} name model{idx}
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

    master_file = output_dir / "view_all_binders.cxc"
    with open(master_file, 'w') as f:
        f.write(master_script)

    print(f"\n✓ Generated master script: {master_file.name}")
    print(f"   Opens all 4 binders in tiled view")

    return master_file


def main():
    """Generate all ChimeraX scripts."""

    print("="*80)
    print("GENERATING CHIMERAX VISUALIZATION SCRIPTS")
    print("="*80)
    print()

    output_dir = Path.home() / "nucleotide_catchers/specificity_library/visualizations/chimerax_scripts"
    output_dir.mkdir(exist_ok=True, parents=True)

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

    base_dir = Path.home() / "nucleotide_catchers/specificity_library/screening_results"

    generated_scripts = []

    for var_info in variants_info:
        variant_id = var_info['variant_id']
        target = var_info['target']

        # Find CIF file
        search_pattern = f"{variant_id}_vs_{target}"
        search_dir = base_dir / search_pattern / f"boltz_results_{search_pattern}" / "predictions" / search_pattern
        cif_path = search_dir / f"{search_pattern}_model_0.cif"

        if not cif_path.exists():
            print(f"⚠ Warning: CIF file not found: {cif_path}")
            continue

        print(f"\nGenerating scripts for {variant_id}:")
        print(f"  Target: {target}")
        print(f"  Mutations: {var_info['mutations']}")
        print(f"  Structure: {cif_path.name}")

        script_file, simple_file = create_chimerax_script(variant_id, target, cif_path, output_dir)
        generated_scripts.append((variant_id, target, script_file, simple_file))
        print()

    # Create master script
    master_file = create_master_chimerax_script(output_dir)

    print()
    print("="*80)
    print("CHIMERAX SCRIPTS GENERATED")
    print("="*80)
    print()
    print(f"Output directory: {output_dir}/")
    print()
    print("Generated files:")
    print("  • 4 full scripts (detailed views + multiple images)")
    print("  • 4 simple scripts (quick viewing)")
    print("  • 1 master script (view all 4 at once)")
    print(f"  Total: {len(generated_scripts) * 2 + 1} script files")
    print()
    print("To use:")
    print("  1. Install ChimeraX: https://www.cgl.ucsf.edu/chimerax/download.html")
    print(f"  2. Run a script: chimerax {output_dir}/dTTP_variant_016_dTTP_simple.cxc")
    print(f"  3. Or view all: chimerax {output_dir}/view_all_binders.cxc")
    print()
    print("Priority (best binder):")
    print(f"  chimerax {output_dir}/dTTP_variant_016_dTTP_chimerax.cxc")
    print()


if __name__ == "__main__":
    main()
