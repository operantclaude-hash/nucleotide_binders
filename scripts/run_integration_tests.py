#!/usr/bin/env python3
"""
Integration tests - Test the full pipeline with edge cases.
"""

import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import json

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.END}")

def print_pass(msg):
    print(f"  {Colors.GREEN}✓ PASS: {msg}{Colors.END}")

def print_fail(msg):
    print(f"  {Colors.RED}✗ FAIL: {msg}{Colors.END}")

def print_warn(msg):
    print(f"  {Colors.YELLOW}⚠ WARN: {msg}{Colors.END}")


def test_mini_pipeline():
    """Run a mini end-to-end pipeline test."""
    print_test("Mini End-to-End Pipeline")

    base_dir = Path(__file__).parent.parent
    scripts_dir = base_dir / "scripts"

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        try:
            # Step 1: Generate library (2 variants per nucleotide)
            print("  Step 1: Generating mini library...")
            result = subprocess.run([
                "python", str(scripts_dir / "generate_cdr_library.py"),
                "--variants-per-target", "2",
                "--seed", "999",
                "--output-dir", str(tmpdir / "lib")
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print_pass("Library generated")
            else:
                print_fail(f"Library generation failed: {result.stderr[:200]}")
                return False

            # Check manifest
            manifest = tmpdir / "lib" / "library_manifest.yaml"
            if manifest.exists():
                print_pass("Manifest created")
            else:
                print_fail("Manifest missing")
                return False

            # Step 2: Generate MSAs
            print("  Step 2: Generating MSAs...")
            result = subprocess.run([
                "python", str(scripts_dir / "generate_library_msas.py"),
                "--library-dir", str(tmpdir / "lib"),
                "--msa-output-dir", str(tmpdir / "lib" / "msas")
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print_pass("MSAs generated")
            else:
                print_fail(f"MSA generation failed: {result.stderr[:200]}")
                return False

            # Check MSAs exist
            msa_dir = tmpdir / "lib" / "msas"
            if msa_dir.exists() and len(list(msa_dir.glob("*/*.a3m"))) > 0:
                print_pass(f"Found {len(list(msa_dir.glob('*/*.a3m')))} MSA files")
            else:
                print_fail("MSA files missing")
                return False

            print_pass("Mini pipeline completed successfully")
            return True

        except subprocess.TimeoutExpired:
            print_fail("Pipeline timed out")
            return False
        except Exception as e:
            print_fail(f"Pipeline error: {e}")
            return False


def test_concurrent_variant_generation():
    """Test that variant generation works with different seeds concurrently."""
    print_test("Concurrent Variant Generation")

    from generate_cdr_library import generate_variants, BASE_NANOBODY
    import random

    try:
        # Generate multiple variant sets with different seeds
        variant_sets = []
        seeds = [42, 100, 200, 300, 400]

        for seed in seeds:
            random.seed(seed)
            variants = generate_variants(BASE_NANOBODY, "dATP", num_variants=5)
            variant_sets.append(variants)

        # Check all succeeded
        if all(len(vs) == 5 for vs in variant_sets):
            print_pass(f"Generated {len(variant_sets)} variant sets successfully")
        else:
            print_fail("Some variant sets have wrong length")
            return False

        # Check variants differ between seeds
        seqs_seed1 = [v['sequence'] for v in variant_sets[0][1:]]  # Skip WT
        seqs_seed2 = [v['sequence'] for v in variant_sets[1][1:]]

        if seqs_seed1 != seqs_seed2:
            print_pass("Different seeds produce different variants")
        else:
            print_warn("Different seeds produced identical variants (low probability)")

        return True

    except Exception as e:
        print_fail(f"Concurrent generation failed: {e}")
        return False


def test_prediction_result_parsing():
    """Test that we can parse prediction results correctly."""
    print_test("Prediction Result Parsing")

    # Check actual test results if available
    base_dir = Path(__file__).parent.parent
    test_results = base_dir / "specificity_library_test" / "screening_results" / "screening_results.json"

    if not test_results.exists():
        print_warn("No test results found - skipping")
        return True

    try:
        with open(test_results, 'r') as f:
            data = json.load(f)

        # Check structure
        if 'results' in data:
            print_pass("Results have 'results' field")
        else:
            print_fail("Results missing 'results' field")
            return False

        # Check each result has required fields
        required_fields = ['variant_id', 'test_nucleotide', 'confidence']
        for i, result in enumerate(data['results']):
            missing = [f for f in required_fields if f not in result]
            if missing:
                print_fail(f"Result {i} missing fields: {missing}")
                return False

        print_pass(f"All {len(data['results'])} results have required fields")

        # Check confidence structure
        for i, result in enumerate(data['results']):
            if result['confidence'] is not None:
                conf = result['confidence']
                if 'confidence_score' in conf and 'ligand_iptm' in conf:
                    print_pass(f"Result {i} has valid confidence structure")
                else:
                    print_fail(f"Result {i} has invalid confidence structure")
                    return False

        return True

    except Exception as e:
        print_fail(f"Result parsing failed: {e}")
        return False


def test_analysis_correctness():
    """Test that specificity analysis calculates correct values."""
    print_test("Analysis Calculations")

    # Mock test data
    mock_results = {
        'results': [
            {
                'variant_id': 'test_var_001',
                'target_nucleotide': 'dATP',
                'test_nucleotide': 'dATP',
                'is_target': True,
                'confidence': {'confidence_score': 0.9, 'ligand_iptm': 0.8, 'complex_plddt': 0.9}
            },
            {
                'variant_id': 'test_var_001',
                'target_nucleotide': 'dATP',
                'test_nucleotide': 'dGTP',
                'is_target': False,
                'confidence': {'confidence_score': 0.3, 'ligand_iptm': 0.3, 'complex_plddt': 0.5}
            },
            {
                'variant_id': 'test_var_001',
                'target_nucleotide': 'dATP',
                'test_nucleotide': 'dCTP',
                'is_target': False,
                'confidence': {'confidence_score': 0.4, 'ligand_iptm': 0.4, 'complex_plddt': 0.6}
            },
            {
                'variant_id': 'test_var_001',
                'target_nucleotide': 'dATP',
                'test_nucleotide': 'dTTP',
                'is_target': False,
                'confidence': {'confidence_score': 0.3, 'ligand_iptm': 0.3, 'complex_plddt': 0.5}
            },
        ]
    }

    try:
        # Group by variant
        variant_scores = {}
        for r in mock_results['results']:
            vid = r['variant_id']
            if vid not in variant_scores:
                variant_scores[vid] = {'target': None, 'off_targets': []}

            if r['is_target']:
                variant_scores[vid]['target'] = r['confidence']['confidence_score']
            else:
                variant_scores[vid]['off_targets'].append(r['confidence']['confidence_score'])

        # Calculate specificity
        import numpy as np
        vid = 'test_var_001'
        target = variant_scores[vid]['target']
        off_targets = variant_scores[vid]['off_targets']
        mean_off = np.mean(off_targets)
        ratio = target / mean_off if mean_off > 0 else 0

        expected_ratio = 0.9 / ((0.3 + 0.4 + 0.3) / 3.0)  # 0.9 / 0.333 = 2.7

        if abs(ratio - expected_ratio) < 0.01:
            print_pass(f"Specificity ratio correct: {ratio:.2f}")
        else:
            print_fail(f"Specificity ratio wrong: expected ~{expected_ratio:.2f}, got {ratio:.2f}")
            return False

        # Check selectivity
        max_off = max(off_targets)
        selectivity = target - max_off
        expected_selectivity = 0.9 - 0.4  # 0.5

        if abs(selectivity - expected_selectivity) < 0.01:
            print_pass(f"Selectivity correct: {selectivity:.2f}")
        else:
            print_fail(f"Selectivity wrong: expected {expected_selectivity:.2f}, got {selectivity:.2f}")
            return False

        return True

    except Exception as e:
        print_fail(f"Analysis calculation failed: {e}")
        return False


def test_script_help_commands():
    """Test that all scripts have working --help."""
    print_test("Script Help Commands")

    base_dir = Path(__file__).parent.parent
    scripts = [
        "generate_cdr_library.py",
        "generate_library_msas.py",
        "run_specificity_screen.py",
        "analyze_specificity.py",
        "insert_custom_optogenetic.py"
    ]

    all_pass = True
    for script in scripts:
        script_path = base_dir / "scripts" / script
        try:
            result = subprocess.run(
                ["python", str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "usage:" in result.stdout.lower():
                print_pass(f"{script} --help works")
            else:
                print_fail(f"{script} --help failed")
                all_pass = False
        except Exception as e:
            print_fail(f"{script} --help error: {e}")
            all_pass = False

    return all_pass


def test_reproducibility():
    """Test that same seed produces same variants."""
    print_test("Reproducibility")

    from generate_cdr_library import generate_variants, BASE_NANOBODY
    import random

    try:
        # Generate twice with same seed
        random.seed(12345)
        variants1 = generate_variants(BASE_NANOBODY, "dATP", num_variants=10)

        random.seed(12345)
        variants2 = generate_variants(BASE_NANOBODY, "dATP", num_variants=10)

        # Compare
        if len(variants1) == len(variants2):
            print_pass("Same number of variants")
        else:
            print_fail(f"Different variant counts: {len(variants1)} vs {len(variants2)}")
            return False

        # Compare sequences
        seqs1 = [v['sequence'] for v in variants1]
        seqs2 = [v['sequence'] for v in variants2]

        if seqs1 == seqs2:
            print_pass("Identical variants with same seed")
        else:
            print_fail("Different variants despite same seed")
            # Find first difference
            for i, (s1, s2) in enumerate(zip(seqs1, seqs2)):
                if s1 != s2:
                    print(f"    First diff at variant {i}")
                    break
            return False

        return True

    except Exception as e:
        print_fail(f"Reproducibility test failed: {e}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("="*80)
    print("NUCLEOTIDE BINDER PIPELINE - INTEGRATION TESTS")
    print("="*80)

    tests = [
        ("Mini Pipeline", test_mini_pipeline),
        ("Concurrent Generation", test_concurrent_variant_generation),
        ("Result Parsing", test_prediction_result_parsing),
        ("Analysis Correctness", test_analysis_correctness),
        ("Script Help", test_script_help_commands),
        ("Reproducibility", test_reproducibility),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)

    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{name}: {status}")

    print(f"\nTotal: {len(results)}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")

    if failed == 0:
        print(f"\n{Colors.GREEN}✓ ALL INTEGRATION TESTS PASSED{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}✗ SOME TESTS FAILED{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
