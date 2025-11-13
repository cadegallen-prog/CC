#!/usr/bin/env python3
"""
Mine product descriptions and specifications for product type signals.
This script analyzes Home Depot product data to extract type indicators.
"""

import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any
import statistics

def load_products(filepath: str) -> List[Dict[str, Any]]:
    """Load product data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_description_length(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze word count statistics for product descriptions."""
    word_counts = []
    char_counts = []
    missing_count = 0

    for product in products:
        desc = product.get('description', '')
        if not desc or desc.strip() == '':
            missing_count += 1
            continue

        words = len(desc.split())
        chars = len(desc)
        word_counts.append(words)
        char_counts.append(chars)

    if not word_counts:
        return {"error": "No descriptions found"}

    return {
        "total_products": len(products),
        "products_with_descriptions": len(word_counts),
        "products_missing_descriptions": missing_count,
        "word_count": {
            "min": min(word_counts),
            "max": max(word_counts),
            "mean": round(statistics.mean(word_counts), 1),
            "median": round(statistics.median(word_counts), 1),
            "stdev": round(statistics.stdev(word_counts), 1) if len(word_counts) > 1 else 0
        },
        "character_count": {
            "min": min(char_counts),
            "max": max(char_counts),
            "mean": round(statistics.mean(char_counts), 1),
            "median": round(statistics.median(char_counts), 1)
        }
    }

def extract_product_type_phrases(description: str) -> List[str]:
    """Extract phrases that signal product type from description."""
    if not description:
        return []

    desc_lower = description.lower()

    # Pattern 1: "This [product type]" or "The [product type]"
    this_patterns = re.findall(r'(?:this|the|these)\s+([a-z\-\s]+?)(?:\s+(?:is|are|has|have|provides?|features?|offers?|comes?|includes?))', desc_lower)

    # Pattern 2: "[Product type] is/are designed" or "[Product type] provides"
    designed_patterns = re.findall(r'^([a-z\-\s]+?)(?:\s+(?:is|are)\s+designed)', desc_lower)

    # Pattern 3: Quoted product types or direct mentions
    # Look for specific product indicators at start of sentences
    sentence_starts = re.findall(r'(?:^|\.\s+)([a-z\-\s]+?)(?:\s+(?:provides?|features?|offers?|is|are))', desc_lower)

    all_phrases = this_patterns + designed_patterns + sentence_starts

    # Clean up phrases - remove common words that aren't product types
    stop_words = {'the', 'this', 'these', 'those', 'that', 'with', 'from', 'into', 'for', 'and', 'or'}
    cleaned_phrases = []

    for phrase in all_phrases:
        words = phrase.strip().split()
        cleaned = ' '.join([w for w in words if w not in stop_words and len(w) > 2])
        if cleaned and len(cleaned.split()) <= 5:  # Keep phrases with 5 or fewer words
            cleaned_phrases.append(cleaned)

    return cleaned_phrases

def detect_category_signals(text: str) -> Dict[str, List[str]]:
    """Detect category signals from text (description or specs)."""
    if not text:
        return {}

    text_lower = text.lower()

    # Category keyword lists
    categories = {
        "lighting": [
            "light", "bulb", "led", "lamp", "fixture", "chandelier", "sconce",
            "lumens", "watt", "brightness", "illumination", "lighting", "lantern",
            "ceiling fan", "track lighting", "pendant", "flush mount", "recessed"
        ],
        "electrical": [
            "breaker", "circuit", "outlet", "switch", "wire", "cable", "volt",
            "amp", "gfci", "electrical", "wiring", "panel", "receptacle",
            "dimmer", "timer", "surge protector", "extension cord"
        ],
        "plumbing": [
            "faucet", "sink", "toilet", "shower", "pipe", "drain", "water",
            "plumbing", "valve", "bathtub", "basin", "sprayer", "spout",
            "gallon", "gpm", "flow rate", "aerator", "cartridge"
        ],
        "hvac": [
            "heater", "fan", "air", "temperature", "cooling", "heating",
            "ventilation", "thermostat", "hvac", "cfm", "btu", "climate"
        ],
        "hardware": [
            "screw", "nail", "bolt", "nut", "hinge", "lock", "handle",
            "knob", "hook", "bracket", "fastener", "anchor", "clamp"
        ],
        "tools": [
            "drill", "saw", "hammer", "wrench", "screwdriver", "tool",
            "power tool", "blade", "bit", "sander", "grinder", "router"
        ],
        "paint": [
            "paint", "primer", "stain", "coating", "brush", "roller",
            "gallon", "finish", "latex", "enamel", "color", "coverage"
        ],
        "flooring": [
            "floor", "flooring", "tile", "carpet", "vinyl", "laminate",
            "hardwood", "planks", "sq ft", "underlayment", "grout"
        ],
        "outdoor_garden": [
            "garden", "lawn", "outdoor", "patio", "deck", "fence",
            "hose", "sprinkler", "mulch", "soil", "plant", "grass"
        ],
        "building_materials": [
            "lumber", "wood", "beam", "board", "plywood", "drywall",
            "insulation", "concrete", "brick", "shingle", "roofing"
        ]
    }

    detected = {}
    for category, keywords in categories.items():
        matches = []
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                matches.append(keyword)
        if matches:
            detected[category] = matches

    return detected

def calculate_category_confidence(category_signals: Dict[str, List[str]]) -> List[tuple]:
    """Calculate confidence scores for each category based on signal count."""
    if not category_signals:
        return []

    # Score by number of unique keyword matches
    scores = [(category, len(keywords)) for category, keywords in category_signals.items()]
    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)

    return scores

def extract_spec_fields(structured_specs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract useful specification fields that help identify product type."""
    if not structured_specs:
        return {}

    useful_fields = {}

    # Extract key specification categories
    if 'dimensions' in structured_specs:
        useful_fields['dimensions'] = structured_specs['dimensions']

    if 'wattage' in structured_specs:
        useful_fields['wattage'] = structured_specs['wattage']

    if 'lumens' in structured_specs:
        useful_fields['lumens'] = structured_specs['lumens']

    if 'color_temp' in structured_specs:
        useful_fields['color_temp'] = structured_specs['color_temp']

    if 'base_type' in structured_specs:
        useful_fields['base_type'] = structured_specs['base_type']

    if 'dimmable' in structured_specs:
        useful_fields['dimmable'] = structured_specs['dimmable']

    if 'product_domains' in structured_specs:
        useful_fields['product_domains'] = structured_specs['product_domains']

    # Add any other fields that exist
    for key in structured_specs:
        if key not in ['dimensions', 'details'] and key not in useful_fields:
            useful_fields[key] = structured_specs[key]

    return useful_fields

def analyze_single_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single product and extract all signals."""
    title = product.get('title', '')
    description = product.get('description', '')
    specs = product.get('structured_specifications', {})

    # Extract type phrases from description
    type_phrases = extract_product_type_phrases(description)

    # Detect category signals from description
    desc_categories = detect_category_signals(description)

    # Detect category signals from title
    title_categories = detect_category_signals(title)

    # Combine category signals
    all_categories = {}
    for cat, keywords in desc_categories.items():
        all_categories[cat] = all_categories.get(cat, []) + keywords
    for cat, keywords in title_categories.items():
        all_categories[cat] = all_categories.get(cat, []) + keywords

    # Remove duplicates
    for cat in all_categories:
        all_categories[cat] = list(set(all_categories[cat]))

    # Calculate confidence
    confidence_scores = calculate_category_confidence(all_categories)

    # Extract useful spec fields
    useful_specs = extract_spec_fields(specs)

    # Determine description clarity
    has_clear_type = len(type_phrases) > 0

    return {
        "title": title,
        "description_word_count": len(description.split()) if description else 0,
        "has_description": bool(description and description.strip()),
        "type_phrases_extracted": type_phrases,
        "has_clear_type_phrase": has_clear_type,
        "category_signals": all_categories,
        "top_category": confidence_scores[0] if confidence_scores else None,
        "category_confidence_scores": confidence_scores,
        "useful_specs": useful_specs,
        "spec_count": len(useful_specs)
    }

def find_clear_and_vague_examples(products: List[Dict[str, Any]], count: int = 5) -> Dict[str, List[Dict]]:
    """Find examples of clear and vague product descriptions."""
    analyzed = [analyze_single_product(p) for p in products]

    # Clear: has type phrases AND good word count AND category signals
    clear = [a for a in analyzed if a['has_clear_type_phrase'] and a['description_word_count'] > 50 and a['category_signals']]
    clear_sorted = sorted(clear, key=lambda x: len(x['type_phrases_extracted']), reverse=True)

    # Vague: short description OR no type phrases OR no category signals
    vague = [a for a in analyzed if not a['has_clear_type_phrase'] or a['description_word_count'] < 30 or not a['category_signals']]
    vague_sorted = sorted(vague, key=lambda x: x['description_word_count'])

    return {
        "clear": clear_sorted[:count],
        "vague": vague_sorted[:count]
    }

def build_type_indicator_dictionary(products: List[Dict[str, Any]]) -> Dict[str, int]:
    """Build a dictionary of type indicator phrases found across all products."""
    phrase_counter = Counter()

    for product in products:
        description = product.get('description', '')
        phrases = extract_product_type_phrases(description)
        phrase_counter.update(phrases)

    # Return phrases that appear at least once, sorted by frequency
    return dict(phrase_counter.most_common())

def build_category_keyword_lists() -> Dict[str, List[str]]:
    """Return the comprehensive category keyword lists."""
    return {
        "lighting": [
            "light", "bulb", "led", "lamp", "fixture", "chandelier", "sconce",
            "lumens", "watt", "brightness", "illumination", "lighting", "lantern",
            "ceiling fan", "track lighting", "pendant", "flush mount", "recessed",
            "spotlight", "floodlight", "tube light", "strip light"
        ],
        "electrical": [
            "breaker", "circuit", "outlet", "switch", "wire", "cable", "volt",
            "amp", "gfci", "electrical", "wiring", "panel", "receptacle",
            "dimmer", "timer", "surge protector", "extension cord", "power strip",
            "conduit", "junction box", "electrical box"
        ],
        "plumbing": [
            "faucet", "sink", "toilet", "shower", "pipe", "drain", "water",
            "plumbing", "valve", "bathtub", "basin", "sprayer", "spout",
            "gallon", "gpm", "flow rate", "aerator", "cartridge", "showerhead",
            "toilet tank", "flush valve", "supply line"
        ],
        "hvac": [
            "heater", "fan", "air", "temperature", "cooling", "heating",
            "ventilation", "thermostat", "hvac", "cfm", "btu", "climate",
            "air conditioner", "furnace", "heat pump", "vent", "ductwork"
        ],
        "hardware": [
            "screw", "nail", "bolt", "nut", "hinge", "lock", "handle",
            "knob", "hook", "bracket", "fastener", "anchor", "clamp",
            "doorknob", "deadbolt", "latch", "hasp", "chain"
        ],
        "tools": [
            "drill", "saw", "hammer", "wrench", "screwdriver", "tool",
            "power tool", "blade", "bit", "sander", "grinder", "router",
            "circular saw", "miter saw", "jigsaw", "impact driver"
        ],
        "paint": [
            "paint", "primer", "stain", "coating", "brush", "roller",
            "gallon", "finish", "latex", "enamel", "color", "coverage",
            "spray paint", "paint can", "paint tray", "drop cloth"
        ],
        "flooring": [
            "floor", "flooring", "tile", "carpet", "vinyl", "laminate",
            "hardwood", "planks", "sq ft", "underlayment", "grout",
            "ceramic tile", "porcelain tile", "wood floor", "floor mat"
        ],
        "outdoor_garden": [
            "garden", "lawn", "outdoor", "patio", "deck", "fence",
            "hose", "sprinkler", "mulch", "soil", "plant", "grass",
            "garden hose", "watering", "fertilizer", "weed", "trimmer"
        ],
        "building_materials": [
            "lumber", "wood", "beam", "board", "plywood", "drywall",
            "insulation", "concrete", "brick", "shingle", "roofing",
            "stud", "joist", "rafter", "siding", "trim"
        ]
    }

def analyze_all_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze all products and return extraction results."""
    results = []
    for i, product in enumerate(products):
        analysis = analyze_single_product(product)
        analysis['product_index'] = i
        analysis['sku'] = product.get('sku', '')
        analysis['internet_sku'] = product.get('internet_sku', '')
        results.append(analysis)
    return results

def main():
    """Main execution function."""
    print("Loading product data...")
    products = load_products('data/scraped_data_output.json')
    print(f"Loaded {len(products)} products")

    # 1. Analyze description lengths
    print("\nAnalyzing description lengths...")
    desc_stats = analyze_description_length(products)
    print(f"Description stats: {json.dumps(desc_stats, indent=2)}")

    # 2. Find clear and vague examples
    print("\nFinding clear and vague description examples...")
    examples = find_clear_and_vague_examples(products, count=5)
    print(f"Found {len(examples['clear'])} clear and {len(examples['vague'])} vague examples")

    # 3. Build type indicator dictionary
    print("\nBuilding type indicator phrase dictionary...")
    type_phrases = build_type_indicator_dictionary(products)
    print(f"Found {len(type_phrases)} unique type indicator phrases")

    # 4. Build category keyword lists
    print("\nBuilding category keyword lists...")
    category_keywords = build_category_keyword_lists()
    print(f"Built {len(category_keywords)} category keyword lists")

    # 5. Analyze all products
    print("\nAnalyzing all products...")
    all_results = analyze_all_products(products)
    print(f"Analyzed {len(all_results)} products")

    # Save outputs
    print("\nSaving outputs...")

    # Save type indicator phrases (keep top 50+ phrases)
    with open('data/type_indicator_phrases.json', 'w', encoding='utf-8') as f:
        # Get at least 30 phrases, or all if fewer
        top_phrases = dict(list(type_phrases.items())[:max(50, len(type_phrases))])
        json.dump(top_phrases, f, indent=2)
    print(f"Saved type_indicator_phrases.json with {len(top_phrases)} phrases")

    # Save category keywords
    with open('data/category_keywords.json', 'w', encoding='utf-8') as f:
        json.dump(category_keywords, f, indent=2)
    print(f"Saved category_keywords.json")

    # Save extracted signals
    with open('outputs/extracted_signals.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved extracted_signals.json")

    # Save summary statistics
    summary = {
        "description_statistics": desc_stats,
        "total_products": len(products),
        "products_with_clear_descriptions": len([r for r in all_results if r['has_clear_type_phrase']]),
        "products_with_vague_descriptions": len([r for r in all_results if not r['has_clear_type_phrase']]),
        "total_unique_type_phrases": len(type_phrases),
        "clear_examples": examples['clear'],
        "vague_examples": examples['vague']
    }

    with open('outputs/analysis_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved analysis_summary.json")

    print("\n✓ Analysis complete!")
    return summary

if __name__ == '__main__':
    main()
