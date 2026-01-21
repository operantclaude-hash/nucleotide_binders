#!/usr/bin/env python3
"""
Utility script to insert optogenetic domains into custom nanobody sequences.
Usage: python insert_custom_optogenetic.py --sequence YOUR_SEQUENCE --domain LOV2 --position 74
"""

import argparse
import sys
import os

# Add parent directory to path to import from insert_optogenetic_domains
sys.path.insert(0, os.path.dirname(__file__))
from insert_optogenetic_domains import OPTOGENETIC_DOMAINS, insert_domain


def main():
    parser = argparse.ArgumentParser(
        description="Insert optogenetic domains into custom nanobody sequences"
    )
    parser.add_argument(
        "--sequence", "-s",
        required=True,
        help="Nanobody sequence (amino acid sequence)"
    )
    parser.add_argument(
        "--domain", "-d",
        required=True,
        choices=list(OPTOGENETIC_DOMAINS.keys()),
        help="Optogenetic domain to insert (LOV2, CRY2, or BphP1)"
    )
    parser.add_argument(
        "--position", "-p",
        type=int,
        default=74,
        help="Insertion position (0-indexed, default: 74)"
    )
    parser.add_argument(
        "--linker", "-l",
        default="GSGSGSG",
        help="Linker sequence (default: GSGSGSG)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output FASTA file (optional)"
    )
    parser.add_argument(
        "--name", "-n",
        default="custom_nanobody",
        help="Name for the construct (default: custom_nanobody)"
    )

    args = parser.parse_args()

    # Validate sequence
    sequence = args.sequence.upper().replace(" ", "").replace("\n", "")
    valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
    if not all(aa in valid_aa for aa in sequence):
        print("ERROR: Invalid amino acid characters in sequence", file=sys.stderr)
        sys.exit(1)

    # Check position
    if args.position < 0 or args.position > len(sequence):
        print(f"ERROR: Position {args.position} out of range (0-{len(sequence)})",
              file=sys.stderr)
        sys.exit(1)

    # Perform insertion
    domain_seq = OPTOGENETIC_DOMAINS[args.domain]
    result = insert_domain(
        sequence,
        domain_seq,
        args.domain,
        position=args.position,
        linker=args.linker
    )

    # Print results
    print(f"\n{'='*80}")
    print(f"OPTOGENETIC DOMAIN INSERTION")
    print(f"{'='*80}\n")
    print(f"Domain: {args.domain}")
    print(f"Insertion Position: {args.position}")
    print(f"Linker: {args.linker}")
    print(f"Original Length: {len(sequence)} aa")
    print(f"Domain Length: {result['domain_length']} aa")
    print(f"Chimeric Length: {result['chimeric_length']} aa")
    print(f"\nChimeric Sequence:")
    print(f"{result['full_sequence']}\n")

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            header = (f">{args.name}_{args.domain}_chimera "
                     f"pos={args.position} length={result['chimeric_length']}")
            f.write(f"{header}\n")

            seq = result['full_sequence']
            for i in range(0, len(seq), 80):
                f.write(f"{seq[i:i+80]}\n")

        print(f"✓ Saved to: {args.output}\n")


if __name__ == "__main__":
    main()
