#!/usr/bin/env python3
"""
Comprehensive Analysis of Product Classification Misclassifications

This script identifies and analyzes products where the ground truth is in the title
but the classification was incorrect.
"""

import json
import csv
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set


class MisclassificationAnalyzer:
    """Analyzes classification failures with focus on title-based ground truth"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.output_dir = Path(__file__).parent.parent / 'outputs'

        # Product type indicators that should be obvious from titles
        self.product_type_indicators = {
            'LED Light Bulb': [
                'led light bulb', 'led bulb', 'light bulb', 'lamp bulb',
                'bulb soft white', 'bulb daylight', 'led lamp',
                'incandescent bulb', 'halogen bulb', 'cfl bulb'
            ],
            'Circuit Breaker': ['circuit breaker', 'breaker', 'gfci breaker', 'afci breaker'],
            'Light Switch': ['light switch', 'dimmer switch', 'rocker switch', 'toggle switch'],
            'Faucet': ['faucet', 'kitchen faucet', 'bathroom faucet', 'lavatory faucet'],
            'Toilet': ['toilet'],
            'Sink': ['sink', 'kitchen sink', 'bathroom sink', 'utility sink'],
            'Door Lock': ['door lock', 'deadbolt', 'smart lock'],
            'Ceiling Fan': ['ceiling fan'],
            'Recessed Light': ['recessed light', 'recessed lighting', 'can light', 'canless'],
            'Pendant Light': ['pendant light', 'mini-pendant', 'mini pendant'],
            'Chandelier': ['chandelier'],
            'Wall Sconce': ['sconce', 'wall sconce'],
            'Track Lighting': ['track light', 'track lighting'],
            'Exhaust Fan': ['exhaust fan', 'bathroom fan', 'ventilation fan'],
            'Ladder': ['ladder', 'step ladder', 'extension ladder'],
            'Drill': ['drill', 'cordless drill', 'hammer drill'],
            'Saw': ['saw', 'circular saw', 'miter saw', 'reciprocating saw'],
            'Drill Bit': ['drill bit', 'bit set', 'driver bit'],
            'Water Heater': ['water heater', 'tankless water heater'],
            'Thermostat': ['thermostat'],
            'String Lights': ['string light', 'string lights'],
            'Shower Pan': ['shower pan', 'shower base'],
            'Showerhead': ['showerhead', 'shower head'],
            'Curtain Rod': ['curtain rod', 'drapery rod'],
            'Skylight': ['skylight'],
            'Window': ['window', 'double-hung window'],
            'Door': ['door panel', 'interior door', 'exterior door', 'barn door'],
            'Shop Vacuum': ['shop vac', 'shop vacuum', 'wet dry vac'],
        }

    def load_data(self):
        """Load all required data files"""
        print("Loading data files...")

        # Load scraped data CSV
        csv_path = self.data_dir / 'scraped_data.csv'
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.products = list(reader)
        print(f"  ✓ Loaded {len(self.products)} products from CSV")

        # Load classifications
        classifications_path = self.output_dir / 'product_classifications.json'
        with open(classifications_path) as f:
            self.classifications = json.load(f)
        print(f"  ✓ Loaded {len(self.classifications)} classifications")

        # Load confidence data
        confidence_path = self.output_dir / 'classification_confidence.csv'
        with open(confidence_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.confidence_data = list(reader)
        print(f"  ✓ Loaded confidence data")

    def identify_ground_truth_from_title(self, title: str) -> Tuple[str, str, float]:
        """
        Identify what product type is mentioned in the title
        Returns: (product_type, matched_phrase, confidence)
        """
        title_lower = title.lower()

        matches = []

        for product_type, indicators in self.product_type_indicators.items():
            for indicator in indicators:
                if indicator in title_lower:
                    # Calculate confidence based on specificity
                    # Longer phrases = more specific = higher confidence
                    specificity = len(indicator.split())
                    confidence = min(100, 50 + (specificity * 20))
                    matches.append((product_type, indicator, confidence))

        if not matches:
            return None, None, 0

        # Return the most specific match (longest phrase)
        best_match = max(matches, key=lambda x: len(x[1]))
        return best_match

    def analyze_title_mismatches(self):
        """Find all products where title indicates one type but classification says another"""
        print("\nAnalyzing title-based ground truth mismatches...")

        mismatches = []
        correct_matches = []

        for row in self.confidence_data:
            title = row['Title']
            classified_as = row['Product Type']
            confidence = float(row['Confidence'])

            # Identify what the title says
            ground_truth, matched_phrase, truth_confidence = self.identify_ground_truth_from_title(title)

            if ground_truth:
                # We have ground truth from the title
                if ground_truth != classified_as:
                    # MISMATCH!
                    mismatches.append({
                        'index': int(row['Index']),
                        'title': title,
                        'brand': row['Brand'],
                        'ground_truth': ground_truth,
                        'matched_phrase': matched_phrase,
                        'truth_confidence': truth_confidence,
                        'classified_as': classified_as,
                        'classification_confidence': confidence,
                        'severity': 'HIGH' if truth_confidence >= 80 else 'MEDIUM'
                    })
                else:
                    # Correct classification
                    correct_matches.append({
                        'index': int(row['Index']),
                        'title': title,
                        'product_type': ground_truth,
                        'confidence': confidence
                    })

        self.mismatches = mismatches
        self.correct_matches = correct_matches

        total_with_ground_truth = len(mismatches) + len(correct_matches)

        print(f"\nResults:")
        print(f"  Total products with title-based ground truth: {total_with_ground_truth}")
        print(f"  Correctly classified: {len(correct_matches)} ({len(correct_matches)/total_with_ground_truth*100:.1f}%)")
        print(f"  Misclassified: {len(mismatches)} ({len(mismatches)/total_with_ground_truth*100:.1f}%)")
        print(f"  HIGH severity mismatches: {sum(1 for m in mismatches if m['severity'] == 'HIGH')}")

        return mismatches, correct_matches

    def analyze_scoring_failures(self):
        """Analyze why the scoring algorithm failed for mismatched products"""
        print("\nAnalyzing scoring algorithm failures...")

        # Import the classifier to re-run scoring
        import sys
        sys.path.append(str(Path(__file__).parent))
        from classify_products import ProductClassifier

        classifier = ProductClassifier()

        # Load full product data
        with open(self.data_dir / 'scraped_data_output.json') as f:
            full_products = json.load(f)

        failure_analysis = []

        for mismatch in self.mismatches[:50]:  # Analyze first 50 for detail
            idx = mismatch['index']
            product = full_products[idx]

            ground_truth = mismatch['ground_truth']
            classified_as = mismatch['classified_as']

            # Skip if classified_as is not a real product type (e.g., "Unknown")
            if classified_as not in classifier.patterns:
                continue

            # Calculate scores for both types
            gt_score, gt_reasons = classifier.calculate_match_score(product, ground_truth)
            ca_score, ca_reasons = classifier.calculate_match_score(product, classified_as)

            failure_analysis.append({
                'index': idx,
                'title': mismatch['title'][:80],
                'ground_truth': ground_truth,
                'ground_truth_score': gt_score,
                'ground_truth_reasons': gt_reasons,
                'classified_as': classified_as,
                'classified_as_score': ca_score,
                'classified_as_reasons': ca_reasons,
                'score_difference': ca_score - gt_score,
                'failure_reason': self._identify_failure_reason(gt_score, gt_reasons, ca_score, ca_reasons)
            })

        self.failure_analysis = failure_analysis
        return failure_analysis

    def _identify_failure_reason(self, gt_score, gt_reasons, ca_score, ca_reasons):
        """Identify why the wrong classification scored higher"""
        reasons = []

        if gt_score < 50:
            reasons.append("Ground truth scored too low")

        if ca_score > gt_score + 20:
            reasons.append("Wrong type scored much higher")

        if not any('Title contains' in r for r in gt_reasons):
            reasons.append("Title keyword not detected for ground truth")

        if any('Title contains' in r for r in ca_reasons):
            reasons.append("Wrong type matched title keyword")

        return "; ".join(reasons) if reasons else "Unknown"

    def analyze_keyword_effectiveness(self):
        """Analyze which keywords lead to correct vs incorrect classifications"""
        print("\nAnalyzing keyword effectiveness...")

        # Track keyword precision
        keyword_stats = defaultdict(lambda: {'correct': 0, 'incorrect': 0, 'total': 0})

        # For each product type, track how often its keywords lead to correct classification
        for product_type, indicators in self.product_type_indicators.items():
            for indicator in indicators:
                # Find all products with this indicator in title
                for row in self.confidence_data:
                    title = row['Title'].lower()
                    classified_as = row['Product Type']

                    if indicator in title:
                        keyword_stats[indicator]['total'] += 1

                        if classified_as == product_type:
                            keyword_stats[indicator]['correct'] += 1
                        else:
                            keyword_stats[indicator]['incorrect'] += 1

        # Calculate precision for each keyword
        keyword_effectiveness = []
        for keyword, stats in keyword_stats.items():
            if stats['total'] > 0:
                precision = stats['correct'] / stats['total']
                keyword_effectiveness.append({
                    'keyword': keyword,
                    'precision': precision,
                    'correct': stats['correct'],
                    'incorrect': stats['incorrect'],
                    'total': stats['total'],
                    'category': 'HIGH' if precision >= 0.9 else 'MEDIUM' if precision >= 0.7 else 'LOW'
                })

        # Sort by precision
        keyword_effectiveness.sort(key=lambda x: x['precision'], reverse=True)

        self.keyword_effectiveness = keyword_effectiveness

        print(f"\nKeyword Effectiveness Summary:")
        print(f"  HIGH precision keywords (≥90%): {sum(1 for k in keyword_effectiveness if k['category'] == 'HIGH')}")
        print(f"  MEDIUM precision keywords (70-89%): {sum(1 for k in keyword_effectiveness if k['category'] == 'MEDIUM')}")
        print(f"  LOW precision keywords (<70%): {sum(1 for k in keyword_effectiveness if k['category'] == 'LOW')}")

        return keyword_effectiveness

    def compare_correct_vs_incorrect(self):
        """Statistical comparison of correct vs incorrect classifications"""
        print("\nComparing correct vs incorrect classifications...")

        correct_stats = {
            'confidence_scores': [m['confidence'] for m in self.correct_matches],
            'title_lengths': [len(m['title']) for m in self.correct_matches],
        }

        incorrect_stats = {
            'gt_confidence_scores': [m['classification_confidence'] for m in self.mismatches],
            'title_lengths': [len(m['title']) for m in self.mismatches],
        }

        comparison = {
            'correct_avg_confidence': sum(correct_stats['confidence_scores']) / len(correct_stats['confidence_scores']),
            'incorrect_avg_confidence': sum(incorrect_stats['gt_confidence_scores']) / len(incorrect_stats['gt_confidence_scores']),
            'correct_avg_title_length': sum(correct_stats['title_lengths']) / len(correct_stats['title_lengths']),
            'incorrect_avg_title_length': sum(incorrect_stats['title_lengths']) / len(incorrect_stats['title_lengths']),
        }

        print(f"\nStatistical Comparison:")
        print(f"  Correct classifications:")
        print(f"    - Avg confidence: {comparison['correct_avg_confidence']:.1f}%")
        print(f"    - Avg title length: {comparison['correct_avg_title_length']:.0f} chars")
        print(f"  Incorrect classifications:")
        print(f"    - Avg confidence: {comparison['incorrect_avg_confidence']:.1f}%")
        print(f"    - Avg title length: {comparison['incorrect_avg_title_length']:.0f} chars")

        return comparison

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\nGenerating comprehensive report...")

        report = {
            'summary': {
                'total_products': len(self.confidence_data),
                'products_with_title_ground_truth': len(self.mismatches) + len(self.correct_matches),
                'correct_classifications': len(self.correct_matches),
                'misclassifications': len(self.mismatches),
                'accuracy_rate': len(self.correct_matches) / (len(self.mismatches) + len(self.correct_matches)),
                'high_severity_mismatches': sum(1 for m in self.mismatches if m['severity'] == 'HIGH')
            },
            'top_misclassification_patterns': self._identify_misclassification_patterns(),
            'keyword_effectiveness_summary': {
                'high_precision': [k for k in self.keyword_effectiveness if k['category'] == 'HIGH'],
                'low_precision': [k for k in self.keyword_effectiveness if k['category'] == 'LOW']
            },
            'failure_analysis_summary': self._summarize_failures(),
            'recommendations': self._generate_recommendations()
        }

        # Save detailed reports
        reports_dir = self.output_dir / 'analysis_reports'
        reports_dir.mkdir(exist_ok=True)

        # Save mismatches
        with open(reports_dir / 'title_mismatches.json', 'w') as f:
            json.dump(self.mismatches, f, indent=2)
        print(f"  ✓ Saved title_mismatches.json ({len(self.mismatches)} cases)")

        # Save failure analysis
        with open(reports_dir / 'scoring_failures.json', 'w') as f:
            json.dump(self.failure_analysis, f, indent=2)
        print(f"  ✓ Saved scoring_failures.json ({len(self.failure_analysis)} cases)")

        # Save keyword effectiveness
        with open(reports_dir / 'keyword_effectiveness.json', 'w') as f:
            json.dump(self.keyword_effectiveness, f, indent=2)
        print(f"  ✓ Saved keyword_effectiveness.json")

        # Save comprehensive report
        with open(reports_dir / 'comprehensive_analysis.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  ✓ Saved comprehensive_analysis.json")

        # Save CSV for easy viewing
        self._save_csv_reports(reports_dir)

        return report

    def _identify_misclassification_patterns(self):
        """Identify common patterns in misclassifications"""
        patterns = defaultdict(int)

        for mismatch in self.mismatches:
            pattern_key = f"{mismatch['ground_truth']} → {mismatch['classified_as']}"
            patterns[pattern_key] += 1

        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:20])

    def _summarize_failures(self):
        """Summarize common failure reasons"""
        failure_reasons = Counter()

        for failure in self.failure_analysis:
            failure_reasons[failure['failure_reason']] += 1

        return dict(failure_reasons.most_common())

    def _generate_recommendations(self):
        """Generate recommendations for fixing the scoring algorithm"""
        recommendations = []

        # Analyze the failures to generate specific recommendations
        low_gt_scores = sum(1 for f in self.failure_analysis if f['ground_truth_score'] < 50)

        if low_gt_scores > len(self.failure_analysis) * 0.3:
            recommendations.append({
                'issue': 'Ground truth products scoring too low',
                'count': low_gt_scores,
                'solution': 'Increase weight for exact title matches',
                'priority': 'HIGH'
            })

        # Check for negative keyword issues
        chandelier_issues = [m for m in self.mismatches if 'chandelier' in m['title'].lower() and 'bulb' in m['title'].lower()]
        if chandelier_issues:
            recommendations.append({
                'issue': 'Negative keywords blocking valid matches (e.g., chandelier bulbs)',
                'count': len(chandelier_issues),
                'solution': 'Implement context-aware negative keyword matching',
                'priority': 'HIGH'
            })

        # Check weak keyword dominance
        weak_keyword_issues = sum(1 for f in self.failure_analysis if f['classified_as_score'] > f['ground_truth_score'] + 30)
        if weak_keyword_issues > 0:
            recommendations.append({
                'issue': 'Wrong types scoring higher due to weak keyword accumulation',
                'count': weak_keyword_issues,
                'solution': 'Reduce weight of weak keywords, increase title match bonus',
                'priority': 'HIGH'
            })

        return recommendations

    def _save_csv_reports(self, reports_dir):
        """Save CSV reports for easy viewing"""
        # Mismatches CSV
        with open(reports_dir / 'title_mismatches.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Index', 'Title', 'Ground Truth', 'Matched Phrase', 'Classified As', 'Severity', 'Classification Confidence']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for m in self.mismatches:
                writer.writerow({
                    'Index': m['index'],
                    'Title': m['title'][:100],
                    'Ground Truth': m['ground_truth'],
                    'Matched Phrase': m['matched_phrase'],
                    'Classified As': m['classified_as'],
                    'Severity': m['severity'],
                    'Classification Confidence': m['classification_confidence']
                })
        print(f"  ✓ Saved title_mismatches.csv")

        # Keyword effectiveness CSV
        with open(reports_dir / 'keyword_effectiveness.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['keyword', 'precision', 'correct', 'incorrect', 'total', 'category']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for kw in self.keyword_effectiveness:
                writer.writerow(kw)
        print(f"  ✓ Saved keyword_effectiveness.csv")


def main():
    """Run comprehensive misclassification analysis"""
    print("="*80)
    print("PRODUCT CLASSIFICATION MISCLASSIFICATION ANALYSIS")
    print("="*80)

    analyzer = MisclassificationAnalyzer()

    # Step 1: Load data
    analyzer.load_data()

    # Step 2: Identify title-based mismatches
    mismatches, correct = analyzer.analyze_title_mismatches()

    # Step 3: Analyze scoring failures
    failures = analyzer.analyze_scoring_failures()

    # Step 4: Analyze keyword effectiveness
    keyword_eff = analyzer.analyze_keyword_effectiveness()

    # Step 5: Compare correct vs incorrect
    comparison = analyzer.compare_correct_vs_incorrect()

    # Step 6: Generate comprehensive report
    report = analyzer.generate_report()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nKey Findings:")
    print(f"  - Accuracy on title-based ground truth: {report['summary']['accuracy_rate']*100:.1f}%")
    print(f"  - Total misclassifications: {report['summary']['misclassifications']}")
    print(f"  - High severity cases: {report['summary']['high_severity_mismatches']}")

    print(f"\nTop Misclassification Patterns:")
    for pattern, count in list(report['top_misclassification_patterns'].items())[:5]:
        print(f"  - {pattern}: {count} cases")

    print(f"\nRecommendations ({len(report['recommendations'])} total):")
    for rec in report['recommendations']:
        print(f"  [{rec['priority']}] {rec['issue']}")
        print(f"         Solution: {rec['solution']}")

    print(f"\n✓ All reports saved to outputs/analysis_reports/")

    return report


if __name__ == '__main__':
    report = main()
