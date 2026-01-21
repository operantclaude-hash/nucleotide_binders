#!/usr/bin/env python3
"""
Generate a library of nanobody CDR variants designed for nucleotide-specific binding.

This script creates rational mutations in CDR regions (especially CDR3) to enhance
specificity for individual nucleotides (dATP, dGTP, dCTP, dTTP).

Strategy:
- Adenine (A): Design for 6-amino group recognition, purine size
- Guanine (G): Design for 6-keto + N1-H recognition, purine size
- Cytosine (C): Design for 4-amino + pyrimidine size
- Thymine (T): Design for 5-methyl + 4-keto, pyrimidine size
"""

import argparse
import random
from pathlib import Path
from typing import List, Dict
import yaml


# Base nanobody scaffold (VHH framework)
BASE_NANOBODY = "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS"

# CDR regions (0-indexed positions)
CDR_REGIONS = {
    "CDR1": (26, 35),   # GFTFSSYAMS
    "CDR2": (50, 58),   # AISGSGGSTY
    "CDR3": (95, 102),  # VSYLSTAS (most important for specificity)
}


# Amino acid groups for rational design
AA_GROUPS = {
    # Polar/H-bond donors (for keto/amino groups)
    "polar_positive": ["K", "R", "H"],      # For phosphate coordination
    "polar_neutral": ["N", "Q", "S", "T"],  # For H-bonding to bases
    "polar_negative": ["D", "E"],           # For amino group recognition

    # Aromatic (for pi-stacking with bases)
    "aromatic": ["F", "Y", "W"],            # Pi-stacking, hydrophobic

    # Hydrophobic (for pyrimidine/purine selectivity)
    "hydrophobic_small": ["A", "V", "I", "L"],  # Size selectivity
    "hydrophobic_large": ["M", "F", "W"],       # Purine-specific pocket

    # Small/flexible
    "small": ["G", "A", "S"],  # Pocket flexibility
}


# Nucleotide-specific design strategies
DESIGN_STRATEGIES = {
    "dATP": {
        "target": "Adenine - 6-amino group, purine",
        "CDR3_mutations": {
            # Position: preferred amino acids
            95: ["N", "Q", "S"],  # H-bond acceptor for 6-amino
            96: ["Y", "F", "W"],  # Aromatic stacking
            97: ["R", "K"],       # Phosphate coordination
            98: ["L", "I", "V"],  # Hydrophobic for purine
            99: ["S", "T", "N"],  # Additional H-bonding
            100: ["D", "E"],      # Negative charge near amino group
        },
        "rationale": "Target 6-amino group (unique to A) with H-bond acceptors (N,Q,S). Use aromatics for stacking. Accommodate purine size."
    },

    "dGTP": {
        "target": "Guanine - 6-keto, N1-H donor, purine",
        "CDR3_mutations": {
            95: ["Q", "N", "T"],  # H-bond donor for 6-keto
            96: ["F", "Y", "W"],  # Aromatic stacking
            97: ["K", "R"],       # Phosphate coordination
            98: ["I", "L", "M"],  # Hydrophobic for purine
            99: ["N", "Q", "S"],  # H-bond network
            100: ["S", "T"],      # Neutral H-bonding
        },
        "rationale": "Target 6-keto (unique to G) with H-bond donors (N,Q). Recognize N1-H. Purine-sized pocket."
    },

    "dCTP": {
        "target": "Cytosine - 4-amino, pyrimidine (smaller)",
        "CDR3_mutations": {
            95: ["S", "T", "N"],  # H-bond for 4-amino
            96: ["F", "Y"],       # Aromatic stacking (smaller)
            97: ["R", "K", "H"],  # Phosphate coordination
            98: ["A", "V"],       # Smaller pocket for pyrimidine
            99: ["Q", "N"],       # H-bonding
            100: ["D", "E"],      # Negative for amino group
        },
        "rationale": "Tighter pocket for smaller pyrimidine. Target 4-amino with H-bond acceptors. Exclude purines by size."
    },

    "dTTP": {
        "target": "Thymine - 5-methyl, 4-keto, pyrimidine",
        "CDR3_mutations": {
            95: ["Q", "N", "T"],  # H-bond donor for 4-keto
            96: ["F", "Y"],       # Aromatic stacking
            97: ["K", "R"],       # Phosphate coordination
            98: ["V", "I", "L"],  # Hydrophobic pocket for 5-methyl
            99: ["A", "G"],       # Small, allow methyl group
            100: ["S", "T"],      # Neutral H-bonding
        },
        "rationale": "Hydrophobic pocket for 5-methyl group (unique to T). H-bond donor for 4-keto. Pyrimidine-sized pocket."
    }
}


def generate_variants(base_seq: str, target_nucleotide: str, num_variants: int = 20) -> List[Dict]:
    """
    Generate CDR variants optimized for specific nucleotide.

    Args:
        base_seq: Base nanobody sequence
        target_nucleotide: dATP, dGTP, dCTP, or dTTP
        num_variants: Number of variants to generate

    Returns:
        List of variant dictionaries with sequence and metadata
    """
    if target_nucleotide not in DESIGN_STRATEGIES:
        raise ValueError(f"Unknown nucleotide: {target_nucleotide}")

    strategy = DESIGN_STRATEGIES[target_nucleotide]
    mutations = strategy["CDR3_mutations"]

    variants = []

    # Always include the wild-type as variant 0
    variants.append({
        "id": f"{target_nucleotide}_variant_000_WT",
        "sequence": base_seq,
        "mutations": "WT",
        "target": target_nucleotide,
        "strategy": "Wild-type control"
    })

    # Generate rational variants
    for i in range(1, num_variants):
        seq_list = list(base_seq)
        mutation_list = []

        # Apply mutations at CDR3 positions
        for pos, aa_options in mutations.items():
            if random.random() < 0.6:  # 60% chance to mutate each position
                original_aa = base_seq[pos]
                new_aa = random.choice(aa_options)

                if new_aa != original_aa:
                    seq_list[pos] = new_aa
                    mutation_list.append(f"{original_aa}{pos+1}{new_aa}")

        # Only add if we made at least one mutation
        if mutation_list:
            variant_seq = "".join(seq_list)
            variants.append({
                "id": f"{target_nucleotide}_variant_{i:03d}",
                "sequence": variant_seq,
                "mutations": ",".join(mutation_list),
                "target": target_nucleotide,
                "strategy": strategy["rationale"]
            })

    return variants


def create_config_files(variants: List[Dict], nucleotides: Dict[str, str], output_dir: Path):
    """
    Create Boltz config files for all variant-nucleotide combinations.

    Args:
        variants: List of variant dictionaries
        nucleotides: Dict of nucleotide SMILES strings
        output_dir: Output directory for configs
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    configs_created = []

    for variant in variants:
        variant_id = variant["id"]
        target_nuc = variant["target"]

        # Test this variant against ALL nucleotides
        for nuc_name, nuc_smiles in nucleotides.items():
            config_name = f"{variant_id}_vs_{nuc_name}"
            config_file = output_dir / f"{config_name}.yaml"

            config_data = {
                "version": 1,
                "sequences": [
                    {
                        "protein": {
                            "id": "A",
                            "sequence": variant["sequence"]
                        }
                    },
                    {
                        "ligand": {
                            "id": "B",
                            "smiles": nuc_smiles
                        }
                    }
                ]
            }

            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

            configs_created.append({
                "config_file": str(config_file),
                "variant_id": variant_id,
                "target_nucleotide": target_nuc,
                "test_nucleotide": nuc_name,
                "mutations": variant["mutations"],
                "is_target": (nuc_name == target_nuc)
            })

    return configs_created


def save_library_manifest(variants: List[Dict], configs: List[Dict], output_dir: Path):
    """Save library manifest with all variants and configs."""

    manifest = {
        "library_size": len(variants),
        "total_predictions": len(configs),
        "nucleotides": ["dATP", "dGTP", "dCTP", "dTTP"],
        "variants": variants,
        "configs": configs,
        "design_strategies": DESIGN_STRATEGIES
    }

    manifest_file = output_dir / "library_manifest.yaml"
    with open(manifest_file, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Library manifest saved: {manifest_file}")

    # Also save a human-readable summary
    summary_file = output_dir / "library_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("NUCLEOTIDE-SPECIFIC NANOBODY LIBRARY\n")
        f.write("="*80 + "\n\n")

        f.write(f"Total variants: {len(variants)}\n")
        f.write(f"Total predictions: {len(configs)}\n")
        f.write(f"Predictions per variant: 4 (all nucleotides)\n\n")

        # Group by target nucleotide
        for nuc in ["dATP", "dGTP", "dCTP", "dTTP"]:
            nuc_variants = [v for v in variants if v["target"] == nuc]
            f.write(f"\n{nuc} Variants: {len(nuc_variants)}\n")
            f.write("-"*80 + "\n")
            f.write(f"Strategy: {DESIGN_STRATEGIES[nuc]['rationale']}\n\n")

            for v in nuc_variants[:5]:  # Show first 5
                f.write(f"  {v['id']}: {v['mutations']}\n")

            if len(nuc_variants) > 5:
                f.write(f"  ... and {len(nuc_variants)-5} more\n")

    print(f"✓ Library summary saved: {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate nucleotide-specific nanobody CDR library"
    )
    parser.add_argument(
        "--variants-per-target",
        type=int,
        default=20,
        help="Number of variants per nucleotide (default: 20)"
    )
    parser.add_argument(
        "--output-dir",
        default="../specificity_library",
        help="Output directory for library and configs"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    if args.seed:
        random.seed(args.seed)
        print(f"Using random seed: {args.seed}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("NUCLEOTIDE-SPECIFIC NANOBODY LIBRARY GENERATOR")
    print("="*80)
    print()

    # Nucleotide SMILES
    nucleotides = {
        "dATP": "Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3",
        "dGTP": "Nc1nc2c(ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3)c(=O)[nH]1",
        "dCTP": "Nc1ccn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)n1",
        "dTTP": "Cc1cn([C@H]2C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O2)c(=O)[nH]c1=O"
    }

    # Generate variants for each nucleotide
    all_variants = []
    for nuc in ["dATP", "dGTP", "dCTP", "dTTP"]:
        print(f"\nGenerating {args.variants_per_target} variants for {nuc}...")
        print(f"  Strategy: {DESIGN_STRATEGIES[nuc]['rationale']}")

        variants = generate_variants(BASE_NANOBODY, nuc, args.variants_per_target)
        all_variants.extend(variants)
        print(f"  ✓ Generated {len(variants)} variants")

    print(f"\n{'='*80}")
    print(f"Total variants: {len(all_variants)}")
    print(f"{'='*80}\n")

    # Create config files for all combinations
    print("Creating Boltz config files...")
    configs_dir = output_dir / "configs"
    configs = create_config_files(all_variants, nucleotides, configs_dir)
    print(f"✓ Created {len(configs)} config files\n")

    # Save manifest
    print("Saving library manifest...")
    save_library_manifest(all_variants, configs, output_dir)

    print(f"\n{'='*80}")
    print("LIBRARY GENERATION COMPLETE")
    print(f"{'='*80}\n")
    print(f"Output directory: {output_dir}")
    print(f"Total variants: {len(all_variants)}")
    print(f"Total predictions needed: {len(configs)}")
    print(f"  (Each variant tested against all 4 nucleotides)\n")

    print("Next steps:")
    print(f"1. Generate MSAs for all variants:")
    print(f"   cd scripts && python generate_library_msas.py")
    print(f"2. Run batch predictions:")
    print(f"   cd scripts && python run_specificity_screen.py")
    print(f"3. Analyze specificity:")
    print(f"   cd scripts && python analyze_specificity.py")


if __name__ == "__main__":
    main()
