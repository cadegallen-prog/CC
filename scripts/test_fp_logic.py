#!/usr/bin/env python3
"""Test the is_false_positive_block logic directly"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from classify_products import ProductClassifier


def main():
    classifier = ProductClassifier()

    # Test text from Product #343 description
    text = "dimmable led ideal for sconces, chandeliers or damp rated fixture"

    negative_kw = "fixture"
    pattern = classifier.patterns['LED Light Bulb']

    print("Testing is_false_positive_block:")
    print(f"Text: {text}")
    print(f"Negative keyword: {negative_kw}")
    print(f"Pattern: LED Light Bulb")
    print()

    result = classifier.is_false_positive_block(text, negative_kw, pattern, 'description')

    print(f"Result: {result}")
    print(f"Should NOT block: {result}")

    # Manual check
    print("\nManual checks:")

    # Check for "ideal for"
    if "ideal for" in text:
        indicator_pos = text.find("ideal for")
        neg_pos = text.find(negative_kw)
        print(f"  'ideal for' found at position {indicator_pos}")
        print(f"  'fixture' found at position {neg_pos}")

        if indicator_pos < neg_pos:
            between = text[indicator_pos:neg_pos]
            word_count = len(between.split())
            print(f"  Between text: '{between}'")
            print(f"  Word count: {word_count}")
            print(f"  Within 15 words: {word_count <= 15}")


if __name__ == '__main__':
    main()
