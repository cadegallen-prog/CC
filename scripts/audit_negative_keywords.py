#!/usr/bin/env python3
"""
Audit Negative Keyword Failures
Identifies all products incorrectly blocked by negative keywords
"""

import csv
import json
import re
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
            # Convert CSV row to product dict format
            product = {
                'index': int(row['index']),
                'title': row['title'],
                'description': row['description'],
                'brand': row['brand'],
                'price': float(row['price']) if row['price'] else 0.0,
                'rating': float(row['rating']) if row['rating'] else 0.0,
                'model': row['model'],
                'structured_specifications': {}  # CSV doesn't have this
            }
            products.append(product)
    return products


def analyze_negative_keyword_blocks(products, classifier):
    """
    Identify all products blocked by negative keywords
    and analyze if they're false positives
    """

    blocked_analysis = []

    for product in products:
        title = classifier.normalize_text(product.get('title', ''))
        description = classifier.normalize_text(product.get('description', ''))

        # Test each pattern
        for product_type, pattern in classifier.patterns.items():
            negative_keywords = pattern.get('negative_keywords', [])

            if not negative_keywords:
                continue

            # Check if this product is blocked by any negative keyword
            for neg_kw in negative_keywords:
                blocked = False
                block_location = None

                # Check title
                if neg_kw in title:
                    # Check if current logic blocks it
                    if neg_kw in ['chandelier', 'sconce', 'pendant']:
                        pattern_str = rf'{neg_kw}\s+(led|light|bulb)'
                        if not re.search(pattern_str, title):
                            blocked = True
                            block_location = 'title'
                    elif neg_kw in ['fixture', 'wall mount', 'ceiling mount']:
                        blocked = True
                        block_location = 'title'
                    else:
                        blocked = True
                        block_location = 'title'

                # Check description
                if not blocked and neg_kw in description:
                    if neg_kw not in ['fixture', 'wall mount', 'ceiling mount']:
                        if neg_kw not in ['chandelier', 'sconce', 'pendant']:
                            blocked = True
                            block_location = 'description'

                if blocked:
                    # Analyze if this is a false positive
                    # Heuristics:
                    # 1. Does title contain strong keywords for the pattern?
                    # 2. Is the negative keyword in a "for X" or "compatible with X" context?
                    # 3. Is it describing USE CASE vs PRODUCT TYPE?

                    has_strong_keyword = any(
                        classifier.contains_keyword(title, kw)
                        for kw in pattern['strong_keywords']
                    )

                    # Check for contextual phrases
                    use_case_phrases = [
                        f'for {neg_kw}',
                        f'for use with {neg_kw}',
                        f'for use in {neg_kw}',
                        f'compatible with {neg_kw}',
                        f'{neg_kw} bulb',
                        f'{neg_kw} light bulb',
                        f'{neg_kw} led',
                        f'{neg_kw} lamp',
                        f'replacement for {neg_kw}',
                        f'accessory for {neg_kw}',
                        f'{neg_kw} replacement',
                        f'{neg_kw} accessory',
                    ]

                    is_use_case = any(phrase in title or phrase in description for phrase in use_case_phrases)

                    # Determine if false positive
                    likely_false_positive = has_strong_keyword or is_use_case

                    blocked_analysis.append({
                        'index': product['index'],
                        'title': product['title'],
                        'product_type': product_type,
                        'negative_keyword': neg_kw,
                        'block_location': block_location,
                        'has_strong_keyword': has_strong_keyword,
                        'is_use_case': is_use_case,
                        'likely_false_positive': likely_false_positive,
                        'title_snippet': title[:100],
                        'description_snippet': description[:200]
                    })

    return blocked_analysis


def generate_linguistic_analysis(blocked_analysis):
    """
    Analyze linguistic patterns in blocked products
    to understand context patterns
    """

    false_positives = [b for b in blocked_analysis if b['likely_false_positive']]
    true_blocks = [b for b in blocked_analysis if not b['likely_false_positive']]

    # Extract n-grams around negative keywords
    def extract_context_window(text, keyword, window_size=3):
        """Extract words before and after keyword"""
        words = text.split()
        contexts = []

        for i, word in enumerate(words):
            if keyword in word:
                start = max(0, i - window_size)
                end = min(len(words), i + window_size + 1)
                context = ' '.join(words[start:end])
                contexts.append(context)

        return contexts

    # Analyze patterns
    false_positive_contexts = defaultdict(list)
    true_block_contexts = defaultdict(list)

    for item in false_positives:
        keyword = item['negative_keyword']
        contexts = extract_context_window(item['title_snippet'], keyword, window_size=4)
        false_positive_contexts[keyword].extend(contexts)

    for item in true_blocks:
        keyword = item['negative_keyword']
        contexts = extract_context_window(item['title_snippet'], keyword, window_size=4)
        true_block_contexts[keyword].extend(contexts)

    # Identify common patterns
    linguistic_patterns = {
        'false_positive_indicators': {},
        'true_block_indicators': {}
    }

    for keyword in false_positive_contexts:
        # Find common words appearing with the keyword in false positives
        all_words = []
        for context in false_positive_contexts[keyword]:
            words = context.lower().split()
            all_words.extend(words)

        word_freq = Counter(all_words)
        # Remove the keyword itself
        if keyword in word_freq:
            del word_freq[keyword]

        top_words = word_freq.most_common(10)
        linguistic_patterns['false_positive_indicators'][keyword] = top_words

    for keyword in true_block_contexts:
        all_words = []
        for context in true_block_contexts[keyword]:
            words = context.lower().split()
            all_words.extend(words)

        word_freq = Counter(all_words)
        if keyword in word_freq:
            del word_freq[keyword]

        top_words = word_freq.most_common(10)
        linguistic_patterns['true_block_indicators'][keyword] = top_words

    return linguistic_patterns, false_positive_contexts, true_block_contexts


def main():
    print("="*80)
    print("NEGATIVE KEYWORD AUDIT")
    print("="*80)

    # Load data
    print("\nLoading CSV data...")
    csv_path = Path(__file__).parent.parent / 'data' / 'scraped_data.csv'
    products = load_csv_data(csv_path)
    print(f"Loaded {len(products)} products")

    # Initialize classifier
    print("\nInitializing classifier...")
    classifier = ProductClassifier()
    print(f"Classifier has {len(classifier.patterns)} patterns")

    # Count negative keywords
    total_neg_kw = sum(len(p.get('negative_keywords', [])) for p in classifier.patterns.values())
    print(f"Total negative keywords across all patterns: {total_neg_kw}")

    # Analyze blocks
    print("\nAnalyzing negative keyword blocks...")
    blocked_analysis = analyze_negative_keyword_blocks(products, classifier)
    print(f"Found {len(blocked_analysis)} total blocks")

    # Separate false positives
    false_positives = [b for b in blocked_analysis if b['likely_false_positive']]
    true_blocks = [b for b in blocked_analysis if not b['likely_false_positive']]

    print(f"  - Likely FALSE POSITIVES: {len(false_positives)} blocks")
    print(f"  - Likely CORRECT blocks: {len(true_blocks)} blocks")

    # Linguistic analysis
    print("\nPerforming linguistic analysis...")
    linguistic_patterns, fp_contexts, tb_contexts = generate_linguistic_analysis(blocked_analysis)

    # Print summary
    print("\n" + "="*80)
    print("FALSE POSITIVE BLOCKS (Products incorrectly rejected)")
    print("="*80)

    # Group by negative keyword
    fp_by_keyword = defaultdict(list)
    for item in false_positives:
        fp_by_keyword[item['negative_keyword']].append(item)

    for keyword, items in sorted(fp_by_keyword.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n❌ Negative Keyword: '{keyword}' - {len(items)} false positive blocks")
        print("-" * 80)

        for item in items[:5]:  # Show first 5 examples
            print(f"\n  Product #{item['index']}: {item['title'][:80]}...")
            print(f"  Pattern: {item['product_type']}")
            print(f"  Block location: {item['block_location']}")
            print(f"  Has strong keyword: {item['has_strong_keyword']}")
            print(f"  Is use case mention: {item['is_use_case']}")

        if len(items) > 5:
            print(f"\n  ... and {len(items) - 5} more")

    # Print linguistic patterns
    print("\n" + "="*80)
    print("LINGUISTIC PATTERNS")
    print("="*80)

    print("\n🔍 FALSE POSITIVE INDICATORS (words appearing in wrongly blocked products):")
    for keyword, word_freq in linguistic_patterns['false_positive_indicators'].items():
        if word_freq:
            top_5 = word_freq[:5]
            words_str = ', '.join([f"{word} ({count})" for word, count in top_5])
            print(f"  '{keyword}': {words_str}")

    # Generate recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    print("\n1. CONTEXT-AWARE PATTERNS NEEDED:")
    print("   - Distinguish 'chandelier bulb' (bulb FOR chandelier) from 'chandelier' (fixture)")
    print("   - Detect prepositional phrases: 'for X', 'compatible with X', 'replacement for X'")
    print("   - Analyze word proximity and n-grams, not just keyword presence")

    print("\n2. SPECIFIC FIXES:")
    for keyword, items in sorted(fp_by_keyword.items(), key=lambda x: len(x[1]), reverse=True):
        if len(items) >= 3:
            print(f"   - '{keyword}': {len(items)} false positives - needs context-aware logic")

    print("\n3. ALGORITHM IMPROVEMENTS:")
    print("   - Implement dependency parsing or phrase-level analysis")
    print("   - Check if negative keyword is MODIFIED by product type (e.g., 'chandelier bulb')")
    print("   - Use context window analysis (words before/after negative keyword)")
    print("   - Distinguish HEAD NOUN from MODIFIER in noun phrases")

    # Save results
    output_dir = Path(__file__).parent.parent / 'outputs'
    output_dir.mkdir(exist_ok=True)

    # Save blocked analysis
    with open(output_dir / 'negative_keyword_audit.json', 'w') as f:
        json.dump({
            'total_blocks': len(blocked_analysis),
            'false_positives': len(false_positives),
            'true_blocks': len(true_blocks),
            'false_positive_details': false_positives,
            'true_block_details': true_blocks,
            'linguistic_patterns': linguistic_patterns
        }, f, indent=2)

    print(f"\n✓ Saved detailed analysis to outputs/negative_keyword_audit.json")

    # Save false positive examples
    with open(output_dir / 'false_positive_examples.json', 'w') as f:
        json.dump(false_positives, f, indent=2)

    print(f"✓ Saved false positive examples to outputs/false_positive_examples.json")

    return blocked_analysis, false_positives, linguistic_patterns


if __name__ == '__main__':
    blocked_analysis, false_positives, linguistic_patterns = main()
