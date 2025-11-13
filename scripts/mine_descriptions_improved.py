#!/usr/bin/env python3
"""
IMPROVED product description and specification mining.
Addresses the problem 14% with better extraction techniques.
"""

import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional
import statistics

def load_products(filepath: str) -> List[Dict[str, Any]]:
    """Load product data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_brand_specialties() -> Dict[str, str]:
    """Load brand specialties if available."""
    try:
        with open('data/brand_specialties.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def extract_product_type_from_title(title: str) -> Optional[str]:
    """Extract product type directly from title using comprehensive patterns."""
    if not title:
        return None

    title_lower = title.lower()

    # Multi-word patterns first (more specific)
    patterns = [
        ('ceiling fan', 'ceiling_fan'),
        ('light bulb', 'light_bulb'),
        ('led bulb', 'light_bulb'),
        ('track light', 'track_lighting'),
        ('circuit breaker', 'circuit_breaker'),
        ('kitchen faucet', 'kitchen_faucet'),
        ('bathroom faucet', 'bathroom_faucet'),
        ('shower head', 'showerhead'),
        ('showerhead', 'showerhead'),
        ('door handle', 'door_handle'),
        ('door lock', 'door_lock'),
        ('handleset', 'door_handleset'),
        ('recessed light', 'recessed_light'),
        ('can light', 'recessed_light'),
        ('pendant light', 'pendant_light'),
        ('vanity light', 'vanity_light'),
        ('outdoor light', 'outdoor_light'),
        ('flood light', 'flood_light'),
        ('floodlight', 'flood_light'),
        ('strip light', 'led_strip'),
        ('led strip', 'led_strip'),
        ('paint sprayer', 'paint_sprayer'),
        ('tool bag', 'tool_bag'),
        ('knee pad', 'knee_pads'),
        ('garden glove', 'garden_gloves'),
        ('work glove', 'work_gloves'),
        ('garden hose', 'garden_hose'),
        ('screen door', 'screen_door'),
        ('roller shade', 'window_shade'),
        ('window shade', 'window_shade'),
        ('vanity top', 'vanity_top'),
        ('shower pan', 'shower_pan'),
        ('shower base', 'shower_base'),
        ('area rug', 'area_rug'),
        ('extension tube', 'skylight_tube'),
        ('sun tunnel', 'skylight_tube'),
        ('valve stem', 'faucet_valve'),
        ('lighting transformer', 'transformer'),
        ('load center', 'electrical_panel'),
        ('breaker box', 'electrical_panel'),
        ('ground fault', 'gfci_breaker'),
        ('gfci', 'gfci_breaker'),
        ('saw blade', 'saw_blade'),
        ('saw chain', 'saw_chain'),
        ('polesaw', 'pole_saw'),
        ('pole saw', 'pole_saw'),
        ('replacement cartridge', 'filter_cartridge'),
        ('vapor cartridge', 'filter_cartridge'),
        ('painter\'s tape', 'painters_tape'),
        ('painters tape', 'painters_tape'),
        ('masking tape', 'painters_tape'),
        ('spray sock', 'paint_sprayer_accessory'),
        ('spray hood', 'paint_sprayer_accessory'),
        ('sweeping pad', 'cleaning_pad'),
        ('duster refill', 'duster'),
        ('toilet paper holder', 'toilet_paper_holder'),
        ('paper holder', 'toilet_paper_holder'),
        ('safety glasses', 'safety_glasses'),
        ('freeze protector', 'faucet_freeze_protector'),
        ('flexible conduit', 'electrical_conduit'),
        ('metal conduit', 'electrical_conduit'),
    ]

    # Check multi-word patterns
    for pattern, product_type in patterns:
        if pattern in title_lower:
            return product_type

    # Single word patterns (less specific, check later)
    single_word_patterns = [
        ('breaker', 'circuit_breaker'),
        ('faucet', 'faucet'),
        ('toilet', 'toilet'),
        ('chandelier', 'chandelier'),
        ('sconce', 'wall_sconce'),
        ('pendant', 'pendant_light'),
        ('fixture', 'light_fixture'),
        ('switch', 'electrical_switch'),
        ('outlet', 'electrical_outlet'),
        ('receptacle', 'electrical_outlet'),
        ('bulb', 'light_bulb'),
        ('drill', 'drill'),
        ('ladder', 'ladder'),
        ('gloves', 'gloves'),
        ('sprinkler', 'sprinkler'),
        ('skylight', 'skylight'),
        ('window', 'window'),
        ('tile', 'tile'),
        ('conduit', 'electrical_conduit'),
    ]

    for pattern, product_type in single_word_patterns:
        if f' {pattern}' in f' {title_lower}' or f'{pattern} ' in f'{title_lower} ':
            return product_type

    # Check for LED + light combination
    if 'led' in title_lower and 'light' in title_lower:
        return 'led_light'

    # Check for wire/cable
    if 'wire' in title_lower or 'cable' in title_lower:
        if 'lamp' in title_lower:
            return 'lamp_wire'
        return 'electrical_wire'

    # Check for saw
    if 'saw' in title_lower:
        return 'saw'

    # Check for rug/mat
    if ' rug' in title_lower or 'rug ' in title_lower:
        return 'rug'

    # Check for hose
    if 'hose' in title_lower:
        return 'hose'

    return None

def extract_product_type_from_brand(brand: str, brand_specialties: Dict[str, str]) -> Optional[str]:
    """Infer product type from brand specialty."""
    if not brand:
        return None

    brand_lower = brand.lower()
    return brand_specialties.get(brand_lower)

def extract_from_spec_fingerprint(specs: Dict[str, Any]) -> Optional[str]:
    """Identify product type from specification fingerprints."""
    if not specs:
        return None

    # Lighting products
    if 'lumens' in specs and 'color_temp' in specs:
        if 'base_type' in specs:
            return 'light_bulb'
        return 'led_light_fixture'

    if 'lumens' in specs and 'wattage' in specs:
        return 'led_light'

    # Electrical breakers
    if 'amperage' in specs and 'voltage' in specs:
        return 'circuit_breaker'

    # Paint products
    if 'gallons' in specs:
        return 'paint_or_liquid_product'

    # Plumbing
    if 'gpm' in specs or 'flow_rate' in specs:
        return 'plumbing_fixture'

    # Check product_domains
    if 'product_domains' in specs:
        domains = specs['product_domains']
        if 'lighting' in domains:
            return 'lighting_product'
        if 'electrical' in domains and 'hvac' not in domains:
            return 'electrical_product'
        if 'plumbing' in domains:
            return 'plumbing_product'

    return None

def extract_product_type_phrases_improved(description: str) -> List[str]:
    """
    IMPROVED: Extract phrases that signal product type from description.
    More patterns and better cleaning.
    """
    if not description:
        return []

    desc_lower = description.lower()
    phrases = []

    # Pattern 1: "This [product type]" or "The [product type]"
    pattern1 = re.findall(
        r'(?:this|the|these|our)\s+([a-z\-\s]{3,40}?)(?:\s+(?:is|are|has|have|provides?|features?|offers?|comes?|includes?|delivers?))',
        desc_lower
    )
    phrases.extend(pattern1)

    # Pattern 2: Start of sentence product mentions
    pattern2 = re.findall(
        r'(?:^|\.\s+)([a-z\-\s]{3,40}?)(?:\s+(?:provides?|features?|offers?|is|are|delivers?))',
        desc_lower
    )
    phrases.extend(pattern2)

    # Pattern 3: "[Product] designed for/to"
    pattern3 = re.findall(
        r'([a-z\-\s]{3,40}?)(?:\s+designed\s+(?:for|to))',
        desc_lower
    )
    phrases.extend(pattern3)

    # Pattern 4: "Get/Enjoy/Experience [product]"
    pattern4 = re.findall(
        r'(?:get|enjoy|experience|choose|select)\s+([a-z\-\s]{3,40}?)(?:\s+(?:that|which|with))',
        desc_lower
    )
    phrases.extend(pattern4)

    # Pattern 5: Direct product mentions with article
    pattern5 = re.findall(
        r'(?:a|an)\s+([a-z\-\s]{3,40}?)(?:\s+(?:that|which|for))',
        desc_lower
    )
    phrases.extend(pattern5)

    # Clean up phrases
    stop_words = {
        'the', 'this', 'these', 'those', 'that', 'with', 'from', 'into',
        'for', 'and', 'or', 'your', 'our', 'their', 'any', 'all', 'each',
        'every', 'some', 'many', 'more', 'most', 'such', 'other', 'another'
    }

    cleaned_phrases = []
    for phrase in phrases:
        words = phrase.strip().split()
        cleaned = ' '.join([w for w in words if w not in stop_words and len(w) > 2])
        if cleaned and 3 <= len(cleaned) <= 40 and len(cleaned.split()) <= 5:
            cleaned_phrases.append(cleaned)

    return list(set(cleaned_phrases))  # Remove duplicates

def detect_category_signals(text: str) -> Dict[str, List[str]]:
    """Detect category signals from text (same as before but extracted for reuse)."""
    if not text:
        return {}

    text_lower = text.lower()

    categories = {
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

    detected = {}
    for category, keywords in categories.items():
        matches = []
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                matches.append(keyword)
        if matches:
            detected[category] = matches

    return detected

def calculate_category_confidence(category_signals: Dict[str, List[str]]) -> List[tuple]:
    """Calculate confidence scores for each category."""
    if not category_signals:
        return []

    scores = [(category, len(keywords)) for category, keywords in category_signals.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def extract_spec_fields(structured_specs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract useful specification fields."""
    if not structured_specs:
        return {}

    useful_fields = {}

    # Extract all relevant fields
    for key in ['dimensions', 'wattage', 'lumens', 'color_temp', 'base_type',
                'dimmable', 'product_domains', 'amperage', 'voltage', 'gallons',
                'gpm', 'flow_rate', 'lifespan', 'cri', 'cfm', 'btu']:
        if key in structured_specs:
            useful_fields[key] = structured_specs[key]

    return useful_fields

def analyze_single_product_improved(product: Dict[str, Any], brand_specialties: Dict[str, str]) -> Dict[str, Any]:
    """IMPROVED: Analyze a single product with all extraction methods."""
    title = product.get('title', '')
    description = product.get('description', '')
    brand = product.get('brand', '')
    specs = product.get('structured_specifications', {})

    # NEW: Extract from title first (highest confidence)
    title_type = extract_product_type_from_title(title)

    # Extract type phrases from description (improved)
    desc_phrases = extract_product_type_phrases_improved(description)

    # Detect category signals
    title_categories = detect_category_signals(title)
    desc_categories = detect_category_signals(description)

    # Combine category signals
    all_categories = {}
    for cat, keywords in title_categories.items():
        all_categories[cat] = all_categories.get(cat, []) + keywords
    for cat, keywords in desc_categories.items():
        all_categories[cat] = all_categories.get(cat, []) + keywords

    # Remove duplicates
    for cat in all_categories:
        all_categories[cat] = list(set(all_categories[cat]))

    # Calculate confidence
    confidence_scores = calculate_category_confidence(all_categories)

    # Extract useful specs
    useful_specs = extract_spec_fields(specs)

    # NEW: Extract from spec fingerprint
    spec_type = extract_from_spec_fingerprint(useful_specs)

    # NEW: Extract from brand
    brand_type = extract_product_type_from_brand(brand, brand_specialties)

    # Determine confidence level
    confidence = "unknown"
    identified_type = None

    if title_type:
        confidence = "very_high"  # Title is most reliable
        identified_type = title_type
    elif spec_type and spec_type not in ['lighting_product', 'electrical_product', 'plumbing_product']:
        # Specific spec types are reliable
        confidence = "high"
        identified_type = spec_type
    elif confidence_scores and confidence_scores[0][1] >= 5:
        # Strong category signal
        confidence = "high"
        identified_type = confidence_scores[0][0]
    elif desc_phrases:
        # Has type phrases from description
        confidence = "medium"
        identified_type = f"from_description: {desc_phrases[0]}"
    elif confidence_scores and confidence_scores[0][1] >= 3:
        # Medium category signal
        confidence = "medium"
        identified_type = confidence_scores[0][0]
    elif brand_type:
        # Brand inference
        confidence = "low"
        identified_type = brand_type
    elif confidence_scores and confidence_scores[0][1] >= 1:
        # Weak category signal
        confidence = "low"
        identified_type = confidence_scores[0][0]

    return {
        "title": title,
        "brand": brand,
        "description_word_count": len(description.split()) if description else 0,
        "has_description": bool(description and description.strip()),

        # Extraction results
        "identified_type": identified_type,
        "confidence": confidence,
        "title_type": title_type,
        "spec_type": spec_type,
        "brand_type": brand_type,
        "description_phrases": desc_phrases,

        # Category analysis
        "category_signals": all_categories,
        "top_category": confidence_scores[0] if confidence_scores else None,
        "category_confidence_scores": confidence_scores,

        # Specs
        "useful_specs": useful_specs,
        "spec_count": len(useful_specs)
    }

def analyze_all_products_improved(products: List[Dict[str, Any]], brand_specialties: Dict[str, str]) -> List[Dict[str, Any]]:
    """Analyze all products with improved extraction."""
    results = []
    for i, product in enumerate(products):
        analysis = analyze_single_product_improved(product, brand_specialties)
        analysis['product_index'] = i
        analysis['sku'] = product.get('sku', '')
        analysis['internet_sku'] = product.get('internet_sku', '')
        results.append(analysis)
    return results

def main():
    """Main execution function."""
    print("="*70)
    print("IMPROVED PRODUCT DESCRIPTION AND SPECIFICATION MINING")
    print("="*70)

    print("\nLoading product data...")
    products = load_products('data/scraped_data_output.json')
    print(f"✓ Loaded {len(products)} products")

    print("\nLoading brand specialties...")
    brand_specialties = load_brand_specialties()
    print(f"✓ Loaded {len(brand_specialties)} brand specialties")

    print("\nAnalyzing all products with improved extraction...")
    results = analyze_all_products_improved(products, brand_specialties)
    print(f"✓ Analyzed {len(results)} products")

    # Calculate success rates by confidence level
    confidence_counts = Counter([r['confidence'] for r in results])

    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)

    print(f"\n📊 Identification Confidence Distribution:")
    print(f"  • Very High Confidence: {confidence_counts['very_high']} products ({confidence_counts['very_high']/len(results)*100:.1f}%)")
    print(f"  • High Confidence:      {confidence_counts['high']} products ({confidence_counts['high']/len(results)*100:.1f}%)")
    print(f"  • Medium Confidence:    {confidence_counts['medium']} products ({confidence_counts['medium']/len(results)*100:.1f}%)")
    print(f"  • Low Confidence:       {confidence_counts['low']} products ({confidence_counts['low']/len(results)*100:.1f}%)")
    print(f"  • Unknown:              {confidence_counts['unknown']} products ({confidence_counts['unknown']/len(results)*100:.1f}%)")

    successful = confidence_counts['very_high'] + confidence_counts['high'] + confidence_counts['medium']
    print(f"\n✅ Successfully Identified: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"⚠️  Need Review: {confidence_counts['low'] + confidence_counts['unknown']} ({(confidence_counts['low'] + confidence_counts['unknown'])/len(results)*100:.1f}%)")

    # Save improved results
    print("\n" + "="*70)
    print("SAVING OUTPUTS")
    print("="*70)

    with open('outputs/extracted_signals_improved.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print("✓ Saved extracted_signals_improved.json")

    # Create comparison summary
    summary = {
        "total_products": len(products),
        "confidence_distribution": dict(confidence_counts),
        "success_rate": f"{successful/len(results)*100:.1f}%",
        "extraction_methods": {
            "from_title": sum(1 for r in results if r['title_type']),
            "from_specs": sum(1 for r in results if r['spec_type']),
            "from_brand": sum(1 for r in results if r['brand_type']),
            "from_description": sum(1 for r in results if r['description_phrases'])
        }
    }

    with open('outputs/improved_analysis_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print("✓ Saved improved_analysis_summary.json")

    # Show some examples
    print("\n" + "="*70)
    print("EXAMPLE IMPROVEMENTS")
    print("="*70)

    print("\n🎯 Very High Confidence Examples:")
    very_high = [r for r in results if r['confidence'] == 'very_high'][:5]
    for r in very_high:
        print(f"\n  • {r['title'][:70]}")
        print(f"    Type: {r['identified_type']}")
        print(f"    Extracted from: Title")

    print("\n\n" + "="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)

if __name__ == '__main__':
    main()
