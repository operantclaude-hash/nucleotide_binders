#!/usr/bin/env python3
"""
Update Boltz YAML configs to include MSA paths.
"""

import yaml
from pathlib import Path
import shutil


def update_config_with_msa(config_file, msa_dir, output_dir):
    """Update a config file to include MSA paths."""

    config_path = Path(config_file)
    msa_path = Path(msa_dir)
    output_path = Path(output_dir)

    # Read original config
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)

    # Extract config name
    config_name = config_path.stem
    config_msa_dir = msa_path / config_name

    if not config_msa_dir.exists():
        print(f"  WARNING: MSA directory not found: {config_msa_dir}")
        return None

    # Add MSA paths to protein sequences
    modified = False
    for seq in data.get('sequences', []):
        if 'protein' in seq:
            chain_id = seq['protein']['id']
            msa_file = config_msa_dir / f"{chain_id}.a3m"

            if msa_file.exists():
                seq['protein']['msa'] = str(msa_file.resolve())
                modified = True
                print(f"    Added MSA for chain {chain_id}: {msa_file}")
            else:
                print(f"    WARNING: MSA file not found for chain {chain_id}")

    if modified:
        # Save updated config
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / config_path.name

        with open(output_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        print(f"  ✓ Updated config saved: {output_file}")
        return str(output_file)
    else:
        print(f"  No modifications made")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Update Boltz configs with MSA paths"
    )
    parser.add_argument(
        "--config-dir",
        default="../configs",
        help="Directory containing original Boltz YAML configs"
    )
    parser.add_argument(
        "--msa-dir",
        default="../msas",
        help="Directory containing generated MSAs"
    )
    parser.add_argument(
        "--output-dir",
        default="../configs_with_msas",
        help="Output directory for updated configs"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Updating Boltz Configs with MSA Paths")
    print("=" * 80)

    # Find all YAML configs
    config_dir = Path(args.config_dir)
    configs = list(config_dir.glob("*.yaml"))

    if not configs:
        print(f"\nNo YAML configs found in {config_dir}")
        return

    print(f"\nFound {len(configs)} config file(s)\n")

    # Process each config
    updated = []
    for config_file in configs:
        print(f"Processing: {config_file.name}")
        result = update_config_with_msa(
            config_file,
            args.msa_dir,
            args.output_dir
        )
        if result:
            updated.append(result)
        print()

    print("=" * 80)
    print(f"Updated {len(updated)} config file(s)")
    print("=" * 80)
    print(f"\nUpdated configs saved to: {args.output_dir}")
    print("\nYou can now run Boltz predictions:")
    print(f"  cd ~/nucleotide_catchers")
    print(f"  boltz predict {args.output_dir}/dATP_binder.yaml --out_dir results/dATP")


if __name__ == "__main__":
    main()
