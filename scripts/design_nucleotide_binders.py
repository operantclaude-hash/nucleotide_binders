#!/usr/bin/env python3
"""
De novo nucleotide binder design pipeline using RFdiffusion3 and LigandMPNN.

This script provides a framework for designing proteins that specifically bind
dNTPs (dATP, dGTP, dCTP, dTTP) with high selectivity.

Pipeline:
1. Generate binding pocket backbones with RFdiffusion3/RFdiffusionAA
2. Design sequences with LigandMPNN
3. Validate with Boltz-2 or AlphaFold2
4. Score selectivity against all four nucleotides

Requirements:
- RFdiffusion3 or RFdiffusionAA (for backbone generation)
- LigandMPNN (for sequence design)
- Boltz-2 (for structure prediction and affinity)
- PyMOL or ChimeraX (for visualization)

Note: This script generates config files and commands. Actual execution
requires the respective tools to be installed (typically on a GPU cluster).

Usage:
    python design_nucleotide_binders.py --target dATP --num_designs 100
"""

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Nucleotide:
    """Nucleotide ligand information."""
    name: str
    full_name: str
    smiles: str
    ccd_code: str
    molecular_weight: float
    base_type: str  # purine or pyrimidine
    distinguishing_features: List[str]


# dNTP definitions
NUCLEOTIDES = {
    "dATP": Nucleotide(
        name="dATP",
        full_name="2'-deoxyadenosine triphosphate",
        smiles="Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3",
        ccd_code="DA",  # or ATP for the nucleotide
        molecular_weight=491.18,
        base_type="purine",
        distinguishing_features=[
            "6-amino group",
            "No carbonyl on base",
            "Fused bicyclic purine ring",
        ],
    ),
    "dGTP": Nucleotide(
        name="dGTP",
        full_name="2'-deoxyguanosine triphosphate",
        smiles="Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1",
        ccd_code="DG",
        molecular_weight=507.18,
        base_type="purine",
        distinguishing_features=[
            "2-amino group",
            "6-oxo (carbonyl) group",
            "Fused bicyclic purine ring",
        ],
    ),
    "dCTP": Nucleotide(
        name="dCTP",
        full_name="2'-deoxycytidine triphosphate",
        smiles="Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1",
        ccd_code="DC",
        molecular_weight=467.16,
        base_type="pyrimidine",
        distinguishing_features=[
            "4-amino group",
            "2-oxo group",
            "Single pyrimidine ring (smaller)",
        ],
    ),
    "dTTP": Nucleotide(
        name="dTTP",
        full_name="2'-deoxythymidine triphosphate",
        smiles="Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O",
        ccd_code="DT",
        molecular_weight=482.17,
        base_type="pyrimidine",
        distinguishing_features=[
            "5-methyl group (unique!)",
            "2,4-dioxo groups (no amino)",
            "Single pyrimidine ring",
        ],
    ),
}


def generate_rfdiffusion_config(
    target_nucleotide: str,
    num_designs: int = 100,
    output_dir: str = "rfdiffusion_output",
    protein_length: int = 120,  # Typical nanobody size
    pocket_distance: float = 6.0,
) -> Dict:
    """
    Generate RFdiffusion3/RFdiffusionAA configuration for nucleotide binder design.

    Returns:
        Dict containing config and command
    """
    nuc = NUCLEOTIDES[target_nucleotide]

    # RFdiffusion3 inference config
    config = {
        "inference": {
            "output_prefix": f"{output_dir}/{target_nucleotide}_binder",
            "num_designs": num_designs,
            "model_runner": "rfdiffusion_aa",  # or "rfdiffusion3"
        },
        "diffuser": {
            "T": 50,  # Diffusion steps
        },
        "contigmap": {
            # Generate a protein of specified length around the ligand
            "contigs": [f"0 {protein_length}-{protein_length}"],
        },
        "potentials": {
            # Encourage binding pocket formation
            "guide_scale": 2.0,
            "guide_decay": "quadratic",
        },
        "ligand": {
            "smiles": nuc.smiles,
            "name": nuc.name,
        },
    }

    # Command for RFdiffusion
    command = f"""# RFdiffusion command for {target_nucleotide} binder design
# Run on a GPU machine with RFdiffusion installed

python run_inference.py \\
    inference.output_prefix={output_dir}/{target_nucleotide}_binder \\
    inference.num_designs={num_designs} \\
    diffuser.T=50 \\
    'contigmap.contigs=[0 {protein_length}-{protein_length}]' \\
    potentials.guide_scale=2.0 \\
    ligand.smiles='{nuc.smiles}'
"""

    return {
        "config": config,
        "command": command,
        "nucleotide": nuc.__dict__,
    }


def generate_ligandmpnn_config(
    backbone_pdb: str,
    ligand_name: str,
    output_dir: str = "ligandmpnn_output",
    num_sequences: int = 8,
) -> Dict:
    """
    Generate LigandMPNN configuration for sequence design.
    """
    config = {
        "pdb_path": backbone_pdb,
        "out_folder": output_dir,
        "num_seq_per_target": num_sequences,
        "batch_size": 1,
        "ligand_mpnn_use_side_chain_context": 1,
        "model_type": "ligand_mpnn",
    }

    command = f"""# LigandMPNN sequence design
python run.py \\
    --pdb_path {backbone_pdb} \\
    --out_folder {output_dir} \\
    --num_seq_per_target {num_sequences} \\
    --ligand_mpnn_use_side_chain_context 1 \\
    --model_type ligand_mpnn
"""

    return {"config": config, "command": command}


def generate_boltz_selectivity_configs(
    designed_sequence: str,
    sequence_name: str,
    output_dir: str = "boltz_selectivity",
) -> List[Dict]:
    """
    Generate Boltz-2 configs to test binding against all four nucleotides.

    This enables negative design - ensuring selectivity for target nucleotide.
    """
    configs = []

    for nuc_name, nuc in NUCLEOTIDES.items():
        config = {
            "version": 1,
            "sequences": [
                {
                    "protein": {
                        "id": "A",
                        "sequence": designed_sequence,
                    }
                },
                {
                    "ligand": {
                        "id": "B",
                        "smiles": nuc.smiles,
                    }
                },
            ],
            "properties": {
                "affinity": {
                    "ligand": "B",
                    "protein": "A",
                }
            },
        }

        configs.append({
            "target_nucleotide": nuc_name,
            "config": config,
            "filename": f"{output_dir}/{sequence_name}_{nuc_name}.yaml",
        })

    return configs


def calculate_selectivity_score(affinities: Dict[str, float], target: str) -> Dict:
    """
    Calculate selectivity metrics from affinity predictions.

    Args:
        affinities: Dict of {nucleotide: predicted_affinity}
        target: The target nucleotide

    Returns:
        Dict with selectivity metrics
    """
    target_affinity = affinities[target]
    off_targets = {k: v for k, v in affinities.items() if k != target}

    # Higher affinity = lower Kd = tighter binding
    # For selectivity, we want target to bind tighter than off-targets

    selectivity_ratios = {}
    for off_target, off_affinity in off_targets.items():
        # Ratio > 1 means better binding to target
        if off_affinity != 0:
            selectivity_ratios[off_target] = target_affinity / off_affinity
        else:
            selectivity_ratios[off_target] = float("inf")

    return {
        "target": target,
        "target_affinity": target_affinity,
        "off_target_affinities": off_targets,
        "selectivity_ratios": selectivity_ratios,
        "min_selectivity": min(selectivity_ratios.values()),
        "passes_threshold": min(selectivity_ratios.values()) > 10,  # 10-fold selectivity
    }


def generate_design_pipeline_script(
    target_nucleotide: str,
    num_designs: int = 100,
    output_base: str = "nucleotide_design",
) -> str:
    """
    Generate a complete bash script for the design pipeline.
    """
    script = f"""#!/bin/bash
# Complete nucleotide binder design pipeline for {target_nucleotide}
# Generated by design_nucleotide_binders.py

set -e

TARGET="{target_nucleotide}"
NUM_DESIGNS={num_designs}
OUTPUT_DIR="{output_base}/$TARGET"

echo "=== Nucleotide Binder Design Pipeline ==="
echo "Target: $TARGET"
echo "Number of designs: $NUM_DESIGNS"
echo "Output: $OUTPUT_DIR"
echo ""

# Create directories
mkdir -p "$OUTPUT_DIR/rfdiffusion"
mkdir -p "$OUTPUT_DIR/ligandmpnn"
mkdir -p "$OUTPUT_DIR/boltz_validation"
mkdir -p "$OUTPUT_DIR/selectivity_screen"

# Step 1: Generate backbones with RFdiffusion
echo "Step 1: Generating binding pocket backbones..."
# Uncomment when RFdiffusion is installed:
# python $RFDIFFUSION_PATH/run_inference.py \\
#     inference.output_prefix="$OUTPUT_DIR/rfdiffusion/{target_nucleotide}_binder" \\
#     inference.num_designs=$NUM_DESIGNS \\
#     diffuser.T=50 \\
#     'contigmap.contigs=[0 120-120]' \\
#     potentials.guide_scale=2.0 \\
#     ligand.smiles='{NUCLEOTIDES[target_nucleotide].smiles}'

echo "  [PLACEHOLDER] RFdiffusion would generate $NUM_DESIGNS backbone structures"

# Step 2: Design sequences with LigandMPNN
echo ""
echo "Step 2: Designing sequences with LigandMPNN..."
# Uncomment when LigandMPNN is installed:
# for pdb in "$OUTPUT_DIR/rfdiffusion/"*.pdb; do
#     python $LIGANDMPNN_PATH/run.py \\
#         --pdb_path "$pdb" \\
#         --out_folder "$OUTPUT_DIR/ligandmpnn" \\
#         --num_seq_per_target 8 \\
#         --ligand_mpnn_use_side_chain_context 1
# done

echo "  [PLACEHOLDER] LigandMPNN would design 8 sequences per backbone"

# Step 3: Validate structures with Boltz-2
echo ""
echo "Step 3: Validating structures with Boltz-2..."
# Uncomment when Boltz is installed:
# boltz predict "$OUTPUT_DIR/boltz_validation/" --use_msa_server

echo "  [PLACEHOLDER] Boltz-2 would predict structures and affinities"

# Step 4: Selectivity screening
echo ""
echo "Step 4: Screening selectivity against off-target nucleotides..."
echo "  Testing binding to: dATP, dGTP, dCTP, dTTP"
echo "  [PLACEHOLDER] Would run Boltz-2 affinity prediction for each nucleotide"

# Step 5: Rank and filter designs
echo ""
echo "Step 5: Ranking designs by selectivity..."
echo "  Filtering for >10-fold selectivity over off-targets"

echo ""
echo "=== Pipeline Complete ==="
echo "Top designs will be in: $OUTPUT_DIR/top_designs/"
"""
    return script


def main():
    parser = argparse.ArgumentParser(
        description="Design nucleotide-specific binding proteins"
    )
    parser.add_argument(
        "--target",
        type=str,
        choices=list(NUCLEOTIDES.keys()),
        default="dATP",
        help="Target nucleotide to design binder for"
    )
    parser.add_argument(
        "--num_designs",
        type=int,
        default=100,
        help="Number of designs to generate"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="nucleotide_designs",
        help="Output directory"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate configs for all four nucleotides"
    )

    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    targets = list(NUCLEOTIDES.keys()) if args.all else [args.target]

    print("=" * 60)
    print("Nucleotide Binder Design Pipeline Generator")
    print("=" * 60)

    for target in targets:
        nuc = NUCLEOTIDES[target]
        target_dir = output_path / target
        target_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n--- {target} ({nuc.full_name}) ---")
        print(f"  Base type: {nuc.base_type}")
        print(f"  MW: {nuc.molecular_weight} Da")
        print(f"  Distinguishing features:")
        for feat in nuc.distinguishing_features:
            print(f"    - {feat}")

        # Generate RFdiffusion config
        rfd_config = generate_rfdiffusion_config(
            target,
            args.num_designs,
            str(target_dir / "rfdiffusion")
        )

        # Save config
        config_file = target_dir / f"{target}_rfdiffusion_config.json"
        with open(config_file, "w") as f:
            json.dump(rfd_config, f, indent=2)
        print(f"  RFdiffusion config: {config_file}")

        # Generate pipeline script
        pipeline_script = generate_design_pipeline_script(
            target,
            args.num_designs,
            str(output_path)
        )
        script_file = target_dir / f"run_{target}_pipeline.sh"
        with open(script_file, "w") as f:
            f.write(pipeline_script)
        os.chmod(script_file, 0o755)
        print(f"  Pipeline script: {script_file}")

    # Generate master script to run all
    if args.all:
        master_script = output_path / "run_all_pipelines.sh"
        with open(master_script, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Run all nucleotide binder design pipelines\n\n")
            for target in targets:
                f.write(f"echo '=== Running {target} pipeline ==='\n")
                f.write(f"bash {target}/run_{target}_pipeline.sh\n\n")
        os.chmod(master_script, 0o755)
        print(f"\nMaster script: {master_script}")

    print("\n" + "=" * 60)
    print("Configuration files generated!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install RFdiffusion3: https://github.com/RosettaCommons/RFdiffusion")
    print("2. Install LigandMPNN: https://github.com/dauparas/LigandMPNN")
    print("3. Install Boltz-2: pip install boltz[cuda]")
    print("4. Run the generated pipeline scripts on a GPU machine")
    print("\nAlternative (no local GPU):")
    print("- Use Tamarind.bio for RFdiffusion3: https://www.tamarind.bio/tools/rfdiffusion3")
    print("- Use ColabFold for structure validation")


if __name__ == "__main__":
    main()
