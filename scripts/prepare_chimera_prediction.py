#!/usr/bin/env python3
"""
Prepare optogenetic chimera for AlphaFold/Boltz structure prediction.
"""

import json
from pathlib import Path

def prepare_chimera_for_boltz(chimera_fasta, nucleotide_smiles, output_dir):
    """
    Prepare chimera + nucleotide for Boltz-1 prediction.

    Args:
        chimera_fasta: Path to chimera FASTA file
        nucleotide_smiles: SMILES string for nucleotide (dATP, dTTP, etc.)
        output_dir: Where to save prediction inputs
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Read chimera sequence
    with open(chimera_fasta, 'r') as f:
        lines = f.readlines()
        header = lines[0].strip()
        sequence = ''.join([line.strip() for line in lines[1:]])

    chimera_name = header.replace('>', '').replace('_sensor', '')

    print(f"Preparing {chimera_name} for structure prediction")
    print(f"  Sequence length: {len(sequence)} aa")
    print()

    # Create Boltz input JSON
    boltz_input = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": ["A"],
                    "sequence": sequence,
                    "msa": None  # Can add MSA path if available
                }
            },
            {
                "ligand": {
                    "id": ["B"],
                    "smiles": nucleotide_smiles
                }
            }
        ]
    }

    json_file = output_dir / f"{chimera_name}_boltz_input.json"
    with open(json_file, 'w') as f:
        json.dump(boltz_input, f, indent=2)

    print(f"✓ Created Boltz input: {json_file}")

    # Also create standalone FASTA for AlphaFold (no ligand)
    fasta_file = output_dir / f"{chimera_name}_alphafold.fasta"
    with open(fasta_file, 'w') as f:
        f.write(f">{chimera_name}\n")
        f.write(f"{sequence}\n")

    print(f"✓ Created AlphaFold FASTA: {fasta_file}")

    # Create regions file to highlight different domains
    regions = {
        "nanobody_n": {"start": 1, "end": 74, "color": "cyan"},
        "linker1": {"start": 75, "end": 81, "color": "gray"},
        "dronpa": {"start": 82, "end": 334, "color": "orange"},
        "linker2": {"start": 335, "end": 341, "color": "gray"},
        "nanobody_c": {"start": 342, "end": 388, "color": "cyan"},
        "cdr3": {"start": 363, "end": 369, "color": "red"},
        "linker3": {"start": 389, "end": 393, "color": "gray"},
        "a_catcher": {"start": 394, "end": 409, "color": "green"}
    }

    regions_file = output_dir / f"{chimera_name}_regions.json"
    with open(regions_file, 'w') as f:
        json.dump(regions, f, indent=2)

    print(f"✓ Created regions file: {regions_file}")
    print()

    print("Domain architecture:")
    print("  Nanobody N-term (1-74):     Cyan")
    print("  Linker 1 (75-81):           Gray")
    print("  Dronpa (82-334):            Orange ← OPTOGENETIC SWITCH")
    print("  Linker 2 (335-341):         Gray")
    print("  Nanobody C-term (342-388):  Cyan")
    print("    └─ CDR3 (363-369):        Red ← BINDING SITE")
    print("  Linker 3 (389-393):         Gray")
    print("  A-Catcher (394-409):        Green ← READOUT")
    print()

    return json_file, fasta_file, regions_file


def main():
    """Prepare the dATP + Dronpa chimera for prediction."""

    print("="*80)
    print("PREPARING OPTOGENETIC CHIMERA FOR STRUCTURE PREDICTION")
    print("="*80)
    print()

    # Input files
    chimera_fasta = Path.home() / "nucleotide_catchers/catcher_sensors/dATP_Dronpa_A_Catcher_sensor.fasta"

    # dATP SMILES string (2'-deoxyadenosine 5'-triphosphate)
    datp_smiles = "C1=NC2=C(C(=N1)N)N=CN2C3CC(C(O3)COP(=O)(O)OP(=O)(O)OP(=O)(O)O)O"

    output_dir = Path.home() / "nucleotide_catchers/chimera_predictions"

    json_file, fasta_file, regions_file = prepare_chimera_for_boltz(
        chimera_fasta,
        datp_smiles,
        output_dir
    )

    print("="*80)
    print("PREDICTION SETUP COMPLETE")
    print("="*80)
    print()
    print("To run predictions:")
    print()
    print("Option 1: Boltz-1 (with dATP ligand)")
    print(f"  boltz predict {json_file} \\")
    print(f"    --out_dir {output_dir}/boltz_results \\")
    print(f"    --devices 0")
    print()
    print("Option 2: AlphaFold 3 (protein only, no ligand)")
    print(f"  # Use {fasta_file}")
    print()
    print("Option 3: Visualize with known Dronpa structure")
    print("  # Download PDB 2IE2 (Dronpa structure)")
    print("  # Align predicted chimera to known Dronpa")
    print()
    print("Expected prediction time:")
    print("  Boltz-1: ~5-10 minutes on GPU")
    print("  AlphaFold 3: ~20-30 minutes")
    print()


if __name__ == "__main__":
    main()
