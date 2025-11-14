#!/usr/bin/env python3
"""Debug specific product classification"""

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
    # Debug Product #0
    product = load_product(0)

    if not product:
        print("Product not found!")
        return

    print("="*80)
    print(f"DEBUGGING PRODUCT #{product['index']}")
    print("="*80)
    print(f"\nTitle: {product['title']}")
    print(f"\nDescription: {product['description'][:200]}...")

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
        print(f"  Reasons:")
        for reason in reasons:
            print(f"    - {reason}")

        # Check negative keywords
        pattern = classifier.patterns[pattern_name]
        title_norm = classifier.normalize_text(product['title'])
        desc_norm = classifier.normalize_text(product['description'])

        blocked_by = []
        for neg_kw in pattern.get('negative_keywords', []):
            if neg_kw in title_norm:
                is_fp = classifier.is_false_positive_block(title_norm, neg_kw, pattern, 'title')
                if not is_fp:
                    blocked_by.append(f"{neg_kw} (in title)")
            if neg_kw in desc_norm:
                is_fp = classifier.is_false_positive_block(desc_norm, neg_kw, pattern, 'description')
                if not is_fp:
                    blocked_by.append(f"{neg_kw} (in description)")

        if score == 0.0:
            print(f"  ❌ BLOCKED by negative keywords: {', '.join(blocked_by) if blocked_by else 'Unknown'}")
        else:
            print(f"  ✓ Not blocked")

    # Run full classification
    print("\n" + "="*80)
    print("FINAL CLASSIFICATION")
    print("="*80)

    result = classifier.classify_product(product)
    print(f"\nClassified as: {result['product_type']}")
    print(f"Confidence: {result['confidence']}% ({result['confidence_level']})")
    print(f"Reasons: {', '.join(result['reasons'])}")
    if result['alternate_types']:
        print(f"\nTop Alternates:")
        for alt_type, alt_score in result['alternate_types'][:5]:
            print(f"  - {alt_type}: {alt_score:.1f}")


if __name__ == '__main__':
    main()
