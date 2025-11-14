#!/usr/bin/env python3
"""
Analyze sampling bias between ground truth and full dataset.
Compares product type distributions and identifies underrepresented categories.
"""

import json
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import math

def load_json(filepath: str) -> dict:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def categorize_product_type(product_type: str) -> str:
    """Categorize product types into broader domains."""
    product_type_lower = product_type.lower()

    # Lighting domain
    lighting_keywords = ['light', 'lamp', 'bulb', 'fixture', 'sconce', 'chandelier',
                        'pendant', 'recessed', 'troffer', 'track', 'flush mount',
                        'under cabinet', 'landscape']

    # Electrical domain
    electrical_keywords = ['electrical', 'circuit', 'breaker', 'outlet', 'gfci',
                          'usb', 'surge', 'protector', 'load center', 'wire',
                          'cable', 'switch']

    # Plumbing domain
    plumbing_keywords = ['plumbing', 'faucet', 'valve', 'toilet', 'sink', 'shower',
                        'tub', 'drain', 'pipe', 'backflow', 'water']

    # HVAC domain
    hvac_keywords = ['hvac', 'air filter', 'exhaust fan', 'ventilation', 'heating',
                    'cooling', 'thermostat']

    # Tools domain
    tools_keywords = ['tool', 'drill', 'bit', 'saw', 'driver', 'cutter', 'wrench',
                     'hammer', 'screwdriver', 'ladder', 'sprayer']

    # Hardware domain
    hardware_keywords = ['bracket', 'hinge', 'screw', 'nail', 'bolt', 'fastener',
                        'hook', 'handle', 'knob', 'trim', 'nosing', 'rod']

    # Safety/PPE domain
    safety_keywords = ['safety', 'gloves', 'earplugs', 'respirator', 'mask',
                      'cartridge', 'protection', 'detector']

    # Home/Decor domain
    home_keywords = ['curtain', 'shade', 'towel bar', 'shelf', 'speaker mount',
                    'window', 'door', 'lock']

    # Paint domain
    paint_keywords = ['paint', 'sprayer', 'coating', 'finish']

    # Check categories
    if any(keyword in product_type_lower for keyword in lighting_keywords):
        return 'Lighting'
    elif any(keyword in product_type_lower for keyword in electrical_keywords):
        return 'Electrical'
    elif any(keyword in product_type_lower for keyword in plumbing_keywords):
        return 'Plumbing'
    elif any(keyword in product_type_lower for keyword in hvac_keywords):
        return 'HVAC'
    elif any(keyword in product_type_lower for keyword in tools_keywords):
        return 'Tools'
    elif any(keyword in product_type_lower for keyword in hardware_keywords):
        return 'Hardware'
    elif any(keyword in product_type_lower for keyword in safety_keywords):
        return 'Safety/PPE'
    elif any(keyword in product_type_lower for keyword in paint_keywords):
        return 'Paint'
    elif any(keyword in product_type_lower for keyword in home_keywords):
        return 'Home & Decor'
    else:
        return 'Other'

def analyze_distribution(items: List[dict], type_field: str) -> Dict:
    """Analyze product type distribution."""
    total = len(items)
    type_counts = Counter([item[type_field] for item in items])

    # Calculate percentages
    type_percentages = {
        ptype: (count / total * 100) for ptype, count in type_counts.items()
    }

    # Categorize by domain
    domain_counts = defaultdict(int)
    domain_types = defaultdict(list)

    for ptype, count in type_counts.items():
        domain = categorize_product_type(ptype)
        domain_counts[domain] += count
        domain_types[domain].append((ptype, count))

    # Calculate domain percentages
    domain_percentages = {
        domain: (count / total * 100) for domain, count in domain_counts.items()
    }

    return {
        'total': total,
        'type_counts': dict(type_counts),
        'type_percentages': type_percentages,
        'domain_counts': dict(domain_counts),
        'domain_percentages': domain_percentages,
        'domain_types': {k: dict(v) for k, v in domain_types.items()}
    }

def calculate_chi_square(observed: Dict[str, int], expected: Dict[str, int]) -> Tuple[float, float]:
    """
    Calculate chi-square statistic for goodness of fit.
    Returns (chi_square, degrees_of_freedom)
    """
    chi_square = 0.0
    categories = set(observed.keys()) | set(expected.keys())

    for category in categories:
        obs = observed.get(category, 0)
        exp = expected.get(category, 0.1)  # Avoid division by zero
        chi_square += ((obs - exp) ** 2) / exp

    df = len(categories) - 1
    return chi_square, df

def compare_distributions(ground_truth_dist: Dict, full_dist: Dict) -> Dict:
    """Compare ground truth and full dataset distributions."""
    gt_total = ground_truth_dist['total']
    full_total = full_dist['total']

    # Domain comparison
    domain_comparison = {}
    all_domains = set(ground_truth_dist['domain_counts'].keys()) | set(full_dist['domain_counts'].keys())

    for domain in all_domains:
        gt_count = ground_truth_dist['domain_counts'].get(domain, 0)
        full_count = full_dist['domain_counts'].get(domain, 0)

        gt_pct = (gt_count / gt_total * 100) if gt_total > 0 else 0
        full_pct = (full_count / full_total * 100) if full_total > 0 else 0

        bias = gt_pct - full_pct

        domain_comparison[domain] = {
            'ground_truth_count': gt_count,
            'ground_truth_percentage': round(gt_pct, 2),
            'full_dataset_count': full_count,
            'full_dataset_percentage': round(full_pct, 2),
            'difference': round(bias, 2),
            'status': 'over-represented' if bias > 5 else 'under-represented' if bias < -5 else 'balanced'
        }

    # Type-level comparison
    type_comparison = {}
    all_types = set(ground_truth_dist['type_counts'].keys()) | set(full_dist['type_counts'].keys())

    for ptype in all_types:
        gt_count = ground_truth_dist['type_counts'].get(ptype, 0)
        full_count = full_dist['type_counts'].get(ptype, 0)

        gt_pct = (gt_count / gt_total * 100) if gt_total > 0 else 0
        full_pct = (full_count / full_total * 100) if full_total > 0 else 0

        type_comparison[ptype] = {
            'ground_truth_count': gt_count,
            'ground_truth_percentage': round(gt_pct, 2),
            'full_dataset_count': full_count,
            'full_dataset_percentage': round(full_pct, 2),
            'difference': round(gt_pct - full_pct, 2)
        }

    return {
        'domain_comparison': domain_comparison,
        'type_comparison': type_comparison
    }

def identify_missing_types(ground_truth_dist: Dict, full_dist: Dict, threshold: int = 5) -> List[Dict]:
    """Identify product types in full dataset that are missing or underrepresented in ground truth."""
    missing_types = []

    for ptype, count in full_dist['type_counts'].items():
        if count >= threshold:
            gt_count = ground_truth_dist['type_counts'].get(ptype, 0)
            if gt_count == 0:
                missing_types.append({
                    'product_type': ptype,
                    'full_dataset_count': count,
                    'full_dataset_percentage': round(full_dist['type_percentages'][ptype], 2),
                    'ground_truth_count': 0,
                    'domain': categorize_product_type(ptype),
                    'status': 'completely_missing'
                })
            elif gt_count < (count * 0.1):  # Less than 10% representation
                missing_types.append({
                    'product_type': ptype,
                    'full_dataset_count': count,
                    'full_dataset_percentage': round(full_dist['type_percentages'][ptype], 2),
                    'ground_truth_count': gt_count,
                    'ground_truth_percentage': round(ground_truth_dist['type_percentages'][ptype], 2),
                    'domain': categorize_product_type(ptype),
                    'status': 'severely_underrepresented'
                })

    # Sort by full dataset count (most common first)
    missing_types.sort(key=lambda x: x['full_dataset_count'], reverse=True)

    return missing_types

def calculate_statistical_metrics(ground_truth_dist: Dict, full_dist: Dict) -> Dict:
    """Calculate statistical metrics for bias analysis."""
    gt_total = ground_truth_dist['total']
    full_total = full_dist['total']

    # Expected counts in ground truth based on full dataset distribution
    expected_gt_counts = {}
    for domain, full_count in full_dist['domain_counts'].items():
        expected_proportion = full_count / full_total
        expected_gt_counts[domain] = expected_proportion * gt_total

    # Chi-square test
    chi_square, df = calculate_chi_square(
        ground_truth_dist['domain_counts'],
        expected_gt_counts
    )

    # Calculate Kullback-Leibler divergence for domain distributions
    kl_divergence = 0.0
    all_domains = set(ground_truth_dist['domain_counts'].keys()) | set(full_dist['domain_counts'].keys())

    for domain in all_domains:
        p = ground_truth_dist['domain_counts'].get(domain, 0.1) / gt_total
        q = full_dist['domain_counts'].get(domain, 0.1) / full_total
        if p > 0 and q > 0:
            kl_divergence += p * math.log(p / q)

    return {
        'chi_square_statistic': round(chi_square, 2),
        'degrees_of_freedom': df,
        'kl_divergence': round(kl_divergence, 4),
        'expected_ground_truth_counts': {k: round(v, 2) for k, v in expected_gt_counts.items()},
        'interpretation': {
            'chi_square': 'Higher values indicate greater deviation from expected distribution',
            'kl_divergence': 'Higher values indicate greater divergence between distributions (0 = identical)'
        }
    }

def generate_recommendations(comparison: Dict, missing_types: List[Dict]) -> List[str]:
    """Generate recommendations for improving ground truth sampling."""
    recommendations = []

    # Check for over-represented domains
    over_represented = [
        (domain, data) for domain, data in comparison['domain_comparison'].items()
        if data['status'] == 'over-represented'
    ]

    # Check for under-represented domains
    under_represented = [
        (domain, data) for domain, data in comparison['domain_comparison'].items()
        if data['status'] == 'under-represented'
    ]

    if over_represented:
        domains_list = [f"{d} ({data['ground_truth_percentage']}% vs {data['full_dataset_percentage']}%)"
                       for d, data in over_represented]
        recommendations.append({
            'priority': 'high',
            'issue': 'Over-represented domains in ground truth',
            'domains': [d for d, _ in over_represented],
            'action': f"Reduce sampling from: {', '.join(domains_list)}. These domains are over-sampled relative to the full dataset."
        })

    if under_represented:
        domains_list = [f"{d} ({data['ground_truth_percentage']}% vs {data['full_dataset_percentage']}%)"
                       for d, data in under_represented]
        recommendations.append({
            'priority': 'high',
            'issue': 'Under-represented domains in ground truth',
            'domains': [d for d, _ in under_represented],
            'action': f"Increase sampling from: {', '.join(domains_list)}. These domains are under-sampled relative to the full dataset."
        })

    if missing_types:
        # Group missing types by domain
        missing_by_domain = defaultdict(list)
        for item in missing_types[:10]:  # Top 10
            missing_by_domain[item['domain']].append(
                f"{item['product_type']} ({item['full_dataset_count']} products)"
            )

        for domain, types in missing_by_domain.items():
            recommendations.append({
                'priority': 'medium',
                'issue': f'Missing product types in {domain}',
                'action': f"Add samples for: {', '.join(types[:5])}"
            })

    # General recommendation
    recommendations.append({
        'priority': 'medium',
        'issue': 'Stratified sampling strategy',
        'action': 'Use proportional stratified sampling: sample each product type in proportion to its frequency in the full dataset'
    })

    # Edge cases
    edge_case_count = sum(1 for item in comparison['type_comparison'].items()
                         if 'missing_data' in item[0])
    if edge_case_count > 5:
        recommendations.append({
            'priority': 'low',
            'issue': 'Too many edge cases',
            'action': f'Reduce edge cases ({edge_case_count} samples). Focus on representative examples instead.'
        })

    return recommendations

def main():
    print("Loading data files...")

    # Load data
    ground_truth = load_json('/home/user/CC/data/ground_truth.json')
    full_classifications = load_json('/home/user/CC/outputs/product_classifications.json')

    print(f"Ground truth samples: {ground_truth['metadata']['total_samples']}")
    print(f"Full dataset products: {len(full_classifications)}")

    # Extract samples from ground truth
    gt_samples = ground_truth['samples']

    # Analyze distributions
    print("\nAnalyzing ground truth distribution...")
    gt_dist = analyze_distribution(gt_samples, 'true_product_type')

    print("Analyzing full dataset distribution...")
    full_dist = analyze_distribution(full_classifications, 'product_type')

    # Compare distributions
    print("Comparing distributions...")
    comparison = compare_distributions(gt_dist, full_dist)

    # Identify missing types
    print("Identifying missing/underrepresented types...")
    missing_types = identify_missing_types(gt_dist, full_dist, threshold=5)

    # Calculate statistical metrics
    print("Calculating statistical metrics...")
    stats = calculate_statistical_metrics(gt_dist, full_dist)

    # Generate recommendations
    print("Generating recommendations...")
    recommendations = generate_recommendations(comparison, missing_types)

    # Prepare output
    output = {
        'metadata': {
            'analysis_date': '2025-11-14',
            'ground_truth_size': gt_dist['total'],
            'full_dataset_size': full_dist['total'],
            'sampling_ratio': f"1:{round(full_dist['total'] / gt_dist['total'], 1)}"
        },
        'ground_truth_distribution': {
            'total_samples': gt_dist['total'],
            'unique_product_types': len(gt_dist['type_counts']),
            'product_type_counts': dict(sorted(gt_dist['type_counts'].items(),
                                              key=lambda x: x[1], reverse=True)),
            'product_type_percentages': {k: round(v, 2) for k, v in
                                        sorted(gt_dist['type_percentages'].items(),
                                              key=lambda x: x[1], reverse=True)},
            'domain_counts': dict(sorted(gt_dist['domain_counts'].items(),
                                        key=lambda x: x[1], reverse=True)),
            'domain_percentages': {k: round(v, 2) for k, v in
                                  sorted(gt_dist['domain_percentages'].items(),
                                        key=lambda x: x[1], reverse=True)}
        },
        'full_dataset_distribution': {
            'total_products': full_dist['total'],
            'unique_product_types': len(full_dist['type_counts']),
            'product_type_counts': dict(sorted(full_dist['type_counts'].items(),
                                              key=lambda x: x[1], reverse=True)),
            'product_type_percentages': {k: round(v, 2) for k, v in
                                        sorted(full_dist['type_percentages'].items(),
                                              key=lambda x: x[1], reverse=True)},
            'domain_counts': dict(sorted(full_dist['domain_counts'].items(),
                                        key=lambda x: x[1], reverse=True)),
            'domain_percentages': {k: round(v, 2) for k, v in
                                  sorted(full_dist['domain_percentages'].items(),
                                        key=lambda x: x[1], reverse=True)}
        },
        'comparison': {
            'domain_comparison': dict(sorted(comparison['domain_comparison'].items(),
                                           key=lambda x: abs(x[1]['difference']),
                                           reverse=True)),
            'top_20_type_comparison': dict(list(sorted(comparison['type_comparison'].items(),
                                                      key=lambda x: abs(x[1]['difference']),
                                                      reverse=True))[:20])
        },
        'missing_and_underrepresented_types': missing_types,
        'statistical_analysis': stats,
        'bias_summary': {
            'is_stratified': stats['chi_square_statistic'] < 20,
            'over_represented_domains': [
                domain for domain, data in comparison['domain_comparison'].items()
                if data['status'] == 'over-represented'
            ],
            'under_represented_domains': [
                domain for domain, data in comparison['domain_comparison'].items()
                if data['status'] == 'under-represented'
            ],
            'balanced_domains': [
                domain for domain, data in comparison['domain_comparison'].items()
                if data['status'] == 'balanced'
            ],
            'total_missing_types': len([m for m in missing_types if m['status'] == 'completely_missing']),
            'total_underrepresented_types': len([m for m in missing_types if m['status'] == 'severely_underrepresented'])
        },
        'recommendations': recommendations
    }

    # Save output
    output_path = '/home/user/CC/outputs/ground_truth_bias_analysis.json'
    print(f"\nSaving results to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n=== ANALYSIS SUMMARY ===")
    print(f"\nGround Truth: {gt_dist['total']} samples across {len(gt_dist['type_counts'])} product types")
    print(f"Full Dataset: {full_dist['total']} products across {len(full_dist['type_counts'])} product types")
    print(f"\nSampling Ratio: 1:{round(full_dist['total'] / gt_dist['total'], 1)}")

    print("\n--- Domain Distribution Comparison ---")
    for domain in sorted(comparison['domain_comparison'].keys()):
        data = comparison['domain_comparison'][domain]
        print(f"{domain:20s}: GT={data['ground_truth_percentage']:5.1f}%  Full={data['full_dataset_percentage']:5.1f}%  Diff={data['difference']:+6.1f}%  [{data['status']}]")

    print(f"\n--- Statistical Metrics ---")
    print(f"Chi-square: {stats['chi_square_statistic']:.2f} (df={stats['degrees_of_freedom']})")
    print(f"KL Divergence: {stats['kl_divergence']:.4f}")
    print(f"Stratified: {'Yes' if output['bias_summary']['is_stratified'] else 'No'}")

    print(f"\n--- Missing/Underrepresented Types ---")
    print(f"Completely missing: {output['bias_summary']['total_missing_types']}")
    print(f"Severely underrepresented: {output['bias_summary']['total_underrepresented_types']}")

    print(f"\nTop 10 missing types:")
    for i, item in enumerate(missing_types[:10], 1):
        print(f"  {i}. {item['product_type']:40s} - {item['full_dataset_count']:3d} products ({item['full_dataset_percentage']:4.1f}%) - {item['domain']}")

    print("\n--- Recommendations ---")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec['priority'].upper()}] {rec['issue']}")
        print(f"   Action: {rec['action']}")

    print(f"\nAnalysis complete! Results saved to: {output_path}")

if __name__ == '__main__':
    main()
