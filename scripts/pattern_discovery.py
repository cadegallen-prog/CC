#!/usr/bin/env python3
"""
Organic Pattern Discovery Script
Extracts natural product-type patterns from titles and descriptions
WITHOUT using taxonomy_paths.txt
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

def load_data(file_path):
    """Load JSON data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def clean_text(text):
    """Clean text for analysis"""
    if not text:
        return ""
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Strip
    text = text.strip()
    return text

def extract_product_type_patterns(data):
    """Extract natural product type patterns from titles"""
    print("=" * 80)
    print("PRODUCT TYPE PATTERN EXTRACTION")
    print("=" * 80)

    # Patterns to extract product types
    # Common patterns: "X-Watt Y", "X in. Y", "X Amp Y", etc.

    # Extract the last 2-3 meaningful words from titles (often the product type)
    product_types = []
    title_endings = []

    for record in data:
        if not isinstance(record, dict):
            continue

        title = clean_text(record.get('title', ''))
        if not title:
            continue

        # Remove common prefixes (brand names often at start)
        # Extract last significant noun phrase
        words = title.split()

        # Get last 2-4 words as potential product type
        if len(words) >= 2:
            ending_2 = ' '.join(words[-2:])
            ending_3 = ' '.join(words[-3:]) if len(words) >= 3 else ''
            ending_4 = ' '.join(words[-4:]) if len(words) >= 4 else ''

            title_endings.append({
                '2_word': ending_2,
                '3_word': ending_3,
                '4_word': ending_4,
                'full_title': title
            })

    # Count most common endings
    ending_2_counter = Counter([e['2_word'] for e in title_endings])
    ending_3_counter = Counter([e['3_word'] for e in title_endings if e['3_word']])

    print(f"\nMost Common 2-Word Title Endings (Top 30):")
    for ending, count in ending_2_counter.most_common(30):
        print(f"  {count:3d}x: {ending}")

    print(f"\nMost Common 3-Word Title Endings (Top 30):")
    for ending, count in ending_3_counter.most_common(30):
        print(f"  {count:3d}x: {ending}")

    return title_endings

def extract_noun_phrases(data):
    """Extract common noun phrases that likely represent product categories"""
    print("\n" + "=" * 80)
    print("NOUN PHRASE EXTRACTION")
    print("=" * 80)

    # Common product type keywords
    product_keywords = [
        'bulb', 'light', 'lamp', 'fixture', 'led', 'bulbs',
        'lock', 'deadbolt', 'door', 'handle', 'knob',
        'breaker', 'switch', 'outlet', 'electrical',
        'paint', 'primer', 'stain', 'coating',
        'tool', 'drill', 'saw', 'hammer', 'kit',
        'board', 'panel', 'plywood', 'lumber',
        'pipe', 'fitting', 'valve', 'faucet',
        'screw', 'nail', 'fastener', 'anchor',
        'wire', 'cable', 'cord', 'extension',
        'tape', 'adhesive', 'glue', 'sealant',
        'fan', 'heater', 'thermostat', 'hvac',
        'toilet', 'sink', 'shower', 'tub',
        'flooring', 'tile', 'carpet', 'vinyl',
        'window', 'glass', 'pane', 'screen',
        'roof', 'shingle', 'gutter', 'flashing'
    ]

    keyword_matches = defaultdict(list)

    for record in data:
        if not isinstance(record, dict):
            continue

        title = clean_text(record.get('title', '')).lower()
        description = clean_text(record.get('description', '')).lower()

        if not title:
            continue

        for keyword in product_keywords:
            if keyword in title or keyword in description:
                keyword_matches[keyword].append({
                    'title': record.get('title', ''),
                    'brand': record.get('brand', '')
                })

    print(f"\nProduct Keyword Frequency (Top 20):")
    sorted_keywords = sorted(keyword_matches.items(), key=lambda x: len(x[1]), reverse=True)

    for keyword, matches in sorted_keywords[:20]:
        print(f"  {len(matches):3d}x: {keyword}")
        # Show sample titles
        sample_titles = matches[:2]
        for sample in sample_titles:
            title_preview = sample['title'][:80]
            print(f"        - {title_preview}")

    return keyword_matches

def extract_attribute_patterns(data):
    """Extract attribute patterns like sizes, colors, materials"""
    print("\n" + "=" * 80)
    print("ATTRIBUTE PATTERN EXTRACTION")
    print("=" * 80)

    # Regex patterns for common attributes
    patterns = {
        'size_inches': r'(\d+(?:\.\d+)?)\s*(?:in\.|inch|inches)',
        'size_feet': r'(\d+(?:\.\d+)?)\s*(?:ft\.|foot|feet)',
        'wattage': r'(\d+(?:\.\d+)?)\s*(?:-)?(?:watt|w\b)',
        'amperage': r'(\d+(?:\.\d+)?)\s*(?:-)?amp',
        'voltage': r'(\d+(?:\.\d+)?)\s*(?:-)?volt',
        'pack_size': r'(\d+)\s*(?:-)?pack',
        'piece_count': r'(\d+)\s*(?:-)?piece',
        'gallon': r'(\d+(?:\.\d+)?)\s*(?:-)?gal',
    }

    # Color patterns
    colors = ['white', 'black', 'gray', 'grey', 'blue', 'red', 'green', 'brown',
              'silver', 'bronze', 'nickel', 'chrome', 'brass', 'copper', 'gold']

    # Material patterns
    materials = ['steel', 'wood', 'plastic', 'glass', 'metal', 'aluminum', 'copper',
                 'brass', 'iron', 'ceramic', 'porcelain', 'vinyl', 'latex', 'oil']

    attribute_findings = defaultdict(list)

    for record in data:
        if not isinstance(record, dict):
            continue

        title = clean_text(record.get('title', '')).lower()
        description = clean_text(record.get('description', '')).lower()
        combined = f"{title} {description}"

        # Extract numeric attributes
        for attr_name, pattern in patterns.items():
            matches = re.findall(pattern, combined, re.IGNORECASE)
            if matches:
                for match in matches:
                    attribute_findings[attr_name].append({
                        'value': match,
                        'title': record.get('title', '')
                    })

        # Extract colors
        for color in colors:
            if re.search(r'\b' + color + r'\b', combined):
                attribute_findings['color'].append({
                    'value': color,
                    'title': record.get('title', '')
                })

        # Extract materials
        for material in materials:
            if re.search(r'\b' + material + r'\b', combined):
                attribute_findings['material'].append({
                    'value': material,
                    'title': record.get('title', '')
                })

    # Report findings
    print(f"\nAttribute Extraction Results:")
    for attr_name, findings in sorted(attribute_findings.items()):
        print(f"\n  {attr_name.upper()}: {len(findings)} occurrences")

        # Show value distribution
        if findings:
            value_counter = Counter([f['value'] for f in findings])
            top_values = value_counter.most_common(5)
            print(f"    Top values:")
            for value, count in top_values:
                print(f"      - {value}: {count}x")

    return attribute_findings

def extract_brand_patterns(data):
    """Extract brand + attribute signature patterns"""
    print("\n" + "=" * 80)
    print("BRAND + ATTRIBUTE SIGNATURES")
    print("=" * 80)

    brand_patterns = defaultdict(lambda: defaultdict(list))

    for record in data:
        if not isinstance(record, dict):
            continue

        brand = clean_text(record.get('brand', ''))
        title = clean_text(record.get('title', ''))

        if not brand or not title:
            continue

        # Extract title without brand
        title_lower = title.lower()
        brand_lower = brand.lower()

        if title_lower.startswith(brand_lower):
            title_without_brand = title[len(brand):].strip()
        else:
            title_without_brand = title

        # Store pattern
        brand_patterns[brand]['titles'].append(title_without_brand)
        brand_patterns[brand]['full_titles'].append(title)

    # Report top brands
    print(f"\nTop Brands by Product Count:")
    sorted_brands = sorted(brand_patterns.items(), key=lambda x: len(x[1]['titles']), reverse=True)

    for brand, patterns in sorted_brands[:15]:
        print(f"\n  {brand}: {len(patterns['titles'])} products")

        # Show sample titles
        sample_titles = patterns['full_titles'][:3]
        print(f"    Sample products:")
        for title in sample_titles:
            print(f"      - {title[:90]}")

        # Analyze common words in this brand's products
        all_words = []
        for title in patterns['titles']:
            words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
            all_words.extend(words)

        word_counter = Counter(all_words)
        common_words = [w for w, c in word_counter.most_common(10) if w != brand.lower()]
        print(f"    Common terms: {', '.join(common_words[:8])}")

    return brand_patterns

def cluster_similar_products(data):
    """Identify natural product clusters"""
    print("\n" + "=" * 80)
    print("PRODUCT CLUSTERING")
    print("=" * 80)

    # Use simple keyword-based clustering
    clusters = defaultdict(list)

    # Define seed keywords for clustering
    cluster_seeds = {
        'lighting': ['light', 'bulb', 'lamp', 'led', 'fixture', 'lumens', 'watt', 'filament'],
        'electrical': ['breaker', 'switch', 'outlet', 'electrical', 'circuit', 'amp', 'volt', 'wire'],
        'smart_home': ['smart', 'wifi', 'keypad', 'electronic', 'digital', 'bluetooth'],
        'locks': ['lock', 'deadbolt', 'door', 'keyless', 'security', 'latch'],
        'paint': ['paint', 'primer', 'coating', 'stain', 'semi-gloss', 'latex', 'enamel'],
        'tools': ['drill', 'saw', 'tool', 'impact', 'cordless', 'battery', 'driver'],
        'hardware': ['screw', 'screws', 'nail', 'nails', 'fastener', 'anchor', 'bolt', 'nut'],
        'plumbing': ['pipe', 'faucet', 'valve', 'plumbing', 'water', 'drain'],
    }

    for record in data:
        if not isinstance(record, dict):
            continue

        title = clean_text(record.get('title', '')).lower()
        description = clean_text(record.get('description', '')).lower()
        combined = f"{title} {description}"

        if not title:
            continue

        # Assign to clusters based on keyword matches
        cluster_scores = defaultdict(int)
        for cluster_name, keywords in cluster_seeds.items():
            for keyword in keywords:
                # Use word boundary matching to avoid partial matches (e.g., "stain" in "stainless")
                if re.search(r'\b' + re.escape(keyword) + r'\b', combined):
                    cluster_scores[cluster_name] += 1

        # Assign to best matching cluster
        if cluster_scores:
            best_cluster = max(cluster_scores.items(), key=lambda x: x[1])[0]
            clusters[best_cluster].append({
                'title': record.get('title', ''),
                'brand': record.get('brand', ''),
                'score': cluster_scores[best_cluster]
            })
        else:
            clusters['uncategorized'].append({
                'title': record.get('title', ''),
                'brand': record.get('brand', ''),
                'score': 0
            })

    print(f"\nProduct Cluster Distribution:")
    for cluster_name, products in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n  {cluster_name.upper()}: {len(products)} products")

        # Show samples
        samples = products[:3]
        for product in samples:
            print(f"    - [{product['brand']}] {product['title'][:70]}")

    return clusters

def main():
    # File path
    data_file = Path("/home/user/CC/data/scraped_data_output.json")

    print("Loading data...\n")
    data = load_data(data_file)

    # Extract product type patterns
    title_patterns = extract_product_type_patterns(data)

    # Extract noun phrases
    keyword_matches = extract_noun_phrases(data)

    # Extract attribute patterns
    attributes = extract_attribute_patterns(data)

    # Extract brand patterns
    brand_patterns = extract_brand_patterns(data)

    # Cluster products
    clusters = cluster_similar_products(data)

    print("\n" + "=" * 80)
    print("PATTERN DISCOVERY COMPLETE")
    print("=" * 80)

    # Save results
    results = {
        'total_records': len(data),
        'clusters': {k: len(v) for k, v in clusters.items()},
        'top_brands': list(dict(sorted(brand_patterns.items(),
                                      key=lambda x: len(x[1]['titles']),
                                      reverse=True)[:20]).keys()),
        'attribute_counts': {k: len(v) for k, v in attributes.items()}
    }

    output_file = Path("/home/user/CC/data/pattern_discovery_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
