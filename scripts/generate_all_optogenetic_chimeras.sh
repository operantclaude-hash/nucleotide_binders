#!/bin/bash
# Generate optogenetic chimeras for all top binders
# All 3 optogenetic domains × 4 top binders = 12 chimeras

echo "=" 80
echo "GENERATING OPTOGENETIC CHIMERAS FOR TOP BINDERS"
echo "="*80
echo ""

# Top binder sequences
DATP_SEQ="QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCWRVTDLSTASSLDYWGQGTLVTVSS"
DGTP_SEQ="QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYTARISYLSTASSLDYWGQGTLVTVSS"
DCTP_SEQ="QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYSFKVQELSTASSLDYWGQGTLVTVSS"
DTTP_SEQ="QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYNARVAYLSTASSLDYWGQGTLVTVSS"

mkdir -p ../optogenetic_chimeras

# dATP binders with all 3 domains
echo "Generating dATP_variant_039 chimeras..."
python insert_custom_optogenetic.py --sequence "$DATP_SEQ" --domain LOV2 --output ../optogenetic_chimeras/dATP_variant_039_LOV2.fasta
python insert_custom_optogenetic.py --sequence "$DATP_SEQ" --domain CRY2 --output ../optogenetic_chimeras/dATP_variant_039_CRY2.fasta
python insert_custom_optogenetic.py --sequence "$DATP_SEQ" --domain BphP1 --output ../optogenetic_chimeras/dATP_variant_039_BphP1.fasta
echo "  ✓ 3 chimeras created"

# dGTP binders with all 3 domains  
echo "Generating dGTP_variant_019 chimeras..."
python insert_custom_optogenetic.py --sequence "$DGTP_SEQ" --domain LOV2 --output ../optogenetic_chimeras/dGTP_variant_019_LOV2.fasta
python insert_custom_optogenetic.py --sequence "$DGTP_SEQ" --domain CRY2 --output ../optogenetic_chimeras/dGTP_variant_019_CRY2.fasta
python insert_custom_optogenetic.py --sequence "$DGTP_SEQ" --domain BphP1 --output ../optogenetic_chimeras/dGTP_variant_019_BphP1.fasta
echo "  ✓ 3 chimeras created"

# dCTP binders with all 3 domains
echo "Generating dCTP_variant_048 chimeras..."
python insert_custom_optogenetic.py --sequence "$DCTP_SEQ" --domain LOV2 --output ../optogenetic_chimeras/dCTP_variant_048_LOV2.fasta
python insert_custom_optogenetic.py --sequence "$DCTP_SEQ" --domain CRY2 --output ../optogenetic_chimeras/dCTP_variant_048_CRY2.fasta
python insert_custom_optogenetic.py --sequence "$DCTP_SEQ" --domain BphP1 --output ../optogenetic_chimeras/dCTP_variant_048_BphP1.fasta
echo "  ✓ 3 chimeras created"

# dTTP binders with all 3 domains (BEST OVERALL)
echo "Generating dTTP_variant_016 chimeras (BEST OVERALL)..."
python insert_custom_optogenetic.py --sequence "$DTTP_SEQ" --domain LOV2 --output ../optogenetic_chimeras/dTTP_variant_016_LOV2.fasta
python insert_custom_optogenetic.py --sequence "$DTTP_SEQ" --domain CRY2 --output ../optogenetic_chimeras/dTTP_variant_016_CRY2.fasta
python insert_custom_optogenetic.py --sequence "$DTTP_SEQ" --domain BphP1 --output ../optogenetic_chimeras/dTTP_variant_016_BphP1.fasta
echo "  ✓ 3 chimeras created"

echo ""
echo "="*80
echo "OPTOGENETIC CHIMERAS COMPLETE"
echo "="*80
echo ""
echo "Total chimeras created: 12"
echo "  - 4 binders × 3 optogenetic domains"
echo ""
echo "Optogenetic domains:"
echo "  • LOV2   (142 aa) - Blue light activated (~450 nm)"
echo "  • CRY2   (351 aa) - Blue light activated (~450 nm, different mechanism)"
echo "  • BphP1  (672 aa) - Far-red light activated (~740 nm)"
echo ""
echo "Output location: ../optogenetic_chimeras/"
echo ""
echo "Files:"
ls -lh ../optogenetic_chimeras/*.fasta
echo ""
