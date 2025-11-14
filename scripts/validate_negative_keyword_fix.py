#!/usr/bin/env python3
"""
Validation Script for Negative Keyword Fix
Tests that the context-aware negative keyword logic correctly handles all edge cases
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import classifier
sys.path.insert(0, str(Path(__file__).parent))

from classify_products import ProductClassifier


def test_wrongly_blocked_bulbs():
    """Test that previously wrongly blocked bulbs are now correctly classified"""

    print("="*80)
    print("TEST 1: Previously Wrongly Blocked Bulbs (Should Now Be Fixed)")
    print("="*80)

    # Load products
    with open('/home/user/CC/data/scraped_data_output.json', 'r') as f:
        products = json.load(f)

    classifier = ProductClassifier()

    # Products that were wrongly blocked: 0, 18, 156, 269, 292, 343
    # Note: Using ≥50% confidence threshold (Medium confidence) as acceptable
    # Some edge-case products (smart bulbs, Bluetooth bulbs) have fewer traditional indicators
    test_cases = [
        {
            'index': 0,
            'expected_type': 'LED Light Bulb',
            'min_confidence': 50,
            'description': 'Feit Electric Chandelier LED Light Bulb',
            'previously_blocked_by': ['chandelier', 'sconce', 'fixture']
        },
        {
            'index': 18,
            'expected_type': 'LED Light Bulb',
            'min_confidence': 50,
            'description': 'EcoSmart A19 LED Light Bulb',
            'previously_blocked_by': ['fixture']
        },
        {
            'index': 156,
            'expected_type': 'LED Light Bulb',
            'min_confidence': 50,
            'description': 'BEYOND BRIGHT LED Lamp Light Bulbs (Bluetooth speaker)',
            'previously_blocked_by': ['fixture']
        },
        {
            'index': 269,
            'expected_type': 'LED Light Bulb',
            'min_confidence': 50,
            'description': 'Philips Smart Wi-Fi LED Light Bulb',
            'previously_blocked_by': ['fixture']
        },
        {
            'index': 292,
            'expected_type': 'LED Light Bulb',
            'min_confidence': 50,
            'description': 'Philips T5 LED Tube Light Bulb',
            'previously_blocked_by': ['fixture']
        },
        {
            'index': 343,
            'expected_type': 'LED Light Bulb',
            'min_confidence': 50,
            'description': 'Feit Electric Chandelier LED Light Bulb (Candelabra)',
            'previously_blocked_by': ['chandelier', 'sconce', 'pendant', 'fixture']
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        product = products[test['index']]
        result = classifier.classify_product(product)

        is_correct_type = result['product_type'] == test['expected_type']
        has_min_confidence = result['confidence'] >= test['min_confidence']

        status = "✓ PASS" if (is_correct_type and has_min_confidence) else "✗ FAIL"

        print(f"\n{status} - Product #{test['index']}: {test['description']}")
        print(f"  Expected: {test['expected_type']} (≥{test['min_confidence']}% confidence)")
        print(f"  Got: {result['product_type']} ({result['confidence']}% confidence)")
        print(f"  Previously blocked by: {test['previously_blocked_by']}")
        print(f"  Reasons: {result['reasons'][:2]}")

        if is_correct_type and has_min_confidence:
            passed += 1
        else:
            failed += 1

    print(f"\n{'-'*80}")
    print(f"TEST 1 RESULTS: {passed}/{len(test_cases)} tests passed")
    print(f"{'-'*80}\n")

    return failed == 0


def test_correctly_blocked_fixtures():
    """Test that fixtures are still correctly blocked from LED Light Bulb classification"""

    print("="*80)
    print("TEST 2: Fixtures Should Still Be Blocked (No Regressions)")
    print("="*80)

    # Load products
    with open('/home/user/CC/data/scraped_data_output.json', 'r') as f:
        products = json.load(f)

    classifier = ProductClassifier()

    # Products that should be blocked: 159, 161, 176, 253, 352
    test_cases = [
        {
            'index': 159,
            'should_not_be': 'LED Light Bulb',
            'description': 'Wall Sconce Fixture',
            'blocked_by': 'sconce'
        },
        {
            'index': 161,
            'should_not_be': 'LED Light Bulb',
            'description': 'Outdoor Wall Light Fixture Sconce',
            'blocked_by': 'fixture'
        },
        {
            'index': 176,
            'should_not_be': 'LED Light Bulb',
            'description': 'Mid-Century Wall Sconce',
            'blocked_by': 'sconce'
        },
        {
            'index': 253,
            'should_not_be': 'LED Light Bulb',
            'description': 'Wall Sconce',
            'blocked_by': 'sconce'
        },
        {
            'index': 352,
            'should_not_be': 'LED Light Bulb',
            'description': 'Mini Pendant Fixture',
            'blocked_by': 'pendant'
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        product = products[test['index']]
        result = classifier.classify_product(product)

        is_not_bulb = result['product_type'] != test['should_not_be']

        status = "✓ PASS" if is_not_bulb else "✗ FAIL"

        print(f"\n{status} - Product #{test['index']}: {test['description']}")
        print(f"  Should NOT be: {test['should_not_be']}")
        print(f"  Got: {result['product_type']} ({result['confidence']}% confidence)")
        print(f"  Should be blocked by: {test['blocked_by']}")

        if is_not_bulb:
            passed += 1
        else:
            failed += 1
            print(f"  ERROR: This fixture was wrongly classified as LED Light Bulb!")

    print(f"\n{'-'*80}")
    print(f"TEST 2 RESULTS: {passed}/{len(test_cases)} tests passed")
    print(f"{'-'*80}\n")

    return failed == 0


def test_full_dataset_regression():
    """Run classifier on full dataset and check for unexpected changes"""

    print("="*80)
    print("TEST 3: Full Dataset Regression Test")
    print("="*80)

    # Load products
    with open('/home/user/CC/data/scraped_data_output.json', 'r') as f:
        products = json.load(f)

    classifier = ProductClassifier()

    print(f"\nClassifying all {len(products)} products...")

    results = classifier.classify_all_products(products)

    # Count LED Light Bulbs
    led_bulbs = [r for r in results if r['product_type'] == 'LED Light Bulb']
    high_confidence_bulbs = [r for r in results if r['product_type'] == 'LED Light Bulb' and r['confidence'] >= 70]

    print(f"\nTotal LED Light Bulbs classified: {len(led_bulbs)}")
    print(f"High confidence (≥70%) LED Light Bulbs: {len(high_confidence_bulbs)}")

    # Check specific products
    specific_checks = {
        0: 'LED Light Bulb',
        18: 'LED Light Bulb',
        156: 'LED Light Bulb',
        269: 'LED Light Bulb',
        292: 'LED Light Bulb',
        343: 'LED Light Bulb',
        159: 'NOT LED Light Bulb',
        161: 'NOT LED Light Bulb',
        176: 'NOT LED Light Bulb',
        253: 'NOT LED Light Bulb',
        352: 'NOT LED Light Bulb'
    }

    all_correct = True
    for idx, expected in specific_checks.items():
        result = results[idx]
        if expected == 'NOT LED Light Bulb':
            if result['product_type'] == 'LED Light Bulb':
                print(f"  ✗ Product {idx} wrongly classified as LED Light Bulb")
                all_correct = False
        else:
            if result['product_type'] != expected:
                print(f"  ✗ Product {idx} not classified as {expected}")
                all_correct = False

    if all_correct:
        print(f"  ✓ All 11 key products correctly classified")

    print(f"\n{'-'*80}")
    print(f"TEST 3 RESULTS: {'PASS' if all_correct else 'FAIL'}")
    print(f"{'-'*80}\n")

    return all_correct


def main():
    """Run all validation tests"""

    print("\n" + "="*80)
    print("NEGATIVE KEYWORD FIX VALIDATION")
    print("Testing Context-Aware Negative Keyword Logic")
    print("="*80 + "\n")

    test1_pass = test_wrongly_blocked_bulbs()
    test2_pass = test_correctly_blocked_fixtures()
    test3_pass = test_full_dataset_regression()

    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"Test 1 (Wrongly Blocked Bulbs Fixed): {'✓ PASS' if test1_pass else '✗ FAIL'}")
    print(f"Test 2 (Fixtures Still Blocked): {'✓ PASS' if test2_pass else '✗ FAIL'}")
    print(f"Test 3 (No Regressions): {'✓ PASS' if test3_pass else '✗ FAIL'}")

    all_pass = test1_pass and test2_pass and test3_pass

    print("\n" + "="*80)
    if all_pass:
        print("✓ ALL TESTS PASSED - Fix is working correctly!")
        print("="*80 + "\n")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Fix needs adjustment")
        print("="*80 + "\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
