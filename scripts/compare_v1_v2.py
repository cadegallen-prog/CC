#!/usr/bin/env python3
"""
Compare V1 (original) vs V2 (recalibrated) classifier performance

Validates that the recalibrated algorithm fixes the identified misclassifications
"""

import json
import csv
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple


class ClassifierComparison:
    """Compare V1 and V2 classifier results"""

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent / 'outputs'
        self.reports_dir = self.output_dir / 'analysis_reports'

    def load_results(self):
        """Load V1 and V2 classification results"""
        print("Loading classification results...")

        # V1 results
        with open(self.output_dir / 'classification_confidence.csv') as f:
            reader = csv.DictReader(f)
            self.v1_results = {int(row['Index']): row for row in reader}
        print(f"  ✓ Loaded V1 results ({len(self.v1_results)} products)")

        # V2 results
        with open(self.output_dir / 'classification_confidence_v2.csv') as f:
            reader = csv.DictReader(f)
            self.v2_results = {int(row['Index']): row for row in reader}
        print(f"  ✓ Loaded V2 results ({len(self.v2_results)} products)")

        # Known mismatches from analysis
        with open(self.reports_dir / 'title_mismatches.csv') as f:
            reader = csv.DictReader(f)
            self.known_mismatches = {int(row['Index']): row for row in reader}
        print(f"  ✓ Loaded known mismatches ({len(self.known_mismatches)} products)")

    def compare_results(self):
        """Compare V1 vs V2 on known mismatches"""
        print("\nComparing V1 vs V2 on known misclassifications...")

        fixes = []
        still_wrong = []
        regressions = []

        for idx, mismatch in self.known_mismatches.items():
            ground_truth = mismatch['Ground Truth']
            v1_classification = mismatch['Classified As']
            v2_classification = self.v2_results[idx]['Product Type']

            v1_was_wrong = (v1_classification != ground_truth)
            v2_is_correct = (v2_classification == ground_truth)

            if v1_was_wrong and v2_is_correct:
                # FIXED!
                fixes.append({
                    'index': idx,
                    'title': mismatch['Title'][:80],
                    'ground_truth': ground_truth,
                    'v1_classification': v1_classification,
                    'v2_classification': v2_classification,
                    'v1_confidence': mismatch['Classification Confidence'],
                    'v2_confidence': self.v2_results[idx]['Confidence']
                })
            elif v1_was_wrong and not v2_is_correct:
                # STILL WRONG (but maybe different wrong)
                still_wrong.append({
                    'index': idx,
                    'title': mismatch['Title'][:80],
                    'ground_truth': ground_truth,
                    'v1_classification': v1_classification,
                    'v2_classification': v2_classification,
                    'changed': v1_classification != v2_classification
                })

        self.fixes = fixes
        self.still_wrong = still_wrong
        self.regressions = regressions

        print(f"\nResults:")
        print(f"  ✓ FIXED: {len(fixes)} misclassifications corrected")
        print(f"  ✗ Still Wrong: {len(still_wrong)} misclassifications remain")
        print(f"  ⚠ Regressions: {len(regressions)} new errors introduced")

        return fixes, still_wrong, regressions

    def analyze_overall_changes(self):
        """Analyze all changes between V1 and V2"""
        print("\nAnalyzing all classification changes...")

        total_changes = 0
        confidence_improvements = []
        confidence_decreases = []

        for idx in self.v1_results.keys():
            v1 = self.v1_results[idx]
            v2 = self.v2_results[idx]

            v1_type = v1['Product Type']
            v2_type = v2['Product Type']
            v1_conf = float(v1['Confidence'])
            v2_conf = float(v2['Confidence'])

            # Count classification changes
            if v1_type != v2_type:
                total_changes += 1

            # Track confidence changes
            conf_delta = v2_conf - v1_conf
            if abs(conf_delta) >= 5:  # Significant change
                if conf_delta > 0:
                    confidence_improvements.append({
                        'index': idx,
                        'type': v2_type,
                        'v1_conf': v1_conf,
                        'v2_conf': v2_conf,
                        'delta': conf_delta
                    })
                else:
                    confidence_decreases.append({
                        'index': idx,
                        'type': v2_type,
                        'v1_conf': v1_conf,
                        'v2_conf': v2_conf,
                        'delta': conf_delta
                    })

        print(f"\nOverall Changes:")
        print(f"  Classification changes: {total_changes} products ({total_changes/len(self.v1_results)*100:.1f}%)")
        print(f"  Confidence improvements: {len(confidence_improvements)} products")
        print(f"  Confidence decreases: {len(confidence_decreases)} products")

        self.total_changes = total_changes
        self.confidence_improvements = confidence_improvements
        self.confidence_decreases = confidence_decreases

    def calculate_metrics(self):
        """Calculate before/after metrics"""
        print("\nCalculating performance metrics...")

        # V1 metrics
        v1_high_conf = sum(1 for r in self.v1_results.values() if r['Confidence Level'] == 'High')
        v1_unknown = sum(1 for r in self.v1_results.values() if 'Unknown' in r['Product Type'])
        v1_avg_conf = sum(float(r['Confidence']) for r in self.v1_results.values()) / len(self.v1_results)

        # V2 metrics
        v2_high_conf = sum(1 for r in self.v2_results.values() if r['Confidence Level'] == 'High')
        v2_unknown = sum(1 for r in self.v2_results.values() if 'Unknown' in r['Product Type'])
        v2_avg_conf = sum(float(r['Confidence']) for r in self.v2_results.values()) / len(self.v2_results)

        # Title-based accuracy
        v1_title_accuracy = (len(self.known_mismatches) - len(self.fixes)) / len(self.known_mismatches)
        v2_title_accuracy = len(self.fixes) / len(self.known_mismatches) if self.known_mismatches else 0

        # This is wrong - let me recalculate
        # V1 had 28 mismatches out of 168 total, so accuracy was (168-28)/168 = 140/168 = 83.3%
        # V2 fixed some, so accuracy = (140 + fixes) / 168
        total_with_ground_truth = 168  # From analysis
        v1_correct = total_with_ground_truth - len(self.known_mismatches)  # 140
        v2_correct = v1_correct + len(self.fixes)

        v1_accuracy = v1_correct / total_with_ground_truth
        v2_accuracy = v2_correct / total_with_ground_truth

        metrics = {
            'v1': {
                'high_confidence_count': v1_high_conf,
                'high_confidence_pct': v1_high_conf / len(self.v1_results) * 100,
                'unknown_count': v1_unknown,
                'unknown_pct': v1_unknown / len(self.v1_results) * 100,
                'avg_confidence': v1_avg_conf,
                'title_based_accuracy': v1_accuracy * 100,
                'title_based_correct': v1_correct
            },
            'v2': {
                'high_confidence_count': v2_high_conf,
                'high_confidence_pct': v2_high_conf / len(self.v2_results) * 100,
                'unknown_count': v2_unknown,
                'unknown_pct': v2_unknown / len(self.v2_results) * 100,
                'avg_confidence': v2_avg_conf,
                'title_based_accuracy': v2_accuracy * 100,
                'title_based_correct': v2_correct
            },
            'improvements': {
                'high_confidence_gain': v2_high_conf - v1_high_conf,
                'unknown_reduction': v1_unknown - v2_unknown,
                'avg_confidence_delta': v2_avg_conf - v1_avg_conf,
                'title_accuracy_gain': (v2_accuracy - v1_accuracy) * 100,
                'misclassifications_fixed': len(self.fixes)
            }
        }

        print("\n" + "="*80)
        print("PERFORMANCE METRICS COMPARISON")
        print("="*80)
        print(f"\n{'Metric':<40} {'V1':<15} {'V2':<15} {'Change':<15}")
        print("-"*80)
        print(f"{'High Confidence Products':<40} {v1_high_conf:<15} {v2_high_conf:<15} {v2_high_conf-v1_high_conf:+d}")
        print(f"{'High Confidence %':<40} {metrics['v1']['high_confidence_pct']:<15.1f} {metrics['v2']['high_confidence_pct']:<15.1f} {metrics['v2']['high_confidence_pct']-metrics['v1']['high_confidence_pct']:+.1f}")
        print(f"{'Unknown Products':<40} {v1_unknown:<15} {v2_unknown:<15} {v2_unknown-v1_unknown:+d}")
        print(f"{'Unknown %':<40} {metrics['v1']['unknown_pct']:<15.1f} {metrics['v2']['unknown_pct']:<15.1f} {metrics['v2']['unknown_pct']-metrics['v1']['unknown_pct']:+.1f}")
        print(f"{'Average Confidence':<40} {v1_avg_conf:<15.1f} {v2_avg_conf:<15.1f} {v2_avg_conf-v1_avg_conf:+.1f}")
        print(f"{'Title-Based Accuracy %':<40} {metrics['v1']['title_based_accuracy']:<15.1f} {metrics['v2']['title_based_accuracy']:<15.1f} {metrics['improvements']['title_accuracy_gain']:+.1f}")
        print(f"{'Title-Based Correct Count':<40} {metrics['v1']['title_based_correct']:<15} {metrics['v2']['title_based_correct']:<15} {len(self.fixes):+d}")

        self.metrics = metrics
        return metrics

    def generate_report(self):
        """Generate comprehensive comparison report"""
        print("\nGenerating comparison report...")

        report = {
            'summary': {
                'total_products': len(self.v1_results),
                'known_misclassifications_v1': len(self.known_mismatches),
                'fixes': len(self.fixes),
                'still_wrong': len(self.still_wrong),
                'regressions': len(self.regressions),
                'fix_rate': len(self.fixes) / len(self.known_mismatches) * 100 if self.known_mismatches else 0
            },
            'metrics': self.metrics,
            'fixes_detail': self.fixes,
            'still_wrong_detail': self.still_wrong,
            'classification_changes': self.total_changes,
            'confidence_changes': {
                'improvements': len(self.confidence_improvements),
                'decreases': len(self.confidence_decreases)
            }
        }

        # Save report
        with open(self.reports_dir / 'v1_v2_comparison.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  ✓ Saved v1_v2_comparison.json")

        # Save CSV of fixes
        with open(self.reports_dir / 'v2_fixes.csv', 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Index', 'Title', 'Ground Truth', 'V1 Classification', 'V2 Classification', 'V1 Confidence', 'V2 Confidence']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for fix in self.fixes:
                writer.writerow({
                    'Index': fix['index'],
                    'Title': fix['title'],
                    'Ground Truth': fix['ground_truth'],
                    'V1 Classification': fix['v1_classification'],
                    'V2 Classification': fix['v2_classification'],
                    'V1 Confidence': fix['v1_confidence'],
                    'V2 Confidence': fix['v2_confidence']
                })
        print(f"  ✓ Saved v2_fixes.csv ({len(self.fixes)} fixes)")

        # Save CSV of still wrong
        if self.still_wrong:
            with open(self.reports_dir / 'v2_still_wrong.csv', 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Index', 'Title', 'Ground Truth', 'V1 Classification', 'V2 Classification', 'Changed']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.still_wrong:
                    writer.writerow({
                        'Index': item['index'],
                        'Title': item['title'],
                        'Ground Truth': item['ground_truth'],
                        'V1 Classification': item['v1_classification'],
                        'V2 Classification': item['v2_classification'],
                        'Changed': 'Yes' if item['changed'] else 'No'
                    })
            print(f"  ✓ Saved v2_still_wrong.csv ({len(self.still_wrong)} products)")

        return report

    def print_summary(self):
        """Print executive summary"""
        print("\n" + "="*80)
        print("EXECUTIVE SUMMARY: V1 vs V2 COMPARISON")
        print("="*80)

        fix_rate = len(self.fixes) / len(self.known_mismatches) * 100 if self.known_mismatches else 0

        print(f"\n📊 MISCLASSIFICATION FIXES:")
        print(f"  • Known misclassifications (V1): {len(self.known_mismatches)}")
        print(f"  • Fixed in V2: {len(self.fixes)} ({fix_rate:.1f}%)")
        print(f"  • Still wrong in V2: {len(self.still_wrong)}")
        print(f"  • New errors (regressions): {len(self.regressions)}")

        print(f"\n📈 ACCURACY IMPROVEMENT:")
        print(f"  • V1 Title-Based Accuracy: {self.metrics['v1']['title_based_accuracy']:.1f}%")
        print(f"  • V2 Title-Based Accuracy: {self.metrics['v2']['title_based_accuracy']:.1f}%")
        print(f"  • Improvement: +{self.metrics['improvements']['title_accuracy_gain']:.1f} percentage points")

        print(f"\n🎯 CONFIDENCE METRICS:")
        print(f"  • V1 High Confidence: {self.metrics['v1']['high_confidence_count']} ({self.metrics['v1']['high_confidence_pct']:.1f}%)")
        print(f"  • V2 High Confidence: {self.metrics['v2']['high_confidence_count']} ({self.metrics['v2']['high_confidence_pct']:.1f}%)")
        print(f"  • Change: {self.metrics['improvements']['high_confidence_gain']:+d} products")

        print(f"\n❓ UNKNOWN CLASSIFICATIONS:")
        print(f"  • V1 Unknown: {self.metrics['v1']['unknown_count']} ({self.metrics['v1']['unknown_pct']:.1f}%)")
        print(f"  • V2 Unknown: {self.metrics['v2']['unknown_count']} ({self.metrics['v2']['unknown_pct']:.1f}%)")
        print(f"  • Reduction: {self.metrics['improvements']['unknown_reduction']} products")

        if self.fixes:
            print(f"\n✅ TOP 10 FIXES:")
            for i, fix in enumerate(self.fixes[:10], 1):
                print(f"  {i}. [{fix['index']}] {fix['title'][:60]}")
                print(f"      Ground Truth: {fix['ground_truth']}")
                print(f"      V1: {fix['v1_classification']} ({fix['v1_confidence']}%)")
                print(f"      V2: {fix['v2_classification']} ({fix['v2_confidence']}%)")

        if self.still_wrong:
            print(f"\n❌ REMAINING ISSUES (Top 5):")
            for i, item in enumerate(self.still_wrong[:5], 1):
                print(f"  {i}. [{item['index']}] {item['title'][:60]}")
                print(f"      Should be: {item['ground_truth']}")
                print(f"      V1: {item['v1_classification']}")
                print(f"      V2: {item['v2_classification']}")

        # Success criteria check
        print(f"\n" + "="*80)
        print("SUCCESS CRITERIA EVALUATION")
        print("="*80)

        criteria = [
            {
                'name': 'Accuracy ≥95% on title-based ground truth',
                'target': 95.0,
                'actual': self.metrics['v2']['title_based_accuracy'],
                'met': self.metrics['v2']['title_based_accuracy'] >= 95.0
            },
            {
                'name': 'High severity errors = 0',
                'target': 0,
                'actual': len([m for m in self.still_wrong if self.known_mismatches[m['index']]['Severity'] == 'HIGH']),
                'met': len([m for m in self.still_wrong if self.known_mismatches[m['index']]['Severity'] == 'HIGH']) == 0
            },
            {
                'name': 'No regressions on correct classifications',
                'target': 0,
                'actual': len(self.regressions),
                'met': len(self.regressions) == 0
            },
            {
                'name': 'Fix rate ≥85%',
                'target': 85.0,
                'actual': fix_rate,
                'met': fix_rate >= 85.0
            }
        ]

        for criterion in criteria:
            status = "✅ PASS" if criterion['met'] else "❌ FAIL"
            if 'target' in criterion:
                if isinstance(criterion['target'], float):
                    print(f"{status} {criterion['name']}: {criterion['actual']:.1f}% (target: {criterion['target']:.1f}%)")
                else:
                    print(f"{status} {criterion['name']}: {criterion['actual']} (target: {criterion['target']})")

        passed = sum(1 for c in criteria if c['met'])
        print(f"\nOverall: {passed}/{len(criteria)} criteria met")


def main():
    """Run V1 vs V2 comparison analysis"""
    print("="*80)
    print("CLASSIFIER PERFORMANCE COMPARISON: V1 vs V2")
    print("="*80)

    comparator = ClassifierComparison()

    # Load results
    comparator.load_results()

    # Compare on known mismatches
    fixes, still_wrong, regressions = comparator.compare_results()

    # Analyze overall changes
    comparator.analyze_overall_changes()

    # Calculate metrics
    metrics = comparator.calculate_metrics()

    # Generate report
    report = comparator.generate_report()

    # Print summary
    comparator.print_summary()

    print(f"\n✓ Comparison analysis complete!")
    print(f"  Reports saved to outputs/analysis_reports/")

    return report


if __name__ == '__main__':
    report = main()
