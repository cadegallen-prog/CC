#!/usr/bin/env python3
"""
Detailed Error Analysis
Deep dive into why specific products fail classification
"""

import json
from pathlib import Path
import sys

# Import the classifier
sys.path.insert(0, str(Path(__file__).parent))
from classify_products import ProductClassifier


def analyze_specific_product(product, classifier):
    """Analyze why a specific product gets its classification"""
    print(f"\n{'='*80}")
    print(f"PRODUCT: {product.get('title', 'No title')[:80]}")
    print(f"{'='*80}")

    # Get classification
    result = classifier.classify_product(product)

    print(f"\nCLASSIFICATION:")
    print(f"  Product Type: {result['product_type']}")
    print(f"  Confidence: {result['confidence']}%")
    print(f"  Confidence Level: {result['confidence_level']}")

    print(f"\nREASONS:")
    for reason in result['reasons']:
        print(f"  - {reason}")

    # Show top 5 alternate types
    print(f"\nALTERNATE TYPES (Top 5):")
    for alt_type, alt_score in result['alternate_types'][:5]:
        print(f"  - {alt_type}: {alt_score}")

    # Show all scores for top patterns
    print(f"\nDETAILED SCORING (All patterns scoring > 0):")
    scores = {}
    for pattern_name in classifier.patterns.keys():
        score, reasons = classifier.calculate_match_score(product, pattern_name)
        if score > 0:
            scores[pattern_name] = (score, reasons)

    for pattern_name, (score, reasons) in sorted(scores.items(), key=lambda x: x[1][0], reverse=True)[:15]:
        print(f"\n  {pattern_name}: {score}")
        for reason in reasons:
            print(f"    - {reason}")


def main():
    """Analyze specific failing products"""
    print("="*80)
    print("DETAILED ERROR ANALYSIS")
    print("="*80)

    # Load data
    data_dir = Path(__file__).parent.parent / 'data'
    output_dir = Path(__file__).parent.parent / 'outputs'

    print("\nLoading ground truth...")
    with open(data_dir / 'ground_truth.json', 'r') as f:
        gt_data = json.load(f)

    print("Loading full product data...")
    with open(data_dir / 'scraped_data_output.json', 'r') as f:
        all_products = json.load(f)

    print("Loading classifications...")
    with open(output_dir / 'product_classifications.json', 'r') as f:
        classifications = json.load(f)

    # Create classifier
    classifier = ProductClassifier()

    # Analyze specific problematic cases
    problematic_indices = [
        166,  # Wall sconce - should be high confidence
        168,  # Wall sconce - should be high confidence
        352,  # Mini pendant - classified as Unknown
        164,  # Stair nosing - Unknown
        301,  # Speaker mounts - Unknown
    ]

    print(f"\n\nAnalyzing {len(problematic_indices)} problematic products...")

    for idx in problematic_indices:
        product = all_products[idx]
        analyze_specific_product(product, classifier)

    # Also check some "unknown" products from ground truth
    print(f"\n\n{'='*80}")
    print("ANALYZING GROUND TRUTH FAILURES")
    print("="*80)

    for gt_sample in gt_data['samples'][:10]:  # First 10 samples
        idx = gt_sample['index']
        product = all_products[idx]
        classification = next((c for c in classifications if c['index'] == idx), None)

        if classification:
            expected = gt_sample['true_product_type']
            predicted = classification['product_type']

            # Check if it's wrong
            if expected.lower().replace('_', ' ') not in predicted.lower().replace('_', ' '):
                print(f"\n\nGROUND TRUTH #{gt_sample['sample_id']}")
                print(f"Expected: {expected}")
                print(f"Got: {predicted}")
                analyze_specific_product(product, classifier)


if __name__ == '__main__':
    main()
