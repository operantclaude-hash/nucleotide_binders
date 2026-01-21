#!/usr/bin/env python3
"""
Generate static structure visualizations without PyMOL.
Uses matplotlib and BioPython for basic structure rendering.
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

def load_cif_basic_info(cif_file):
    """Extract basic info from CIF file."""
    try:
        with open(cif_file, 'r') as f:
            lines = f.readlines()

        # Count atoms
        n_atoms = sum(1 for line in lines if line.startswith('ATOM'))

        # Try to find chains
        chains = set()
        for line in lines:
            if line.startswith('ATOM'):
                parts = line.split()
                if len(parts) > 6:
                    chains.add(parts[6])

        return {
            'n_atoms': n_atoms,
            'chains': sorted(chains),
            'file_size': Path(cif_file).stat().st_size
        }
    except Exception as e:
        return {'error': str(e)}

def visualize_binding_overview(results_json, output_dir):
    """Create overview visualization of binding results."""

    with open(results_json, 'r') as f:
        data = json.load(f)

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Extract data
    variants = []
    for result in data:
        variant_id = result['variant_id']
        target = result['target']
        conf = result['confidence_metrics']

        variants.append({
            'name': variant_id,
            'nucleotide': target,
            'confidence': conf['confidence_score'],
            'ligand_iptm': conf['ligand_iptm'],
            'plddt': conf['complex_plddt']
        })

    # Sort by confidence
    variants = sorted(variants, key=lambda x: x['confidence'], reverse=True)

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Top 4 Nucleotide Binder Predictions', fontsize=16, fontweight='bold')

    for idx, (var, ax) in enumerate(zip(variants[:4], axes.flat)):
        # Create bar chart of metrics
        metrics = ['Confidence', 'Ligand iPTM', 'pLDDT']
        values = [var['confidence'], var['ligand_iptm'], var['plddt']]
        colors = ['#2ecc71' if v > 0.85 else '#f39c12' if v > 0.70 else '#e74c3c' for v in values]

        bars = ax.barh(metrics, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, val in zip(bars, values):
            width = bar.get_width()
            ax.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                   f'{val:.3f}', ha='left', va='center', fontsize=11, fontweight='bold')

        # Add threshold lines
        ax.axvline(0.85, color='green', linestyle='--', alpha=0.5, linewidth=2, label='High confidence')
        ax.axvline(0.70, color='orange', linestyle='--', alpha=0.5, linewidth=2, label='Medium confidence')

        ax.set_xlim(0, 1.0)
        ax.set_xlabel('Score', fontsize=12, fontweight='bold')
        ax.set_title(f"{var['name']}\nTarget: {var['nucleotide']}",
                    fontsize=12, fontweight='bold', pad=10)
        ax.grid(axis='x', alpha=0.3)

        if idx == 0:
            ax.legend(loc='lower right', fontsize=9)

    plt.tight_layout()
    output_file = output_dir / 'top_binders_metrics_overview.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

    # Create detailed comparison plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    # Prepare data for scatter plot
    x_vals = [v['confidence'] for v in variants[:4]]
    y_vals = [v['ligand_iptm'] for v in variants[:4]]
    sizes = [v['plddt'] * 500 for v in variants[:4]]
    labels = [v['name'].replace('_variant_', '\nv') for v in variants[:4]]
    nucleotides = [v['nucleotide'] for v in variants[:4]]

    # Color by nucleotide
    color_map = {'dATP': '#3498db', 'dTTP': '#e74c3c', 'dGTP': '#2ecc71', 'dCTP': '#f39c12'}
    colors = [color_map.get(n, 'gray') for n in nucleotides]

    scatter = ax.scatter(x_vals, y_vals, s=sizes, c=colors, alpha=0.6,
                        edgecolors='black', linewidth=2)

    # Add labels
    for i, (x, y, label) in enumerate(zip(x_vals, y_vals, labels)):
        ax.annotate(label, (x, y), xytext=(10, 10), textcoords='offset points',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[i], alpha=0.3),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=1.5))

    # Add threshold lines
    ax.axvline(0.85, color='green', linestyle='--', alpha=0.5, linewidth=2, label='High confidence threshold')
    ax.axhline(0.80, color='blue', linestyle='--', alpha=0.5, linewidth=2, label='High iPTM threshold')

    ax.set_xlabel('Confidence Score', fontsize=14, fontweight='bold')
    ax.set_ylabel('Ligand iPTM', fontsize=14, fontweight='bold')
    ax.set_title('Binding Prediction Quality\n(Bubble size = pLDDT)',
                fontsize=16, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)

    ax.set_xlim(0.82, 0.92)
    ax.set_ylim(0.75, 0.90)

    plt.tight_layout()
    output_file = output_dir / 'binding_quality_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

    # Create architecture diagram
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    y_positions = [3.5, 2.5, 1.5, 0.5]

    for idx, (var, y_pos) in enumerate(zip(variants[:4], y_positions)):
        # Main box for the variant
        rect = Rectangle((0, y_pos-0.3), 10, 0.6,
                        facecolor=color_map.get(var['nucleotide'], 'gray'),
                        edgecolor='black', linewidth=2, alpha=0.3)
        ax.add_patch(rect)

        # Add text
        ax.text(0.5, y_pos, var['name'], fontsize=11, fontweight='bold', va='center')
        ax.text(5, y_pos, f"Conf: {var['confidence']:.3f}", fontsize=10, va='center')
        ax.text(7.5, y_pos, f"iPTM: {var['ligand_iptm']:.3f}", fontsize=10, va='center')

        # Add checkmark or warning
        if var['confidence'] > 0.85 and var['ligand_iptm'] > 0.80:
            ax.text(9.5, y_pos, '✓', fontsize=20, color='green', va='center', ha='center', fontweight='bold')
        else:
            ax.text(9.5, y_pos, '⚠', fontsize=18, color='orange', va='center', ha='center')

    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.2, 4.2)
    ax.axis('off')
    ax.set_title('Top 4 Binders - Quick Reference', fontsize=16, fontweight='bold', pad=20)

    # Add legend
    legend_text = """
    ✓ = High confidence (>0.85) + Good binding (iPTM >0.80)
    ⚠ = Review carefully

    Colors: Blue=dATP, Red=dTTP, Green=dGTP, Orange=dCTP
    """
    ax.text(0.5, -0.5, legend_text, fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()
    output_file = output_dir / 'quick_reference.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_file}")
    plt.close()

    print("\n✓ Generated 3 static visualization images!")
    return True


def main():
    """Generate static visualizations."""

    print("="*80)
    print("GENERATING STATIC STRUCTURE VISUALIZATIONS")
    print("="*80)
    print()

    results_json = Path.home() / "nucleotide_catchers/specificity_library/visualizations/binding_analysis_summary.json"
    output_dir = Path.home() / "nucleotide_catchers/specificity_library/visualizations/static_images"

    if not results_json.exists():
        print(f"❌ Results file not found: {results_json}")
        return

    visualize_binding_overview(results_json, output_dir)

    print()
    print("="*80)
    print("VISUALIZATION COMPLETE")
    print("="*80)
    print()
    print(f"Output directory: {output_dir}/")
    print()
    print("Generated files:")
    print("  1. top_binders_metrics_overview.png - Bar charts of all metrics")
    print("  2. binding_quality_comparison.png - Scatter plot comparison")
    print("  3. quick_reference.png - Quick reference card")
    print()
    print("To view:")
    print(f"  eog {output_dir}/*.png")
    print("  or")
    print(f"  firefox {output_dir}/*.png")
    print()

if __name__ == "__main__":
    main()
