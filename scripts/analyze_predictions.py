#!/usr/bin/env python3
"""
Analyze Boltz predictions: extract metrics, compare models, and provide recommendations.
"""

import json
import numpy as np
from pathlib import Path
import argparse


def load_confidence(json_file):
    """Load confidence metrics from JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)


def analyze_prediction(prediction_dir):
    """Analyze a single prediction directory."""
    pred_dir = Path(prediction_dir)

    # Find all confidence JSON files
    confidence_files = sorted(pred_dir.glob("confidence_*_model_*.json"))

    if not confidence_files:
        print(f"No confidence files found in {prediction_dir}")
        return None

    results = []
    for conf_file in confidence_files:
        conf = load_confidence(conf_file)

        # Extract model number
        model_num = conf_file.stem.split('_model_')[-1]
        structure_file = pred_dir / f"{pred_dir.parent.name}_model_{model_num}.cif"

        results.append({
            'model': model_num,
            'confidence_score': conf.get('confidence_score', 0),
            'ptm': conf.get('ptm', 0),
            'iptm': conf.get('iptm', 0),
            'ligand_iptm': conf.get('ligand_iptm', 0),
            'complex_plddt': conf.get('complex_plddt', 0),
            'complex_iplddt': conf.get('complex_iplddt', 0),
            'structure_file': structure_file,
            'conf_file': conf_file,
            'full_data': conf
        })

    return results


def print_analysis(results, prediction_name):
    """Print formatted analysis of predictions."""

    print(f"\n{'='*80}")
    print(f"ANALYSIS: {prediction_name}")
    print(f"{'='*80}\n")

    if not results:
        print("No results to analyze")
        return

    # Sort by confidence score
    results_sorted = sorted(results, key=lambda x: x['confidence_score'], reverse=True)

    # Print summary table
    print(f"{'Model':<8} {'Confidence':<12} {'PTM':<8} {'iPTM':<8} {'Ligand iPTM':<14} {'pLDDT':<8}")
    print(f"{'-'*80}")

    for r in results_sorted:
        print(f"{r['model']:<8} "
              f"{r['confidence_score']:>11.4f} "
              f"{r['ptm']:>7.4f} "
              f"{r['iptm']:>7.4f} "
              f"{r['ligand_iptm']:>13.4f} "
              f"{r['complex_plddt']:>7.4f}")

    # Best model
    best = results_sorted[0]
    print(f"\n{'='*80}")
    print(f"BEST MODEL: {best['model']}")
    print(f"{'='*80}\n")

    print(f"Confidence Score:     {best['confidence_score']:.4f}")
    print(f"PTM (structure):      {best['ptm']:.4f}")
    print(f"iPTM (interface):     {best['iptm']:.4f}")
    print(f"Ligand iPTM:          {best['ligand_iptm']:.4f}")
    print(f"Complex pLDDT:        {best['complex_plddt']:.4f}")
    print(f"Complex ipLDDT:       {best['complex_iplddt']:.4f}")

    print(f"\nStructure file: {best['structure_file']}")

    # Quality assessment
    print(f"\n{'='*80}")
    print(f"QUALITY ASSESSMENT")
    print(f"{'='*80}\n")

    score = best['confidence_score']
    ligand_iptm = best['ligand_iptm']
    plddt = best['complex_plddt']

    def get_rating(value, thresholds):
        """Get rating based on thresholds."""
        if value >= thresholds[0]:
            return "Excellent ✓✓✓"
        elif value >= thresholds[1]:
            return "Good ✓✓"
        elif value >= thresholds[2]:
            return "Fair ✓"
        else:
            return "Poor ✗"

    print(f"Overall Confidence:   {get_rating(score, [0.8, 0.7, 0.5])}")
    print(f"  Score: {score:.4f} (higher is better)")
    print(f"  >0.8: Excellent, 0.7-0.8: Good, 0.5-0.7: Fair, <0.5: Poor\n")

    print(f"Binding Interface:    {get_rating(ligand_iptm, [0.7, 0.5, 0.3])}")
    print(f"  Ligand iPTM: {ligand_iptm:.4f}")
    print(f"  >0.7: Strong binding, 0.5-0.7: Moderate, 0.3-0.5: Weak, <0.3: Very weak\n")

    print(f"Structure Quality:    {get_rating(plddt, [0.9, 0.8, 0.7])}")
    print(f"  pLDDT: {plddt:.4f}")
    print(f"  >0.9: High confidence, 0.8-0.9: Good, 0.7-0.8: Moderate, <0.7: Low\n")

    # Recommendations
    print(f"{'='*80}")
    print(f"RECOMMENDATIONS")
    print(f"{'='*80}\n")

    if score >= 0.7 and ligand_iptm >= 0.5:
        print("✓ This prediction looks promising for experimental validation")
        print("✓ The nanobody-nucleotide interface appears well-formed")
        print("✓ Proceed with optogenetic domain insertion")
    elif score >= 0.5:
        print("⚠ Moderate quality prediction")
        print("  Consider:")
        print("  - Generating full MSAs (not minimal) for better accuracy")
        print("  - Running more diffusion samples")
        print("  - Checking the binding interface manually in PyMOL/ChimeraX")
    else:
        print("✗ Low confidence prediction")
        print("  Recommendations:")
        print("  - Generate full MSAs using sequence databases")
        print("  - Increase sampling steps (>200)")
        print("  - Try different nanobody sequences/CDR designs")
        print("  - Validate interface geometry manually")

    print(f"\n{'='*80}")
    print(f"VISUALIZATION")
    print(f"{'='*80}\n")

    print(f"To visualize the structure:")
    print(f"\n  # PyMOL")
    print(f"  pymol {best['structure_file']}\n")
    print(f"  # ChimeraX")
    print(f"  chimerax {best['structure_file']}\n")

    print(f"Look for:")
    print(f"  - Nucleotide positioned in binding pocket")
    print(f"  - Hydrogen bonds between nanobody and nucleotide")
    print(f"  - Proper coordination of phosphate groups")
    print(f"  - Well-structured CDR loops")

    return best


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Boltz predictions"
    )
    parser.add_argument(
        "prediction_dir",
        help="Directory containing predictions (e.g., results/dATP_production/boltz_results_dATP_binder/predictions/dATP_binder)"
    )

    args = parser.parse_args()

    pred_path = Path(args.prediction_dir)
    if not pred_path.exists():
        print(f"ERROR: Directory not found: {pred_path}")
        return

    prediction_name = pred_path.name
    results = analyze_prediction(pred_path)

    if results:
        best = print_analysis(results, prediction_name)

        # Save summary
        summary_file = pred_path / "analysis_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Best Model: {best['model']}\n")
            f.write(f"Confidence Score: {best['confidence_score']:.4f}\n")
            f.write(f"Ligand iPTM: {best['ligand_iptm']:.4f}\n")
            f.write(f"Structure: {best['structure_file']}\n")

        print(f"\nSummary saved to: {summary_file}")


if __name__ == "__main__":
    main()
