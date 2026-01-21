#!/usr/bin/env python3
"""
Generate MSAs for all variants in the specificity library.
Creates minimal MSAs (query-only) for rapid predictions.
"""

import yaml
from pathlib import Path
import argparse
from tqdm import tqdm


def read_variant_sequences(manifest_file):
    """Extract all unique variant sequences from library manifest."""
    with open(manifest_file, 'r') as f:
        manifest = yaml.safe_load(f)

    sequences = {}
    for variant in manifest['variants']:
        sequences[variant['id']] = variant['sequence']

    return sequences


def create_minimal_msa(sequence, output_file, seq_id="A"):
    """Create a minimal MSA file (A3M format) with just the query sequence."""
    with open(output_file, 'w') as f:
        f.write(f">{seq_id}\n")
        f.write(f"{sequence}\n")


def generate_msas_for_library(library_dir, msa_output_dir):
    """Generate MSAs for all variants in the library."""

    library_path = Path(library_dir)
    manifest_file = library_path / "library_manifest.yaml"

    if not manifest_file.exists():
        print(f"ERROR: Manifest not found: {manifest_file}")
        print("Run generate_cdr_library.py first!")
        return

    print("="*80)
    print("GENERATING MSAs FOR SPECIFICITY LIBRARY")
    print("="*80)
    print()

    # Read variant sequences
    print("Loading library manifest...")
    sequences = read_variant_sequences(manifest_file)
    print(f"Found {len(sequences)} unique variants\n")

    # Create output directory
    msa_dir = Path(msa_output_dir)
    msa_dir.mkdir(parents=True, exist_ok=True)

    # Generate MSAs
    print("Generating minimal MSAs...")
    for variant_id, sequence in tqdm(sequences.items(), desc="Creating MSAs"):
        variant_msa_dir = msa_dir / variant_id
        variant_msa_dir.mkdir(parents=True, exist_ok=True)

        msa_file = variant_msa_dir / "A.a3m"
        create_minimal_msa(sequence, msa_file, "A")

    print(f"\n✓ Generated {len(sequences)} MSAs")
    print(f"✓ Saved to: {msa_dir}\n")

    # Update configs with MSA paths
    print("Updating config files with MSA paths...")
    configs_dir = library_path / "configs"
    configs_with_msas_dir = library_path / "configs_with_msas"
    configs_with_msas_dir.mkdir(parents=True, exist_ok=True)

    config_files = list(configs_dir.glob("*.yaml"))
    print(f"Found {len(config_files)} config files")

    updated_count = 0
    for config_file in tqdm(config_files, desc="Updating configs"):
        # Extract variant ID from config name
        # Format: {variant_id}_vs_{nucleotide}.yaml
        config_name = config_file.stem
        variant_id = "_".join(config_name.split("_vs_")[0].split("_"))

        # Find the full variant ID that matches
        matching_variant = None
        for vid in sequences.keys():
            if vid.startswith(variant_id) or variant_id in vid:
                matching_variant = vid
                break

        if not matching_variant:
            print(f"Warning: Could not find variant for {config_name}")
            continue

        # Read original config
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Add MSA path
        msa_file = msa_dir / matching_variant / "A.a3m"
        if msa_file.exists():
            for seq in config_data['sequences']:
                if 'protein' in seq:
                    seq['protein']['msa'] = str(msa_file.resolve())

            # Save updated config
            output_file = configs_with_msas_dir / config_file.name
            with open(output_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

            updated_count += 1

    print(f"\n✓ Updated {updated_count} config files")
    print(f"✓ Saved to: {configs_with_msas_dir}\n")

    print("="*80)
    print("MSA GENERATION COMPLETE")
    print("="*80)
    print()
    print("Next step: Run batch predictions")
    print("  python run_specificity_screen.py")


def main():
    parser = argparse.ArgumentParser(
        description="Generate MSAs for specificity library"
    )
    parser.add_argument(
        "--library-dir",
        default="../specificity_library",
        help="Library directory containing manifest"
    )
    parser.add_argument(
        "--msa-output-dir",
        default="../specificity_library/msas",
        help="Output directory for MSAs"
    )

    args = parser.parse_args()

    generate_msas_for_library(args.library_dir, args.msa_output_dir)


if __name__ == "__main__":
    main()
