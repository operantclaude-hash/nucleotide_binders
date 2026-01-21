#!/usr/bin/env python3
"""
Generate MSAs for nanobody sequences using MMseqs2 against UniRef30.
This script creates MSA files that Boltz can use for predictions.
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path


def read_yaml_sequences(yaml_file):
    """Extract protein sequences from Boltz YAML config."""
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    proteins = []
    for seq in data.get('sequences', []):
        if 'protein' in seq:
            proteins.append({
                'id': seq['protein']['id'],
                'sequence': seq['protein']['sequence']
            })

    return proteins


def create_fasta(sequence, output_file, seq_id="query"):
    """Create a FASTA file from a sequence."""
    with open(output_file, 'w') as f:
        f.write(f">{seq_id}\n")
        # Write sequence in 80-character lines
        for i in range(0, len(sequence), 80):
            f.write(f"{sequence[i:i+80]}\n")


def create_minimal_msa(sequence, output_file, seq_id="query"):
    """
    Create a minimal MSA file (A3M format) with just the query sequence.
    This is sufficient for Boltz to run predictions.
    """
    with open(output_file, 'w') as f:
        f.write(f">{seq_id}\n")
        f.write(f"{sequence}\n")

    print(f"  Created minimal MSA: {output_file}")


def run_mmseqs_search(fasta_file, db_path, output_dir, threads=8):
    """
    Run MMseqs2 search against a database.
    NOTE: This requires a pre-downloaded database (e.g., UniRef30, ColabFold).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create MMseqs2 database from query
    query_db = output_dir / "query_db"
    result_db = output_dir / "result_db"
    msa_db = output_dir / "msa_db"

    try:
        # Create query database
        subprocess.run([
            "mmseqs", "createdb",
            str(fasta_file),
            str(query_db)
        ], check=True, capture_output=True)

        # Search against database
        subprocess.run([
            "mmseqs", "search",
            str(query_db),
            str(db_path),
            str(result_db),
            str(output_dir / "tmp"),
            "--threads", str(threads),
            "-e", "0.001",
            "--max-seqs", "1000"
        ], check=True, capture_output=True)

        # Convert to MSA format
        subprocess.run([
            "mmseqs", "result2msa",
            str(query_db),
            str(db_path),
            str(result_db),
            str(msa_db)
        ], check=True, capture_output=True)

        # Convert to A3M format
        output_a3m = output_dir / "query.a3m"
        subprocess.run([
            "mmseqs", "convertmsa",
            str(msa_db),
            str(output_a3m),
            "--format", "a3m"
        ], check=True, capture_output=True)

        print(f"  Generated MSA with MMseqs2: {output_a3m}")
        return str(output_a3m)

    except subprocess.CalledProcessError as e:
        print(f"  MMseqs2 search failed: {e}")
        print(f"  Falling back to minimal MSA")
        return None


def process_config(config_file, output_dir, use_mmseqs=False, db_path=None):
    """Process a single Boltz config and generate MSAs."""
    config_name = Path(config_file).stem
    print(f"\nProcessing: {config_name}")

    # Read sequences
    proteins = read_yaml_sequences(config_file)

    if not proteins:
        print(f"  No protein sequences found in {config_file}")
        return

    # Create output directory for this config
    msa_dir = Path(output_dir) / config_name
    msa_dir.mkdir(parents=True, exist_ok=True)

    # Generate MSA for each protein
    for protein in proteins:
        seq_id = protein['id']
        sequence = protein['sequence']

        print(f"  Processing chain {seq_id}: {len(sequence)} aa")

        # Create FASTA file
        fasta_file = msa_dir / f"{seq_id}.fasta"
        create_fasta(sequence, fasta_file, seq_id)

        # Generate MSA
        msa_file = msa_dir / f"{seq_id}.a3m"

        if use_mmseqs and db_path and os.path.exists(db_path):
            # Try MMseqs2 search
            result = run_mmseqs_search(fasta_file, db_path, msa_dir)
            if result:
                # Rename to expected filename
                os.rename(result, msa_file)
            else:
                # Fall back to minimal MSA
                create_minimal_msa(sequence, msa_file, seq_id)
        else:
            # Create minimal MSA (just the query sequence)
            create_minimal_msa(sequence, msa_file, seq_id)

    print(f"  ✓ MSAs saved to: {msa_dir}")
    return str(msa_dir)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate MSAs for Boltz predictions"
    )
    parser.add_argument(
        "--config-dir",
        default="../configs",
        help="Directory containing Boltz YAML configs"
    )
    parser.add_argument(
        "--output-dir",
        default="../msas",
        help="Output directory for MSAs"
    )
    parser.add_argument(
        "--use-mmseqs",
        action="store_true",
        help="Use MMseqs2 for full MSA generation (requires database)"
    )
    parser.add_argument(
        "--db-path",
        help="Path to MMseqs2 database (e.g., UniRef30)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("MSA Generation for Nucleotide Binder Design")
    print("=" * 80)

    # Check if using MMseqs2
    if args.use_mmseqs:
        if not args.db_path:
            print("\nERROR: --db-path required when using --use-mmseqs")
            sys.exit(1)
        if not os.path.exists(args.db_path):
            print(f"\nERROR: Database not found: {args.db_path}")
            print("\nTo download ColabFold databases:")
            print("  bash setup_databases.sh /path/to/databases")
            sys.exit(1)
        print(f"\nUsing MMseqs2 with database: {args.db_path}")
    else:
        print("\nCreating minimal MSAs (query-only)")
        print("Note: For better predictions, use --use-mmseqs with a sequence database")

    # Find all YAML configs
    config_dir = Path(args.config_dir)
    configs = list(config_dir.glob("*.yaml"))

    if not configs:
        print(f"\nNo YAML configs found in {config_dir}")
        sys.exit(1)

    print(f"\nFound {len(configs)} config file(s)")

    # Process each config
    for config_file in configs:
        process_config(
            config_file,
            args.output_dir,
            use_mmseqs=args.use_mmseqs,
            db_path=args.db_path
        )

    print("\n" + "=" * 80)
    print("MSA generation complete!")
    print("=" * 80)
    print(f"\nMSAs saved to: {args.output_dir}")
    print("\nNext steps:")
    print("1. Update Boltz configs to include MSA paths, OR")
    print("2. Run Boltz predictions without --use_msa_server")
    print("\nFor minimal MSAs (created by default):")
    print("  Boltz can run but predictions may be less accurate")
    print("\nFor better predictions:")
    print("  Download sequence databases and run with --use-mmseqs")


if __name__ == "__main__":
    main()
