#!/usr/bin/env python3
"""
Insert optogenetic domains into nanobody sequences at specific loop positions.

This script generates chimera sequences for optogenetically-controlled nanobodies
following the OptoNB/Sunbody/Moonbody design principles.

Usage:
    python insert_optodomain.py --nanobody SEQUENCE --domain LOV2 --site loop6
"""

import argparse
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class OptoDomain:
    """Optogenetic domain sequences and properties."""
    name: str
    sequence: str
    activation_wavelength: str
    deactivation: str
    chromophore: str
    size_aa: int


# Optogenetic domain sequences
# AsLOV2 (short version, residues 408-543 of Avena sativa Phototropin 1)
ASLОВ2_SHORT = (
    "GLTELLNALLPGHQDGAAFRRVTELLSQLVNFTQSRVLGAAIAASDALALGEATGGAAAE"
    "GVVAPTETSPAFMQGVLKGGANATASILDLRDIAGQLVVGNDDGTEIPGPWGRCNPFSSR"
    "LFVELEGVPDHQQPNFRATLA"
)

# CRY2 PHR domain (residues 1-498 of Arabidopsis CRY2)
CRY2_PHR = (
    "MKMDKKTIVWFRRDLRIEDNPALAAAAHEGSVFPVFIWCPEEEGQFYPGRASRWWMKQSL"
    "FHLVKPSQEFWQAGFIHPQGDAPFTGCDLVKILSRCNFSQGLGCRGSSEKLTDSIHTAIA"
    "KEPDKYHRGVSQRFDFKIDTSKRNPLLHIQPGAETVTKIISVLGNTYNRLRVTSDKVSTT"
    "EDLNSGLTLSDLQKALEQGNELPLRCLVGVPSAISTKVSVFVNSPKTFHCAGSTVNGKQF"
    "GSLVAPGCYGNSTWEDHQGLIPFLWGKADEFAVEKAQAEIQQAVKPLGKACPQCVLAWTR"
    "WDADQQVQSVACYRGCVFVPRLRKRVLMTRYLLQAEQFLNNPILQGILTYSPVGNGCSPN"
    "TLLLNLVFMHFLPVHWIQKGQEVVPQGWVQWYNPGKLYYHAGLPGDLIRLNQVGSVMPCS"
    "YLFKLAGLWLTLTEPNVFVLSSTASAARTARFQTLRRMQATRLVDRLTQFLIRFCSSFPV"
    "HQVYFAEQF"
)

# BphP1 (Rhodopseudomonas palustris, photosensory module)
BPHP1_PSM = (
    "MSDTLPLRSIELGSRWGEPLSPAEVRRRLRQVLHELGCRVICGVFYGKEGPFPVGETRYD"
    "GTHFWGKNHPVLAPGAPALYAVSVFEHHHRYRGTLDLRQVGIDVNFPIAPRPHRAGCGQV"
    "IQYAPTLFELLRGELAASVSHQRVGIDVFVPGVNTSAELRALVRQLADLSVGTLTDRLGL"
    "LESFFARQTEVIVRPDDGPVLVSNPVLSPDVLRCFEAVLPGQPLHLDAFSAELFPRQVDP"
    "AGIPAHAGGVQTVLYPGDEVRIIRAGDALRVR"
)

# Q-PAS1 (truncated PpsR2 partner for BphP1)
QPAS1 = (
    "MGSSHHHHHHARAAETLRQLNALLDDGPVRAEILNVAARLGIRVSILDVQEQFDVSGVDV"
    "TLNTGSTLSSATTSQLASQLPSLTSLVVDLTPDAPLSLSGSQITLTAAPEKFAKQLAADV"
    "RVLVVDDRRAAVG"
)

# PhyB N-terminal photosensory module (residues 1-651, Arabidopsis)
# Note: Requires phycocyanobilin chromophore
PHYB_PSM = "..."  # Full sequence too long, use PDB structure

# Standard linkers
LINKERS = {
    "short": "GSGS",
    "medium": "GSGSGSG",
    "long": "GSGSGSGSGSGS",
    "flexible": "GGGGSGGGGSGGGGS",
    "rigid": "AEAAAKEAAAKEAAAKA",
}


# Nanobody framework and CDR positions (IMGT numbering approximation)
# Standard VHH structure:
#   FR1: 1-25
#   CDR1: 26-35
#   FR2: 36-49
#   CDR2: 50-65
#   FR3: 66-94
#   CDR3: 95-102
#   FR4: 103-113

INSERTION_SITES = {
    "loop1": {
        "description": "Loop 1 (GG15 equivalent) - Dark-binding phenotype",
        "position": 15,
        "mechanism": "allosteric",
    },
    "loop5": {
        "description": "Loop 5 (DG62-66 equivalent) - Near CDR2",
        "position": 62,
        "mechanism": "steric/allosteric",
    },
    "loop6": {
        "description": "Loop 6 (AK74 equivalent) - Light-binding phenotype",
        "position": 74,
        "mechanism": "allosteric",
    },
    "n_terminus": {
        "description": "N-terminal fusion - Enhances effect with internal insertion",
        "position": 0,
        "mechanism": "allosteric",
    },
    "c_terminus": {
        "description": "C-terminal fusion",
        "position": -1,
        "mechanism": "tethering",
    },
}


# Optogenetic domains for each nucleotide catcher
OPTO_ASSIGNMENTS = {
    "A_catcher": OptoDomain(
        name="LOV2",
        sequence=ASLОВ2_SHORT,
        activation_wavelength="450nm",
        deactivation="Dark (~60s auto-reset)",
        chromophore="FMN (endogenous)",
        size_aa=len(ASLОВ2_SHORT),
    ),
    "T_catcher": OptoDomain(
        name="CRY2",
        sequence=CRY2_PHR,
        activation_wavelength="488nm",
        deactivation="Dark (~30s auto-reset)",
        chromophore="FAD (endogenous)",
        size_aa=len(CRY2_PHR),
    ),
    "G_catcher": OptoDomain(
        name="BICYCL-Green",
        sequence="[PLACEHOLDER - Use specific BICYCL-Green sequence]",
        activation_wavelength="520nm",
        deactivation="580nm (active OFF)",
        chromophore="Biliverdin",
        size_aa=0,
    ),
    "C_catcher": OptoDomain(
        name="BphP1",
        sequence=BPHP1_PSM,
        activation_wavelength="750nm",
        deactivation="650nm (active OFF)",
        chromophore="Biliverdin (endogenous)",
        size_aa=len(BPHP1_PSM),
    ),
}


def insert_domain(
    nanobody_seq: str,
    opto_domain: str,
    position: int,
    linker: str = "medium",
    delete_residues: int = 0
) -> str:
    """
    Insert an optogenetic domain into a nanobody sequence.

    Args:
        nanobody_seq: Full nanobody amino acid sequence
        opto_domain: Optogenetic domain sequence to insert
        position: Residue number for insertion (0-indexed)
        linker: Linker type from LINKERS dict
        delete_residues: Number of residues to delete at insertion site

    Returns:
        Chimera sequence with optogenetic domain inserted
    """
    linker_seq = LINKERS.get(linker, linker)

    if position == 0:
        # N-terminal fusion
        return f"{opto_domain}{linker_seq}{nanobody_seq}"
    elif position == -1:
        # C-terminal fusion
        return f"{nanobody_seq}{linker_seq}{opto_domain}"
    else:
        # Internal insertion
        before = nanobody_seq[:position]
        after = nanobody_seq[position + delete_residues:]
        return f"{before}{linker_seq}{opto_domain}{linker_seq}{after}"


def create_chimera_for_catcher(
    nanobody_seq: str,
    catcher_type: str,
    insertion_site: str = "loop6",
    linker: str = "medium"
) -> Tuple[str, Dict]:
    """
    Create a complete optogenetic nanobody chimera for a nucleotide catcher.

    Args:
        nanobody_seq: Designed nanobody sequence for nucleotide binding
        catcher_type: One of 'A_catcher', 'T_catcher', 'G_catcher', 'C_catcher'
        insertion_site: Where to insert the optogenetic domain
        linker: Linker type

    Returns:
        Tuple of (chimera_sequence, metadata_dict)
    """
    if catcher_type not in OPTO_ASSIGNMENTS:
        raise ValueError(f"Unknown catcher type: {catcher_type}")

    opto = OPTO_ASSIGNMENTS[catcher_type]
    site = INSERTION_SITES.get(insertion_site, INSERTION_SITES["loop6"])

    chimera = insert_domain(
        nanobody_seq,
        opto.sequence,
        site["position"],
        linker
    )

    metadata = {
        "catcher_type": catcher_type,
        "nanobody_length": len(nanobody_seq),
        "opto_domain": opto.name,
        "opto_length": opto.size_aa,
        "insertion_site": insertion_site,
        "site_position": site["position"],
        "mechanism": site["mechanism"],
        "activation": opto.activation_wavelength,
        "deactivation": opto.deactivation,
        "chromophore": opto.chromophore,
        "total_length": len(chimera),
        "linker": linker,
    }

    return chimera, metadata


def generate_all_catchers(nanobody_sequences: Dict[str, str]) -> Dict[str, Tuple[str, Dict]]:
    """
    Generate chimera sequences for all four nucleotide catchers.

    Args:
        nanobody_sequences: Dict mapping catcher type to nanobody sequence
            e.g., {"A_catcher": "QVQL...", "T_catcher": "QVQL...", ...}

    Returns:
        Dict mapping catcher type to (chimera_sequence, metadata)
    """
    results = {}

    for catcher_type, nb_seq in nanobody_sequences.items():
        try:
            chimera, metadata = create_chimera_for_catcher(
                nb_seq,
                catcher_type,
                insertion_site="loop6",  # Default to light-binding phenotype
                linker="medium"
            )
            results[catcher_type] = (chimera, metadata)
        except Exception as e:
            print(f"Error processing {catcher_type}: {e}")

    return results


def format_fasta(name: str, sequence: str, line_length: int = 60) -> str:
    """Format a sequence as FASTA."""
    lines = [f">{name}"]
    for i in range(0, len(sequence), line_length):
        lines.append(sequence[i:i + line_length])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Insert optogenetic domains into nanobody sequences"
    )
    parser.add_argument(
        "--nanobody",
        type=str,
        help="Nanobody amino acid sequence"
    )
    parser.add_argument(
        "--catcher",
        type=str,
        choices=["A_catcher", "T_catcher", "G_catcher", "C_catcher"],
        default="A_catcher",
        help="Type of nucleotide catcher"
    )
    parser.add_argument(
        "--site",
        type=str,
        choices=list(INSERTION_SITES.keys()),
        default="loop6",
        help="Insertion site for optogenetic domain"
    )
    parser.add_argument(
        "--linker",
        type=str,
        choices=list(LINKERS.keys()),
        default="medium",
        help="Linker type"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output FASTA file"
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run example with placeholder nanobody"
    )

    args = parser.parse_args()

    if args.example or not args.nanobody:
        # Example nanobody sequence (anti-caffeine VHH-like)
        example_nb = (
            "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTY"
            "YADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKDRLSITIRPRYYGLDVWGQG"
            "TLVTVSS"
        )

        print("=" * 60)
        print("Optogenetic Nucleotide Catcher Chimera Generator")
        print("=" * 60)
        print()

        # Generate all four catchers
        test_sequences = {
            "A_catcher": example_nb,
            "T_catcher": example_nb,
            "G_catcher": example_nb,
            "C_catcher": example_nb,
        }

        results = generate_all_catchers(test_sequences)

        for catcher_type, (chimera, metadata) in results.items():
            print(f"\n{'-' * 40}")
            print(f"Catcher: {catcher_type}")
            print(f"Optogenetic domain: {metadata['opto_domain']}")
            print(f"Activation: {metadata['activation']}")
            print(f"Deactivation: {metadata['deactivation']}")
            print(f"Chromophore: {metadata['chromophore']}")
            print(f"Insertion site: {metadata['insertion_site']} (position {metadata['site_position']})")
            print(f"Total length: {metadata['total_length']} aa")
            print(f"\nChimera sequence (first 100 aa):")
            print(chimera[:100] + "...")

    else:
        # Generate single chimera
        chimera, metadata = create_chimera_for_catcher(
            args.nanobody,
            args.catcher,
            args.site,
            args.linker
        )

        print(f"Generated {args.catcher} chimera:")
        print(f"  Opto domain: {metadata['opto_domain']}")
        print(f"  Insertion site: {metadata['insertion_site']}")
        print(f"  Total length: {metadata['total_length']} aa")

        if args.output:
            with open(args.output, "w") as f:
                f.write(format_fasta(
                    f"{args.catcher}_{metadata['opto_domain']}_{args.site}",
                    chimera
                ))
            print(f"  Saved to: {args.output}")
        else:
            print(f"\nSequence:\n{chimera}")


if __name__ == "__main__":
    main()
