#!/usr/bin/env python3
"""
Comprehensive analysis of Unknown products from classifier output.
"""

import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

def load_json_file(filepath: str) -> List[Dict]:
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text."""
    if not text:
        return []

    # Convert to lowercase and split
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Common words to exclude
    stopwords = {
        'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have',
        'has', 'are', 'was', 'were', 'been', 'being', 'can', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'your',
        'our', 'their', 'its', 'all', 'each', 'any', 'some', 'more',
        'less', 'than', 'into', 'over', 'under', 'above', 'below',
        'between', 'through', 'during', 'before', 'after', 'about',
        'against', 'within', 'without', 'along', 'among', 'across'
    }

    return [w for w in words if w not in stopwords]

def infer_product_type(title: str, description: str) -> str:
    """Infer likely product type from title and description."""
    text = (title + ' ' + (description or '')).lower()

    # Product type patterns - ordered by specificity
    patterns = [
        # Mirrors
        (r'\bmirror\b', 'Mirror'),

        # Lighting
        (r'\b(string light|fairy light|rope light)\b', 'String Lights'),
        (r'\b(table lamp|desk lamp)\b', 'Table Lamp'),
        (r'\b(floor lamp|standing lamp)\b', 'Floor Lamp'),
        (r'\b(pendant light|pendant lamp)\b', 'Pendant Light'),
        (r'\b(chandelier)\b', 'Chandelier'),
        (r'\b(ceiling light|ceiling fixture|flush mount)\b', 'Ceiling Light'),
        (r'\b(wall lamp|wall light|sconce)\b', 'Wall Light'),
        (r'\b(night light)\b', 'Night Light'),
        (r'\b(track light)\b', 'Track Light'),
        (r'\b(vanity light)\b', 'Vanity Light'),
        (r'\b(outdoor light|landscape light)\b', 'Outdoor Light'),

        # Bathroom fixtures
        (r'\b(bathroom faucet|sink faucet|lavatory faucet)\b', 'Bathroom Faucet'),
        (r'\b(kitchen faucet)\b', 'Kitchen Faucet'),
        (r'\b(shower head|showerhead)\b', 'Shower Head'),
        (r'\b(shower faucet|shower valve)\b', 'Shower Faucet'),
        (r'\b(bathtub faucet|tub faucet)\b', 'Bathtub Faucet'),
        (r'\b(toilet)\b', 'Toilet'),
        (r'\b(toilet seat)\b', 'Toilet Seat'),
        (r'\b(vanity|bathroom vanity)\b', 'Bathroom Vanity'),
        (r'\b(medicine cabinet)\b', 'Medicine Cabinet'),
        (r'\b(towel bar|towel rack|towel holder)\b', 'Towel Bar'),

        # Door hardware
        (r'\b(door handle|door knob|doorknob)\b', 'Door Handle'),
        (r'\b(door hinge)\b', 'Door Hinge'),
        (r'\b(door closer)\b', 'Door Closer'),
        (r'\b(door stop|doorstop)\b', 'Door Stop'),

        # Cabinet hardware
        (r'\b(cabinet hinge)\b', 'Cabinet Hinge'),
        (r'\b(cabinet pull|drawer pull)\b', 'Cabinet Pull'),
        (r'\b(cabinet knob|drawer knob)\b', 'Cabinet Knob'),
        (r'\b(cabinet handle|drawer handle)\b', 'Cabinet Handle'),

        # Shelving and storage
        (r'\b(shelf|shelving)\b', 'Shelf'),
        (r'\b(storage cabinet)\b', 'Storage Cabinet'),
        (r'\b(storage bin|storage box)\b', 'Storage Container'),

        # Flooring
        (r'\b(vinyl plank|vinyl flooring)\b', 'Vinyl Flooring'),
        (r'\b(laminate flooring)\b', 'Laminate Flooring'),
        (r'\b(tile|floor tile|wall tile)\b', 'Tile'),
        (r'\b(grout)\b', 'Grout'),

        # Paint and supplies
        (r'\b(paint brush)\b', 'Paint Brush'),
        (r'\b(paint roller)\b', 'Paint Roller'),
        (r'\b(paint tray)\b', 'Paint Tray'),
        (r'\b(primer)\b', 'Primer'),

        # Tools
        (r'\b(drill bit)\b', 'Drill Bit'),
        (r'\b(saw blade)\b', 'Saw Blade'),
        (r'\b(wrench)\b', 'Wrench'),
        (r'\b(screwdriver)\b', 'Screwdriver'),
        (r'\b(hammer)\b', 'Hammer'),

        # Electrical
        (r'\b(outlet|receptacle)\b', 'Electrical Outlet'),
        (r'\b(switch|light switch)\b', 'Light Switch'),
        (r'\b(switch plate|outlet cover|wall plate)\b', 'Switch Plate'),
        (r'\b(extension cord)\b', 'Extension Cord'),
        (r'\b(power strip)\b', 'Power Strip'),

        # Plumbing
        (r'\b(pipe|pvc pipe|copper pipe)\b', 'Pipe'),
        (r'\b(fitting|pipe fitting)\b', 'Pipe Fitting'),
        (r'\b(valve)\b', 'Valve'),
        (r'\b(drain)\b', 'Drain'),

        # HVAC
        (r'\b(air filter|furnace filter)\b', 'Air Filter'),
        (r'\b(thermostat)\b', 'Thermostat'),
        (r'\b(vent|air vent|register)\b', 'Air Vent'),

        # Outdoor
        (r'\b(mailbox)\b', 'Mailbox'),
        (r'\b(house number)\b', 'House Numbers'),
        (r'\b(door bell|doorbell)\b', 'Doorbell'),
        (r'\b(garden hose)\b', 'Garden Hose'),
        (r'\b(sprinkler)\b', 'Sprinkler'),

        # Fasteners and hardware
        (r'\b(screw|screws)\b', 'Screw'),
        (r'\b(nail|nails)\b', 'Nail'),
        (r'\b(bolt|bolts)\b', 'Bolt'),
        (r'\b(anchor|wall anchor)\b', 'Wall Anchor'),
        (r'\b(hook)\b', 'Hook'),

        # Miscellaneous
        (r'\b(step stool|stool)\b', 'Step Stool'),
        (r'\b(ladder)\b', 'Ladder'),
        (r'\b(trash can|garbage can)\b', 'Trash Can'),
    ]

    for pattern, product_type in patterns:
        if re.search(pattern, text):
            return product_type

    return 'Unidentifiable'

def analyze_data_quality(product: Dict, original_data: Dict) -> List[str]:
    """Analyze data quality issues."""
    issues = []

    title = product.get('title', '')
    description = original_data.get('description', '')

    # Check title length
    if len(title) < 20:
        issues.append('Very short title')
    elif len(title) < 40:
        issues.append('Short title')

    # Check if title is truncated
    if title.endswith('..') or title.endswith('...'):
        issues.append('Truncated title')

    # Check description
    if not description:
        issues.append('Missing description')
    elif len(description) < 50:
        issues.append('Very short description')
    elif len(description) < 150:
        issues.append('Short description')

    # Check for vague words
    vague_words = ['item', 'product', 'various', 'assorted', 'mixed']
    if any(word in title.lower() for word in vague_words):
        issues.append('Vague title')

    return issues

def categorize_unknown_product(product: Dict, original_data: Dict, inferred_type: str) -> str:
    """Categorize unknown product into analysis categories."""
    confidence = product.get('confidence', 0)
    title = product.get('title', '')
    description = original_data.get('description', '')

    # Check if it's missing data
    if product.get('product_type') == 'Unknown - Missing Data':
        return 'missing_data'

    # Check data quality issues
    data_issues = analyze_data_quality(product, original_data)

    # If we can infer a type, it's a missing pattern
    if inferred_type != 'Unidentifiable':
        return 'missing_pattern'

    # If confidence is low but has some signal
    if 0 < confidence < 20:
        return 'weak_match'

    # If there are data quality issues
    if data_issues:
        return 'data_quality'

    # Truly ambiguous
    return 'truly_ambiguous'

def main():
    print("Loading classification results...")
    classifications = load_json_file('/home/user/CC/outputs/product_classifications.json')

    print("Loading original product data...")
    original_products = load_json_file('/home/user/CC/data/scraped_data_output.json')

    # Create index mapping for original products
    original_by_index = {i: p for i, p in enumerate(original_products)}

    print(f"Total products: {len(classifications)}")

    # Extract all Unknown products
    unknown_products = [
        p for p in classifications
        if 'Unknown' in p.get('product_type', '')
    ]

    print(f"Unknown products: {len(unknown_products)}")

    # Categorize unknowns
    categories = {
        'missing_pattern': [],
        'weak_match': [],
        'data_quality': [],
        'truly_ambiguous': [],
        'missing_data': []
    }

    # Track inferred types
    inferred_types = Counter()
    all_keywords = Counter()

    # Analyze each unknown product
    for product in unknown_products:
        idx = product['index']
        original = original_by_index.get(idx, {})

        title = product.get('title', '')
        description = original.get('description', '')

        # Infer product type
        inferred_type = infer_product_type(title, description)
        if inferred_type != 'Unidentifiable':
            inferred_types[inferred_type] += 1

        # Extract keywords
        keywords = extract_keywords(title + ' ' + (description or ''))
        all_keywords.update(keywords)

        # Categorize
        category = categorize_unknown_product(product, original, inferred_type)

        # Store with additional info
        product_info = {
            'index': idx,
            'title': title,
            'brand': product.get('brand', ''),
            'confidence': product.get('confidence', 0),
            'product_type': product.get('product_type', ''),
            'inferred_type': inferred_type,
            'data_quality_issues': analyze_data_quality(product, original),
            'description_length': len(description) if description else 0,
            'keywords': keywords[:10],  # Top 10 keywords
            'reasons': product.get('reasons', [])
        }

        categories[category].append(product_info)

    # Build comprehensive analysis
    analysis = {
        'summary': {
            'total_products': len(classifications),
            'unknown_products': len(unknown_products),
            'unknown_percentage': round(len(unknown_products) / len(classifications) * 100, 2),
            'breakdown_by_type': {
                'Unknown - Unable to Classify': len([p for p in unknown_products if 'Unable to Classify' in p.get('product_type', '')]),
                'Unknown - Missing Data': len([p for p in unknown_products if 'Missing Data' in p.get('product_type', '')])
            }
        },
        'categories': {},
        'top_missing_product_types': [],
        'top_keywords': [],
        'confidence_distribution': {
            '0': 0,
            '1-10': 0,
            '11-20': 0,
            '21-30': 0,
            '31-40': 0,
            '41+': 0
        }
    }

    # Confidence distribution
    for product in unknown_products:
        conf = product.get('confidence', 0)
        if conf == 0:
            analysis['confidence_distribution']['0'] += 1
        elif conf <= 10:
            analysis['confidence_distribution']['1-10'] += 1
        elif conf <= 20:
            analysis['confidence_distribution']['11-20'] += 1
        elif conf <= 30:
            analysis['confidence_distribution']['21-30'] += 1
        elif conf <= 40:
            analysis['confidence_distribution']['31-40'] += 1
        else:
            analysis['confidence_distribution']['41+'] += 1

    # Process each category
    for category_name, products in categories.items():
        if not products:
            continue

        # Get top keywords for this category
        category_keywords = Counter()
        for p in products:
            category_keywords.update(p['keywords'])

        # Get examples (up to 10)
        examples = []
        for p in products[:10]:
            examples.append({
                'index': p['index'],
                'title': p['title'],
                'brand': p['brand'],
                'confidence': p['confidence'],
                'inferred_type': p['inferred_type'],
                'data_quality_issues': p['data_quality_issues']
            })

        analysis['categories'][category_name] = {
            'count': len(products),
            'percentage': round(len(products) / len(unknown_products) * 100, 2),
            'description': get_category_description(category_name),
            'top_keywords': [{'keyword': k, 'count': v} for k, v in category_keywords.most_common(20)],
            'examples': examples,
            'all_products': [
                {
                    'index': p['index'],
                    'title': p['title'],
                    'inferred_type': p['inferred_type']
                }
                for p in products
            ]
        }

    # Top 20 missing product types
    analysis['top_missing_product_types'] = [
        {'product_type': k, 'count': v}
        for k, v in inferred_types.most_common(20)
    ]

    # Top keywords overall
    analysis['top_keywords'] = [
        {'keyword': k, 'count': v}
        for k, v in all_keywords.most_common(50)
    ]

    # Save analysis
    output_path = '/home/user/CC/outputs/unknown_products_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"\nAnalysis complete! Saved to: {output_path}")
    print(f"\nSummary:")
    print(f"  Total Unknown: {len(unknown_products)}")
    print(f"  Missing Pattern: {len(categories['missing_pattern'])}")
    print(f"  Weak Match: {len(categories['weak_match'])}")
    print(f"  Data Quality Issues: {len(categories['data_quality'])}")
    print(f"  Truly Ambiguous: {len(categories['truly_ambiguous'])}")
    print(f"  Missing Data: {len(categories['missing_data'])}")
    print(f"\nTop 10 Missing Product Types:")
    for i, (ptype, count) in enumerate(inferred_types.most_common(10), 1):
        print(f"  {i}. {ptype}: {count}")

def get_category_description(category: str) -> str:
    """Get description for each category."""
    descriptions = {
        'missing_pattern': 'Products that can be identified from title/description but lack matching patterns in the classifier',
        'weak_match': 'Products with very low confidence scores that should match existing patterns',
        'data_quality': 'Products with insufficient or poor quality data (short titles, missing descriptions, etc.)',
        'truly_ambiguous': 'Products that are genuinely difficult to classify even with good data',
        'missing_data': 'Products flagged as having missing or insufficient data'
    }
    return descriptions.get(category, 'Unknown category')

if __name__ == '__main__':
    main()
