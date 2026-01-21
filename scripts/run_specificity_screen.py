#!/usr/bin/env python3
"""
Run batch Boltz predictions for specificity screening.
Tests each variant against all 4 nucleotides to assess specificity.
"""

import subprocess
import yaml
import json
from pathlib import Path
import argparse
import time
from datetime import datetime


def load_manifest(library_dir):
    """Load library manifest."""
    manifest_file = Path(library_dir) / "library_manifest.yaml"
    with open(manifest_file, 'r') as f:
        return yaml.safe_load(f)


def run_boltz_prediction(config_file, output_dir, devices=1, quick_mode=False):
    """
    Run a single Boltz prediction.

    Returns:
        (success, prediction_dir, elapsed_time)
    """
    start_time = time.time()

    # Set parameters based on mode
    if quick_mode:
        diffusion_samples = 1
        sampling_steps = 50
        recycling_steps = 1
    else:
        diffusion_samples = 3
        sampling_steps = 150
        recycling_steps = 2

    cmd = [
        "boltz", "predict", str(config_file),
        "--out_dir", str(output_dir),
        "--devices", str(devices),
        "--accelerator", "gpu",
        "--diffusion_samples", str(diffusion_samples),
        "--sampling_steps", str(sampling_steps),
        "--recycling_steps", str(recycling_steps),
        "--write_full_pae"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per prediction
        )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            # Find prediction directory
            output_path = Path(output_dir)
            pred_dirs = list(output_path.glob("boltz_results_*"))
            if pred_dirs:
                return True, pred_dirs[0], elapsed
            else:
                return False, None, elapsed
        else:
            print(f"  ERROR: {result.stderr[:200]}")
            return False, None, elapsed

    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after 10 minutes")
        return False, None, time.time() - start_time
    except Exception as e:
        print(f"  EXCEPTION: {str(e)[:200]}")
        return False, None, time.time() - start_time


def extract_confidence(prediction_dir):
    """Extract confidence metrics from prediction directory."""
    pred_path = Path(prediction_dir)

    # Find confidence JSON files
    confidence_files = list(pred_path.rglob("confidence_*_model_*.json"))

    if not confidence_files:
        return None

    # Use best model (model_0)
    best_conf_file = None
    for cf in confidence_files:
        if "model_0" in cf.name:
            best_conf_file = cf
            break

    if not best_conf_file:
        best_conf_file = confidence_files[0]

    with open(best_conf_file, 'r') as f:
        return json.load(f)


def run_batch_predictions(library_dir, results_dir, quick_mode=False, limit=None):
    """
    Run predictions for all variant-nucleotide combinations.

    Args:
        library_dir: Library directory
        results_dir: Results output directory
        quick_mode: Use faster settings
        limit: Limit number of predictions (for testing)
    """
    print("="*80)
    print("SPECIFICITY SCREENING - BATCH PREDICTIONS")
    print("="*80)
    print()

    library_path = Path(library_dir)
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)

    # Load manifest
    manifest = load_manifest(library_dir)
    configs = manifest['configs']

    if limit:
        configs = configs[:limit]
        print(f"LIMIT MODE: Running only {limit} predictions\n")

    total = len(configs)
    print(f"Total predictions to run: {total}")
    print(f"Mode: {'QUICK' if quick_mode else 'PRODUCTION'}")
    print(f"Estimated time: {total * (3 if quick_mode else 8)} minutes\n")

    # Run predictions
    results = []
    success_count = 0
    fail_count = 0

    start_time = time.time()

    for i, config_info in enumerate(configs, 1):
        config_file = Path(library_dir) / "configs_with_msas" / Path(config_info['config_file']).name
        variant_id = config_info['variant_id']
        test_nuc = config_info['test_nucleotide']
        is_target = config_info['is_target']

        print(f"\n[{i}/{total}] {variant_id} vs {test_nuc} {'[TARGET]' if is_target else '[OFF-TARGET]'}")
        print(f"  Config: {config_file.name}")

        if not config_file.exists():
            print(f"  ERROR: Config not found!")
            fail_count += 1
            continue

        # Run prediction
        output_dir = results_path / f"{variant_id}_vs_{test_nuc}"
        success, pred_dir, elapsed = run_boltz_prediction(
            config_file, output_dir, devices=1, quick_mode=quick_mode
        )

        if success:
            print(f"  ✓ Success in {elapsed:.1f}s")

            # Extract confidence
            confidence = extract_confidence(pred_dir)

            result = {
                "variant_id": variant_id,
                "target_nucleotide": config_info['target_nucleotide'],
                "test_nucleotide": test_nuc,
                "is_target": is_target,
                "mutations": config_info['mutations'],
                "prediction_dir": str(pred_dir),
                "confidence": confidence,
                "elapsed_time": elapsed
            }

            results.append(result)
            success_count += 1

            # Print key metrics
            if confidence:
                print(f"  Confidence: {confidence['confidence_score']:.3f}")
                print(f"  Ligand iPTM: {confidence['ligand_iptm']:.3f}")

        else:
            print(f"  ✗ Failed")
            fail_count += 1

        # Save intermediate results
        if i % 10 == 0 or i == total:
            intermediate_file = results_path / "results_intermediate.json"
            with open(intermediate_file, 'w') as f:
                json.dump(results, f, indent=2)

    total_time = time.time() - start_time

    # Save final results
    final_results = {
        "timestamp": datetime.now().isoformat(),
        "total_predictions": total,
        "successful": success_count,
        "failed": fail_count,
        "total_time_seconds": total_time,
        "mode": "quick" if quick_mode else "production",
        "results": results
    }

    results_file = results_path / "screening_results.json"
    with open(results_file, 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\n{'='*80}")
    print("BATCH PREDICTIONS COMPLETE")
    print(f"{'='*80}\n")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Success: {success_count}/{total}")
    print(f"Failed: {fail_count}/{total}")
    print(f"Results saved: {results_file}\n")

    print("Next step: Analyze specificity")
    print("  python analyze_specificity.py")


def main():
    parser = argparse.ArgumentParser(
        description="Run batch predictions for specificity screening"
    )
    parser.add_argument(
        "--library-dir",
        default="../specificity_library",
        help="Library directory"
    )
    parser.add_argument(
        "--results-dir",
        default="../specificity_library/screening_results",
        help="Results output directory"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode (faster but lower quality)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of predictions (for testing)"
    )

    args = parser.parse_args()

    run_batch_predictions(
        args.library_dir,
        args.results_dir,
        quick_mode=args.quick,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
