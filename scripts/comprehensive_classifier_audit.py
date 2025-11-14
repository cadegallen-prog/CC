#!/usr/bin/env python3
"""
Comprehensive Classifier Accuracy Audit
Analyzes current performance and identifies all improvement opportunities
"""

import json
import csv
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
import re


class ClassifierAuditor:
    """Comprehensive classifier performance auditor"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.output_dir = Path(__file__).parent.parent / 'outputs'
        self.products = []
        self.classifications = []
        self.ground_truth = {}

    def load_data(self):
        """Load all data files"""
        print("Loading data files...")

        # Load CSV data
        csv_file = self.data_dir / 'scraped_data.csv'
        print(f"  Loading {csv_file}...")
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.products = list(reader)
        print(f"  ✓ Loaded {len(self.products)} products from CSV")

        # Load classifications
        classifications_file = self.output_dir / 'product_classifications.json'
        print(f"  Loading {classifications_file}...")
        with open(classifications_file, 'r') as f:
            self.classifications = json.load(f)
        print(f"  ✓ Loaded {len(self.classifications)} classifications")

        # Load ground truth
        ground_truth_file = self.data_dir / 'ground_truth.json'
        print(f"  Loading {ground_truth_file}...")
        with open(ground_truth_file, 'r') as f:
            gt_data = json.load(f)
            # Create index lookup
            for sample in gt_data['samples']:
                self.ground_truth[sample['index']] = sample
        print(f"  ✓ Loaded {len(self.ground_truth)} ground truth samples")

    def validate_against_ground_truth(self) -> Dict:
        """Validate classifications against ground truth"""
        print("\nValidating against ground truth...")

        results = {
            'correct': [],
            'incorrect': [],
            'missing': []
        }

        for idx, gt_sample in self.ground_truth.items():
            # Find classification for this product
            classification = None
            for c in self.classifications:
                if c['index'] == idx:
                    classification = c
                    break

            if not classification:
                results['missing'].append({
                    'index': idx,
                    'title': gt_sample['title'],
                    'expected': gt_sample['true_product_type']
                })
                continue

            # Normalize product types for comparison
            predicted = self.normalize_product_type(classification['product_type'])
            expected = self.normalize_product_type(gt_sample['true_product_type'])

            if predicted == expected or self.is_equivalent_type(predicted, expected):
                results['correct'].append({
                    'index': idx,
                    'title': gt_sample['title'],
                    'predicted': classification['product_type'],
                    'confidence': classification['confidence']
                })
            else:
                results['incorrect'].append({
                    'index': idx,
                    'title': gt_sample['title'],
                    'expected': gt_sample['true_product_type'],
                    'predicted': classification['product_type'],
                    'confidence': classification['confidence'],
                    'difficulty': gt_sample.get('difficulty', 'unknown')
                })

        total = len(results['correct']) + len(results['incorrect'])
        accuracy = (len(results['correct']) / total * 100) if total > 0 else 0

        print(f"  Correct: {len(results['correct'])}/{total} ({accuracy:.1f}%)")
        print(f"  Incorrect: {len(results['incorrect'])}")
        print(f"  Missing: {len(results['missing'])}")

        return results

    def normalize_product_type(self, product_type: str) -> str:
        """Normalize product type for comparison"""
        if not product_type:
            return "unknown"

        # Convert to lowercase and remove special characters
        normalized = product_type.lower().replace('-', '_').replace(' ', '_')

        # Handle Unknown variations
        if 'unknown' in normalized or 'missing' in normalized:
            return 'unknown'

        return normalized

    def is_equivalent_type(self, type1: str, type2: str) -> bool:
        """Check if two product types are equivalent"""
        equivalents = {
            ('led_light_bulb', 'light_bulb'),
            ('gfci_usb_outlet', 'usb_outlet'),
            ('smart_flush_mount_light', 'flush_mount_light'),
            ('landscape_flood_light', 'flood_light', 'landscape_lighting'),
            ('smart_deadbolt_lock', 'door_lock'),
            ('circuit_breaker_kit', 'circuit_breaker'),
            ('led_track_lighting_kit', 'track_lighting'),
            ('mini_pendant_light', 'pendant_light'),
            ('electrical_load_center', 'load_center'),
            ('hvac_air_filter', 'air_filter'),
            ('bathroom_exhaust_fan', 'exhaust_fan'),
            ('dual_flush_toilet', 'toilet'),
            ('kitchen_sink_with_faucet', 'sink'),
            ('chainsaw_tuneup_kit', 'tool_kit'),
            ('hex_driver_bits', 'drill_bit'),
            ('sds_plus_rebar_cutter', 'specialty_cutter'),
            ('hvlp_paint_sprayer', 'paint_sprayer'),
            ('velcro_fastener_tape', 'tape'),
            ('safety_respirator_cartridge', 'safety_respirator'),
        }

        # Check direct equivalence
        for equiv_set in equivalents:
            if type1 in equiv_set and type2 in equiv_set:
                return True

        return False

    def analyze_failure_modes(self, validation_results: Dict) -> Dict:
        """Analyze failure modes in detail"""
        print("\nAnalyzing failure modes...")

        failure_modes = {
            'unknown_classifications': [],
            'confident_wrong': [],
            'low_confidence_correct': [],
            'pattern_missing': [],
            'pattern_ambiguous': [],
            'negative_keyword_issues': []
        }

        # Analyze all classifications
        for classification in self.classifications:
            product_type = classification['product_type']
            confidence = classification['confidence']

            # Unknown classifications
            if 'Unknown' in product_type or 'Unable to Classify' in product_type:
                failure_modes['unknown_classifications'].append({
                    'index': classification['index'],
                    'title': classification['title'],
                    'confidence': confidence,
                    'reasons': classification.get('reasons', [])
                })

        # Analyze incorrect predictions
        for error in validation_results['incorrect']:
            # Check if it's a confident wrong prediction
            if error['confidence'] >= 60:
                failure_modes['confident_wrong'].append(error)

            # Check for pattern missing
            expected_type = error['expected']
            if 'Unknown' in error['predicted']:
                failure_modes['pattern_missing'].append({
                    'index': error['index'],
                    'title': error['title'],
                    'missing_type': expected_type
                })

        # Analyze correct but low confidence
        for correct in validation_results['correct']:
            if correct['confidence'] < 60:
                failure_modes['low_confidence_correct'].append(correct)

        # Summary
        print(f"  Unknown classifications: {len(failure_modes['unknown_classifications'])}")
        print(f"  Confident but wrong: {len(failure_modes['confident_wrong'])}")
        print(f"  Low confidence correct: {len(failure_modes['low_confidence_correct'])}")
        print(f"  Missing patterns: {len(failure_modes['pattern_missing'])}")

        return failure_modes

    def analyze_pattern_coverage(self) -> Dict:
        """Analyze which patterns are working and which need improvement"""
        print("\nAnalyzing pattern coverage...")

        # Count all classified types
        type_counts = Counter([c['product_type'] for c in self.classifications])

        # Analyze confidence distribution per type
        type_confidence = defaultdict(list)
        for c in self.classifications:
            type_confidence[c['product_type']].append(c['confidence'])

        # Calculate average confidence per type
        type_avg_confidence = {}
        for ptype, confidences in type_confidence.items():
            type_avg_confidence[ptype] = sum(confidences) / len(confidences)

        # Identify weak patterns (low average confidence)
        weak_patterns = []
        for ptype, avg_conf in sorted(type_avg_confidence.items(), key=lambda x: x[1]):
            if avg_conf < 60 and type_counts[ptype] > 1:
                weak_patterns.append({
                    'type': ptype,
                    'count': type_counts[ptype],
                    'avg_confidence': round(avg_conf, 1)
                })

        print(f"  Total unique types: {len(type_counts)}")
        print(f"  Weak patterns (avg conf < 60): {len(weak_patterns)}")

        return {
            'type_counts': dict(type_counts),
            'type_avg_confidence': type_avg_confidence,
            'weak_patterns': weak_patterns
        }

    def identify_missing_product_types(self, failure_modes: Dict) -> List[str]:
        """Identify product types that need to be added to the classifier"""
        print("\nIdentifying missing product types...")

        missing_types = set()

        # From ground truth errors
        for pattern in failure_modes['pattern_missing']:
            missing_types.add(pattern['missing_type'])

        # From ground truth (compare all expected types vs available patterns)
        from classify_products import ProductClassifier
        classifier = ProductClassifier()
        available_patterns = set(classifier.patterns.keys())

        for idx, gt_sample in self.ground_truth.items():
            expected_type = self.normalize_product_type(gt_sample['true_product_type'])
            # Check if we have a pattern for this type
            pattern_exists = False
            for pattern in available_patterns:
                if self.normalize_product_type(pattern) == expected_type:
                    pattern_exists = True
                    break

            if not pattern_exists:
                missing_types.add(gt_sample['true_product_type'])

        print(f"  Missing product types: {len(missing_types)}")
        for mtype in sorted(missing_types):
            print(f"    - {mtype}")

        return list(missing_types)

    def analyze_scoring_issues(self, validation_results: Dict) -> Dict:
        """Analyze issues with the scoring system"""
        print("\nAnalyzing scoring system...")

        issues = {
            'high_score_wrong': [],
            'low_score_correct': [],
            'score_distribution': defaultdict(int)
        }

        # Analyze incorrect predictions with high scores
        for error in validation_results['incorrect']:
            if error['confidence'] >= 70:
                issues['high_score_wrong'].append(error)

        # Analyze correct predictions with low scores
        for correct in validation_results['correct']:
            if correct['confidence'] < 50:
                issues['low_score_correct'].append(correct)

        # Score distribution
        for c in self.classifications:
            score_bucket = int(c['confidence'] // 10) * 10
            issues['score_distribution'][score_bucket] += 1

        print(f"  High confidence wrong: {len(issues['high_score_wrong'])}")
        print(f"  Low confidence correct: {len(issues['low_score_correct'])}")

        return issues

    def generate_confusion_matrix(self, validation_results: Dict) -> Dict:
        """Generate confusion matrix for ground truth validation"""
        print("\nGenerating confusion matrix...")

        confusion = defaultdict(lambda: defaultdict(int))

        for error in validation_results['incorrect']:
            expected = error['expected']
            predicted = error['predicted']
            confusion[expected][predicted] += 1

        for correct in validation_results['correct']:
            # Find expected type from ground truth
            idx = correct['index']
            if idx in self.ground_truth:
                expected = self.ground_truth[idx]['true_product_type']
                confusion[expected][expected] += 1

        return dict(confusion)

    def generate_comprehensive_report(self, validation_results: Dict, failure_modes: Dict,
                                     pattern_coverage: Dict, missing_types: List[str],
                                     scoring_issues: Dict, confusion_matrix: Dict) -> Dict:
        """Generate comprehensive audit report"""
        print("\nGenerating comprehensive report...")

        total_products = len(self.classifications)
        unknown_count = sum(1 for c in self.classifications if 'Unknown' in c['product_type'])

        # Calculate accuracy metrics
        gt_total = len(validation_results['correct']) + len(validation_results['incorrect'])
        gt_accuracy = (len(validation_results['correct']) / gt_total * 100) if gt_total > 0 else 0

        # Confidence distribution
        confidence_dist = {
            'high': sum(1 for c in self.classifications if c['confidence'] >= 70),
            'medium': sum(1 for c in self.classifications if 50 <= c['confidence'] < 70),
            'low': sum(1 for c in self.classifications if 30 <= c['confidence'] < 50),
            'very_low': sum(1 for c in self.classifications if c['confidence'] < 30)
        }

        report = {
            'executive_summary': {
                'total_products': total_products,
                'ground_truth_accuracy': round(gt_accuracy, 1),
                'unknown_products': unknown_count,
                'unknown_percentage': round(unknown_count / total_products * 100, 1),
                'target_accuracy': 95.0,
                'accuracy_gap': round(95.0 - gt_accuracy, 1)
            },
            'validation_results': {
                'correct': len(validation_results['correct']),
                'incorrect': len(validation_results['incorrect']),
                'missing': len(validation_results['missing']),
                'total_samples': gt_total
            },
            'failure_taxonomy': {
                'unknown_classifications': len(failure_modes['unknown_classifications']),
                'confident_wrong': len(failure_modes['confident_wrong']),
                'low_confidence_correct': len(failure_modes['low_confidence_correct']),
                'pattern_missing': len(failure_modes['pattern_missing'])
            },
            'confidence_distribution': confidence_dist,
            'pattern_analysis': {
                'total_patterns': len(pattern_coverage['type_counts']),
                'weak_patterns': len(pattern_coverage['weak_patterns']),
                'missing_types': missing_types
            },
            'scoring_issues': {
                'high_score_wrong': len(scoring_issues['high_score_wrong']),
                'low_score_correct': len(scoring_issues['low_score_correct'])
            },
            'detailed_errors': validation_results['incorrect'][:20],  # Top 20 errors
            'detailed_unknowns': failure_modes['unknown_classifications'][:20],  # Top 20 unknowns
            'confusion_matrix': confusion_matrix,
            'weak_patterns_detail': pattern_coverage['weak_patterns']
        }

        return report

    def run_full_audit(self) -> Dict:
        """Run complete audit pipeline"""
        print("="*80)
        print("COMPREHENSIVE CLASSIFIER ACCURACY AUDIT")
        print("="*80)

        # Load data
        self.load_data()

        # Validate against ground truth
        validation_results = self.validate_against_ground_truth()

        # Analyze failure modes
        failure_modes = self.analyze_failure_modes(validation_results)

        # Analyze pattern coverage
        pattern_coverage = self.analyze_pattern_coverage()

        # Identify missing types
        missing_types = self.identify_missing_product_types(failure_modes)

        # Analyze scoring issues
        scoring_issues = self.analyze_scoring_issues(validation_results)

        # Generate confusion matrix
        confusion_matrix = self.generate_confusion_matrix(validation_results)

        # Generate comprehensive report
        report = self.generate_comprehensive_report(
            validation_results, failure_modes, pattern_coverage,
            missing_types, scoring_issues, confusion_matrix
        )

        # Save detailed data
        detailed_output = {
            'report': report,
            'validation_results': validation_results,
            'failure_modes': failure_modes,
            'pattern_coverage': pattern_coverage,
            'scoring_issues': scoring_issues
        }

        return detailed_output


def print_report_summary(report: Dict):
    """Print human-readable report summary"""
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)

    summary = report['executive_summary']
    print(f"\nCURRENT PERFORMANCE:")
    print(f"  Ground Truth Accuracy: {summary['ground_truth_accuracy']}%")
    print(f"  Target Accuracy: {summary['target_accuracy']}%")
    print(f"  ACCURACY GAP: {summary['accuracy_gap']}% ⚠️")
    print(f"  Unknown Products: {summary['unknown_products']} ({summary['unknown_percentage']}%)")

    print(f"\nVALIDATION BREAKDOWN:")
    val = report['validation_results']
    print(f"  Correct: {val['correct']}/{val['total_samples']}")
    print(f"  Incorrect: {val['incorrect']}/{val['total_samples']}")

    print(f"\nFAILURE MODES:")
    failures = report['failure_taxonomy']
    print(f"  Unknown classifications: {failures['unknown_classifications']}")
    print(f"  Confident but wrong: {failures['confident_wrong']}")
    print(f"  Low confidence correct: {failures['low_confidence_correct']}")
    print(f"  Missing patterns: {failures['pattern_missing']}")

    print(f"\nCONFIDENCE DISTRIBUTION:")
    conf = report['confidence_distribution']
    print(f"  High (≥70%): {conf['high']} products")
    print(f"  Medium (50-70%): {conf['medium']} products")
    print(f"  Low (30-50%): {conf['low']} products")
    print(f"  Very Low (<30%): {conf['very_low']} products")

    print(f"\nPATTERN ANALYSIS:")
    patterns = report['pattern_analysis']
    print(f"  Total patterns defined: {patterns['total_patterns']}")
    print(f"  Weak patterns: {patterns['weak_patterns']}")
    print(f"  Missing product types: {len(patterns['missing_types'])}")
    if patterns['missing_types']:
        print(f"\n  Missing types that need patterns:")
        for mtype in patterns['missing_types'][:10]:
            print(f"    - {mtype}")

    print(f"\nSCORING ISSUES:")
    scoring = report['scoring_issues']
    print(f"  High confidence but wrong: {scoring['high_score_wrong']}")
    print(f"  Low confidence but correct: {scoring['low_score_correct']}")


def main():
    """Main execution"""
    auditor = ClassifierAuditor()
    results = auditor.run_full_audit()

    # Print summary
    print_report_summary(results['report'])

    # Save full results
    output_file = Path(__file__).parent.parent / 'outputs' / 'comprehensive_audit_report.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Full audit report saved to: {output_file}")

    return results


if __name__ == '__main__':
    results = main()
