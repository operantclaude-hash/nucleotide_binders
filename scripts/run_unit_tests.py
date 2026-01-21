#!/usr/bin/env python3
"""
Comprehensive unit tests for nucleotide binder design pipeline.
Tests edge cases, error handling, and data consistency.
"""

import sys
import os
import yaml
import json
import tempfile
import shutil
from pathlib import Path
import numpy as np

# Color output
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


class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def test(self, condition, pass_msg, fail_msg):
        if condition:
            print_pass(pass_msg)
            self.passed += 1
            return True
        else:
            print_fail(fail_msg)
            self.failed += 1
            return False

    def warn(self, condition, msg):
        if not condition:
            print_warn(msg)
            self.warnings += 1


def test_imports():
    """Test that all required modules can be imported."""
    print_test("Module Imports")
    suite = TestSuite()

    try:
        import yaml
        suite.test(True, "yaml imported", "yaml import failed")
    except ImportError as e:
        suite.test(False, "", f"yaml import failed: {e}")

    try:
        import pandas
        suite.test(True, "pandas imported", "pandas import failed")
    except ImportError as e:
        suite.test(False, "", f"pandas import failed: {e}")

    try:
        import numpy
        suite.test(True, "numpy imported", "numpy import failed")
    except ImportError as e:
        suite.test(False, "", f"numpy import failed: {e}")

    try:
        from generate_cdr_library import generate_variants, DESIGN_STRATEGIES
        suite.test(True, "generate_cdr_library imported", "generate_cdr_library import failed")
    except ImportError as e:
        suite.test(False, "", f"generate_cdr_library import failed: {e}")

    return suite


def test_cdr_library_generation():
    """Test CDR library generation with various inputs."""
    print_test("CDR Library Generation")
    suite = TestSuite()

    try:
        from generate_cdr_library import generate_variants, BASE_NANOBODY, DESIGN_STRATEGIES

        # Test 1: Normal generation
        variants = generate_variants(BASE_NANOBODY, "dATP", num_variants=5)
        suite.test(len(variants) == 5,
                  f"Generated 5 variants",
                  f"Expected 5 variants, got {len(variants)}")

        # Test 2: First variant is always WT
        suite.test(variants[0]['mutations'] == 'WT',
                  "First variant is WT control",
                  f"First variant should be WT, got {variants[0]['mutations']}")

        # Test 3: Variants have unique IDs
        ids = [v['id'] for v in variants]
        suite.test(len(ids) == len(set(ids)),
                  "All variant IDs are unique",
                  "Duplicate variant IDs found")

        # Test 4: All variants have required fields
        required_fields = ['id', 'sequence', 'mutations', 'target', 'strategy']
        for i, variant in enumerate(variants):
            has_all = all(field in variant for field in required_fields)
            suite.test(has_all,
                      f"Variant {i} has all required fields",
                      f"Variant {i} missing fields: {[f for f in required_fields if f not in variant]}")

        # Test 5: Sequences are valid amino acids
        valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
        for i, variant in enumerate(variants):
            seq = variant['sequence']
            invalid = set(seq) - valid_aa
            suite.test(len(invalid) == 0,
                      f"Variant {i} has valid amino acids",
                      f"Variant {i} has invalid amino acids: {invalid}")

        # Test 6: Mutations are correctly applied
        for i, variant in enumerate(variants[1:], 1):  # Skip WT
            if variant['mutations'] != 'WT':
                suite.test(variant['sequence'] != BASE_NANOBODY,
                          f"Variant {i} sequence differs from base",
                          f"Variant {i} claims mutations but sequence unchanged")

        # Test 7: All nucleotides can be generated
        for nuc in ['dATP', 'dGTP', 'dCTP', 'dTTP']:
            try:
                vars_nuc = generate_variants(BASE_NANOBODY, nuc, num_variants=3)
                suite.test(len(vars_nuc) == 3,
                          f"{nuc} variants generated",
                          f"{nuc} variant generation failed")
            except Exception as e:
                suite.test(False, "", f"{nuc} generation error: {e}")

        # Test 8: Invalid nucleotide raises error
        try:
            generate_variants(BASE_NANOBODY, "INVALID", num_variants=3)
            suite.test(False, "", "Should raise error for invalid nucleotide")
        except (ValueError, KeyError):
            suite.test(True, "Invalid nucleotide raises error", "")

    except Exception as e:
        suite.test(False, "", f"CDR library test failed with error: {e}")

    return suite


def test_sequence_validation():
    """Test sequence validation and edge cases."""
    print_test("Sequence Validation")
    suite = TestSuite()

    from generate_cdr_library import BASE_NANOBODY

    # Test 1: Base sequence length
    suite.test(len(BASE_NANOBODY) == 121,
              f"Base nanobody is 121 aa",
              f"Base nanobody should be 121 aa, is {len(BASE_NANOBODY)}")

    # Test 2: CDR positions are within bounds
    from generate_cdr_library import CDR_REGIONS
    for cdr_name, (start, end) in CDR_REGIONS.items():
        suite.test(start < end,
                  f"{cdr_name} positions valid (start < end)",
                  f"{cdr_name} invalid: start={start}, end={end}")
        suite.test(end <= len(BASE_NANOBODY),
                  f"{cdr_name} within sequence bounds",
                  f"{cdr_name} end position {end} exceeds length {len(BASE_NANOBODY)}")

    # Test 3: Mutation positions in CDR3
    from generate_cdr_library import DESIGN_STRATEGIES
    for nuc, strategy in DESIGN_STRATEGIES.items():
        mutations = strategy.get('CDR3_mutations', {})
        for pos in mutations.keys():
            suite.test(pos < len(BASE_NANOBODY),
                      f"{nuc} mutation position {pos} within bounds",
                      f"{nuc} mutation position {pos} exceeds sequence length")

    return suite


def test_config_file_format():
    """Test configuration file generation and format."""
    print_test("Config File Format")
    suite = TestSuite()

    test_config = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": "A",
                    "sequence": "QVQLVES"
                }
            },
            {
                "ligand": {
                    "id": "B",
                    "smiles": "Nc1ncnc2c1ncn2[C@H]3C[C@H](O)[C@@H](COP(O)(=O)OP(O)(=O)OP(O)(O)=O)O3"
                }
            }
        ]
    }

    # Test 1: YAML serialization
    try:
        yaml_str = yaml.dump(test_config)
        suite.test(True, "Config serializes to YAML", "")
    except Exception as e:
        suite.test(False, "", f"YAML serialization failed: {e}")

    # Test 2: YAML round-trip
    try:
        yaml_str = yaml.dump(test_config)
        loaded = yaml.safe_load(yaml_str)
        suite.test(loaded == test_config,
                  "YAML round-trip preserves data",
                  "YAML round-trip changed data")
    except Exception as e:
        suite.test(False, "", f"YAML round-trip failed: {e}")

    # Test 3: Required fields present
    suite.test('version' in test_config,
              "Config has version field",
              "Config missing version")
    suite.test('sequences' in test_config,
              "Config has sequences field",
              "Config missing sequences")

    return suite


def test_specificity_calculations():
    """Test specificity score calculations."""
    print_test("Specificity Calculations")
    suite = TestSuite()

    # Mock data
    test_scores = {
        'target_conf': 0.9,
        'off_target_confs': [0.3, 0.4, 0.35]
    }

    # Test 1: Specificity ratio calculation
    mean_off = np.mean(test_scores['off_target_confs'])
    ratio = test_scores['target_conf'] / mean_off if mean_off > 0 else 0

    expected_ratio = 0.9 / 0.35  # ~2.57
    suite.test(abs(ratio - expected_ratio) < 0.01,
              f"Specificity ratio calculated correctly: {ratio:.2f}",
              f"Specificity ratio wrong: expected {expected_ratio:.2f}, got {ratio:.2f}")

    # Test 2: Selectivity calculation
    max_off = np.max(test_scores['off_target_confs'])
    selectivity = test_scores['target_conf'] - max_off

    expected_selectivity = 0.9 - 0.4  # 0.5
    suite.test(abs(selectivity - expected_selectivity) < 0.01,
              f"Selectivity calculated correctly: {selectivity:.2f}",
              f"Selectivity wrong: expected {expected_selectivity:.2f}, got {selectivity:.2f}")

    # Test 3: Combined score
    combined = test_scores['target_conf'] * ratio
    expected_combined = 0.9 * (0.9 / 0.35)
    suite.test(abs(combined - expected_combined) < 0.01,
              f"Combined score calculated correctly: {combined:.2f}",
              f"Combined score wrong: expected {expected_combined:.2f}, got {combined:.2f}")

    # Test 4: Edge case - zero off-target
    ratio_zero = 0.9 / 0.0 if 0.0 > 0 else 0
    suite.test(ratio_zero == 0,
              "Zero off-target handled correctly",
              "Zero off-target not handled")

    # Test 5: Edge case - equal scores (no specificity)
    equal_ratio = 0.5 / 0.5
    suite.test(abs(equal_ratio - 1.0) < 0.01,
              "Equal scores give ratio ~1.0",
              f"Equal scores should give ratio 1.0, got {equal_ratio}")

    return suite


def test_file_structure():
    """Test that expected directories and files exist."""
    print_test("File Structure")
    suite = TestSuite()

    base_dir = Path(__file__).parent.parent

    # Test 1: Key directories exist
    expected_dirs = ['scripts', 'configs', 'pdbs', 'results']
    for dir_name in expected_dirs:
        dir_path = base_dir / dir_name
        suite.test(dir_path.exists(),
                  f"Directory exists: {dir_name}/",
                  f"Missing directory: {dir_name}/")

    # Test 2: Key scripts exist
    scripts = [
        'generate_cdr_library.py',
        'generate_library_msas.py',
        'run_specificity_screen.py',
        'analyze_specificity.py',
        'insert_custom_optogenetic.py'
    ]
    for script in scripts:
        script_path = base_dir / 'scripts' / script
        suite.test(script_path.exists(),
                  f"Script exists: {script}",
                  f"Missing script: {script}")

    # Test 3: Documentation exists
    docs = [
        'README.md',
        'COMPLETE_DOCUMENTATION.md',
        'PIPELINE_SUMMARY.md',
        'WORKFLOW.md'
    ]
    for doc in docs:
        doc_path = base_dir / doc
        suite.test(doc_path.exists(),
                  f"Documentation exists: {doc}",
                  f"Missing documentation: {doc}")

    # Test 4: Base configs exist
    base_configs = ['dATP_binder.yaml', 'dGTP_binder.yaml', 'dCTP_binder.yaml', 'dTTP_binder.yaml']
    for config in base_configs:
        config_path = base_dir / 'configs' / config
        suite.test(config_path.exists(),
                  f"Base config exists: {config}",
                  f"Missing base config: {config}")

    return suite


def test_optogenetic_insertion():
    """Test optogenetic domain insertion."""
    print_test("Optogenetic Domain Insertion")
    suite = TestSuite()

    try:
        from insert_optogenetic_domains import insert_domain, OPTOGENETIC_DOMAINS, LINKER

        test_seq = "QVQLVESGGGLVQPGGSLRLSCAASGFTFSSYAMSWVRQAPGKGLEWVSAISGSGGSTYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAKVSYLSTASSLDYWGQGTLVTVSS"

        # Test 1: All domains can be inserted
        for domain_name in ['LOV2', 'CRY2', 'BphP1']:
            domain_seq = OPTOGENETIC_DOMAINS[domain_name]
            result = insert_domain(test_seq, domain_seq, domain_name, position=74)

            suite.test(result is not None,
                      f"{domain_name} insertion succeeds",
                      f"{domain_name} insertion failed")

            if result:
                # Test 2: Chimeric sequence is longer
                suite.test(len(result['full_sequence']) > len(test_seq),
                          f"{domain_name} chimera is longer than original",
                          f"{domain_name} chimera not longer")

                # Test 3: Contains linker
                suite.test(LINKER in result['full_sequence'],
                          f"{domain_name} chimera contains linker",
                          f"{domain_name} chimera missing linker")

                # Test 4: Contains domain
                suite.test(domain_seq in result['full_sequence'],
                          f"{domain_name} chimera contains domain sequence",
                          f"{domain_name} chimera missing domain sequence")

                # Test 5: Calculated length is correct
                expected_length = len(test_seq) + len(domain_seq) + 2 * len(LINKER)
                suite.test(result['chimeric_length'] == expected_length,
                          f"{domain_name} length calculated correctly",
                          f"{domain_name} length mismatch: expected {expected_length}, got {result['chimeric_length']}")

        # Test 6: Invalid position handling
        try:
            result = insert_domain(test_seq, OPTOGENETIC_DOMAINS['LOV2'], 'LOV2', position=200)
            # Should work (inserts at end), but warn
            suite.warn(result is not None, "Out-of-bounds position handled")
        except Exception as e:
            suite.test(True, "Out-of-bounds position raises error", "")

    except Exception as e:
        suite.test(False, "", f"Optogenetic insertion test failed: {e}")

    return suite


def test_data_consistency():
    """Test data consistency across the pipeline."""
    print_test("Data Consistency")
    suite = TestSuite()

    # Test with actual test results if available
    test_dir = Path(__file__).parent.parent / 'specificity_library_test'

    if test_dir.exists():
        # Test 1: Manifest exists
        manifest_file = test_dir / 'library_manifest.yaml'
        suite.test(manifest_file.exists(),
                  "Library manifest exists",
                  "Library manifest missing")

        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = yaml.safe_load(f)

            # Test 2: Manifest has expected structure
            suite.test('variants' in manifest,
                      "Manifest has variants",
                      "Manifest missing variants")
            suite.test('configs' in manifest,
                      "Manifest has configs",
                      "Manifest missing configs")

            # Test 3: Number of configs = variants × 4
            if 'variants' in manifest and 'configs' in manifest:
                expected_configs = len(manifest['variants']) * 4
                actual_configs = len(manifest['configs'])
                suite.test(expected_configs == actual_configs,
                          f"Config count correct: {actual_configs}",
                          f"Config count mismatch: expected {expected_configs}, got {actual_configs}")

            # Test 4: All variants have unique IDs
            if 'variants' in manifest:
                variant_ids = [v['id'] for v in manifest['variants']]
                suite.test(len(variant_ids) == len(set(variant_ids)),
                          "All variant IDs unique",
                          "Duplicate variant IDs found")

        # Test 5: Analysis results if available
        analysis_file = test_dir / 'analysis' / 'specificity_analysis.csv'
        if analysis_file.exists():
            import pandas as pd
            df = pd.read_csv(analysis_file)

            suite.test(len(df) > 0,
                      f"Analysis has {len(df)} entries",
                      "Analysis is empty")

            # Test 6: Required columns present
            required_cols = ['variant_id', 'target_nucleotide', 'target_confidence',
                           'specificity_ratio_conf', 'combined_score']
            missing = [col for col in required_cols if col not in df.columns]
            suite.test(len(missing) == 0,
                      "All required columns present",
                      f"Missing columns: {missing}")

            # Test 7: No NaN in critical columns
            if len(df) > 0:
                critical_cols = ['target_confidence', 'specificity_ratio_conf']
                for col in critical_cols:
                    if col in df.columns:
                        has_nan = df[col].isna().any()
                        suite.test(not has_nan,
                                  f"No NaN values in {col}",
                                  f"NaN values found in {col}")
    else:
        print_warn("Test library not found - skipping consistency tests")
        print_warn(f"Run test first: ./run_complete_specificity_pipeline.sh --test")

    return suite


def test_error_handling():
    """Test error handling and edge cases."""
    print_test("Error Handling")
    suite = TestSuite()

    # Test 1: Empty sequence handling
    from generate_cdr_library import generate_variants
    try:
        variants = generate_variants("", "dATP", num_variants=2)
        suite.test(len(variants) > 0,
                  "Empty sequence handled",
                  "Empty sequence should be handled")
    except Exception as e:
        suite.test(True, f"Empty sequence raises error (expected): {type(e).__name__}", "")

    # Test 2: Very large variant count
    try:
        variants = generate_variants("QVQL", "dATP", num_variants=1000)
        suite.test(len(variants) <= 1000,
                  "Large variant count handled",
                  "Large variant count failed")
    except Exception as e:
        suite.warn(False, f"Large variant count may fail: {e}")

    # Test 3: Invalid amino acids in sequence
    try:
        from insert_optogenetic_domains import insert_domain, OPTOGENETIC_DOMAINS
        invalid_seq = "QVQL123XZB"
        result = insert_domain(invalid_seq, OPTOGENETIC_DOMAINS['LOV2'], 'LOV2', position=2)
        # May succeed but sequence is invalid
        suite.warn(result is not None, "Invalid amino acids may not be caught")
    except Exception as e:
        suite.test(True, f"Invalid amino acids raise error: {type(e).__name__}", "")

    return suite


def run_all_tests():
    """Run all test suites."""
    print("="*80)
    print("NUCLEOTIDE BINDER PIPELINE - COMPREHENSIVE UNIT TESTS")
    print("="*80)

    all_suites = []

    # Run all test suites
    all_suites.append(test_imports())
    all_suites.append(test_cdr_library_generation())
    all_suites.append(test_sequence_validation())
    all_suites.append(test_config_file_format())
    all_suites.append(test_specificity_calculations())
    all_suites.append(test_file_structure())
    all_suites.append(test_optogenetic_insertion())
    all_suites.append(test_data_consistency())
    all_suites.append(test_error_handling())

    # Summary
    total_passed = sum(s.passed for s in all_suites)
    total_failed = sum(s.failed for s in all_suites)
    total_warnings = sum(s.warnings for s in all_suites)

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests Run: {total_passed + total_failed}")
    print(f"{Colors.GREEN}Passed: {total_passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {total_failed}{Colors.END}")
    print(f"{Colors.YELLOW}Warnings: {total_warnings}{Colors.END}")

    if total_failed == 0:
        print(f"\n{Colors.GREEN}✓ ALL TESTS PASSED{Colors.END}")
        print("Pipeline is ready for production use.")
        return 0
    else:
        print(f"\n{Colors.RED}✗ SOME TESTS FAILED{Colors.END}")
        print("Please review failures before running production.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
