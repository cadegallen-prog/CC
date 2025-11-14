#!/usr/bin/env python3
"""
Validate Negative Keyword Fix
Runs the classifier on the full dataset and shows improvements
"""

import csv
import json
from pathlib import Path
from collections import defaultdict, Counter

# Import the classifier
import sys
sys.path.append(str(Path(__file__).parent))
from classify_products import ProductClassifier


def load_csv_data(csv_path):
    """Load product data from CSV file"""
    products = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = {
                'index': int(row['index']),
                'title': row['title'],
                'description': row['description'],
                'brand': row['brand'],
                'price': float(row['price']) if row['price'] else 0.0,
                'rating': float(row['rating']) if row['rating'] else 0.0,
                'model': row['model'],
                'structured_specifications': {}
            }
            products.append(product)
    return products


def main():
    print("="*80)
    print("NEGATIVE KEYWORD FIX VALIDATION")
    print("="*80)

    # Load data
    print("\nLoading CSV data...")
    csv_path = Path(__file__).parent.parent / 'data' / 'scraped_data.csv'
    products = load_csv_data(csv_path)
    print(f"Loaded {len(products)} products")

    # Initialize classifier
    print("\nInitializing classifier with NEW context-aware logic...")
    classifier = ProductClassifier()

    # Run classification
    print("\nClassifying all products...")
    results = classifier.classify_all_products(products)

    # Analyze specific examples that were previously blocked
    print("\n" + "="*80)
    print("PREVIOUSLY BLOCKED PRODUCTS - NOW CORRECTLY CLASSIFIED")
    print("="*80)

    # Test cases from our audit
    test_cases = [
        {
            'index': 0,
            'title': 'Feit Electric 60-Watt Equivalent B10 E26 Base Dim White Filament Clear Glass Chandelier LED Light Bulb',
            'expected_type': 'LED Light Bulb',
            'should_not_be': 'Chandelier'
        },
        {
            'index': 18,
            'title': 'EcoSmart 60-Watt Equivalent A19 Dimmable LED Light Bulb',
            'expected_type': 'LED Light Bulb',
            'should_not_be': 'Light Switch'
        },
        {
            'index': 343,
            'title': 'Feit Electric 40-Watt Equivalent B10 E12 Candelabra Chandelier LED Light Bulb',
            'expected_type': 'LED Light Bulb',
            'should_not_be': 'Chandelier'
        },
    ]

    for test in test_cases:
        idx = test['index']
        result = results[idx]

        print(f"\nProduct #{idx}: {test['title'][:70]}...")
        print(f"  Expected Type: {test['expected_type']}")
        print(f"  Classified As: {result['product_type']}")
        print(f"  Confidence: {result['confidence']}% ({result['confidence_level']})")

        if result['product_type'] == test['expected_type']:
            print(f"  ✓ CORRECT - Successfully avoided false positive!")
        elif result['product_type'] == test['should_not_be']:
            print(f"  ✗ STILL BLOCKED - Incorrectly classified as {test['should_not_be']}")
        else:
            print(f"  ? DIFFERENT - Classified as {result['product_type']} (not expected)")

        if result['alternate_types']:
            print(f"  Alternates: {', '.join([f'{t} ({s:.1f})' for t, s in result['alternate_types'][:3]])}")

    # Overall statistics
    print("\n" + "="*80)
    print("OVERALL CLASSIFICATION STATISTICS")
    print("="*80)

    type_counts = Counter([r['product_type'] for r in results])
    confidence_counts = Counter([r['confidence_level'] for r in results])

    print(f"\nTotal Products: {len(results)}")
    print(f"Unique Product Types: {len(type_counts)}")

    # Count Unknown products
    unknown_count = sum(1 for r in results if 'Unknown' in r['product_type'])
    unknown_pct = (unknown_count / len(results)) * 100
    print(f"Unknown Products: {unknown_count} ({unknown_pct:.1f}%)")

    # Average confidence
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    print(f"Average Confidence: {avg_confidence:.1f}%")

    print(f"\n{'='*80}")
    print("CONFIDENCE DISTRIBUTION")
    print(f"{'='*80}")
    for level in ['High', 'Medium', 'Low', 'Very Low', 'No Match', 'No Data']:
        count = confidence_counts.get(level, 0)
        pct = (count / len(results)) * 100
        print(f"  {level:15s}: {count:3d} products ({pct:5.1f}%)")

    print(f"\n{'='*80}")
    print("TOP 20 PRODUCT TYPES")
    print(f"{'='*80}")
    for i, (ptype, count) in enumerate(list(type_counts.most_common(20)), 1):
        pct = (count / len(results)) * 100
        print(f"{i:2}. {ptype:40s} {count:3d} ({pct:5.1f}%)")

    # LED Light Bulb statistics
    print(f"\n{'='*80}")
    print("LED LIGHT BULB CLASSIFICATION ANALYSIS")
    print(f"{'='*80}")

    led_bulbs = [r for r in results if r['product_type'] == 'LED Light Bulb']
    print(f"\nTotal LED Light Bulbs: {len(led_bulbs)}")

    if len(led_bulbs) > 0:
        led_avg_conf = sum(r['confidence'] for r in led_bulbs) / len(led_bulbs)
        print(f"Average Confidence: {led_avg_conf:.1f}%")

        high_conf = sum(1 for r in led_bulbs if r['confidence'] >= 70)
        print(f"High Confidence (≥70%): {high_conf} ({high_conf/len(led_bulbs)*100:.1f}%)")

        # Show some examples
        print(f"\nSample LED Light Bulb Classifications:")
        for i, bulb in enumerate(led_bulbs[:5], 1):
            print(f"  {i}. {bulb['title'][:60]}...")
            print(f"     Confidence: {bulb['confidence']}% - {bulb['reasons'][0] if bulb['reasons'] else 'N/A'}")

    # Check for chandelier bulbs specifically
    chandelier_bulbs = [r for r in results if 'chandelier' in r['title'].lower() and 'bulb' in r['title'].lower()]
    print(f"\nChandelier Bulb Products: {len(chandelier_bulbs)}")
    if len(chandelier_bulbs) > 0:
        correctly_classified = sum(1 for r in chandelier_bulbs if r['product_type'] == 'LED Light Bulb')
        print(f"  Correctly classified as LED Light Bulb: {correctly_classified}/{len(chandelier_bulbs)}")

        print(f"\n  Examples:")
        for bulb in chandelier_bulbs[:3]:
            print(f"    - Product #{bulb['index']}: {bulb['product_type']} (Conf: {bulb['confidence']}%)")
            print(f"      {bulb['title'][:70]}...")

    # Save results
    output_dir = Path(__file__).parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / 'validation_results.json', 'w') as f:
        json.dump({
            'total_products': len(results),
            'unknown_count': unknown_count,
            'unknown_percentage': unknown_pct,
            'average_confidence': avg_confidence,
            'type_distribution': dict(type_counts.most_common()),
            'confidence_distribution': dict(confidence_counts),
            'test_cases': test_cases,
            'led_bulb_count': len(led_bulbs),
            'chandelier_bulb_count': len(chandelier_bulbs)
        }, f, indent=2)

    print(f"\n✓ Saved validation results to outputs/validation_results.json")

    return results


if __name__ == '__main__':
    results = main()
