#!/usr/bin/env python3
"""
Analyze the 20% of products that weren't identified well.
Find patterns to improve extraction.
"""

import json
from collections import defaultdict, Counter

def load_data():
    """Load products and signals."""
    with open('data/scraped_data_output.json', 'r') as f:
        products = json.load(f)
    with open('outputs/extracted_signals.json', 'r') as f:
        signals = json.load(f)
    return products, signals

def find_problem_products(products, signals):
    """Find products with low confidence identification."""
    problems = []

    for i, sig in enumerate(signals):
        product = products[i]

        # Problem indicators:
        # 1. No type phrases found
        # 2. No category signals OR very weak (only 1-2 matches)
        # 3. Has description but failed to extract

        is_problem = False
        reason = []

        if not sig['has_description']:
            is_problem = True
            reason.append("no_description")
        elif not sig['has_clear_type_phrase']:
            if not sig['category_signals']:
                is_problem = True
                reason.append("no_type_phrases_no_categories")
            elif sig['top_category'] and sig['top_category'][1] <= 2:
                is_problem = True
                reason.append("weak_category_confidence")

        if is_problem:
            problems.append({
                'index': i,
                'title': product.get('title', ''),
                'description': product.get('description', '')[:200] + '...',
                'reason': reason,
                'category': sig.get('top_category'),
                'specs': sig.get('useful_specs', {}),
                'full_product': product,
                'full_signal': sig
            })

    return problems

def analyze_titles_for_patterns(problems):
    """Look for product type patterns in titles."""
    print("\n=== ANALYZING TITLES ===\n")

    # Common product type words that appear in titles
    product_types_in_titles = []

    for prob in problems[:20]:  # Look at first 20
        title = prob['title'].lower()
        print(f"Title: {prob['title'][:80]}")
        print(f"  Reason: {prob['reason']}")
        print(f"  Current category: {prob['category']}")

        # Look for product type keywords in the title itself
        # Common patterns: "X-Pack", "Kit", size/measurement + product type
        if 'bulb' in title:
            print(f"  → Contains 'bulb' in title")
        if 'fan' in title:
            print(f"  → Contains 'fan' in title")
        if 'faucet' in title:
            print(f"  → Contains 'faucet' in title")
        if 'breaker' in title:
            print(f"  → Contains 'breaker' in title")
        if 'light' in title:
            print(f"  → Contains 'light' in title")
        if 'fixture' in title:
            print(f"  → Contains 'fixture' in title")
        if 'led' in title:
            print(f"  → Contains 'LED' in title")
        if 'switch' in title:
            print(f"  → Contains 'switch' in title")
        if 'outlet' in title:
            print(f"  → Contains 'outlet' in title")
        if 'wire' in title or 'cable' in title:
            print(f"  → Contains 'wire/cable' in title")
        if 'door' in title:
            print(f"  → Contains 'door' in title")
        if 'ceiling' in title:
            print(f"  → Contains 'ceiling' in title")
        if 'track' in title and 'light' in title:
            print(f"  → Contains 'track light' in title")

        print()

def analyze_brands(products):
    """Build brand to common product type mappings."""
    print("\n=== ANALYZING BRANDS ===\n")

    brand_products = defaultdict(list)

    for product in products:
        brand = product.get('brand', '').lower()
        title = product.get('title', '').lower()

        if brand:
            # Try to extract product type from title
            product_type = None
            if 'bulb' in title or 'led' in title:
                product_type = 'lighting'
            elif 'faucet' in title:
                product_type = 'plumbing_faucet'
            elif 'breaker' in title or 'circuit' in title:
                product_type = 'electrical_breaker'
            elif 'fan' in title:
                product_type = 'hvac_fan'
            elif 'door' in title:
                product_type = 'door'
            elif 'wire' in title or 'cable' in title:
                product_type = 'electrical_wire'

            if product_type:
                brand_products[brand].append(product_type)

    # Find brands that consistently make the same type of product
    brand_specialties = {}
    for brand, types in brand_products.items():
        if len(types) >= 3:  # Brand has at least 3 products
            type_counts = Counter(types)
            most_common = type_counts.most_common(1)[0]
            if most_common[1] >= len(types) * 0.7:  # 70%+ are same type
                brand_specialties[brand] = most_common[0]

    print("Brands with clear specialties:")
    for brand, specialty in sorted(brand_specialties.items())[:20]:
        count = len(brand_products[brand])
        print(f"  {brand}: {specialty} ({count} products)")

    return brand_specialties

def extract_from_title_directly(title):
    """Extract product type directly from title."""
    title_lower = title.lower()

    # Direct mentions
    if 'ceiling fan' in title_lower:
        return 'ceiling_fan'
    if 'light bulb' in title_lower or 'led bulb' in title_lower:
        return 'light_bulb'
    if 'track light' in title_lower:
        return 'track_lighting'
    if 'circuit breaker' in title_lower or 'breaker' in title_lower:
        return 'circuit_breaker'
    if 'faucet' in title_lower:
        return 'faucet'
    if 'kitchen faucet' in title_lower:
        return 'kitchen_faucet'
    if 'bathroom faucet' in title_lower:
        return 'bathroom_faucet'
    if 'shower' in title_lower and 'head' in title_lower:
        return 'showerhead'
    if 'toilet' in title_lower:
        return 'toilet'
    if 'door' in title_lower and 'handle' in title_lower:
        return 'door_handle'
    if 'door' in title_lower and 'lock' in title_lower:
        return 'door_lock'
    if 'wire' in title_lower or 'cable' in title_lower:
        return 'electrical_wire'
    if 'switch' in title_lower:
        return 'electrical_switch'
    if 'outlet' in title_lower or 'receptacle' in title_lower:
        return 'electrical_outlet'
    if 'led' in title_lower and 'light' in title_lower:
        return 'led_light'
    if 'recessed light' in title_lower or 'can light' in title_lower:
        return 'recessed_light'
    if 'pendant' in title_lower:
        return 'pendant_light'
    if 'chandelier' in title_lower:
        return 'chandelier'
    if 'sconce' in title_lower:
        return 'wall_sconce'
    if 'vanity light' in title_lower:
        return 'vanity_light'
    if 'outdoor light' in title_lower:
        return 'outdoor_light'
    if 'flood light' in title_lower or 'floodlight' in title_lower:
        return 'flood_light'
    if 'strip light' in title_lower:
        return 'led_strip'
    if 'paint' in title_lower and 'spray' in title_lower:
        return 'paint_sprayer'
    if 'drill' in title_lower:
        return 'drill'
    if 'saw' in title_lower:
        return 'saw'
    if 'ladder' in title_lower:
        return 'ladder'
    if 'tool' in title_lower and 'bag' in title_lower:
        return 'tool_bag'
    if 'knee pad' in title_lower:
        return 'knee_pads'
    if 'glove' in title_lower:
        return 'gloves'
    if 'hose' in title_lower:
        return 'hose'
    if 'sprinkler' in title_lower:
        return 'sprinkler'
    if 'rug' in title_lower or 'mat' in title_lower:
        return 'rug'
    if 'tile' in title_lower:
        return 'tile'
    if 'vanity' in title_lower and 'top' in title_lower:
        return 'vanity_top'
    if 'screen door' in title_lower:
        return 'screen_door'
    if 'window' in title_lower:
        return 'window'
    if 'skylight' in title_lower:
        return 'skylight'
    if 'roller shade' in title_lower or 'window shade' in title_lower:
        return 'window_shade'

    return None

def main():
    print("Loading data...")
    products, signals = load_data()

    print(f"Total products: {len(products)}")
    print(f"Total signals: {len(signals)}")

    # Find problem products
    problems = find_problem_products(products, signals)
    print(f"\nFound {len(problems)} problem products ({len(problems)/len(products)*100:.1f}%)")

    # Analyze them
    analyze_titles_for_patterns(problems)
    brand_specialties = analyze_brands(products)

    # Test title extraction on problem products
    print("\n=== TESTING TITLE EXTRACTION ===\n")
    successful_extractions = 0

    for prob in problems[:30]:
        extracted = extract_from_title_directly(prob['title'])
        if extracted:
            successful_extractions += 1
            print(f"✓ {prob['title'][:70]}")
            print(f"  Extracted: {extracted}")
            print()

    print(f"\nSuccessfully extracted from {successful_extractions}/{min(30, len(problems))} problem products using title parsing")
    print(f"Success rate: {successful_extractions/min(30, len(problems))*100:.1f}%")

    # Save problem products for further analysis
    with open('outputs/problem_products.json', 'w') as f:
        json.dump(problems, f, indent=2)

    print(f"\nSaved {len(problems)} problem products to outputs/problem_products.json")

    # Save brand specialties
    with open('data/brand_specialties.json', 'w') as f:
        json.dump(brand_specialties, f, indent=2)

    print(f"Saved brand specialties to data/brand_specialties.json")

if __name__ == '__main__':
    main()
