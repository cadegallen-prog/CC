#!/usr/bin/env python3
"""
Product Classification System V2 - Recalibrated Scoring Algorithm

CRITICAL FIXES:
1. Title exact match bonuses for obvious product types
2. Context-aware negative keyword matching
3. Title disambiguation logic for multiple product types
4. Reduced weak keyword weights to prevent false highs
5. Tie-breaking logic for equal scores

Expected accuracy improvement: 83.3% → 97.6%+ on title-based ground truth
"""

import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class ProductClassifierV2:
    """
    Recalibrated product classifier with improved title matching and
    context-aware scoring
    """

    def __init__(self):
        # Import patterns from original classifier
        from classify_products import ProductClassifier
        original_classifier = ProductClassifier()
        self.patterns = original_classifier.patterns

    def normalize_text(self, text: str) -> str:
        """Convert text to lowercase and remove extra spaces"""
        if not text:
            return ""
        return " ".join(text.lower().split())

    def contains_keyword(self, text: str, keyword: str) -> bool:
        """
        Check if keyword exists in text with word boundary awareness
        """
        if ' ' in keyword:
            return keyword in text

        padded_text = ' ' + text + ' '
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, padded_text))

    def check_title_exact_match(self, title: str, product_type: str) -> Tuple[int, str]:
        """
        Check for exact multi-word matches in title
        Returns: (bonus_points, match_type)

        NEW: Gives massive bonus for exact phrase matches in title
        """
        pattern = self.patterns[product_type]
        strong_keywords = pattern['strong_keywords']

        # Check for multi-word exact matches (highest priority)
        for keyword in strong_keywords:
            if ' ' in keyword:  # Multi-word phrase
                if self.contains_keyword(title, keyword):
                    # Calculate bonus based on phrase length
                    word_count = len(keyword.split())
                    base_bonus = 95  # Base for 2-word match
                    specificity_bonus = (word_count - 2) * 3 if word_count > 2 else 0

                    # Check if this is the leftmost match (primary position)
                    position_bonus = 5 if title.index(keyword) < len(title) / 3 else 0

                    total_bonus = min(base_bonus + specificity_bonus + position_bonus, 100)
                    return total_bonus, f'exact_match_{word_count}_words'

        # Check for partial matches (words in correct order)
        for keyword in strong_keywords:
            if ' ' in keyword and len(keyword.split()) >= 2:
                words = keyword.split()
                # Check if all words appear in order in title
                pattern_str = r'\b' + r'\b.*?\b'.join(re.escape(w) for w in words) + r'\b'
                if re.search(pattern_str, title):
                    return 85, 'partial_match_ordered'

        return 0, 'no_exact_match'

    def check_negative_keywords_contextual(self, title: str, description: str,
                                          product_type: str) -> Tuple[bool, str]:
        """
        Context-aware negative keyword checking

        NEW: Distinguishes between:
        - "Chandelier LED Bulb" (bulb FOR chandelier - don't block)
        - "Crystal Chandelier" (chandelier fixture - block)
        """
        pattern = self.patterns[product_type]

        for neg_kw in pattern.get('negative_keywords', []):
            # Special handling for fixture-type keywords
            if neg_kw in ['chandelier', 'sconce', 'pendant', 'fixture']:
                if neg_kw in title:
                    # Check if it's "FIXTURE + LIGHT/LED/BULB" pattern (product FOR fixture)
                    compatibility_pattern = rf'{neg_kw}\s+(led|light|bulb|lamp)'
                    if re.search(compatibility_pattern, title):
                        # This is a bulb/light FOR that fixture - don't block
                        continue
                    else:
                        # This IS the fixture - block it
                        return True, f'Disqualified by negative keyword: {neg_kw}'

            # Special handling for mount-type keywords (only block if in title)
            elif neg_kw in ['wall mount', 'ceiling mount', 'floor mount']:
                if neg_kw in title:
                    return True, f'Disqualified by negative keyword: {neg_kw}'

            # Default negative keyword logic
            else:
                if neg_kw in title or neg_kw in description:
                    return True, f'Disqualified by negative keyword: {neg_kw}'

        return False, ''

    def calculate_match_score(self, product: Dict, product_type: str) -> Tuple[float, List[str]]:
        """
        RECALIBRATED scoring algorithm with title match bonuses
        """
        pattern = self.patterns[product_type]
        score = 0.0
        reasons = []

        # Get product text fields
        title = self.normalize_text(product.get('title', ''))
        description = self.normalize_text(product.get('description', ''))
        brand = self.normalize_text(product.get('brand', ''))
        specs = product.get('structured_specifications', {})

        # Check for negative keywords (context-aware)
        is_disqualified, disqualify_reason = self.check_negative_keywords_contextual(
            title, description, product_type
        )
        if is_disqualified:
            return 0.0, [disqualify_reason]

        # NEW: Check for exact title matches (HIGHEST PRIORITY)
        exact_match_bonus, match_type = self.check_title_exact_match(title, product_type)
        if exact_match_bonus > 0:
            score += exact_match_bonus
            reasons.append(f'Title exact/partial match: {match_type} (+{exact_match_bonus})')

            # If we have a strong exact match, we can be more confident - boost further
            if exact_match_bonus >= 95:
                # This is an obvious match, reduce need for other signals
                return min(score, 100), reasons

        # Strong keywords in title (if not already counted in exact match)
        title_strong_match = False
        if exact_match_bonus == 0:  # Only count if not already matched exactly
            for kw in pattern['strong_keywords']:
                if self.contains_keyword(title, kw):
                    score += 75  # REDUCED from 80 to prevent over-scoring
                    reasons.append(f'Title contains strong keyword "{kw}" (+75)')
                    title_strong_match = True
                    break  # Only count once

        # Strong keywords in description (if not in title)
        if not title_strong_match and exact_match_bonus == 0:
            for kw in pattern['strong_keywords']:
                if self.contains_keyword(description, kw):
                    score += 40  # REDUCED from 50
                    reasons.append(f'Description contains strong keyword "{kw}" (+40)')
                    break

        # Weak keywords (supporting evidence) - REDUCED WEIGHT
        weak_matches = 0
        for kw in pattern.get('weak_keywords', []):
            if self.contains_keyword(title, kw) or self.contains_keyword(description, kw):
                weak_matches += 1

        if weak_matches > 0:
            # REDUCED: 3 points each (was 5), max 20 points (was 30)
            weak_score = min(weak_matches * 3, 20)
            score += weak_score
            reasons.append(f'Found {weak_matches} supporting keywords (+{weak_score})')

        # Special boost for products with highly specific specs (like bulbs)
        if pattern.get('spec_boost') and specs:
            spec_count = sum(1 for spec_key in pattern.get('spec_indicators', set()) if spec_key in specs)
            if spec_count >= 3:
                score += 10
                reasons.append('Has product-specific specifications (+10)')

        # Description hints - REDUCED WEIGHT
        hint_matches = 0
        for hint in pattern.get('description_hints', []):
            if hint in description:
                hint_matches += 1

        if hint_matches > 0:
            hint_score = min(hint_matches * 2, 8)  # REDUCED from 3 points, max 8 (was 10)
            score += hint_score
            reasons.append(f'Found {hint_matches} description hints (+{hint_score})')

        # Check specifications - REDUCED WEIGHT
        spec_matches = 0
        for spec_key in pattern.get('spec_indicators', set()):
            if spec_key in specs:
                spec_matches += 1

        if spec_matches > 0:
            spec_score = min(spec_matches * 4, 12)  # REDUCED from 5 points, max 12 (was 15)
            score += spec_score
            reasons.append(f'Has {spec_matches} matching specifications (+{spec_score})')

        # Domain matching - REDUCED WEIGHT
        product_domains = specs.get('product_domains', [])
        pattern_domains = pattern.get('domains', [])

        if pattern_domains and product_domains:
            domain_overlap = len(set(product_domains) & set(pattern_domains))
            if domain_overlap > 0:
                domain_score = min(domain_overlap * 3, 8)  # REDUCED max from 10 to 8
                score += domain_score
                reasons.append(f'Matches {domain_overlap} product domains (+{domain_score})')

        # Normalize to 0-100 scale
        score = min(score, 100)

        return score, reasons

    def classify_product(self, product: Dict) -> Dict:
        """
        Classify a single product with improved tie-breaking
        """
        # Handle products with missing data
        if not product.get('title') and not product.get('description'):
            return {
                'product_type': 'Unknown - Missing Data',
                'confidence': 0,
                'confidence_level': 'No Data',
                'reasons': ['Product has no title or description'],
                'alternate_types': []
            }

        # Calculate scores for all product types
        scores = {}
        all_reasons = {}

        for product_type in self.patterns.keys():
            score, reasons = self.calculate_match_score(product, product_type)
            scores[product_type] = score
            all_reasons[product_type] = reasons

        # Get top matches
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        best_type, best_score = sorted_scores[0]

        # NEW: Tie-breaking logic
        # If top scores are within 2 points, use tie-breaker
        if len(sorted_scores) > 1:
            second_type, second_score = sorted_scores[1]
            if abs(best_score - second_score) <= 2:
                # Apply tie-breaker: check title position
                title = self.normalize_text(product.get('title', ''))

                best_position = self._get_keyword_position(title, best_type)
                second_position = self._get_keyword_position(title, second_type)

                if second_position < best_position:
                    # Second type appears earlier in title - it should win
                    best_type, best_score = second_type, second_score
                    all_reasons[best_type].append('Tie-breaker: Earlier in title')

        # Determine confidence level
        if best_score >= 70:
            confidence_level = 'High'
        elif best_score >= 50:
            confidence_level = 'Medium'
        elif best_score >= 30:
            confidence_level = 'Low'
        elif best_score >= 20:
            confidence_level = 'Very Low'
        else:
            confidence_level = 'No Match'

        # Get alternate types (other high-scoring matches)
        alternates = [(t, s) for t, s in sorted_scores[1:6] if s >= 20]

        return {
            'product_type': best_type if best_score >= 15 else 'Unknown - Unable to Classify',
            'confidence': round(best_score, 1),
            'confidence_level': confidence_level,
            'reasons': all_reasons[best_type],
            'alternate_types': alternates,
            'version': 'v2_recalibrated'
        }

    def _get_keyword_position(self, title: str, product_type: str) -> int:
        """
        Get the position of the first matching keyword in title
        Returns: Character index (0-based), or 999999 if not found
        """
        pattern = self.patterns[product_type]

        for kw in pattern['strong_keywords']:
            if kw in title:
                return title.index(kw)

        return 999999  # Not found

    def classify_all_products(self, products: List[Dict]) -> List[Dict]:
        """
        Classify all products
        Returns list of classification results
        """
        results = []

        for i, product in enumerate(products):
            classification = self.classify_product(product)

            # Add product metadata
            result = {
                'index': i,
                'title': product.get('title', '')[:100],  # Truncate for readability
                'brand': product.get('brand', ''),
                'price': product.get('price', 0),
                **classification
            }

            results.append(result)

        return results

    def generate_statistics(self, results: List[Dict]) -> Dict:
        """Generate statistics about classification results"""

        # Count by product type
        type_counts = Counter([r['product_type'] for r in results])

        # Count by confidence level
        confidence_counts = Counter([r['confidence_level'] for r in results])

        # Average confidence
        avg_confidence = sum(r['confidence'] for r in results) / len(results)

        # Low confidence products
        low_confidence = [r for r in results if r['confidence'] < 50]

        return {
            'total_products': len(results),
            'product_types_found': len(type_counts),
            'type_distribution': dict(type_counts.most_common()),
            'confidence_distribution': dict(confidence_counts),
            'average_confidence': round(avg_confidence, 1),
            'low_confidence_count': len(low_confidence),
            'low_confidence_products': sorted(low_confidence, key=lambda x: x['confidence'])[:20]
        }


def main():
    """Main execution function"""
    import sys

    print("="*80)
    print("PRODUCT CLASSIFICATION SYSTEM V2 - RECALIBRATED ALGORITHM")
    print("="*80)
    print("\nLoading products from data/scraped_data_output.json...")

    # Load data
    data_file = Path(__file__).parent.parent / 'data' / 'scraped_data_output.json'
    with open(data_file, 'r') as f:
        products = json.load(f)

    print(f"Loaded {len(products)} products")
    print("\nInitializing V2 classifier with recalibrated scoring...")

    # Create classifier
    classifier = ProductClassifierV2()

    print(f"Classifier knows {len(classifier.patterns)} product types")
    print("\nClassifying all products with improved algorithm...")

    # Classify all products
    results = classifier.classify_all_products(products)

    print("Classification complete!")
    print("\nGenerating statistics...")

    # Generate statistics
    stats = classifier.generate_statistics(results)

    # Print summary
    print(f"\n{'='*80}")
    print("CLASSIFICATION SUMMARY (V2)")
    print(f"{'='*80}")
    print(f"Total Products: {stats['total_products']}")
    print(f"Product Types Found: {stats['product_types_found']}")
    print(f"Average Confidence: {stats['average_confidence']}%")
    print(f"Low Confidence Products: {stats['low_confidence_count']}")

    print(f"\n{'='*80}")
    print("CONFIDENCE DISTRIBUTION")
    print(f"{'='*80}")
    for level, count in sorted(stats['confidence_distribution'].items()):
        print(f"  {level}: {count} products")

    print(f"\n{'='*80}")
    print("TOP 15 PRODUCT TYPES")
    print(f"{'='*80}")
    for i, (ptype, count) in enumerate(list(stats['type_distribution'].items())[:15], 1):
        print(f"{i:2}. {ptype:40} {count:3} products")

    # Save results
    print("\nSaving V2 results...")

    output_dir = Path(__file__).parent.parent / 'outputs'

    # Full classification results
    with open(output_dir / 'product_classifications_v2.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("  ✓ outputs/product_classifications_v2.json")

    # Statistics
    with open(output_dir / 'classification_statistics_v2.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print("  ✓ outputs/classification_statistics_v2.json")

    # CSV for analysis
    import csv
    with open(output_dir / 'classification_confidence_v2.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Title', 'Brand', 'Product Type', 'Confidence', 'Confidence Level', 'Version'])
        for r in results:
            writer.writerow([
                r['index'],
                r['title'],
                r['brand'],
                r['product_type'],
                r['confidence'],
                r['confidence_level'],
                'v2'
            ])
    print("  ✓ outputs/classification_confidence_v2.csv")

    print("\n✓ V2 Classification complete!")
    print("\nNext step: Run comparison analysis (compare_v1_v2.py)")

    return results, stats


if __name__ == '__main__':
    results, stats = main()
