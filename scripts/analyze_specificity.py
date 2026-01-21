#!/usr/bin/env python3
"""
Analyze specificity screening results.
Calculate specificity scores and rank candidates.

Specificity Score = Target Confidence / Mean(Off-Target Confidences)
Higher score = better specificity
"""

import json
import pandas as pd
from pathlib import Path
import argparse
import numpy as np


def load_screening_results(results_file):
    """Load screening results JSON."""
    with open(results_file, 'r') as f:
        return json.load(f)


def calculate_specificity_scores(results_data):
    """
    Calculate specificity scores for each variant.

    For each variant:
    - Extract confidence for target nucleotide
    - Extract confidences for 3 off-targets
    - Calculate specificity ratio
    """
    results = results_data['results']

    # Group by variant
    variants_data = {}
    for r in results:
        variant_id = r['variant_id']
        if variant_id not in variants_data:
            variants_data[variant_id] = {
                'target_nucleotide': r['target_nucleotide'],
                'mutations': r['mutations'],
                'scores': {}
            }

        test_nuc = r['test_nucleotide']
        confidence = r['confidence']

        if confidence:
            variants_data[variant_id]['scores'][test_nuc] = {
                'confidence_score': confidence['confidence_score'],
                'ligand_iptm': confidence['ligand_iptm'],
                'complex_plddt': confidence['complex_plddt'],
                'is_target': r['is_target']
            }

    # Calculate specificity for each variant
    specificity_results = []

    for variant_id, data in variants_data.items():
        target_nuc = data['target_nucleotide']
        scores = data['scores']

        # Check if we have all 4 nucleotides
        if len(scores) != 4:
            continue

        # Target score
        if target_nuc in scores:
            target_conf = scores[target_nuc]['confidence_score']
            target_iptm = scores[target_nuc]['ligand_iptm']
        else:
            continue

        # Off-target scores
        off_target_confs = []
        off_target_iptms = []
        for nuc, score_data in scores.items():
            if nuc != target_nuc:
                off_target_confs.append(score_data['confidence_score'])
                off_target_iptms.append(score_data['ligand_iptm'])

        if len(off_target_confs) != 3:
            continue

        mean_off_target_conf = np.mean(off_target_confs)
        mean_off_target_iptm = np.mean(off_target_iptms)
        max_off_target_conf = np.max(off_target_confs)

        # Specificity scores
        # Higher = better specificity
        specificity_ratio_conf = target_conf / mean_off_target_conf if mean_off_target_conf > 0 else 0
        specificity_ratio_iptm = target_iptm / mean_off_target_iptm if mean_off_target_iptm > 0 else 0

        # Selectivity (target - max_off_target)
        selectivity_conf = target_conf - max_off_target_conf
        selectivity_iptm = target_iptm - max(off_target_iptms)

        # Combined score (high target binding + high specificity)
        combined_score = target_conf * specificity_ratio_conf

        specificity_results.append({
            'variant_id': variant_id,
            'target_nucleotide': target_nuc,
            'mutations': data['mutations'],
            'target_confidence': target_conf,
            'target_iptm': target_iptm,
            'mean_off_target_conf': mean_off_target_conf,
            'mean_off_target_iptm': mean_off_target_iptm,
            'max_off_target_conf': max_off_target_conf,
            'specificity_ratio_conf': specificity_ratio_conf,
            'specificity_ratio_iptm': specificity_ratio_iptm,
            'selectivity_conf': selectivity_conf,
            'selectivity_iptm': selectivity_iptm,
            'combined_score': combined_score,
            'all_scores': scores
        })

    return specificity_results


def rank_candidates(specificity_results, metric='combined_score'):
    """Rank candidates by specificity metric."""
    df = pd.DataFrame(specificity_results)

    # Sort by metric
    df_sorted = df.sort_values(metric, ascending=False).reset_index(drop=True)

    return df_sorted


def print_top_candidates(df, n=10):
    """Print top N candidates."""
    print(f"\n{'='*80}")
    print(f"TOP {n} SPECIFIC BINDERS (by combined score)")
    print(f"{'='*80}\n")

    for i, row in df.head(n).iterrows():
        print(f"Rank {i+1}: {row['variant_id']}")
        print(f"  Target: {row['target_nucleotide']}")
        print(f"  Mutations: {row['mutations']}")
        print(f"  Target confidence: {row['target_confidence']:.4f}")
        print(f"  Mean off-target: {row['mean_off_target_conf']:.4f}")
        print(f"  Specificity ratio: {row['specificity_ratio_conf']:.2f}x")
        print(f"  Selectivity: {row['selectivity_conf']:.4f}")
        print(f"  Combined score: {row['combined_score']:.4f}")

        # Show individual scores
        print(f"  Individual scores:")
        for nuc, score in row['all_scores'].items():
            marker = "★" if nuc == row['target_nucleotide'] else " "
            print(f"    {marker} {nuc}: {score['confidence_score']:.4f} (iPTM: {score['ligand_iptm']:.4f})")
        print()


def print_summary_by_nucleotide(df):
    """Print summary statistics by target nucleotide."""
    print(f"\n{'='*80}")
    print("SUMMARY BY TARGET NUCLEOTIDE")
    print(f"{'='*80}\n")

    for nuc in ['dATP', 'dGTP', 'dCTP', 'dTTP']:
        nuc_df = df[df['target_nucleotide'] == nuc]

        if len(nuc_df) == 0:
            continue

        print(f"{nuc}:")
        print(f"  Variants tested: {len(nuc_df)}")
        print(f"  Best specificity ratio: {nuc_df['specificity_ratio_conf'].max():.2f}x")
        print(f"  Best target confidence: {nuc_df['target_confidence'].max():.4f}")
        print(f"  Mean specificity ratio: {nuc_df['specificity_ratio_conf'].mean():.2f}x")

        # Best variant for this nucleotide
        best_idx = nuc_df['combined_score'].idxmax()
        best = df.loc[best_idx]
        print(f"  Best variant: {best['variant_id']}")
        print(f"    Mutations: {best['mutations']}")
        print(f"    Combined score: {best['combined_score']:.4f}")
        print()


def save_analysis_results(df, output_dir):
    """Save analysis results to files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save full results as CSV
    csv_file = output_path / "specificity_analysis.csv"
    df.to_csv(csv_file, index=False)
    print(f"✓ Full results saved: {csv_file}")

    # Save top candidates by nucleotide
    for nuc in ['dATP', 'dGTP', 'dCTP', 'dTTP']:
        nuc_df = df[df['target_nucleotide'] == nuc].head(5)
        nuc_file = output_path / f"top_binders_{nuc}.csv"
        nuc_df.to_csv(nuc_file, index=False)
        print(f"✓ Top {nuc} binders: {nuc_file}")

    # Save summary report
    report_file = output_path / "specificity_report.txt"
    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("SPECIFICITY SCREENING ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")

        f.write(f"Total variants analyzed: {len(df)}\n\n")

        # Top 10 overall
        f.write("TOP 10 SPECIFIC BINDERS (Combined Score)\n")
        f.write("-"*80 + "\n")
        for i, row in df.head(10).iterrows():
            f.write(f"\n{i+1}. {row['variant_id']} ({row['target_nucleotide']})\n")
            f.write(f"   Mutations: {row['mutations']}\n")
            f.write(f"   Target conf: {row['target_confidence']:.4f}\n")
            f.write(f"   Specificity: {row['specificity_ratio_conf']:.2f}x\n")
            f.write(f"   Combined: {row['combined_score']:.4f}\n")

        # Best per nucleotide
        f.write("\n\n" + "="*80 + "\n")
        f.write("BEST BINDER PER NUCLEOTIDE\n")
        f.write("="*80 + "\n\n")

        for nuc in ['dATP', 'dGTP', 'dCTP', 'dTTP']:
            nuc_df = df[df['target_nucleotide'] == nuc]
            if len(nuc_df) > 0:
                best = nuc_df.iloc[0]
                f.write(f"{nuc}:\n")
                f.write(f"  {best['variant_id']}\n")
                f.write(f"  Mutations: {best['mutations']}\n")
                f.write(f"  Target confidence: {best['target_confidence']:.4f}\n")
                f.write(f"  Specificity ratio: {best['specificity_ratio_conf']:.2f}x\n")
                f.write(f"  Individual scores:\n")
                for test_nuc, score in best['all_scores'].items():
                    marker = "★" if test_nuc == nuc else " "
                    f.write(f"    {marker} {test_nuc}: {score['confidence_score']:.4f}\n")
                f.write("\n")

    print(f"✓ Analysis report: {report_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze specificity screening results"
    )
    parser.add_argument(
        "--results-file",
        default="../specificity_library/screening_results/screening_results.json",
        help="Screening results JSON file"
    )
    parser.add_argument(
        "--output-dir",
        default="../specificity_library/analysis",
        help="Output directory for analysis results"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Number of top candidates to display (default: 10)"
    )

    args = parser.parse_args()

    print("="*80)
    print("SPECIFICITY ANALYSIS")
    print("="*80)

    # Load results
    print(f"\nLoading results from {args.results_file}...")
    results_data = load_screening_results(args.results_file)

    total = results_data['total_predictions']
    success = results_data['successful']
    print(f"Total predictions: {total}")
    print(f"Successful: {success}")

    # Calculate specificity scores
    print("\nCalculating specificity scores...")
    specificity_results = calculate_specificity_scores(results_data)
    print(f"Variants with complete data: {len(specificity_results)}")

    # Rank candidates
    df = rank_candidates(specificity_results, metric='combined_score')

    # Print results
    print_top_candidates(df, n=args.top_n)
    print_summary_by_nucleotide(df)

    # Save results
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}\n")
    save_analysis_results(df, args.output_dir)

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}\n")

    print("Next steps:")
    print("1. Review top candidates in analysis/specificity_report.txt")
    print("2. Visualize structures of best binders")
    print("3. Select candidates for experimental validation")
    print("4. Add optogenetic domains to selected binders")


if __name__ == "__main__":
    main()
