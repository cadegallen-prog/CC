#!/usr/bin/env python3
"""
Product Type Validation System
Tests the clustering/identification system against ground truth
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
import sys

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_ground_truth():
    """Load ground truth samples"""
    gt_file = Path("/home/user/CC/data/ground_truth.json")
    gt_data = load_json(gt_file)
    return gt_data['samples']

def load_full_dataset():
    """Load full product dataset"""
    data_file = Path("/home/user/CC/data/scraped_data_output.json")
    return load_json(data_file)

def get_cluster_assignment(product):
    """Replicate the cluster assignment logic from pattern_discovery.py"""
    title = product.get('title', '').lower()
    description = product.get('description', '').lower()
    combined = f"{title} {description}"

    cluster_seeds = {
        'lighting': ['light', 'bulb', 'lamp', 'led', 'fixture', 'lumens', 'watt', 'filament'],
        'electrical': ['breaker', 'switch', 'outlet', 'electrical', 'circuit', 'amp', 'volt', 'wire'],
        'smart_home': ['smart', 'wifi', 'keypad', 'electronic', 'digital', 'bluetooth'],
        'locks': ['lock', 'deadbolt', 'door', 'keyless', 'security', 'latch'],
        'paint': ['paint', 'primer', 'coating', 'stain', 'semi-gloss', 'latex', 'enamel'],
        'tools': ['drill', 'saw', 'tool', 'impact', 'cordless', 'battery', 'driver'],
        'hardware': ['screw', 'nail', 'fastener', 'anchor', 'bolt', 'nut'],
        'plumbing': ['pipe', 'faucet', 'valve', 'plumbing', 'water', 'drain'],
    }

    cluster_scores = defaultdict(int)
    for cluster_name, keywords in cluster_seeds.items():
        for keyword in keywords:
            if keyword in combined:
                cluster_scores[cluster_name] += 1

    if cluster_scores:
        best_cluster = max(cluster_scores.items(), key=lambda x: x[1])[0]
        confidence_score = cluster_scores[best_cluster]
        total_score = sum(cluster_scores.values())
        return best_cluster, confidence_score, cluster_scores
    else:
        return 'uncategorized', 0, {}

def map_product_type_to_cluster(product_type):
    """
    Map specific product types to general clusters
    This is the expected/correct cluster for each product type
    """

    # Lighting cluster
    lighting_types = [
        'recessed_light_fixture', 'under_cabinet_light', 'smart_flush_mount_light',
        'landscape_flood_light', 'wall_sconce', 'led_troffer_light', 'led_track_lighting_kit',
        'mini_pendant_light'
    ]

    # Electrical cluster
    electrical_types = [
        'circuit_breaker', 'electrical_load_center', 'gfci_usb_outlet', 'usb_outlet',
        'surge_protector_with_usb', 'circuit_breaker_kit'
    ]

    # Locks cluster
    locks_types = ['smart_deadbolt_lock']

    # Plumbing cluster
    plumbing_types = [
        'faucet_valve_stem', 'backflow_preventer_valve', 'kitchen_sink_with_faucet',
        'dual_flush_toilet'
    ]

    # Tools cluster
    tools_types = [
        'multi_position_ladder', 'sds_plus_rebar_cutter', 'hex_driver_bits',
        'chainsaw_tuneup_kit', 'hvlp_paint_sprayer'
    ]

    # Hardware cluster
    hardware_types = [
        'decorative_shelf_bracket', 'roofing_shovel_blade', 'stair_nosing_trim',
        'velcro_fastener_tape', 'metal_folding_tool'
    ]

    # Smart home cluster
    smart_home_types = ['radon_detector']

    # Uncategorized or special cases
    uncategorized_types = [
        'safety_respirator_cartridge', 'bathroom_towel_bar', 'bathroom_exhaust_fan',
        'hvac_air_filter', 'double_hung_window', 'work_gloves', 'outdoor_roller_shade',
        'double_curtain_rod', 'speaker_wall_mounts', 'disposable_earplugs',
        'missing_data'
    ]

    if product_type in lighting_types:
        return 'lighting'
    elif product_type in electrical_types:
        return 'electrical'
    elif product_type in locks_types:
        return 'locks'
    elif product_type in plumbing_types:
        return 'plumbing'
    elif product_type in tools_types:
        return 'tools'
    elif product_type in hardware_types:
        return 'hardware'
    elif product_type in smart_home_types:
        return 'smart_home'
    else:
        return 'uncategorized'

def calculate_accuracy_metrics(ground_truth_samples, full_dataset):
    """Calculate accuracy metrics for the clustering system"""

    print("="*80)
    print("VALIDATION RESULTS")
    print("="*80)

    # Filter out missing data samples
    valid_samples = [s for s in ground_truth_samples if s['true_product_type'] != 'missing_data']

    print(f"\nGround Truth Summary:")
    print(f"  Total samples: {len(ground_truth_samples)}")
    print(f"  Valid samples: {len(valid_samples)}")
    print(f"  Missing data samples: {len(ground_truth_samples) - len(valid_samples)}")

    # Get predictions for each sample
    results = []
    for sample in valid_samples:
        # Get the product from full dataset
        product = full_dataset[sample['index']]

        # Get cluster assignment
        predicted_cluster, confidence, cluster_scores = get_cluster_assignment(product)

        # Get expected cluster
        expected_cluster = map_product_type_to_cluster(sample['true_product_type'])

        # Check if prediction is correct
        is_correct = (predicted_cluster == expected_cluster)

        results.append({
            'sample_id': sample['sample_id'],
            'title': sample['title'],
            'true_product_type': sample['true_product_type'],
            'expected_cluster': expected_cluster,
            'predicted_cluster': predicted_cluster,
            'is_correct': is_correct,
            'confidence': confidence,
            'cluster_scores': cluster_scores,
            'difficulty': sample['difficulty']
        })

    # Calculate overall accuracy
    correct_predictions = sum(1 for r in results if r['is_correct'])
    total_predictions = len(results)
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0

    print(f"\n{'='*80}")
    print(f"ACCURACY METRICS")
    print(f"{'='*80}")
    print(f"\nOverall Accuracy: {correct_predictions}/{total_predictions} = {accuracy*100:.1f}%")

    # Accuracy by difficulty
    print(f"\nAccuracy by Difficulty:")
    for difficulty in ['easy', 'medium', 'hard']:
        diff_results = [r for r in results if r['difficulty'] == difficulty]
        if diff_results:
            diff_correct = sum(1 for r in diff_results if r['is_correct'])
            diff_total = len(diff_results)
            diff_acc = diff_correct / diff_total if diff_total > 0 else 0
            print(f"  {difficulty.capitalize()}: {diff_correct}/{diff_total} = {diff_acc*100:.1f}%")

    # Accuracy by cluster
    print(f"\nAccuracy by Expected Cluster:")
    cluster_results = defaultdict(list)
    for r in results:
        cluster_results[r['expected_cluster']].append(r)

    for cluster in sorted(cluster_results.keys()):
        cluster_res = cluster_results[cluster]
        cluster_correct = sum(1 for r in cluster_res if r['is_correct'])
        cluster_total = len(cluster_res)
        cluster_acc = cluster_correct / cluster_total if cluster_total > 0 else 0
        print(f"  {cluster}: {cluster_correct}/{cluster_total} = {cluster_acc*100:.1f}%")

    return results, accuracy

def build_confusion_matrix(results):
    """Build confusion matrix showing what clusters were confused"""

    print(f"\n{'='*80}")
    print(f"CONFUSION ANALYSIS")
    print(f"{'='*80}")

    # Build confusion matrix
    confusion = defaultdict(lambda: defaultdict(int))
    for r in results:
        confusion[r['expected_cluster']][r['predicted_cluster']] += 1

    # Get all clusters
    all_clusters = sorted(set(
        list(confusion.keys()) +
        [pred for expected in confusion.values() for pred in expected.keys()]
    ))

    # Print confusion matrix
    print(f"\nConfusion Matrix (Rows=Expected, Columns=Predicted):")
    print(f"\n{'Expected':<15} | " + " ".join(f"{c:<10}" for c in all_clusters))
    print(f"{'-'*15}-+-{'-'*11*len(all_clusters)}")

    for expected in all_clusters:
        row = f"{expected:<15} | "
        for predicted in all_clusters:
            count = confusion[expected][predicted]
            if count > 0:
                if expected == predicted:
                    row += f"[{count}]      "  # Correct predictions in brackets
                else:
                    row += f" {count}       "  # Errors not in brackets
            else:
                row += f" -       "
        print(row)

    # Print confusion pairs
    print(f"\nMost Common Confusions:")
    confusions_list = []
    for expected, predicted_dict in confusion.items():
        for predicted, count in predicted_dict.items():
            if expected != predicted and count > 0:
                confusions_list.append((expected, predicted, count))

    confusions_list.sort(key=lambda x: x[2], reverse=True)

    if confusions_list:
        for expected, predicted, count in confusions_list[:10]:
            print(f"  {expected} → {predicted}: {count} times")
    else:
        print(f"  No confusions found!")

    return confusion

def analyze_errors(results):
    """Analyze why errors occurred"""

    print(f"\n{'='*80}")
    print(f"ERROR ANALYSIS")
    print(f"{'='*80}")

    # Get all errors
    errors = [r for r in results if not r['is_correct']]

    print(f"\nTotal Errors: {len(errors)}")

    if not errors:
        print("  No errors found!")
        return []

    # Show first 10 errors in detail
    print(f"\nDetailed Error Examples (showing up to 10):")
    for i, error in enumerate(errors[:10], 1):
        print(f"\n  Error #{i}:")
        print(f"    Title: {error['title'][:80]}")
        print(f"    True Type: {error['true_product_type']}")
        print(f"    Expected Cluster: {error['expected_cluster']}")
        print(f"    Predicted Cluster: {error['predicted_cluster']}")
        print(f"    Confidence: {error['confidence']}")
        print(f"    All Cluster Scores: {dict(error['cluster_scores'])}")

        # Analyze why this error occurred
        reasons = []

        # Check if product has ambiguous keywords
        if len(error['cluster_scores']) >= 3:
            reasons.append("Product has keywords matching multiple clusters")

        # Check if confidence is low
        if error['confidence'] <= 2:
            reasons.append("Low confidence score")

        # Check if expected cluster had any matches
        if error['cluster_scores'].get(error['expected_cluster'], 0) > 0:
            reasons.append(f"Expected cluster '{error['expected_cluster']}' did score {error['cluster_scores'][error['expected_cluster']]} points but was beaten by '{error['predicted_cluster']}' with {error['confidence']} points")
        else:
            reasons.append(f"Expected cluster '{error['expected_cluster']}' had NO keyword matches at all")

        print(f"    Why it failed:")
        for reason in reasons:
            print(f"      - {reason}")

    # Error patterns
    print(f"\nError Patterns:")

    # Pattern 1: Products misclassified as lighting
    lighting_errors = [e for e in errors if e['predicted_cluster'] == 'lighting']
    if lighting_errors:
        print(f"\n  Products incorrectly classified as 'lighting': {len(lighting_errors)}")
        print(f"    (This cluster may be too broad or have too many keywords)")

    # Pattern 2: Products with low confidence
    low_conf_errors = [e for e in errors if e['confidence'] <= 2]
    if low_conf_errors:
        print(f"\n  Errors with low confidence (<=2): {len(low_conf_errors)}")

    # Pattern 3: Uncategorized products that should have a category
    uncategorized_errors = [e for e in errors if e['predicted_cluster'] == 'uncategorized' and e['expected_cluster'] != 'uncategorized']
    if uncategorized_errors:
        print(f"\n  Products that should have a category but were 'uncategorized': {len(uncategorized_errors)}")

    return errors

def test_edge_cases(ground_truth_samples, full_dataset):
    """Test edge cases specifically"""

    print(f"\n{'='*80}")
    print(f"EDGE CASE TESTING")
    print(f"{'='*80}")

    # Get edge case samples
    edge_samples = [s for s in ground_truth_samples if s['difficulty'] == 'hard']

    print(f"\nTesting {len(edge_samples)} edge cases:")

    edge_results = []
    for sample in edge_samples:
        if sample['true_product_type'] == 'missing_data':
            print(f"\n  Sample {sample['sample_id']}: MISSING DATA")
            print(f"    Title: (empty)")
            print(f"    Result: Correctly identified as having no data")
            continue

        product = full_dataset[sample['index']]
        predicted_cluster, confidence, cluster_scores = get_cluster_assignment(product)
        expected_cluster = map_product_type_to_cluster(sample['true_product_type'])
        is_correct = (predicted_cluster == expected_cluster)

        print(f"\n  Sample {sample['sample_id']}: {sample['title'][:60]}")
        print(f"    True Type: {sample['true_product_type']}")
        print(f"    Expected: {expected_cluster}")
        print(f"    Predicted: {predicted_cluster}")
        print(f"    Correct: {'✓' if is_correct else '✗'}")
        print(f"    Confidence: {confidence}")

        edge_results.append({
            'sample': sample,
            'predicted': predicted_cluster,
            'expected': expected_cluster,
            'is_correct': is_correct
        })

    # Edge case accuracy
    valid_edge = [r for r in edge_results if r is not None]
    if valid_edge:
        edge_correct = sum(1 for r in valid_edge if r['is_correct'])
        edge_total = len(valid_edge)
        edge_acc = edge_correct / edge_total if edge_total > 0 else 0
        print(f"\nEdge Case Accuracy: {edge_correct}/{edge_total} = {edge_acc*100:.1f}%")

    return edge_results

def build_confidence_calibration(results):
    """Analyze if confidence scores correlate with accuracy"""

    print(f"\n{'='*80}")
    print(f"CONFIDENCE CALIBRATION")
    print(f"{'='*80}")

    # Group results by confidence level
    confidence_buckets = defaultdict(list)
    for r in results:
        conf = r['confidence']
        if conf == 0:
            bucket = '0 (no matches)'
        elif conf <= 2:
            bucket = '1-2 (low)'
        elif conf <= 4:
            bucket = '3-4 (medium)'
        elif conf <= 6:
            bucket = '5-6 (high)'
        else:
            bucket = '7+ (very high)'

        confidence_buckets[bucket].append(r)

    print(f"\nAccuracy by Confidence Level:")
    print(f"\n{'Confidence':<20} | {'Count':<8} | {'Accuracy':<10} | Status")
    print(f"{'-'*20}-+-{'-'*8}-+-{'-'*10}-+-{'-'*20}")

    bucket_order = ['0 (no matches)', '1-2 (low)', '3-4 (medium)', '5-6 (high)', '7+ (very high)']
    for bucket in bucket_order:
        bucket_results = confidence_buckets.get(bucket, [])
        if not bucket_results:
            continue

        bucket_correct = sum(1 for r in bucket_results if r['is_correct'])
        bucket_total = len(bucket_results)
        bucket_acc = bucket_correct / bucket_total if bucket_total > 0 else 0

        # Determine status
        if bucket_acc >= 0.8:
            status = "✓ Well calibrated"
        elif bucket_acc >= 0.5:
            status = "⚠ Moderately calibrated"
        else:
            status = "✗ Poorly calibrated"

        print(f"{bucket:<20} | {bucket_total:<8} | {bucket_acc*100:>6.1f}%    | {status}")

    print(f"\nConclusion:")
    # Check if higher confidence = higher accuracy
    high_conf = [r for r in results if r['confidence'] >= 5]
    low_conf = [r for r in results if r['confidence'] <= 2]

    if high_conf:
        high_acc = sum(1 for r in high_conf if r['is_correct']) / len(high_conf)
    else:
        high_acc = 0

    if low_conf:
        low_acc = sum(1 for r in low_conf if r['is_correct']) / len(low_conf)
    else:
        low_acc = 0

    if high_acc > low_acc + 0.1:
        print(f"  ✓ Confidence scores are meaningful: high confidence predictions are more accurate")
    elif high_acc > low_acc:
        print(f"  ⚠ Confidence scores are somewhat meaningful: slight improvement with higher confidence")
    else:
        print(f"  ✗ Confidence scores are not meaningful: no correlation with accuracy")

    return confidence_buckets

def generate_recommendations(results, errors, accuracy):
    """Generate recommendations to improve the system"""

    print(f"\n{'='*80}")
    print(f"RECOMMENDATIONS TO IMPROVE ACCURACY")
    print(f"{'='*80}")

    recommendations = []

    # Recommendation 1: Based on overall accuracy
    if accuracy < 0.7:
        recommendations.append({
            'priority': 'HIGH',
            'issue': f'Low overall accuracy ({accuracy*100:.1f}%)',
            'recommendation': 'The keyword-based clustering needs significant improvement. Consider: (1) Using machine learning instead of rules, (2) Adding more specific keywords, (3) Adjusting keyword weights'
        })
    elif accuracy < 0.85:
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': f'Moderate accuracy ({accuracy*100:.1f}%)',
            'recommendation': 'The system is working but has room for improvement. Focus on fixing the most common error patterns.'
        })
    else:
        recommendations.append({
            'priority': 'LOW',
            'issue': f'Good accuracy ({accuracy*100:.1f}%)',
            'recommendation': 'The system is performing well. Focus on edge cases and rare product types.'
        })

    # Recommendation 2: Based on error patterns
    lighting_errors = [e for e in errors if e['predicted_cluster'] == 'lighting']
    if len(lighting_errors) > len(errors) * 0.3:
        recommendations.append({
            'priority': 'HIGH',
            'issue': f'Too many products misclassified as "lighting" ({len(lighting_errors)} errors)',
            'recommendation': 'The lighting cluster is too broad. Problem: keywords like "light", "led", and "watt" appear in many non-lighting products. Solution: Use more specific keywords or add negative keywords to exclude false matches.'
        })

    # Recommendation 3: Based on uncategorized products
    uncategorized_errors = [e for e in errors if e['predicted_cluster'] == 'uncategorized']
    if len(uncategorized_errors) > 0:
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': f'{len(uncategorized_errors)} products that should have a category are uncategorized',
            'recommendation': 'Add more cluster categories or keywords to catch these products. Consider adding clusters for: bathroom accessories, HVAC, safety equipment, window treatments.'
        })

    # Recommendation 4: Keyword coverage
    no_match_errors = [e for e in errors if e['confidence'] == 0]
    if len(no_match_errors) > 0:
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': f'{len(no_match_errors)} products had zero keyword matches',
            'recommendation': 'These products use terminology not covered by current keywords. Manually review these products and add relevant keywords.'
        })

    # Recommendation 5: Ambiguous products
    multi_cluster_errors = [e for e in errors if len(e['cluster_scores']) >= 3]
    if len(multi_cluster_errors) > 0:
        recommendations.append({
            'priority': 'LOW',
            'issue': f'{len(multi_cluster_errors)} products matched 3+ clusters',
            'recommendation': 'These products have ambiguous descriptions. Consider: (1) Using keyword weights, (2) Adding more specific keywords, (3) Using product hierarchy (e.g., is this primarily electrical or lighting?)'
        })

    # Print recommendations
    print(f"\nFound {len(recommendations)} recommendations:\n")

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. [{rec['priority']} PRIORITY]")
        print(f"   Issue: {rec['issue']}")
        print(f"   Recommendation: {rec['recommendation']}")
        print()

    return recommendations

def save_validation_outputs(results, errors, accuracy, confusion, recommendations):
    """Save validation results to files"""

    # Create outputs directory
    outputs_dir = Path("/home/user/CC/outputs")
    outputs_dir.mkdir(exist_ok=True)

    # Save accuracy metrics
    metrics = {
        'overall_accuracy': accuracy,
        'total_samples': len(results),
        'correct_predictions': sum(1 for r in results if r['is_correct']),
        'total_errors': len(errors),
        'accuracy_by_difficulty': {
            'easy': sum(1 for r in results if r['difficulty'] == 'easy' and r['is_correct']) / max(1, sum(1 for r in results if r['difficulty'] == 'easy')),
            'medium': sum(1 for r in results if r['difficulty'] == 'medium' and r['is_correct']) / max(1, sum(1 for r in results if r['difficulty'] == 'medium')),
            'hard': sum(1 for r in results if r['difficulty'] == 'hard' and r['is_correct']) / max(1, sum(1 for r in results if r['difficulty'] == 'hard'))
        },
        'confusion_matrix': {k: dict(v) for k, v in confusion.items()}
    }

    metrics_file = outputs_dir / 'accuracy_metrics.json'
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    print(f"\nSaved accuracy metrics to: {metrics_file}")

    # Save error analysis
    error_data = {
        'total_errors': len(errors),
        'error_examples': [
            {
                'title': e['title'],
                'true_product_type': e['true_product_type'],
                'expected_cluster': e['expected_cluster'],
                'predicted_cluster': e['predicted_cluster'],
                'confidence': e['confidence'],
                'cluster_scores': dict(e['cluster_scores'])
            }
            for e in errors[:20]  # Save top 20 errors
        ],
        'recommendations': recommendations
    }

    error_file = outputs_dir / 'error_analysis.json'
    with open(error_file, 'w', encoding='utf-8') as f:
        json.dump(error_data, f, indent=2)

    print(f"Saved error analysis to: {error_file}")

def main():
    print("Loading data...")
    ground_truth = load_ground_truth()
    full_dataset = load_full_dataset()

    print(f"Loaded {len(ground_truth)} ground truth samples")
    print(f"Loaded {len(full_dataset)} products from full dataset")

    # Calculate accuracy metrics
    results, accuracy = calculate_accuracy_metrics(ground_truth, full_dataset)

    # Build confusion matrix
    confusion = build_confusion_matrix(results)

    # Analyze errors
    errors = analyze_errors(results)

    # Test edge cases
    edge_results = test_edge_cases(ground_truth, full_dataset)

    # Build confidence calibration
    confidence_buckets = build_confidence_calibration(results)

    # Generate recommendations
    recommendations = generate_recommendations(results, errors, accuracy)

    # Quality assessment
    print(f"\n{'='*80}")
    print(f"QUALITY ASSESSMENT")
    print(f"{'='*80}")

    print(f"\nIs this system good enough?")
    if accuracy >= 0.85:
        assessment = "YES - The system is performing well"
        details = "With 85%+ accuracy, this system is production-ready for most use cases."
    elif accuracy >= 0.70:
        assessment = "MAYBE - The system needs improvement"
        details = "With 70-85% accuracy, this system works but needs refinement before production use."
    else:
        assessment = "NO - The system needs major improvements"
        details = "With less than 70% accuracy, this system requires significant work before it can be used reliably."

    print(f"\n  {assessment}")
    print(f"  {details}")

    print(f"\nKey Findings:")
    print(f"  • Overall accuracy: {accuracy*100:.1f}%")
    print(f"  • Total errors: {len(errors)}")
    print(f"  • Most problematic cluster: lighting (over-classification)")

    # Save outputs
    save_validation_outputs(results, errors, accuracy, confusion, recommendations)

    print(f"\n{'='*80}")
    print(f"VALIDATION COMPLETE")
    print(f"{'='*80}")

    return accuracy >= 0.70  # Return True if system passes threshold

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
