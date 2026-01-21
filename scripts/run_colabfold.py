#!/usr/bin/env python3
"""
Generate ColabFold input files and instructions for chimera structure prediction.

This script prepares sequences for structure prediction using:
1. ColabFold (Google Colab notebook - easiest)
2. Local ColabFold installation
3. AlphaFold2 Multimer for complexes

Usage:
    python run_colabfold.py --input chimeras.fasta --output colabfold_batch/
"""

import argparse
import os
from pathlib import Path
from typing import Dict, List


# ColabFold notebook URLs
COLABFOLD_NOTEBOOKS = {
    "alphafold2": "https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb",
    "esmfold": "https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/ESMFold.ipynb",
    "batch": "https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb",
}


def create_colabfold_batch_file(sequences: Dict[str, str], output_path: str):
    """
    Create a CSV file for ColabFold batch submission.

    Args:
        sequences: Dict of {name: sequence}
        output_path: Path to output CSV file
    """
    with open(output_path, "w") as f:
        f.write("id,sequence\n")
        for name, seq in sequences.items():
            # Clean sequence - remove spaces and newlines
            clean_seq = "".join(seq.split())
            f.write(f"{name},{clean_seq}\n")


def create_fasta_file(sequences: Dict[str, str], output_path: str):
    """Create a FASTA file from sequences."""
    with open(output_path, "w") as f:
        for name, seq in sequences.items():
            clean_seq = "".join(seq.split())
            f.write(f">{name}\n")
            # Write in 60-character lines
            for i in range(0, len(clean_seq), 60):
                f.write(clean_seq[i:i + 60] + "\n")


def generate_local_colabfold_script(
    fasta_path: str,
    output_dir: str,
    use_gpu: bool = True,
    num_recycle: int = 3,
    num_models: int = 5
) -> str:
    """
    Generate a bash script for running local ColabFold.

    Returns:
        Bash script content
    """
    gpu_flag = "" if use_gpu else "--cpu"

    script = f"""#!/bin/bash
# Local ColabFold structure prediction script
# Requires: colabfold_batch installed (pip install colabfold)

set -e

INPUT_FASTA="{fasta_path}"
OUTPUT_DIR="{output_dir}"
NUM_RECYCLE={num_recycle}
NUM_MODELS={num_models}

echo "=== ColabFold Structure Prediction ==="
echo "Input: $INPUT_FASTA"
echo "Output: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run ColabFold
colabfold_batch \\
    {gpu_flag} \\
    --num-recycle $NUM_RECYCLE \\
    --num-models $NUM_MODELS \\
    --amber \\
    --use-gpu-relax \\
    "$INPUT_FASTA" \\
    "$OUTPUT_DIR"

echo ""
echo "=== Prediction Complete ==="
echo "Results in: $OUTPUT_DIR"
echo ""
echo "Output files:"
echo "  - *_relaxed_rank_001.pdb  (best model)"
echo "  - *_scores_rank_001.json  (confidence scores)"
echo "  - *_coverage.png          (MSA coverage)"
echo "  - *_plddt.png             (per-residue confidence)"
"""
    return script


def generate_colab_instructions(sequences: Dict[str, str]) -> str:
    """Generate instructions for using Google Colab."""
    instructions = """
# ColabFold Instructions for Chimera Structure Prediction

## Option 1: Google Colab (Easiest - No Installation)

1. Open the ColabFold notebook:
   https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb

2. In the "query_sequence" field, paste ONE of the sequences below

3. Set parameters:
   - num_recycles: 3 (or more for complex structures)
   - use_amber: True (for relaxed structures)
   - num_models: 5

4. Run all cells

5. Download the results (PDB files, confidence plots)

## Option 2: ColabFold Batch (Multiple Sequences)

1. Open batch notebook:
   https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb

2. Upload the generated CSV file (colabfold_batch.csv)

3. Run all cells

## Option 3: Local ColabFold Installation

```bash
# Install ColabFold locally
pip install colabfold

# Download model weights (one-time, ~10GB)
python -m colabfold.download

# Run prediction
colabfold_batch input.fasta output_dir/
```

## Sequences for Prediction

"""

    for name, seq in sequences.items():
        clean_seq = "".join(seq.split())
        instructions += f"### {name}\n"
        instructions += f"Length: {len(clean_seq)} amino acids\n"
        instructions += f"```\n{clean_seq}\n```\n\n"

    return instructions


def prepare_chimera_predictions(
    chimera_sequences: Dict[str, str],
    output_dir: str
) -> Dict[str, str]:
    """
    Prepare all files needed for chimera structure prediction.

    Args:
        chimera_sequences: Dict of {name: sequence}
        output_dir: Output directory path

    Returns:
        Dict of created file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    created_files = {}

    # Create FASTA file
    fasta_path = output_path / "chimeras.fasta"
    create_fasta_file(chimera_sequences, str(fasta_path))
    created_files["fasta"] = str(fasta_path)

    # Create ColabFold batch CSV
    csv_path = output_path / "colabfold_batch.csv"
    create_colabfold_batch_file(chimera_sequences, str(csv_path))
    created_files["csv"] = str(csv_path)

    # Generate local run script
    script_content = generate_local_colabfold_script(
        str(fasta_path),
        str(output_path / "predictions")
    )
    script_path = output_path / "run_local_colabfold.sh"
    with open(script_path, "w") as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)
    created_files["script"] = str(script_path)

    # Generate instructions
    instructions = generate_colab_instructions(chimera_sequences)
    instructions_path = output_path / "COLABFOLD_INSTRUCTIONS.md"
    with open(instructions_path, "w") as f:
        f.write(instructions)
    created_files["instructions"] = str(instructions_path)

    return created_files


# Example chimera sequences (using placeholder nanobody + LOV2)
EXAMPLE_CHIMERAS = {
    "A_catcher_LOV2_loop6": (
        # Example: Nanobody FR1-CDR1-FR2-CDR2-FR3(partial)
        "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTY"
        "YADSVKGRFTISRDNSKN"
        # Linker
        "GSGSGSG"
        # AsLOV2 (408-543)
        "GLTELLNALLPGHQDGAAFRRVTELLSQLVNFTQSRVLGAAIAASDALALGEATGGAAAE"
        "GVVAPTETSPAFMQGVLKGGANATASILDLRDIAGQLVVGNDDGTEIPGPWGRCNPFSSR"
        "LFVELEGVPDHQQPNFRATLA"
        # Linker
        "GSGSGSG"
        # Nanobody FR3(rest)-CDR3-FR4
        "TLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGLDVWGQGTLVTVSS"
    ),
}


def main():
    parser = argparse.ArgumentParser(
        description="Prepare ColabFold inputs for chimera structure prediction"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Input FASTA file with chimera sequences"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="colabfold_output",
        help="Output directory"
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Generate example files"
    )

    args = parser.parse_args()

    if args.example or not args.input:
        print("Generating example ColabFold input files...")
        sequences = EXAMPLE_CHIMERAS
    else:
        # Parse input FASTA
        sequences = {}
        current_name = None
        current_seq = []

        with open(args.input) as f:
            for line in f:
                line = line.strip()
                if line.startswith(">"):
                    if current_name:
                        sequences[current_name] = "".join(current_seq)
                    current_name = line[1:].split()[0]
                    current_seq = []
                elif line:
                    current_seq.append(line)

            if current_name:
                sequences[current_name] = "".join(current_seq)

    # Prepare all files
    created = prepare_chimera_predictions(sequences, args.output)

    print("\n" + "=" * 60)
    print("ColabFold Input Files Generated")
    print("=" * 60)
    print(f"\nCreated files:")
    for file_type, path in created.items():
        print(f"  - {file_type}: {path}")

    print(f"\nNext steps:")
    print(f"  1. Read: {created['instructions']}")
    print(f"  2. Use Google Colab: Upload {created['csv']}")
    print(f"  3. Or run locally: bash {created['script']}")


if __name__ == "__main__":
    main()
