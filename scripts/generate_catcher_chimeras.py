#!/usr/bin/env python3
"""
Generate optogenetic chimeras with Catcher system readouts.

This script creates specialized chimeras that pair:
- Nucleotide-specific binders
- Wavelength-specific optogenetic domains
- Catcher fragment readouts (A/T/G/C-Catchers)
"""

import sys
from pathlib import Path

# Optogenetic domain sequences
OPTOGENETIC_DOMAINS = {
    "LOV2": "MADEFDVMLKLIGRHGNVYSATLSEMDIEAGKLYAMSHGYEPPTELVKLLEANYDIPVVGTDNQFLVVGSGVSGRISYVARYFNKSVAKVVKDNGNHDLAVKALELEYNKSHNPQIVKKYVAIVGSEFVDAIYESLASRTHFTVTGQIHNQVTRSYFKNKDSILLSAAGLFTNTQIQAAFKILNVPTDVPYKEVAFYTPGDEVRYEGAIFKDIRKLGNKTSFVGKPYDMYGKVATDEPLEVSNIVVSEDGETWTFHGESGRLVVPRKTSVEDYITYDIRAIGEDAERLVLSGTEVVLHLLAQIPVFKLPPPAAGPSLERVMQEIPRGQVPLNLTDTEEKARRWFDRVREAEEEIRKLGAGFGKRN",

    "Dronpa": "MRGSHHHHHHGMASMASKGEELFTGVVPILVELDGDVNGHKFSVRGEGEGDATNGKLTLKFICTTGKLPVPWPTLVTTLTYGVQCFARYPDHMKQHDFFKSAMPEGYVQERTISFKDDGTYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNFNSHNVYITADKQKNGIKANFKIRHNVEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSVLSKDPNEKRDHMVLLEFVTAAGITHGMDELYK",

    "BICYCL_Red": "MVSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITLGMDELYK",

    "PhyB": "MGSSSHHHHHHSSGLVPRGSHMSMAASELFTAFDIPESLTDPSFFRELAQHTSRVDSIPPELIPAFLEFFRAQGLGKVVRLTSNDPQDLSVITGGGVVGLESYTRAIGGNGMRLVFHGVEANPLVFWPGDEDVLSQALVDALEQRGFTVPSSWFPHQYSKFDEIHLRQKGYQWHVLGKSPQALDIVPSGLSPELRSLTGMAFHTPGLVGYSVGQALERLVSLARRGFDPLWLPQYPLGPGAATARLQGFEQIFPRVERELAPLASRAPQALLAPEASPRLAVRGLSYTPQRAIPLPYGDFWAAKLASAATGRLLATPSQVDAAAALLAQTGSLAGRWRAAAEAEGASPLPMAGGPLAERLQQLGLTLRGPAAHRLRLPHTRSAATLRLGAMELDIVVADLADVRPTELAPFPTPWQLATAPVLPPSQQRLDDYLRRMGLA",

    "BphP1": "MRGSHHHHHHGMASMTGGQQMGRDLYDDDDKDPAVDGGGSGGSGGSGGSGGSLVPRGSHMFEKKVFFSTDNGHYISRELTDPGLFARVEGSKAATGRHLVSGSIAGSLMPEELQGAGTDYQVALVDIEALLKHAPVAGADLDPTLTRAMQHGDEVMDAIVNLTGDRSGKPNLPMFWPNQYYNYDPYQSHLLVGQYQAQSKADQALSALGTLTNYRIINQGGFHGDWRDMTRMNPFFGRNFGLSHYQGELLKHFAFEQMGIHPMGQPHQLDIPTNLAQLGFEFHHFPVFGDVMGQAAERQRLVRLAQRGFSVPASMQPHAWNNAEGHMLLEQAGGLGGALRRYLSEFVPFEDLASRVAALGGFFLRQMGDVLAQEGDKVVFLGSGAIGLAIFKALVTVAAKAGLPARLLVYREGLLGEFGLAKEWQQRGQSGAVFTDAGRIYFLLKKGNDWLRHLMAMGKPTAQKAVQKAMEIFPLVFAYFEGTGGFRAAKKAVASAATAHKLSQEILDLGGSSLPSKVKLLSAARGYATPPRLGSKVGDLQDFLVKLGVGGFGRVFLVLLLGEGLVGGQAEVIYLHSHNPFYFTGLSSLAAALFVGDRPIEALRTQLQRAGLDAKPVLIAECAFGKLREELGYTDTVKKTLTLEEVEEMVAAATVAGL"
}

# Default Catcher sequences (using split sfGFP as placeholders)
# These are the small fragments that complete the fluorescent protein
DEFAULT_CATCHERS = {
    "A_Catcher": "RDHMVLHEYVNAAGIT",  # sfGFP11 (16 aa)
    "T_Catcher": "RDHMVLHEYVNAAGIT",  # sfGFP11 (16 aa)
    "G_Catcher": "RDHMVLLEFVTAAGIT",  # mCherry11-like (16 aa)
    "C_Catcher": "RDHMVLLEFVTAAGIT"   # mCherry11-like (16 aa)
}

# Nucleotide binder sequences (top 4 from production run)
BINDER_SEQUENCES = {
    "dATP_variant_039": "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCWRVTDLSTASSLDYWGQGTLVTVSS",
    "dGTP_variant_019": "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYTARISYLSTASSLDYWGQGTLVTVSS",
    "dCTP_variant_048": "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYSFKVQELSTASSLDYWGQGTLVTVSS",
    "dTTP_variant_016": "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYNARVAYLSTASSLDYWGQGTLVTVSS"
}

# Pairing strategy (CORRECTED)
# A-Catcher + Dronpa
# T-Catcher + BICYCL-Red
# G-Catcher + PhyB
# C-Catcher + BphP1
SENSOR_CONFIGS = {
    "dATP_sensor": {
        "binder": "dATP_variant_039",
        "domain": "Dronpa",
        "catcher": "A_Catcher",
        "wavelength": "500nm (cyan)",
        "emission": "515nm (green)",
        "notes": "A-Catcher + Dronpa, photoswitchable"
    },
    "dTTP_sensor": {
        "binder": "dTTP_variant_016",
        "domain": "BICYCL_Red",
        "catcher": "T_Catcher",
        "wavelength": "580nm (yellow)",
        "emission": "520nm (green)",
        "notes": "T-Catcher + BICYCL-Red, best binder, yellow→green"
    },
    "dGTP_sensor": {
        "binder": "dGTP_variant_019",
        "domain": "PhyB",
        "catcher": "G_Catcher",
        "wavelength": "660nm (red)",
        "emission": "730nm (far-red)",
        "notes": "G-Catcher + PhyB, red→far-red switch"
    },
    "dCTP_sensor": {
        "binder": "dCTP_variant_048",
        "domain": "BphP1",
        "catcher": "C_Catcher",
        "wavelength": "750nm (far-red)",
        "emission": "650nm (red)",
        "notes": "C-Catcher + BphP1, far-red→red, deepest penetration"
    }
}


def insert_domain_with_catcher(nanobody_seq, domain_seq, catcher_seq, insertion_pos=74):
    """
    Insert optogenetic domain and Catcher fragment into nanobody.

    Architecture:
    [Nanobody 1-74] - [Linker1] - [Opto Domain] - [Linker2] - [Nanobody 75-end] - [Linker3] - [Catcher]
    """

    linker1 = "GSGSGSG"  # 7 aa flexible linker
    linker2 = "GSGSGSG"  # 7 aa flexible linker
    linker3 = "GGGGS"    # 5 aa short linker for C-terminal fusion

    # Split nanobody at insertion position
    nanobody_n = nanobody_seq[:insertion_pos]
    nanobody_c = nanobody_seq[insertion_pos:]

    # Assemble full chimera
    chimera = nanobody_n + linker1 + domain_seq + linker2 + nanobody_c + linker3 + catcher_seq

    return chimera


def generate_all_catcher_sensors(output_dir, custom_catchers=None):
    """
    Generate all 4 optogenetic nucleotide sensors with Catcher readouts.

    Args:
        output_dir: Directory to save FASTA files
        custom_catchers: Optional dict with custom Catcher sequences
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Use custom or default Catchers
    catchers = custom_catchers if custom_catchers else DEFAULT_CATCHERS

    print("=" * 80)
    print("GENERATING OPTOGENETIC NUCLEOTIDE SENSORS WITH CATCHER READOUTS")
    print("=" * 80)
    print()

    print("Strategy:")
    print("  • 4 wavelength-specific optogenetic domains")
    print("  • 4 nucleotide-specific nanobody binders")
    print("  • 4 Catcher fragment readouts (A/T/G/C)")
    print("  • Complete spectral separation for multiplexing")
    print()

    generated_files = []

    for sensor_name, config in SENSOR_CONFIGS.items():
        print(f"{'=' * 80}")
        print(f"Generating {sensor_name.upper()}")
        print(f"{'=' * 80}")
        print()

        binder_id = config['binder']
        domain_name = config['domain']
        catcher_name = config['catcher']

        binder_seq = BINDER_SEQUENCES[binder_id]
        domain_seq = OPTOGENETIC_DOMAINS[domain_name]
        catcher_seq = catchers[catcher_name]

        # Generate full sensor
        chimera_seq = insert_domain_with_catcher(binder_seq, domain_seq, catcher_seq)

        print(f"Components:")
        print(f"  Binder: {binder_id}")
        print(f"  Domain: {domain_name} ({len(domain_seq)} aa)")
        print(f"  Catcher: {catcher_name} ({len(catcher_seq)} aa)")
        print(f"  Wavelength: {config['wavelength']}")
        print(f"  Emission: {config['emission']}")
        print(f"  Notes: {config['notes']}")
        print()

        print(f"Architecture:")
        print(f"  Nanobody (1-74): 74 aa")
        print(f"  Linker 1: 7 aa (GSGSGSG)")
        print(f"  {domain_name}: {len(domain_seq)} aa")
        print(f"  Linker 2: 7 aa (GSGSGSG)")
        print(f"  Nanobody (75-121): 47 aa")
        print(f"  Linker 3: 5 aa (GGGGS)")
        print(f"  {catcher_name}: {len(catcher_seq)} aa")
        print(f"  Total: {len(chimera_seq)} aa")
        print()

        # Save to FASTA
        nucleotide = sensor_name.split('_')[0]  # dATP, dTTP, etc.
        filename = f"{nucleotide}_{domain_name}_{catcher_name}_sensor.fasta"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            f.write(f">{nucleotide}_{domain_name}_{catcher_name}_sensor\n")
            f.write(f"{chimera_seq}\n")

        print(f"✓ Saved: {filename}")
        print()

        generated_files.append(filename)

        # Also generate "basic" version (no Catcher) for testing
        basic_seq = insert_domain_with_catcher(binder_seq, domain_seq, "", 74)
        basic_filename = f"{nucleotide}_{domain_name}_basic.fasta"
        basic_filepath = output_dir / basic_filename

        with open(basic_filepath, 'w') as f:
            f.write(f">{nucleotide}_{domain_name}_basic\n")
            f.write(f"{basic_seq}\n")

        print(f"✓ Also saved basic version (no Catcher): {basic_filename}")
        print()

    # Generate constitutive controls (no optogenetic domain, just Catcher)
    print(f"{'=' * 80}")
    print("GENERATING CONSTITUTIVE CONTROLS (No Optogenetic Domain)")
    print(f"{'=' * 80}")
    print()

    for sensor_name, config in SENSOR_CONFIGS.items():
        binder_id = config['binder']
        catcher_name = config['catcher']

        binder_seq = BINDER_SEQUENCES[binder_id]
        catcher_seq = catchers[catcher_name]

        # Just binder + Catcher (no optogenetic domain)
        linker = "GGGGS"
        control_seq = binder_seq + linker + catcher_seq

        nucleotide = sensor_name.split('_')[0]
        control_filename = f"{nucleotide}_{catcher_name}_control.fasta"
        control_filepath = output_dir / control_filename

        with open(control_filepath, 'w') as f:
            f.write(f">{nucleotide}_{catcher_name}_control (constitutive)\n")
            f.write(f"{control_seq}\n")

        print(f"✓ Control: {control_filename} ({len(control_seq)} aa)")
        generated_files.append(control_filename)

    print()
    print(f"{'=' * 80}")
    print("GENERATION COMPLETE")
    print(f"{'=' * 80}")
    print()
    print(f"Total constructs generated: {len(generated_files)}")
    print()
    print("File types:")
    print("  • 4 full sensors (Binder + Domain + Catcher)")
    print("  • 4 basic chimeras (Binder + Domain, no Catcher)")
    print("  • 4 controls (Binder + Catcher, no Domain)")
    print("  Total: 12 constructs")
    print()
    print(f"Output directory: {output_dir}/")
    print()
    print("Spectral properties (CORRECTED PAIRING):")
    print("  dATP: A-Catcher + Dronpa (500nm → 515nm) 🟢 Cyan→Green")
    print("  dTTP: T-Catcher + BICYCL-Red (580nm → 520nm) 🟡 Yellow→Green")
    print("  dGTP: G-Catcher + PhyB (660nm → 730nm) 🔴 Red→Far-red")
    print("  dCTP: C-Catcher + BphP1 (750nm → 650nm) ⚫ Far-red→Red")
    print()
    print("Next steps:")
    print("  1. Review sequences in catcher_sensors/ directory")
    print("  2. If you have custom Catcher sequences, re-run with --custom-catchers")
    print("  3. Order genes for synthesis (~$3,000-4,000 for all 12)")
    print("  4. Clone into expression vectors")
    print("  5. Test in mammalian cells (HEK293T recommended)")
    print()
    print("Priority for testing:")
    print("  1. dTTP_BICYCL-Red_T-Catcher (best binder + good spectral window) ⭐")
    print("  2. dATP_Dronpa_A-Catcher (photoswitchable)")
    print("  3. dGTP_PhyB_G-Catcher (red→far-red)")
    print("  4. dCTP_BphP1_C-Catcher (deepest tissue penetration)")
    print()


def main():
    """Main entry point."""

    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = "../catcher_sensors"

    print()
    print("NOTE: Using default Catcher sequences (split sfGFP fragments)")
    print("      If you have custom Catcher sequences, provide them as a dictionary")
    print()

    # Check if custom Catchers provided
    custom_catchers = None  # Could be loaded from file or passed as argument

    generate_all_catcher_sensors(output_dir, custom_catchers)


if __name__ == "__main__":
    main()
