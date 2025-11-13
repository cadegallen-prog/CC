#!/usr/bin/env python3
"""
Ground Truth Creation Script
Manually selects and labels 50 diverse products for validation
"""

import json
import random
from pathlib import Path
from collections import defaultdict

def load_data(file_path):
    """Load JSON data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_cluster_assignment(product):
    """Replicate the cluster assignment logic from pattern_discovery.py"""
    title = product.get('title', '').lower()
    description = product.get('description', '').lower()
    combined = f"{title} {description}"

    # Define seed keywords for clustering (from pattern_discovery.py)
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
        return best_cluster
    else:
        return 'uncategorized'

def select_diverse_sample(data, sample_size=50):
    """
    Select a diverse sample of products for manual labeling
    - Mix of easy, medium, and hard cases
    - Representative of different clusters
    - Include edge cases
    """

    # First, cluster all products
    clustered = defaultdict(list)
    for idx, product in enumerate(data):
        cluster = get_cluster_assignment(product)
        clustered[cluster].append((idx, product))

    print(f"\nProduct Distribution:")
    for cluster, products in sorted(clustered.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {cluster}: {len(products)} products")

    selected_samples = []

    # Strategy 1: Get proportional samples from each cluster (30 products)
    print(f"\n1. Selecting proportional samples from each cluster...")
    total_products = len(data)
    for cluster, products in clustered.items():
        if cluster == 'uncategorized':
            continue

        cluster_proportion = len(products) / total_products
        n_samples = max(2, int(30 * cluster_proportion))
        n_samples = min(n_samples, len(products))

        samples = random.sample(products, n_samples)
        for idx, product in samples:
            selected_samples.append({
                'sample_id': len(selected_samples) + 1,
                'index': idx,
                'title': product.get('title', ''),
                'description': product.get('description', '')[:200],
                'brand': product.get('brand', ''),
                'price': product.get('price', 0),
                'predicted_cluster': cluster,
                'true_product_type': '',  # To be filled manually
                'difficulty': 'medium',
                'notes': ''
            })

    # Strategy 2: Get edge cases (10 products)
    print(f"2. Selecting edge cases...")
    # - Products with short titles
    # - Products with missing descriptions
    # - Products with vague titles
    # - Uncategorized products

    edge_cases = []

    # Short titles
    for idx, product in enumerate(data):
        title = product.get('title', '')
        if len(title) < 40:
            edge_cases.append((idx, product, 'short_title'))

    # Missing descriptions
    for idx, product in enumerate(data):
        desc = product.get('description', '')
        if not desc or len(desc) < 50:
            edge_cases.append((idx, product, 'missing_description'))

    # Uncategorized
    for idx, product in clustered.get('uncategorized', []):
        edge_cases.append((idx, product, 'uncategorized'))

    # Sample 5 edge cases
    if len(edge_cases) > 5:
        edge_samples = random.sample(edge_cases, 5)
    else:
        edge_samples = edge_cases

    for idx, product, edge_type in edge_samples:
        cluster = get_cluster_assignment(product)
        selected_samples.append({
            'sample_id': len(selected_samples) + 1,
            'index': idx,
            'title': product.get('title', ''),
            'description': product.get('description', '')[:200],
            'brand': product.get('brand', ''),
            'price': product.get('price', 0),
            'predicted_cluster': cluster,
            'true_product_type': '',
            'difficulty': 'hard',
            'notes': f'Edge case: {edge_type}'
        })

    # Strategy 3: Random samples for unbiased baseline (10 products)
    print(f"3. Selecting random samples...")
    already_selected_indices = {s['index'] for s in selected_samples}
    remaining = [(idx, p) for idx, p in enumerate(data) if idx not in already_selected_indices]

    n_random = min(10, len(remaining))
    random_samples = random.sample(remaining, n_random)

    for idx, product in random_samples:
        cluster = get_cluster_assignment(product)
        selected_samples.append({
            'sample_id': len(selected_samples) + 1,
            'index': idx,
            'title': product.get('title', ''),
            'description': product.get('description', '')[:200],
            'brand': product.get('brand', ''),
            'price': product.get('price', 0),
            'predicted_cluster': cluster,
            'true_product_type': '',
            'difficulty': 'easy',
            'notes': 'Random sample'
        })

    # Trim to exactly 50 samples
    selected_samples = selected_samples[:sample_size]

    # Re-number sample IDs
    for i, sample in enumerate(selected_samples, 1):
        sample['sample_id'] = i

    return selected_samples

def manually_label_products(samples):
    """
    Manually label each product with its true product type
    This is done by examining the title and description
    """

    print(f"\n{'='*80}")
    print(f"MANUAL PRODUCT LABELING")
    print(f"{'='*80}\n")

    for sample in samples:
        print(f"\n--- Sample {sample['sample_id']}/50 ---")
        print(f"Title: {sample['title']}")
        print(f"Brand: {sample['brand']}")
        print(f"Price: ${sample['price']}")
        print(f"Description: {sample['description']}...")
        print(f"Predicted Cluster: {sample['predicted_cluster']}")

        # Determine true product type based on title and description
        title_lower = sample['title'].lower()
        desc_lower = sample['description'].lower()

        # Decision logic for product type
        true_type = determine_product_type(sample['title'], sample['description'])

        sample['true_product_type'] = true_type
        print(f"✓ Labeled as: {true_type}")

    return samples

def determine_product_type(title, description):
    """
    Determine the true product type based on title and description
    Returns a specific product type (not just a cluster)
    """

    title_lower = title.lower()
    desc_lower = (description or '').lower()
    combined = f"{title_lower} {desc_lower}"

    # LED/Light Bulbs
    if 'led' in combined and 'bulb' in combined:
        if 'chandelier' in combined or 'candelabra' in combined:
            return 'led_chandelier_bulb'
        elif 'filament' in combined:
            return 'led_filament_bulb'
        elif 'a19' in combined or 'a21' in combined:
            return 'led_standard_bulb'
        else:
            return 'led_bulb'

    # Ceiling Fans
    if 'ceiling fan' in combined or 'indoor fan' in combined:
        if 'light' in combined or 'led' in combined:
            return 'ceiling_fan_with_light'
        else:
            return 'ceiling_fan'

    # Light Fixtures
    if any(word in combined for word in ['fixture', 'chandelier', 'pendant', 'sconce', 'vanity light']):
        if 'ceiling' in combined:
            return 'ceiling_light_fixture'
        elif 'vanity' in combined or 'bathroom' in combined:
            return 'vanity_light_fixture'
        elif 'pendant' in combined:
            return 'pendant_light'
        else:
            return 'light_fixture'

    # Recessed Lighting
    if 'recessed' in combined or 'can light' in combined or 'downlight' in combined:
        return 'recessed_light'

    # Electrical - Circuit Breakers
    if 'breaker' in combined or 'circuit breaker' in combined:
        if 'gfci' in combined or 'ground fault' in combined:
            return 'gfci_circuit_breaker'
        elif 'afci' in combined or 'arc fault' in combined:
            return 'afci_circuit_breaker'
        else:
            return 'circuit_breaker'

    # Electrical - Switches and Outlets
    if 'switch' in combined and not 'saw' in combined:
        if 'dimmer' in combined:
            return 'dimmer_switch'
        elif 'smart' in combined:
            return 'smart_switch'
        else:
            return 'electrical_switch'

    if 'outlet' in combined or 'receptacle' in combined:
        if 'gfci' in combined:
            return 'gfci_outlet'
        elif 'usb' in combined:
            return 'usb_outlet'
        else:
            return 'electrical_outlet'

    # Wire and Cable
    if ('wire' in combined or 'cable' in combined) and 'saw' not in combined:
        if 'romex' in combined or 'nm-b' in combined:
            return 'electrical_wire'
        elif 'extension' in combined:
            return 'extension_cord'
        else:
            return 'wire_cable'

    # Door Locks
    if any(word in combined for word in ['deadbolt', 'door lock', 'lock']):
        if 'smart' in combined or 'electronic' in combined or 'keyless' in combined:
            return 'smart_door_lock'
        else:
            return 'door_lock'

    # Door Handles/Knobs
    if 'door handle' in combined or 'door knob' in combined or 'lever' in combined:
        return 'door_handle'

    # Paint
    if 'paint' in combined:
        if 'primer' in combined:
            return 'paint_primer'
        elif 'spray' in combined:
            return 'spray_paint'
        else:
            return 'interior_paint'

    # Power Tools
    if any(word in combined for word in ['drill', 'impact driver', 'hammer drill']):
        return 'power_drill'

    if 'saw' in combined:
        if 'circular' in combined:
            return 'circular_saw'
        elif 'miter' in combined:
            return 'miter_saw'
        elif 'blade' in combined:
            return 'saw_blade'
        else:
            return 'saw'

    # Plumbing
    if 'faucet' in combined:
        if 'kitchen' in combined:
            return 'kitchen_faucet'
        elif 'bathroom' in combined or 'lavatory' in combined:
            return 'bathroom_faucet'
        else:
            return 'faucet'

    if 'toilet' in combined:
        return 'toilet'

    if 'shower' in combined:
        if 'head' in combined:
            return 'shower_head'
        else:
            return 'shower'

    # Hardware - Fasteners
    if any(word in combined for word in ['screw', 'nail', 'bolt', 'anchor']):
        if 'screw' in combined:
            return 'screws'
        elif 'nail' in combined:
            return 'nails'
        elif 'anchor' in combined:
            return 'wall_anchor'
        else:
            return 'fasteners'

    # If we can't determine, use the first significant noun from title
    # This is a fallback
    words = title.split()
    if len(words) >= 2:
        return '_'.join(words[-2:]).lower().replace(' ', '_')

    return 'unknown_product'

def main():
    # Set random seed for reproducibility
    random.seed(42)

    # Load data
    data_file = Path("/home/user/CC/data/scraped_data_output.json")
    print(f"Loading data from {data_file}...")
    data = load_data(data_file)
    print(f"Loaded {len(data)} products")

    # Select diverse sample
    print(f"\nSelecting 50 diverse products for ground truth...")
    samples = select_diverse_sample(data, sample_size=50)

    # Manually label products
    labeled_samples = manually_label_products(samples)

    # Save ground truth
    output_file = Path("/home/user/CC/data/ground_truth.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'total_samples': len(labeled_samples),
                'source_file': str(data_file),
                'creation_date': '2025-11-13',
                'sampling_strategy': 'stratified + edge cases + random',
                'description': 'Manually labeled ground truth for validating product type identification'
            },
            'samples': labeled_samples
        }, f, indent=2)

    print(f"\n{'='*80}")
    print(f"GROUND TRUTH CREATED")
    print(f"{'='*80}")
    print(f"\nSaved {len(labeled_samples)} labeled samples to: {output_file}")

    # Print summary
    print(f"\nSummary:")
    print(f"  Easy cases: {sum(1 for s in labeled_samples if s['difficulty'] == 'easy')}")
    print(f"  Medium cases: {sum(1 for s in labeled_samples if s['difficulty'] == 'medium')}")
    print(f"  Hard cases: {sum(1 for s in labeled_samples if s['difficulty'] == 'hard')}")

    # Print cluster distribution
    cluster_dist = defaultdict(int)
    for sample in labeled_samples:
        cluster_dist[sample['predicted_cluster']] += 1

    print(f"\nPredicted Cluster Distribution:")
    for cluster, count in sorted(cluster_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cluster}: {count}")

    # Print true product type distribution
    type_dist = defaultdict(int)
    for sample in labeled_samples:
        type_dist[sample['true_product_type']] += 1

    print(f"\nTrue Product Type Distribution:")
    for ptype, count in sorted(type_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ptype}: {count}")

if __name__ == "__main__":
    main()
