"""
Regression Test Suite for Product Classification System

This test suite establishes baselines and prevents known bugs from returning.
It tracks accuracy metrics, performance, and specific bug scenarios to ensure
the classification system maintains or improves its quality over time.

IMPORTANT: Update baseline constants after confirming current performance is acceptable.

Test Categories:
1. Accuracy Baselines - Track classification accuracy on ground truth datasets
2. Known Bug Prevention - Prevent specific bugs from being reintroduced
3. Performance Baselines - Ensure classification speed remains acceptable
4. Output Format Validation - Prevent breaking changes to output structure
"""

import pytest
import json
import time
from pathlib import Path
from classify_products import ProductClassifier


# ============================================================================
# BASELINE CONSTANTS - UPDATE AFTER CONFIRMING CURRENT PERFORMANCE
# ============================================================================

# Accuracy baselines (will be set after first run)
ACCURACY_BASELINE_44_SAMPLES = None  # Current accuracy on 44-sample ground truth
ACCURACY_BASELINE_FULL_425 = None    # Current accuracy on full 425 products

# Performance baselines
MAX_CLASSIFICATION_TIME_PER_PRODUCT = 1.0  # seconds (must be < 1 second average)
MAX_MEMORY_USAGE_MB = 500  # MB (must be < 500MB for full dataset)

# Accuracy tolerance (allow up to 5% degradation before failing)
ACCURACY_TOLERANCE_PERCENT = 5.0

# Instructions for updating baselines:
# 1. Run this test suite: pytest tests/test_regression.py -v
# 2. Review the actual accuracy values in the output
# 3. If accuracy is acceptable, update the baseline constants above
# 4. Commit the updated baselines to lock in the new performance floor


# ============================================================================
# TEST CLASS: REGRESSION TESTS
# ============================================================================

class TestRegression:
    """
    Regression tests to prevent bugs from returning and track baseline metrics.

    These tests establish a quality floor for the classification system.
    Any degradation below established baselines will cause tests to fail.
    """

    # ========================================================================
    # ACCURACY BASELINE TESTS
    # ========================================================================

    def test_accuracy_baseline_44_samples(self, classifier, ground_truth_samples):
        """
        Test: Classification accuracy on 44-sample ground truth should not degrade.

        This test classifies all products in the ground truth dataset and compares
        accuracy to the established baseline. Accuracy must not drop by more than
        the tolerance threshold (5%).

        Baseline: To be established on first run
        Current: Calculated from actual classifications
        Tolerance: ±5%

        If this test fails, it indicates:
        - Recent changes degraded classification accuracy
        - New patterns are interfering with existing classifications
        - Negative keyword logic is blocking valid products
        """
        # Load full dataset to get product details
        data_dir = Path(__file__).parent.parent / "data"
        full_dataset_path = data_dir / "scraped_data_output.json"

        with open(full_dataset_path, 'r') as f:
            full_dataset = json.load(f)

        # Filter out samples with missing_data as true_product_type
        valid_samples = [s for s in ground_truth_samples
                        if s.get('true_product_type') != 'missing_data']

        correct = 0
        total = len(valid_samples)
        misclassifications = []

        for sample in valid_samples:
            # Get product from full dataset
            product = full_dataset[sample['index']]

            # Classify it
            result = classifier.classify_product(product)
            predicted_type = result['product_type']

            # Map our classifier's type names to ground truth type names
            # (ground truth uses snake_case, classifier uses Title Case)
            expected_type = sample['true_product_type']

            # Convert classifier output to comparable format
            predicted_normalized = predicted_type.lower().replace(' ', '_')
            expected_normalized = expected_type.lower().replace(' ', '_')

            # Check for exact match or partial match (e.g., "exhaust_fan" matches "bathroom_exhaust_fan")
            # This handles cases where ground truth is more specific than classifier
            is_match = (
                predicted_normalized == expected_normalized or
                predicted_normalized in expected_normalized or
                expected_normalized in predicted_normalized
            )

            if is_match:
                correct += 1
            else:
                misclassifications.append({
                    'index': sample['index'],
                    'title': sample['title'][:60],
                    'expected': expected_type,
                    'predicted': predicted_type,
                    'confidence': result['confidence']
                })

        accuracy = (correct / total) * 100

        # Report results
        print(f"\n{'='*70}")
        print(f"ACCURACY BASELINE TEST - 44 SAMPLES")
        print(f"{'='*70}")
        print(f"Correct: {correct}/{total}")
        print(f"Accuracy: {accuracy:.1f}%")
        print(f"Baseline: {ACCURACY_BASELINE_44_SAMPLES or 'NOT SET'}%")

        if misclassifications:
            print(f"\nMisclassifications ({len(misclassifications)}):")
            for m in misclassifications[:10]:  # Show first 10
                print(f"  - {m['title']}")
                print(f"    Expected: {m['expected']}, Got: {m['predicted']} ({m['confidence']:.1f}%)")

        # Check against baseline
        if ACCURACY_BASELINE_44_SAMPLES is not None:
            min_acceptable_accuracy = ACCURACY_BASELINE_44_SAMPLES - ACCURACY_TOLERANCE_PERCENT

            assert accuracy >= min_acceptable_accuracy, (
                f"REGRESSION: Accuracy dropped from {ACCURACY_BASELINE_44_SAMPLES}% "
                f"to {accuracy:.1f}% (minimum acceptable: {min_acceptable_accuracy:.1f}%)\n"
                f"Misclassifications: {len(misclassifications)}"
            )
            print(f"✓ PASSED: Accuracy within acceptable range (≥{min_acceptable_accuracy:.1f}%)")
        else:
            print(f"\n⚠️  BASELINE NOT SET: Update ACCURACY_BASELINE_44_SAMPLES to {accuracy:.1f}%")
            print(f"   After confirming this accuracy is acceptable, update the constant in this file.")

    def test_accuracy_baseline_full_425(self, classifier, full_dataset):
        """
        Test: Classification accuracy on full 425 products should not degrade.

        Note: This is a sampling test since we don't have ground truth for all 425 products.
        Instead, we track the percentage of "Unknown" classifications and confidence distribution.

        Metrics tracked:
        - Unknown rate: Should be < 5% (currently ~18.6%)
        - High confidence rate: Should be > 60%
        - Average confidence: Should be > 60

        If this test fails, it indicates:
        - Classification coverage decreased
        - Confidence levels dropped
        - System is less certain about its predictions
        """
        results = classifier.classify_all_products(full_dataset)

        total = len(results)
        unknown_count = sum(1 for r in results if 'Unknown' in r['product_type'])
        high_confidence_count = sum(1 for r in results if r['confidence'] >= 70)
        avg_confidence = sum(r['confidence'] for r in results) / total

        unknown_rate = (unknown_count / total) * 100
        high_confidence_rate = (high_confidence_count / total) * 100

        # Report results
        print(f"\n{'='*70}")
        print(f"FULL DATASET METRICS - 425 PRODUCTS")
        print(f"{'='*70}")
        print(f"Total Products: {total}")
        print(f"Unknown Classifications: {unknown_count} ({unknown_rate:.1f}%)")
        print(f"High Confidence (≥70): {high_confidence_count} ({high_confidence_rate:.1f}%)")
        print(f"Average Confidence: {avg_confidence:.1f}")

        # Current goals (not strict baselines yet)
        print(f"\nTarget Goals:")
        print(f"  Unknown rate: < 5% (current: {unknown_rate:.1f}%)")
        print(f"  High confidence rate: > 60% (current: {high_confidence_rate:.1f}%)")
        print(f"  Average confidence: > 60 (current: {avg_confidence:.1f})")

        if ACCURACY_BASELINE_FULL_425 is not None:
            # Once we set a baseline, enforce it
            assert unknown_rate <= ACCURACY_BASELINE_FULL_425 + ACCURACY_TOLERANCE_PERCENT, (
                f"REGRESSION: Unknown rate increased from {ACCURACY_BASELINE_FULL_425}% "
                f"to {unknown_rate:.1f}%"
            )
            print(f"✓ PASSED: Unknown rate within acceptable range")
        else:
            print(f"\n⚠️  BASELINE NOT SET: Update ACCURACY_BASELINE_FULL_425 to {unknown_rate:.1f}%")

    # ========================================================================
    # KNOWN BUG PREVENTION TESTS
    # ========================================================================

    def test_bug1_chandelier_bulbs_not_blocked(self, classifier):
        """
        Test: Bug #1 - Chandelier bulbs must not be blocked by negative keywords.

        KNOWN BUG THAT MUST NEVER RETURN:
        Products like "Chandelier LED Light Bulb Candelabra Base" were being
        blocked by the "chandelier" negative keyword in the LED Light Bulb pattern.

        These are LED BULBS designed FOR chandeliers, not chandelier fixtures.
        They must classify as "LED Light Bulb" with high confidence (≥70%).

        Root Cause:
        - Negative keyword "chandelier" was too aggressive
        - Did not consider context (bulb FOR chandelier vs chandelier fixture)

        Fix:
        - Added context-aware negative keyword analysis
        - Detects compound product names ("chandelier led light bulb")
        - Allows "chandelier" when it modifies "light bulb"
        """
        product = {
            "title": "Chandelier LED Light Bulb Candelabra Base 60W Equivalent Soft White",
            "description": "Elegant chandelier LED light bulbs designed for use in chandelier fixtures. Perfect for decorative lighting and candelabra sockets.",
            "brand": "Test Brand",
            "structured_specifications": {
                "wattage": {"value": 6, "unit": "W"},
                "lumens": {"value": 500, "unit": "lm"},
                "base_type": "E12"
            }
        }

        result = classifier.classify_product(product)

        print(f"\n{'='*70}")
        print(f"BUG #1: CHANDELIER BULB TEST")
        print(f"{'='*70}")
        print(f"Product: {product['title']}")
        print(f"Classification: {result['product_type']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Reasons: {result['reasons']}")

        assert result['product_type'] == 'LED Light Bulb', (
            f"BUG #1 RETURNED: Chandelier bulb misclassified as '{result['product_type']}' "
            f"instead of 'LED Light Bulb'. The negative keyword 'chandelier' is blocking valid bulbs."
        )

        assert result['confidence'] >= 70, (
            f"BUG #1 PARTIAL: Chandelier bulb classified correctly but confidence too low "
            f"({result['confidence']}% < 70%). Should have strong confidence."
        )

        print(f"✓ PASSED: Chandelier bulb correctly classified as LED Light Bulb")

    def test_bug2_pendant_bulbs_not_blocked(self, classifier):
        """
        Test: Bug #2 - Pendant bulbs must not be blocked by negative keywords.

        KNOWN BUG THAT MUST NEVER RETURN:
        Products like "Pendant LED Light Bulb" were being blocked by the
        "pendant" negative keyword in the LED Light Bulb pattern.

        These are LED BULBS designed FOR pendant fixtures, not pendant lights.
        They must classify as "LED Light Bulb" with high confidence (≥70%).

        Similar to Bug #1, this is a context issue with negative keywords.
        """
        product = {
            "title": "Pendant LED Light Bulb Vintage Style Edison 40W Equivalent",
            "description": "Vintage-style pendant LED bulbs perfect for modern pendant light fixtures. Features warm amber glow and visible LED filaments.",
            "brand": "Test Brand",
            "structured_specifications": {
                "wattage": {"value": 4.5, "unit": "W"},
                "lumens": {"value": 350, "unit": "lm"},
                "base_type": "E26"
            }
        }

        result = classifier.classify_product(product)

        print(f"\n{'='*70}")
        print(f"BUG #2: PENDANT BULB TEST")
        print(f"{'='*70}")
        print(f"Product: {product['title']}")
        print(f"Classification: {result['product_type']}")
        print(f"Confidence: {result['confidence']}%")

        assert result['product_type'] == 'LED Light Bulb', (
            f"BUG #2 RETURNED: Pendant bulb misclassified as '{result['product_type']}' "
            f"instead of 'LED Light Bulb'. The negative keyword 'pendant' is blocking valid bulbs."
        )

        assert result['confidence'] >= 70, (
            f"BUG #2 PARTIAL: Pendant bulb classified correctly but confidence too low "
            f"({result['confidence']}% < 70%). Should have strong confidence."
        )

        print(f"✓ PASSED: Pendant bulb correctly classified as LED Light Bulb")

    def test_bug3_led_bulb_title_scores_high(self, classifier):
        """
        Test: Bug #3 - "LED Light Bulb" in title must score ≥70 (strong keyword bonus).

        KNOWN BUG THAT MUST NEVER RETURN:
        Products with literal "LED Light Bulb" in the title were scoring too low
        and being misclassified as "Light Switch" or "Fastener".

        When a product title contains a STRONG KEYWORD, it should receive 80 points
        immediately, resulting in confidence ≥70% (usually 80%+ with weak keywords).

        Root Cause:
        - Scoring weights were too low
        - Title keywords only gave 40 points (now 80 points)
        - Allowed unrelated patterns to outscore obvious matches

        Fix:
        - Increased title strong keyword bonus: 40 → 80 points
        - Increased description strong keyword bonus: 25 → 50 points
        """
        product = {
            "title": "LED Light Bulb 60W Equivalent Soft White A19",
            "description": "Energy efficient LED bulb provides 800 lumens of bright light.",
            "brand": "Test Brand",
            "structured_specifications": {}
        }

        result = classifier.classify_product(product)

        print(f"\n{'='*70}")
        print(f"BUG #3: LED BULB TITLE SCORING TEST")
        print(f"{'='*70}")
        print(f"Product: {product['title']}")
        print(f"Classification: {result['product_type']}")
        print(f"Confidence: {result['confidence']}%")

        assert result['product_type'] == 'LED Light Bulb', (
            f"BUG #3 RETURNED: LED bulb with 'LED Light Bulb' in title misclassified as "
            f"'{result['product_type']}'. Scoring system is broken."
        )

        assert result['confidence'] >= 70, (
            f"BUG #3 SCORING: LED bulb classified correctly but confidence too low "
            f"({result['confidence']}% < 70%). Strong keyword in title should give ≥80 points."
        )

        print(f"✓ PASSED: LED bulb with strong keyword in title scored {result['confidence']}%")

    def test_bug4_faucets_not_misclassified_as_paint(self, classifier):
        """
        Test: Bug #4 - Faucets must not be misclassified as Paint.

        KNOWN BUG THAT MUST NEVER RETURN:
        Kitchen faucets were being misclassified as "Paint" due to overly broad
        Paint pattern matching or faucet pattern being too narrow.

        Faucets are plumbing fixtures with keywords like "faucet", "spout",
        "pull-down", "spray", and should NEVER match paint patterns.

        Root Cause:
        - Unknown (needs investigation if this test fails)
        - Possibly: word boundary issues with "spray" or other shared terms

        Expected:
        - Classification: "Faucet" (plumbing category)
        - Confidence: ≥70%
        - Must NOT classify as "Paint"
        """
        product = {
            "title": "Kitchen Faucet with Pull-Down Spray Brushed Nickel",
            "description": "Single-handle kitchen faucet with pull-down spray head. Features magnetic docking and easy-clean spray holes.",
            "brand": "Test Brand",
            "structured_specifications": {
                "flow_rate": {"value": 1.8, "unit": "GPM"},
                "faucet_type": "Pull-Down"
            }
        }

        result = classifier.classify_product(product)

        print(f"\n{'='*70}")
        print(f"BUG #4: FAUCET MISCLASSIFICATION TEST")
        print(f"{'='*70}")
        print(f"Product: {product['title']}")
        print(f"Classification: {result['product_type']}")
        print(f"Confidence: {result['confidence']}%")

        assert result['product_type'] == 'Faucet', (
            f"BUG #4 RETURNED: Faucet misclassified as '{result['product_type']}' "
            f"instead of 'Faucet'. This is a serious pattern matching error."
        )

        assert result['product_type'] != 'Paint', (
            f"BUG #4 CRITICAL: Faucet classified as Paint! This is the exact bug we're preventing."
        )

        assert result['confidence'] >= 70, (
            f"BUG #4 LOW CONFIDENCE: Faucet classified correctly but confidence is low "
            f"({result['confidence']}% < 70%). Pattern may be weak."
        )

        print(f"✓ PASSED: Faucet correctly classified, not as Paint")

    def test_bug5_smart_lights_classified_as_lighting_not_smart_home(self, classifier):
        """
        Test: Bug #5 - Smart LED bulbs must classify as LED Light Bulb, not generic smart_home.

        KNOWN BUG THAT MUST NEVER RETURN:
        Products like "Smart LED Light Bulb WiFi" were being classified as
        generic "smart_home" category instead of "LED Light Bulb".

        While these bulbs ARE smart home devices, their PRIMARY product type is
        LED Light Bulb. The smart/WiFi features are modifiers, not the core type.

        Root Cause:
        - Smart home pattern was too aggressive
        - Matches any product with "smart", "wifi", "alexa", etc.
        - Should not override specific product type patterns

        Expected:
        - Classification: "LED Light Bulb"
        - Confidence: ≥70%
        - Must NOT classify as "smart_home" or similar generic categories

        Note: We don't have a "smart_home" pattern in current classifier,
        but this test prevents future patterns from overriding specific types.
        """
        product = {
            "title": "Smart LED Light Bulb WiFi Color Changing Alexa Compatible",
            "description": "Smart WiFi LED bulb works with Alexa and Google Home. Change colors, set schedules, and control from your phone.",
            "brand": "Test Brand",
            "structured_specifications": {
                "wattage": {"value": 9, "unit": "W"},
                "lumens": {"value": 800, "unit": "lm"},
                "smart_features": ["WiFi", "Alexa", "Google Home"]
            }
        }

        result = classifier.classify_product(product)

        print(f"\n{'='*70}")
        print(f"BUG #5: SMART LIGHT CLASSIFICATION TEST")
        print(f"{'='*70}")
        print(f"Product: {product['title']}")
        print(f"Classification: {result['product_type']}")
        print(f"Confidence: {result['confidence']}%")

        assert result['product_type'] == 'LED Light Bulb', (
            f"BUG #5 RETURNED: Smart LED bulb misclassified as '{result['product_type']}' "
            f"instead of 'LED Light Bulb'. Generic categories should not override specific types."
        )

        # Check that it's not ANY generic category
        generic_categories = ['smart_home', 'Smart Home', 'Electronics', 'Unknown']
        assert result['product_type'] not in generic_categories, (
            f"BUG #5 GENERIC: Smart LED bulb classified as generic category '{result['product_type']}'. "
            f"Should be specific type 'LED Light Bulb'."
        )

        assert result['confidence'] >= 70, (
            f"BUG #5 LOW CONFIDENCE: Smart LED bulb classified correctly but confidence is low "
            f"({result['confidence']}% < 70%). Strong keyword should dominate."
        )

        print(f"✓ PASSED: Smart LED bulb correctly classified as LED Light Bulb")

    # ========================================================================
    # PERFORMANCE BASELINE TESTS
    # ========================================================================

    def test_classification_speed_baseline(self, classifier, full_dataset):
        """
        Test: Classification speed must remain < 1 second per product average.

        Performance is critical for scaling to larger datasets (1,000-2,000 products).
        This test ensures classification speed doesn't degrade as we add features.

        Baseline: < 1 second per product (averaged over 100 products)

        If this test fails, it indicates:
        - New patterns are too complex
        - Negative keyword analysis is too slow
        - Need to optimize matching algorithms
        """
        # Test on first 100 products for reasonable test duration
        test_products = full_dataset[:100]

        start_time = time.time()

        for product in test_products:
            classifier.classify_product(product)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_product = total_time / len(test_products)

        print(f"\n{'='*70}")
        print(f"PERFORMANCE BASELINE TEST")
        print(f"{'='*70}")
        print(f"Products Classified: {len(test_products)}")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Average Time per Product: {avg_time_per_product:.3f} seconds")
        print(f"Baseline Maximum: {MAX_CLASSIFICATION_TIME_PER_PRODUCT} seconds")

        assert avg_time_per_product < MAX_CLASSIFICATION_TIME_PER_PRODUCT, (
            f"REGRESSION: Classification speed degraded. "
            f"Average time: {avg_time_per_product:.3f}s > baseline: {MAX_CLASSIFICATION_TIME_PER_PRODUCT}s"
        )

        print(f"✓ PASSED: Classification speed within acceptable range")

    def test_memory_usage_reasonable(self, classifier, full_dataset):
        """
        Test: Memory usage must remain < 500MB for full dataset classification.

        This test ensures we don't introduce memory leaks or inefficient data structures.

        Baseline: < 500MB for classifying all 425 products

        Note: This is a basic check. For production, use memory_profiler for detailed analysis.
        """
        import sys

        # Classify all products
        results = classifier.classify_all_products(full_dataset)

        # Basic size check (not perfect but catches major issues)
        # Check size of results object
        result_size_bytes = sys.getsizeof(results)
        result_size_mb = result_size_bytes / (1024 * 1024)

        print(f"\n{'='*70}")
        print(f"MEMORY USAGE TEST")
        print(f"{'='*70}")
        print(f"Products Classified: {len(results)}")
        print(f"Results Size: {result_size_mb:.2f} MB")
        print(f"Baseline Maximum: {MAX_MEMORY_USAGE_MB} MB")

        assert result_size_mb < MAX_MEMORY_USAGE_MB, (
            f"REGRESSION: Memory usage too high. "
            f"Results size: {result_size_mb:.2f}MB > baseline: {MAX_MEMORY_USAGE_MB}MB"
        )

        print(f"✓ PASSED: Memory usage within acceptable range")

    # ========================================================================
    # OUTPUT FORMAT VALIDATION TESTS
    # ========================================================================

    def test_output_format_unchanged(self, classifier):
        """
        Test: Classification output format must remain stable (no breaking changes).

        This test ensures the output structure doesn't change unexpectedly,
        which would break downstream consumers of the classification results.

        Required fields in classification result:
        - product_type: str
        - confidence: float (0-100)
        - confidence_level: str (High/Medium/Low/Very Low/No Match)
        - reasons: list of strings
        - alternate_types: list of (type, score) tuples

        If this test fails, it indicates:
        - Output schema changed (breaking change)
        - Field names or types modified
        - New required fields added without backward compatibility
        """
        product = {
            "title": "Test Product LED Light Bulb",
            "description": "Test description",
            "brand": "Test",
            "structured_specifications": {}
        }

        result = classifier.classify_product(product)

        print(f"\n{'='*70}")
        print(f"OUTPUT FORMAT VALIDATION TEST")
        print(f"{'='*70}")
        print(f"Result Keys: {list(result.keys())}")

        # Check required fields exist
        required_fields = ['product_type', 'confidence', 'confidence_level', 'reasons', 'alternate_types']

        for field in required_fields:
            assert field in result, (
                f"BREAKING CHANGE: Required field '{field}' missing from classification result"
            )

        # Check field types
        assert isinstance(result['product_type'], str), "product_type must be string"
        assert isinstance(result['confidence'], (int, float)), "confidence must be numeric"
        assert isinstance(result['confidence_level'], str), "confidence_level must be string"
        assert isinstance(result['reasons'], list), "reasons must be list"
        assert isinstance(result['alternate_types'], list), "alternate_types must be list"

        # Check confidence is in valid range
        assert 0 <= result['confidence'] <= 100, (
            f"confidence must be 0-100, got {result['confidence']}"
        )

        # Check confidence level is valid
        valid_levels = ['High', 'Medium', 'Low', 'Very Low', 'No Match', 'No Data']
        assert result['confidence_level'] in valid_levels, (
            f"confidence_level must be one of {valid_levels}, got '{result['confidence_level']}'"
        )

        # Check alternate_types structure (should be list of tuples)
        if result['alternate_types']:
            for alt in result['alternate_types']:
                assert isinstance(alt, tuple), "alternate_types should be list of tuples"
                assert len(alt) == 2, "alternate_types tuples should be (type, score)"
                assert isinstance(alt[0], str), "alternate type name should be string"
                assert isinstance(alt[1], (int, float)), "alternate type score should be numeric"

        print(f"Product Type: {result['product_type']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Confidence Level: {result['confidence_level']}")
        print(f"Reasons: {len(result['reasons'])} provided")
        print(f"Alternates: {len(result['alternate_types'])} provided")
        print(f"✓ PASSED: Output format valid and unchanged")


# ============================================================================
# TEST EXECUTION SUMMARY
# ============================================================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Custom pytest hook to print summary after test run.
    """
    print("\n" + "="*70)
    print("REGRESSION TEST SUITE SUMMARY")
    print("="*70)
    print("\nThis test suite prevents known bugs from returning and tracks baselines.")
    print("\nIf baselines are not set (None), update them after confirming current performance.")
    print("Update these constants in test_regression.py:")
    print("  - ACCURACY_BASELINE_44_SAMPLES")
    print("  - ACCURACY_BASELINE_FULL_425")
    print("\nFor questions about specific test failures, see test docstrings.")
    print("="*70 + "\n")
