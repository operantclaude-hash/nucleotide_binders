#!/usr/bin/env python3
"""
Script to insert optogenetic domains (LOV2, CRY2, BphP1) at position 74
of nanobody sequences with GSGSGSG linkers.
"""

# Standard nanobody scaffold sequence (VHH)
NANOBODY_SCAFFOLD = "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS"

# Optogenetic domain sequences
OPTOGENETIC_DOMAINS = {
    "LOV2": """
MADEFDVMLKLIGRHGNVYSATLSEMDIEAGKLYAMSHGYEPPTELVKLLEANYDIPVVGTDNQFLVVGSGVSGRISYVARYFNKSVAKVVKDNGNHDLAVKALELEYNKSHNPQIVKKYVAIVGSEFVDAIYESLASRTHFTVTGQIHNQVTRSYFKNKDSILLSAAGLFTNTQIQAAFKILNVPTDVPYKEVAFYTPGDEVRYEGAIFKDIRKLGNKTSFVGKPYDMYGKVATDEPLEVSNIVVSEDGETWTFHGESGRLVVPRKTSVEDYITYDIRAIGEDAERLVLSGTEVVLHLLAQIPVFKLPPPAAGPSLERVMQEIPRGQVPLNLTDTEEKARRWFDRVREAEEEIRKLGAGFGKRN
""".replace('\n', '').strip(),

    "CRY2": """
MSQLWLQECPEFFRAFSYKYQQDVNKIFPGGYGGLHPYSNLIGGRCSQVIEALEKGKYQMLGGDGWKRAIVFTQRKGERGPRKLVDDEEAVRRGDVFLNHPDIDPSLMKPGRGVLLPEMAQRMLKSAGIDAEYRVVDGAHVEPGVQFLASWREGHCRLSVETAKLGEDGDYRRNLFGLLDSPEIHALHRYWQQVMPRPSLRTGGSMLVLPVLLLGLYLLPRHRPSSGSRTSMSSSQSSLKHSRSRSSADTTNRTRCLQTQTQSFSAALSNSQKQKQTQKQRREALILLLREVLRKLRQEQEERLLQEVRERKARLWDRVRGEEEDLRRLGRGFGRQV
""".replace('\n', '').strip(),

    "BphP1": """
MRGSHHHHHHGMASMTGGQQMGRDLYDDDDKDPAVDGGGSGGSGGSGGSGGSLVPRGSHMFEKKVFFSTDNGHYISRELTDPGLFARVEGSKAATGRHLVSGSIAGSLMPEELQGAGTDYQVALVDIEALLKHAPVAGADLDPTLTRAMQHGDEVMDAIVNLTGDRSGKPNLPMFWPNQYYNYDPYQSHLLVGQYQAQSKADQALSALGTLTNYRIINQGGFHGDWRDMTRMNPFFGRNFGLSHYQGELLKHFAFEQMGIHPMGQPHQLDIPTNLAQLGFEFHHFPVFGDVMGQAAERQRLVRLAQRGFSVPASMQPHAWNNAEGHMLLEQAGGLGGALRRYLSEFVPFEDLASRVAALGGFFLRQMGDVLAQEGDKVVFLGSGAIGLAIFKALVTVAAKAGLPARLLVYREGLLGEFGLAKEWQQRGQSGAVFTDAGRIYFLLKKGNDWLRHLMAMGKPTAQKAVQKAMEIFPLVFAYFEGTGGFRAAKKAVASAATAHKLSQEILDLGGSSLPSKVKLLSAARGYATPPRLGSKVGDLQDFLVKLGVGGFGRVFLVLLLGEGLVGGQAEVIYLHSHNPFYFTGLSSLAAALFVGDRPIEALRTQLQRAGLDAKPVLIAECAFGKLREELGYTDTVKKTLTLEEVEEMVAAATVAGL
""".replace('\n', '').strip(),
}

# Flexible linker
LINKER = "GSGSGSG"

# Insertion position (0-indexed)
INSERTION_POS = 74


def insert_domain(nanobody_seq: str, domain_seq: str, domain_name: str,
                  position: int = INSERTION_POS, linker: str = LINKER) -> dict:
    """
    Insert an optogenetic domain at the specified position in a nanobody sequence.

    Args:
        nanobody_seq: Nanobody sequence
        domain_seq: Optogenetic domain sequence
        domain_name: Name of the optogenetic domain
        position: Position to insert the domain (0-indexed)
        linker: Linker sequence

    Returns:
        Dictionary with insertion details
    """
    # Split the nanobody at the insertion position
    before = nanobody_seq[:position]
    after = nanobody_seq[position:]

    # Create the chimeric sequence
    chimeric_seq = f"{before}{linker}{domain_seq}{linker}{after}"

    return {
        "domain_name": domain_name,
        "insertion_position": position,
        "nanobody_length": len(nanobody_seq),
        "domain_length": len(domain_seq),
        "chimeric_length": len(chimeric_seq),
        "linker": linker,
        "before_segment": before,
        "after_segment": after,
        "full_sequence": chimeric_seq,
    }


def generate_all_chimeras(nanobody_seq: str = NANOBODY_SCAFFOLD) -> dict:
    """
    Generate all optogenetic domain insertions for a nanobody.

    Args:
        nanobody_seq: Nanobody sequence to modify

    Returns:
        Dictionary of all chimeric constructs
    """
    chimeras = {}

    for domain_name, domain_seq in OPTOGENETIC_DOMAINS.items():
        result = insert_domain(nanobody_seq, domain_seq, domain_name)
        chimeras[domain_name] = result

    return chimeras


def save_fasta(chimeras: dict, output_file: str):
    """
    Save chimeric sequences to a FASTA file.

    Args:
        chimeras: Dictionary of chimeric constructs
        output_file: Output FASTA file path
    """
    with open(output_file, 'w') as f:
        for domain_name, data in chimeras.items():
            header = (f">{domain_name}_nanobody_chimera "
                     f"pos={data['insertion_position']} "
                     f"length={data['chimeric_length']}")
            f.write(f"{header}\n")

            # Write sequence in 80-character lines
            seq = data['full_sequence']
            for i in range(0, len(seq), 80):
                f.write(f"{seq[i:i+80]}\n")
            f.write("\n")


def save_report(chimeras: dict, output_file: str):
    """
    Save a detailed report of the chimeric constructs.

    Args:
        chimeras: Dictionary of chimeric constructs
        output_file: Output report file path
    """
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("OPTOGENETIC NANOBODY CHIMERAS - DETAILED REPORT\n")
        f.write("=" * 80 + "\n\n")

        for domain_name, data in chimeras.items():
            f.write(f"\n{'='*80}\n")
            f.write(f"DOMAIN: {domain_name}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Insertion Position: {data['insertion_position']}\n")
            f.write(f"Linker: {data['linker']}\n")
            f.write(f"Nanobody Length: {data['nanobody_length']} aa\n")
            f.write(f"Domain Length: {data['domain_length']} aa\n")
            f.write(f"Chimeric Length: {data['chimeric_length']} aa\n\n")

            f.write(f"Construct Architecture:\n")
            f.write(f"  N-term (1-{data['insertion_position']}): {len(data['before_segment'])} aa\n")
            f.write(f"  Linker: {len(data['linker'])} aa\n")
            f.write(f"  {domain_name}: {data['domain_length']} aa\n")
            f.write(f"  Linker: {len(data['linker'])} aa\n")
            f.write(f"  C-term: {len(data['after_segment'])} aa\n\n")

            f.write(f"Full Sequence:\n")
            seq = data['full_sequence']
            for i in range(0, len(seq), 80):
                f.write(f"{seq[i:i+80]}\n")
            f.write("\n")


if __name__ == "__main__":
    import os

    # Generate all chimeras
    print("Generating optogenetic nanobody chimeras...")
    chimeras = generate_all_chimeras()

    # Create output directory
    output_dir = "../results/optogenetic_chimeras"
    os.makedirs(output_dir, exist_ok=True)

    # Save FASTA file
    fasta_file = os.path.join(output_dir, "optogenetic_nanobody_chimeras.fasta")
    save_fasta(chimeras, fasta_file)
    print(f"✓ Saved FASTA file: {fasta_file}")

    # Save detailed report
    report_file = os.path.join(output_dir, "chimera_report.txt")
    save_report(chimeras, report_file)
    print(f"✓ Saved report: {report_file}")

    # Print summary
    print(f"\nGenerated {len(chimeras)} chimeric constructs:")
    for domain_name, data in chimeras.items():
        print(f"  - {domain_name}: {data['chimeric_length']} aa")

    print(f"\nInsertion details:")
    print(f"  Position: {INSERTION_POS}")
    print(f"  Linker: {LINKER}")
    print(f"  Original nanobody: {len(NANOBODY_SCAFFOLD)} aa")
