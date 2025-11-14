#!/usr/bin/env python3
"""Test with full Product #343 description"""

import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from classify_products import ProductClassifier


def main():
    # Load actual description
    csv_path = Path(__file__).parent.parent / 'data' / 'scraped_data.csv'
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['index']) == 343:
                title = row['title']
                description = row['description']
                break

    classifier = ProductClassifier()

    # Normalize like the classifier does
    title_norm = classifier.normalize_text(title)
    desc_norm = classifier.normalize_text(description)

    negative_kw = "fixture"
    pattern = classifier.patterns['LED Light Bulb']

    print("Testing with actual Product #343 data:")
    print(f"Title: {title}")
    print()
    print(f"Description (first 200 chars): {description[:200]}...")
    print()
    print(f"Normalized description (first 200 chars): {desc_norm[:200]}...")
    print()

    # Test the function
    print("Testing is_false_positive_block on DESCRIPTION:")
    result = classifier.is_false_positive_block(desc_norm, negative_kw, pattern, 'description')
    print(f"Result: {result} (True = don't block, False = block)")
    print()

    # Now test the full calculate_match_score
    product = {
        'title': title,
        'description': description,
        'brand': '',
        'structured_specifications': {}
    }

    print("Testing calculate_match_score:")
    score, reasons = classifier.calculate_match_score(product, 'LED Light Bulb')
    print(f"Score: {score}")
    print(f"Reasons: {reasons}")


if __name__ == '__main__':
    main()
