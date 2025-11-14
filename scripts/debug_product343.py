#!/usr/bin/env python3
"""Debug Product #343"""

import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from classify_products import ProductClassifier


def load_product(index):
    """Load a single product from CSV"""
    csv_path = Path(__file__).parent.parent / 'data' / 'scraped_data.csv'
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['index']) == index:
                return {
                    'index': int(row['index']),
                    'title': row['title'],
                    'description': row['description'],
                    'brand': row['brand'],
                    'price': float(row['price']) if row['price'] else 0.0,
                    'rating': float(row['rating']) if row['rating'] else 0.0,
                    'model': row['model'],
                    'structured_specifications': {}
                }
    return None


def main():
    product = load_product(343)

    if not product:
        print("Product not found!")
        return

    print("="*80)
    print(f"DEBUGGING PRODUCT #{product['index']}")
    print("="*80)
    print(f"\nTitle: {product['title']}")
    print(f"\nDescription: {product['description']}")

    # Initialize classifier
    classifier = ProductClassifier()

    # Test against specific patterns
    patterns_to_test = ['LED Light Bulb', 'Chandelier', 'Wall Sconce', 'Pendant Light']

    print("\n" + "="*80)
    print("PATTERN MATCHING ANALYSIS")
    print("="*80)

    for pattern_name in patterns_to_test:
        score, reasons = classifier.calculate_match_score(product, pattern_name)

        print(f"\n{pattern_name}:")
        print(f"  Score: {score}")
        if reasons:
            print(f"  Reasons:")
            for reason in reasons:
                print(f"    - {reason}")

    # Run full classification
    print("\n" + "="*80)
    print("FINAL CLASSIFICATION")
    print("="*80)

    result = classifier.classify_product(product)
    print(f"\nClassified as: {result['product_type']}")
    print(f"Confidence: {result['confidence']}% ({result['confidence_level']})")
    if result['alternate_types']:
        print(f"\nTop Alternates:")
        for alt_type, alt_score in result['alternate_types'][:5]:
            print(f"  - {alt_type}: {alt_score:.1f}")


if __name__ == '__main__':
    main()
