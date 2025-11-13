#!/usr/bin/env python3
"""
Description Analyzer
Analyzes product descriptions to identify products that have unclear titles.
Focuses on the 33% of products with clarity scores <= 6.
"""

import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple

# ============================================================================
# EXPANDED PRODUCT TYPE KEYWORDS FOR DESCRIPTIONS
# ============================================================================

# More detailed keywords that appear in descriptions
DESCRIPTION_KEYWORDS = {
    # Lighting products
    'light bulb': ['bulb', 'light bulb', 'led bulb', 'incandescent', 'cfl', 'halogen bulb'],
    'ceiling light': ['ceiling light', 'flush mount', 'semi-flush', 'ceiling fixture'],
    'chandelier': ['chandelier', 'hanging light', 'pendant light'],
    'wall sconce': ['wall sconce', 'wall light', 'wall fixture', 'wall mount light'],
    'recessed light': ['recessed light', 'can light', 'downlight', 'pot light'],
    'under cabinet light': ['under cabinet', 'under counter light', 'task lighting'],
    'outdoor light': ['outdoor light', 'exterior light', 'landscape light', 'pathway light'],
    'track light': ['track light', 'track head', 'track fixture'],

    # Electrical
    'circuit breaker': ['circuit breaker', 'breaker', 'electrical breaker', 'gfci breaker', 'afci breaker'],
    'electrical outlet': ['outlet', 'receptacle', 'wall outlet', 'electrical outlet', 'duplex outlet', 'gfci outlet', 'usb outlet'],
    'electrical switch': ['switch', 'light switch', 'wall switch', 'dimmer switch', 'toggle switch'],
    'electrical wire': ['wire', 'electrical wire', 'copper wire', 'romex', 'thhn', 'cable'],
    'electrical conduit': ['conduit', 'electrical conduit', 'pvc conduit', 'metallic conduit'],
    'electrical panel': ['electrical panel', 'breaker panel', 'load center', 'service panel'],
    'electrical box': ['electrical box', 'junction box', 'outlet box', 'switch box'],

    # Plumbing
    'faucet': ['faucet', 'tap', 'kitchen faucet', 'bathroom faucet', 'sink faucet'],
    'sink': ['sink', 'basin', 'washbasin', 'kitchen sink', 'bathroom sink', 'utility sink'],
    'toilet': ['toilet', 'commode', 'water closet', 'elongated toilet', 'round toilet'],
    'shower head': ['shower head', 'showerhead', 'rain shower', 'handheld shower'],
    'bathtub': ['bathtub', 'tub', 'soaking tub', 'alcove tub', 'freestanding tub'],
    'water heater': ['water heater', 'hot water heater', 'tankless water heater', 'gas water heater'],
    'pipe': ['pipe', 'plumbing pipe', 'pvc pipe', 'copper pipe', 'drain pipe'],
    'valve': ['valve', 'shut-off valve', 'ball valve', 'gate valve', 'check valve'],

    # Fans & HVAC
    'ceiling fan': ['ceiling fan', 'fan', 'indoor ceiling fan', 'outdoor ceiling fan'],
    'exhaust fan': ['exhaust fan', 'bathroom fan', 'ventilation fan', 'vent fan'],
    'portable fan': ['portable fan', 'floor fan', 'desk fan', 'table fan'],
    'thermostat': ['thermostat', 'programmable thermostat', 'smart thermostat', 'digital thermostat'],
    'hvac filter': ['air filter', 'hvac filter', 'furnace filter', 'ac filter'],

    # Tools - Power Tools
    'power drill': ['drill', 'power drill', 'cordless drill', 'hammer drill', 'impact driver'],
    'circular saw': ['circular saw', 'saw', 'power saw'],
    'miter saw': ['miter saw', 'compound miter saw', 'sliding miter saw'],
    'table saw': ['table saw'],
    'jigsaw': ['jigsaw', 'jig saw'],
    'reciprocating saw': ['reciprocating saw', 'recip saw', 'sawzall'],
    'angle grinder': ['angle grinder', 'grinder', 'disc grinder'],
    'sander': ['sander', 'orbital sander', 'belt sander', 'palm sander'],
    'router': ['router', 'wood router', 'trim router'],
    'nail gun': ['nail gun', 'nailer', 'brad nailer', 'finish nailer', 'framing nailer'],

    # Tools - Hand Tools
    'wrench': ['wrench', 'socket wrench', 'adjustable wrench', 'torque wrench'],
    'screwdriver': ['screwdriver', 'phillips screwdriver', 'flathead screwdriver'],
    'hammer': ['hammer', 'claw hammer', 'framing hammer', 'sledgehammer'],
    'pliers': ['pliers', 'needle nose pliers', 'locking pliers', 'wire cutters'],
    'level': ['level', 'spirit level', 'laser level', 'torpedo level', 'box level'],
    'tape measure': ['tape measure', 'measuring tape', 'ruler'],

    # Hardware
    'door hardware': ['door handle', 'door knob', 'door lever', 'door lock', 'deadbolt', 'door hinge'],
    'cabinet hardware': ['cabinet knob', 'cabinet pull', 'cabinet handle', 'cabinet hinge'],
    'fasteners': ['screw', 'nail', 'bolt', 'nut', 'washer', 'anchor'],
    'hook': ['hook', 'coat hook', 'wall hook', 'utility hook'],

    # Building Materials
    'drywall': ['drywall', 'sheetrock', 'gypsum board', 'wallboard'],
    'lumber': ['lumber', 'wood', '2x4', '2x6', 'plywood', 'board'],
    'insulation': ['insulation', 'fiberglass insulation', 'foam insulation'],
    'roofing': ['roofing', 'shingles', 'roof shingles', 'roofing material'],
    'flooring': ['flooring', 'vinyl flooring', 'laminate flooring', 'hardwood flooring', 'tile flooring'],

    # Paint & Supplies
    'paint': ['paint', 'interior paint', 'exterior paint', 'latex paint', 'oil-based paint'],
    'primer': ['primer', 'paint primer', 'sealer'],
    'wood stain': ['stain', 'wood stain', 'deck stain'],
    'caulk': ['caulk', 'caulking', 'sealant', 'silicone caulk'],

    # Outdoor & Garden
    'garden hose': ['hose', 'garden hose', 'water hose'],
    'sprinkler': ['sprinkler', 'lawn sprinkler', 'irrigation sprinkler'],
    'lawn mower': ['lawn mower', 'mower', 'push mower', 'riding mower'],
    'string trimmer': ['string trimmer', 'trimmer', 'weed eater', 'weed whacker'],
    'leaf blower': ['leaf blower', 'blower'],
    'pressure washer': ['pressure washer', 'power washer'],

    # Storage & Organization
    'shelving': ['shelf', 'shelving', 'shelving unit', 'wall shelf', 'storage shelf'],
    'cabinet': ['cabinet', 'storage cabinet', 'base cabinet', 'wall cabinet'],
    'storage bin': ['storage bin', 'bin', 'storage container', 'tote'],
    'rack': ['rack', 'storage rack', 'shelving rack', 'wire rack'],

    # Windows & Doors
    'door': ['door', 'entry door', 'interior door', 'exterior door', 'front door'],
    'window': ['window', 'vinyl window', 'wood window', 'sliding window'],
    'window blind': ['blind', 'window blind', 'mini blind', 'venetian blind'],
    'window shade': ['shade', 'window shade', 'roller shade', 'cellular shade'],
    'curtain rod': ['curtain rod', 'drapery rod', 'rod'],

    # Cleaning & Maintenance
    'vacuum': ['vacuum', 'shop vacuum', 'wet dry vac', 'shop vac'],
    'cleaning supplies': ['cleaner', 'cleaning solution', 'disinfectant', 'all-purpose cleaner'],
    'mop': ['mop', 'floor mop', 'wet mop', 'dust mop'],
    'broom': ['broom', 'push broom', 'angle broom'],

    # Safety & Security
    'smoke detector': ['smoke detector', 'smoke alarm', 'fire alarm'],
    'carbon monoxide detector': ['carbon monoxide detector', 'co detector'],
    'fire extinguisher': ['fire extinguisher', 'extinguisher'],
    'safety equipment': ['safety glasses', 'safety goggles', 'hard hat', 'work gloves', 'respirator'],
    'door lock': ['lock', 'door lock', 'smart lock', 'keypad lock', 'deadbolt'],
}

# Usage context patterns - help identify products by what they do
USAGE_PATTERNS = {
    'ceiling fan': ['install on ceiling', 'ceiling mount', 'downrod', 'airflow', 'fan blades'],
    'light bulb': ['lumens', 'brightness', 'color temperature', 'kelvin', 'wattage equivalent'],
    'circuit breaker': ['overload protection', 'trip', 'electrical panel', 'amp rating'],
    'faucet': ['water flow', 'gpm', 'spout', 'aerator', 'install on sink'],
    'toilet': ['flush', 'bowl', 'elongated', 'gpf', 'water sense'],
    'power drill': ['drilling', 'driver', 'chuck', 'torque', 'cordless', 'battery'],
    'paint': ['coverage', 'square feet', 'coat', 'finish', 'apply to walls'],
    'thermostat': ['temperature control', 'programmable', 'heating', 'cooling', 'schedule'],
}

# Category indicators - phrases that hint at product category
CATEGORY_INDICATORS = {
    'lighting': ['light', 'lighting', 'illuminate', 'brightness', 'lumens', 'watt', 'led', 'bulb'],
    'electrical': ['electrical', 'electric', 'power', 'amp', 'volt', 'wire', 'circuit', 'breaker'],
    'plumbing': ['plumbing', 'water', 'drain', 'pipe', 'faucet', 'toilet', 'shower', 'sink'],
    'tools': ['tool', 'drill', 'saw', 'cut', 'sand', 'grind', 'cordless', 'battery powered'],
    'hardware': ['hardware', 'mount', 'install', 'attach', 'secure', 'fastener'],
    'hvac': ['heating', 'cooling', 'ventilation', 'air flow', 'fan', 'filter', 'thermostat'],
    'paint': ['paint', 'coating', 'finish', 'color', 'stain', 'primer', 'coverage'],
    'outdoor': ['outdoor', 'garden', 'lawn', 'yard', 'exterior', 'landscape'],
}

# ============================================================================
# DESCRIPTION ANALYSIS FUNCTIONS
# ============================================================================

def extract_first_sentence(description: str) -> str:
    """Extract the first sentence from description (usually most informative)."""
    if not description:
        return ""

    # Find first period, exclamation, or question mark
    match = re.search(r'^[^.!?]+[.!?]', description)
    if match:
        return match.group(0).strip()

    # If no sentence end, take first 150 characters
    return description[:150].strip()


def find_product_type_in_description(description: str, title: str = "") -> Tuple[Optional[str], float, List[str]]:
    """
    Find product type from description text.
    Returns (product_type, confidence_score, evidence_list)
    """
    if not description:
        return None, 0.0, []

    description_lower = description.lower()
    title_lower = title.lower()
    combined = f"{title_lower} {description_lower}"

    # Track evidence
    evidence = []
    matches = []

    # Strategy 1: Look for explicit product type keywords
    for product_type, keywords in DESCRIPTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                matches.append({
                    'type': product_type,
                    'keyword': keyword,
                    'confidence': 0.8,
                    'source': 'keyword_match'
                })
                evidence.append(f"Found '{keyword}' in description")
                break  # Only count each product type once

    # Strategy 2: Look for usage context patterns
    for product_type, patterns in USAGE_PATTERNS.items():
        pattern_count = sum(1 for pattern in patterns if pattern in description_lower)
        if pattern_count >= 2:  # At least 2 usage patterns
            matches.append({
                'type': product_type,
                'keyword': 'usage_pattern',
                'confidence': 0.7,
                'source': 'usage_context'
            })
            evidence.append(f"Found {pattern_count} usage patterns for {product_type}")

    # Strategy 3: Look at first sentence (often contains product type)
    first_sentence = extract_first_sentence(description).lower()
    for product_type, keywords in DESCRIPTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in first_sentence:
                matches.append({
                    'type': product_type,
                    'keyword': keyword,
                    'confidence': 0.9,  # Higher confidence if in first sentence
                    'source': 'first_sentence'
                })
                evidence.append(f"Found '{keyword}' in first sentence")
                break

    # No matches found
    if not matches:
        return None, 0.0, ["No product type keywords found in description"]

    # Score each product type by total confidence
    type_scores = defaultdict(float)
    for match in matches:
        type_scores[match['type']] += match['confidence']

    # Get highest scoring type
    best_type = max(type_scores.items(), key=lambda x: x[1])
    product_type = best_type[0]
    confidence = min(best_type[1], 1.0)  # Cap at 1.0

    return product_type, confidence, evidence


def identify_product_category(description: str) -> Tuple[Optional[str], List[str]]:
    """
    Identify broad product category from description.
    Returns (category, evidence_list)
    """
    if not description:
        return None, []

    description_lower = description.lower()

    category_scores = defaultdict(int)
    evidence = []

    for category, indicators in CATEGORY_INDICATORS.items():
        for indicator in indicators:
            if indicator in description_lower:
                category_scores[category] += 1

    if not category_scores:
        return None, ["No category indicators found"]

    best_category = max(category_scores.items(), key=lambda x: x[1])
    evidence.append(f"Found {best_category[1]} indicators for {best_category[0]} category")

    return best_category[0], evidence


def analyze_single_product(product: Dict, clarity_score: int) -> Dict:
    """
    Analyze a single product's description to enhance identification.
    """
    title = product.get('title', '')
    description = product.get('description', '')

    # Extract product type from description
    desc_type, confidence, evidence = find_product_type_in_description(description, title)

    # Identify category
    category, category_evidence = identify_product_category(description)

    # Extract first sentence for context
    first_sentence = extract_first_sentence(description)

    return {
        'item_id': product.get('item_id', 'unknown'),
        'title': title,
        'original_clarity_score': clarity_score,
        'description_product_type': desc_type,
        'description_confidence': confidence,
        'category': category,
        'evidence': evidence,
        'category_evidence': category_evidence,
        'first_sentence': first_sentence,
        'has_description': bool(description),
        'description_length': len(description) if description else 0,
    }


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_descriptions():
    """
    Main function to analyze descriptions for products with unclear titles.
    """
    print("Loading product data...\n")

    # Load products
    with open('data/scraped_data_output.json', 'r') as f:
        products = json.load(f)

    # Load clarity scores
    with open('outputs/title_clarity_scores.json', 'r') as f:
        clarity_scores = json.load(f)

    # Create lookup dict
    clarity_lookup = {s['item_id']: s['clarity_score'] for s in clarity_scores}

    print(f"Total products: {len(products)}")

    # Focus on products with unclear titles (score <= 6)
    unclear_products = []
    for i, product in enumerate(products):
        item_id = product.get('item_id', f'product_{i}')
        clarity = clarity_lookup.get(item_id, 5)

        if clarity <= 6:
            unclear_products.append({
                'product': product,
                'clarity': clarity,
                'item_id': item_id
            })

    print(f"Products with unclear titles (score ≤6): {len(unclear_products)}\n")

    # Analyze each unclear product
    print("Analyzing descriptions...\n")
    results = []
    improvements = []

    for item in unclear_products:
        product = item['product']
        clarity = item['clarity']

        result = analyze_single_product(product, clarity)
        results.append(result)

        # Track improvements (found a type in description)
        if result['description_product_type']:
            improvements.append(result)

    print(f"✓ Analyzed {len(results)} products")
    print(f"✓ Found product types for {len(improvements)} products ({len(improvements)/len(results)*100:.1f}%)\n")

    # Generate outputs
    generate_outputs(results, improvements, products, clarity_scores)

    return results, improvements


def generate_outputs(results, improvements, all_products, clarity_scores):
    """
    Generate all output files and reports.
    """
    print("Generating output files...\n")

    # 1. Enhanced product types (combining title + description)
    enhanced_types = []

    # Create lookup for description results
    desc_lookup = {r['item_id']: r for r in results}

    for score in clarity_scores:
        item_id = score['item_id']
        enhanced = {
            'item_id': item_id,
            'title': score['title'],
            'title_clarity_score': score['clarity_score'],
            'product_type_from_title': None,  # Would need to parse from title analysis
            'product_type_from_description': None,
            'description_confidence': 0.0,
            'final_product_type': None,
            'identification_method': 'title_only'
        }

        # If we analyzed this product's description
        if item_id in desc_lookup:
            desc_result = desc_lookup[item_id]
            enhanced['product_type_from_description'] = desc_result['description_product_type']
            enhanced['description_confidence'] = desc_result['description_confidence']

            if desc_result['description_product_type']:
                enhanced['final_product_type'] = desc_result['description_product_type']
                enhanced['identification_method'] = 'title_and_description'

        enhanced_types.append(enhanced)

    with open('outputs/enhanced_product_types.json', 'w') as f:
        json.dump(enhanced_types, f, indent=2)
    print("✓ Created outputs/enhanced_product_types.json")

    # 2. Description analysis results
    with open('outputs/description_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✓ Created outputs/description_analysis_results.json")

    # 3. Description keywords usage
    keyword_usage = Counter()
    for result in improvements:
        if result['description_product_type']:
            keyword_usage[result['description_product_type']] += 1

    keywords_data = {
        'total_keywords': len(DESCRIPTION_KEYWORDS),
        'keywords_found': dict(keyword_usage.most_common()),
        'keyword_dictionary': {k: v[:5] for k, v in DESCRIPTION_KEYWORDS.items()}  # Sample
    }

    with open('data/description_keywords.json', 'w') as f:
        json.dump(keywords_data, f, indent=2)
    print("✓ Created data/description_keywords.json")

    # 4. Generate markdown report
    generate_report(results, improvements, all_products, clarity_scores)
    print("✓ Created reports/description_analysis.md")

    print("\n✅ Description analysis complete!")


def generate_report(results, improvements, all_products, clarity_scores):
    """
    Generate comprehensive markdown report.
    """
    with open('reports/description_analysis.md', 'w') as f:
        f.write("# Product Description Analysis Report\n\n")
        f.write(f"**Analysis Date:** 2025-11-13\n")
        f.write(f"**Products Analyzed:** {len(results)} (products with title clarity ≤6)\n")
        f.write(f"**Products Improved:** {len(improvements)}\n\n")
        f.write("---\n\n")

        # SECTION 1: Overview
        f.write("## 1. Analysis Overview\n\n")
        f.write("This analysis focuses on the 33% of products that couldn't be clearly identified from titles alone.\n\n")

        # Stats
        total_analyzed = len(results)
        found_type = len(improvements)
        not_found = total_analyzed - found_type

        f.write("### Results Summary\n\n")
        f.write(f"- **Total products with unclear titles:** {total_analyzed}\n")
        f.write(f"- **Product types found in descriptions:** {found_type} ({found_type/total_analyzed*100:.1f}%)\n")
        f.write(f"- **Still unclear after description analysis:** {not_found} ({not_found/total_analyzed*100:.1f}%)\n\n")

        # Breakdown by original clarity score
        score_breakdown = defaultdict(lambda: {'total': 0, 'found': 0})
        for result in results:
            score = result['original_clarity_score']
            score_breakdown[score]['total'] += 1
            if result['description_product_type']:
                score_breakdown[score]['found'] += 1

        f.write("### Improvement by Original Clarity Score\n\n")
        f.write("| Original Score | Total Products | Types Found | Success Rate |\n")
        f.write("|----------------|----------------|-------------|-------------|\n")
        for score in sorted(score_breakdown.keys(), reverse=True):
            data = score_breakdown[score]
            success = (data['found'] / data['total'] * 100) if data['total'] > 0 else 0
            f.write(f"| {score}/10 | {data['total']} | {data['found']} | {success:.1f}% |\n")
        f.write("\n")

        # SECTION 2: Success Stories
        f.write("## 2. Success Stories - Vague Titles Identified\n\n")
        f.write("### Examples of Products Successfully Identified from Descriptions\n\n")

        # Show 15 good examples
        good_examples = [r for r in improvements if r['description_confidence'] >= 0.7][:15]

        for i, example in enumerate(good_examples, 1):
            f.write(f"#### Example {i}\n\n")
            f.write(f"**Title:** {example['title']}\n\n")
            f.write(f"- **Original Clarity:** {example['original_clarity_score']}/10\n")
            f.write(f"- **Identified Type:** {example['description_product_type']}\n")
            f.write(f"- **Confidence:** {example['description_confidence']:.0%}\n")
            f.write(f"- **Category:** {example['category']}\n")
            f.write(f"- **Evidence:** {example['evidence'][0] if example['evidence'] else 'N/A'}\n")
            if example['first_sentence']:
                f.write(f"- **First Sentence:** {example['first_sentence'][:150]}...\n")
            f.write("\n---\n\n")

        # SECTION 3: Product Types Found
        f.write("## 3. Product Types Found in Descriptions\n\n")

        # Count types
        type_counts = Counter()
        for result in improvements:
            if result['description_product_type']:
                type_counts[result['description_product_type']] += 1

        f.write("### Top 20 Product Types Identified\n\n")
        f.write("| Product Type | Count | Percentage |\n")
        f.write("|--------------|-------|------------|\n")

        for product_type, count in type_counts.most_common(20):
            pct = (count / len(improvements) * 100) if improvements else 0
            f.write(f"| {product_type} | {count} | {pct:.1f}% |\n")

        f.write("\n")

        # SECTION 4: Still Unclear
        f.write("## 4. Products Still Unclear After Description Analysis\n\n")

        still_unclear = [r for r in results if not r['description_product_type']]

        f.write(f"Found {len(still_unclear)} products that need specifications analysis.\n\n")

        # Show examples
        f.write("### Examples of Products Needing Further Analysis\n\n")
        for i, unclear in enumerate(still_unclear[:10], 1):
            f.write(f"**{i}. Title:** {unclear['title'][:80]}...\n\n")
            f.write(f"- **Clarity Score:** {unclear['original_clarity_score']}/10\n")
            f.write(f"- **Has Description:** {'Yes' if unclear['has_description'] else 'No'}\n")
            f.write(f"- **Description Length:** {unclear['description_length']} characters\n")
            if unclear['category']:
                f.write(f"- **Detected Category:** {unclear['category']}\n")
            if unclear['first_sentence']:
                f.write(f"- **First Sentence:** {unclear['first_sentence'][:100]}...\n")
            f.write("\n")

        # SECTION 5: Category Distribution
        f.write("## 5. Product Category Distribution\n\n")

        category_counts = Counter()
        for result in results:
            if result['category']:
                category_counts[result['category']] += 1

        f.write("| Category | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")

        for category, count in category_counts.most_common():
            pct = (count / len(results) * 100) if results else 0
            f.write(f"| {category} | {count} | {pct:.1f}% |\n")

        f.write("\n")

        # SECTION 6: Key Insights
        f.write("## 6. Key Insights & Recommendations\n\n")

        f.write("### What Worked\n\n")
        f.write("1. **First Sentence Analysis:** Product type is often explicitly stated in the first sentence\n")
        f.write("2. **Keyword Matching:** Expanded keyword dictionary caught most common product types\n")
        f.write("3. **Usage Context:** Phrases like 'install on ceiling' help identify ambiguous products\n")
        f.write(f"4. **Success Rate:** {found_type/total_analyzed*100:.1f}% of unclear titles were resolved using descriptions\n\n")

        f.write("### What Didn't Work\n\n")
        f.write(f"1. **Missing Descriptions:** Some products have very short or missing descriptions\n")
        f.write(f"2. **Generic Language:** Descriptions with only marketing fluff, no technical details\n")
        f.write(f"3. **Complex Products:** Multi-function products hard to classify into single type\n\n")

        f.write("### Next Steps\n\n")
        f.write(f"1. **For {found_type} products:** Successfully identified using title + description\n")
        f.write(f"2. **For {not_found} remaining products:** Need specifications analysis\n")
        f.write("3. **Build specifications analyzer:** Parse specs like 'Amps', 'Voltage', 'Dimensions' for final identification\n")
        f.write("4. **Consider hybrid approach:** Combine title + description + specs for maximum accuracy\n\n")

        # SECTION 7: Detailed Examples
        f.write("## 7. Detailed Analysis Examples\n\n")
        f.write("### High Confidence Identifications\n\n")

        high_conf = [r for r in improvements if r['description_confidence'] >= 0.8][:5]
        for i, result in enumerate(high_conf, 1):
            f.write(f"#### Product {i}\n\n")
            f.write(f"**Title:** {result['title']}\n\n")
            f.write(f"**Identified As:** {result['description_product_type']}\n\n")
            f.write(f"**Confidence:** {result['description_confidence']:.0%}\n\n")
            f.write(f"**Evidence:**\n")
            for evidence in result['evidence']:
                f.write(f"- {evidence}\n")
            f.write("\n")
            if result['first_sentence']:
                f.write(f"**First Sentence:** {result['first_sentence']}\n\n")
            f.write("---\n\n")

        f.write("\n*End of Report*\n")


if __name__ == '__main__':
    analyze_descriptions()
