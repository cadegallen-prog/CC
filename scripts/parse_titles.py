#!/usr/bin/env python3
"""
Title Intelligence and Parsing System
Analyzes product titles to extract maximum intelligence about what products are.
"""

import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import statistics

# ============================================================================
# PRODUCT TYPE KEYWORDS - Words that indicate what a product is
# ============================================================================

# These are the keywords we look for in titles to identify product types
PRODUCT_TYPE_KEYWORDS = {
    # Lighting
    'bulb': 'light bulb',
    'led': 'LED light',
    'chandelier': 'chandelier light fixture',
    'sconce': 'wall sconce light',
    'lamp': 'lamp',
    'fixture': 'light fixture',
    'lighting': 'lighting product',
    'floodlight': 'floodlight',
    'spotlight': 'spotlight',
    'lantern': 'lantern',

    # Fans
    'fan': 'fan',
    'ceiling fan': 'ceiling fan',
    'exhaust fan': 'exhaust fan',
    'ventilation': 'ventilation fan',

    # Tools
    'drill': 'power drill',
    'saw': 'saw',
    'sander': 'sander',
    'grinder': 'grinder',
    'wrench': 'wrench',
    'hammer': 'hammer',
    'screwdriver': 'screwdriver',
    'tool': 'tool',

    # Hardware
    'screw': 'screw',
    'nail': 'nail',
    'bolt': 'bolt',
    'hinge': 'hinge',
    'lock': 'lock',
    'handle': 'handle',
    'knob': 'knob',

    # Plumbing
    'faucet': 'faucet',
    'sink': 'sink',
    'toilet': 'toilet',
    'shower': 'shower fixture',
    'pipe': 'pipe',
    'valve': 'valve',
    'drain': 'drain',

    # Paint & Flooring
    'paint': 'paint',
    'stain': 'wood stain',
    'primer': 'paint primer',
    'tile': 'tile',
    'flooring': 'flooring',
    'carpet': 'carpet',
    'vinyl': 'vinyl flooring',

    # Outdoor
    'hose': 'hose',
    'sprinkler': 'sprinkler',
    'mower': 'lawn mower',
    'trimmer': 'trimmer',
    'blower': 'leaf blower',
    'fertilizer': 'fertilizer',
    'mulch': 'mulch',
    'soil': 'soil',

    # Appliances
    'heater': 'heater',
    'cooler': 'cooler',
    'dehumidifier': 'dehumidifier',
    'humidifier': 'humidifier',
    'thermostat': 'thermostat',

    # Storage
    'shelf': 'shelf',
    'cabinet': 'cabinet',
    'drawer': 'drawer',
    'storage': 'storage unit',
    'rack': 'rack',
    'bin': 'storage bin',
    'box': 'storage box',

    # Windows & Doors
    'door': 'door',
    'window': 'window',
    'blind': 'window blind',
    'shade': 'window shade',
    'curtain': 'curtain',

    # Building Materials
    'lumber': 'lumber',
    'plywood': 'plywood',
    'drywall': 'drywall',
    'insulation': 'insulation',
    'roofing': 'roofing material',
    'siding': 'siding',
}

# ============================================================================
# PATTERN DETECTION
# ============================================================================

def detect_title_pattern(title: str) -> str:
    """
    Detect the structural pattern of a product title.
    Returns a pattern name describing how the title is organized.
    """
    # Clean title for analysis
    parts = title.split()

    # Pattern 1: Brand + Number + Type (e.g., "Feit Electric 60-Watt LED Bulb")
    if len(parts) >= 3 and any(char.isdigit() for char in parts[1]):
        has_product_type = any(keyword in title.lower() for keyword in PRODUCT_TYPE_KEYWORDS.keys())
        if has_product_type:
            return "Brand-Number-Type"

    # Pattern 2: Brand + Type + Specs (e.g., "Hampton Bay Ceiling Fan 52-inch")
    if len(parts) >= 2:
        has_product_type_early = False
        for i, part in enumerate(parts[:4]):  # Check first 4 words
            if any(keyword in part.lower() for keyword in PRODUCT_TYPE_KEYWORDS.keys()):
                has_product_type_early = True
                break
        if has_product_type_early:
            return "Brand-Type-Specs"

    # Pattern 3: Brand + Model + Details (e.g., "Everbilt AB1234 Heavy Duty Hook")
    if len(parts) >= 2 and re.search(r'^[A-Z0-9]+$', parts[1]):
        return "Brand-Model-Details"

    # Pattern 4: Type-first (e.g., "LED Light Bulb 60W Soft White")
    first_words = ' '.join(parts[:3]).lower()
    if any(keyword in first_words for keyword in PRODUCT_TYPE_KEYWORDS.keys()):
        return "Type-First-Format"

    # Pattern 5: Vague (brand and model, no clear type)
    if len(parts) >= 2 and not any(keyword in title.lower() for keyword in PRODUCT_TYPE_KEYWORDS.keys()):
        return "Vague-No-Type"

    # Pattern 6: Model-heavy (lots of codes and numbers)
    if sum(1 for part in parts if any(char.isdigit() for char in part)) >= len(parts) / 2:
        return "Model-Heavy"

    return "Other"


def extract_title_components(title: str) -> Dict[str, Optional[str]]:
    """
    Extract key components from a product title.
    Returns dictionary with brand, model, size, type, and other attributes.
    """
    components = {
        'brand': None,
        'model': None,
        'size': None,
        'wattage': None,
        'color': None,
        'material': None,
        'product_type': None,
        'pack_size': None,
    }

    # Extract brand (usually first 1-2 words before numbers or specs)
    parts = title.split()
    if parts:
        # Brand is typically the first word or two
        if len(parts) >= 2 and not any(char.isdigit() for char in parts[1]):
            components['brand'] = f"{parts[0]} {parts[1]}"
        else:
            components['brand'] = parts[0]

    # Extract model number (alphanumeric codes, often at end)
    model_pattern = r'\b[A-Z0-9]{4,}(?:[/-][A-Z0-9]+)*\b'
    models = re.findall(model_pattern, title)
    if models:
        components['model'] = models[-1]  # Usually at the end

    # Extract size (measurements with units)
    size_pattern = r'\b(\d+(?:\.\d+)?)\s?(?:in|inch|inches|ft|feet|mm|cm|"|\')\b'
    sizes = re.findall(size_pattern, title, re.IGNORECASE)
    if sizes:
        components['size'] = sizes[0]

    # Extract wattage
    wattage_pattern = r'\b(\d+(?:\.\d+)?)\s?-?\s?[Ww]att\b'
    wattages = re.findall(wattage_pattern, title)
    if wattages:
        components['wattage'] = f"{wattages[0]}W"

    # Extract pack size
    pack_pattern = r'\((\d+)-[Pp]ack\)'
    packs = re.findall(pack_pattern, title)
    if packs:
        components['pack_size'] = f"{packs[0]}-pack"

    # Extract color (common color words)
    colors = ['white', 'black', 'gray', 'grey', 'brown', 'silver', 'bronze',
              'brass', 'chrome', 'nickel', 'red', 'blue', 'green']
    title_lower = title.lower()
    for color in colors:
        if color in title_lower:
            components['color'] = color.title()
            break

    # Extract product type (match against our keyword dictionary)
    for keyword, product_type in PRODUCT_TYPE_KEYWORDS.items():
        if keyword in title_lower:
            components['product_type'] = product_type
            break

    return components


def score_title_clarity(title: str, components: Dict) -> Tuple[int, str]:
    """
    Score how clear a title is for product identification (1-10 scale).
    Returns (score, reason).

    10 = Crystal clear (type, brand, key specs all present)
    5 = Moderate (some info, but vague)
    1 = Very unclear (just brand/model, no product type)
    """
    score = 5  # Start at middle
    reasons = []

    # Bonus points for having product type
    if components['product_type']:
        score += 3
        reasons.append("has product type")
    else:
        score -= 2
        reasons.append("missing product type")

    # Bonus for having brand
    if components['brand']:
        score += 1
        reasons.append("has brand")

    # Bonus for having measurements (size/wattage)
    if components['size'] or components['wattage']:
        score += 1
        reasons.append("has specifications")

    # Penalty for being too short (likely vague)
    if len(title.split()) < 4:
        score -= 1
        reasons.append("very short title")

    # Penalty for being model-heavy (hard to understand)
    if components['model'] and len(components['model']) > 10:
        score -= 1
        reasons.append("heavy on model codes")

    # Bonus for having descriptive words (not just codes)
    descriptive_words = len([w for w in title.split() if len(w) > 3 and not any(char.isdigit() for char in w)])
    if descriptive_words >= 5:
        score += 1
        reasons.append("descriptive")

    # Clamp score between 1 and 10
    score = max(1, min(10, score))

    return score, ', '.join(reasons)


def find_product_type_keywords_in_data(products: List[Dict]) -> Dict[str, int]:
    """
    Find all potential product type keywords used in the actual data.
    Returns keyword frequency.
    """
    keyword_freq = Counter()

    for product in products:
        title_lower = product['title'].lower()
        words = re.findall(r'\b[a-z]+\b', title_lower)
        keyword_freq.update(words)

    # Filter to keep only likely product type words (appear 3+ times, not common words)
    common_words = {'the', 'and', 'with', 'for', 'pack', 'set', 'new', 'in', 'inch'}
    relevant_keywords = {
        word: count for word, count in keyword_freq.items()
        if count >= 3 and word not in common_words and len(word) > 3
    }

    return relevant_keywords


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_all_titles():
    """
    Main analysis function - analyzes all product titles and generates reports.
    """
    print("Loading product data...")
    with open('data/scraped_data_output.json', 'r') as f:
        products = json.load(f)

    print(f"Analyzing {len(products)} products...\n")

    # Storage for analysis results
    pattern_counts = Counter()
    pattern_examples = defaultdict(list)
    all_components = []
    clarity_scores = []
    vague_titles = []
    keyword_usage = Counter()

    # Analyze each product
    for i, product in enumerate(products):
        title = product['title']

        # Detect pattern
        pattern = detect_title_pattern(title)
        pattern_counts[pattern] += 1
        if len(pattern_examples[pattern]) < 3:
            pattern_examples[pattern].append({
                'title': title,
                'product_id': i
            })

        # Extract components
        components = extract_title_components(title)
        components['title'] = title
        components['item_id'] = product.get('item_id', f'product_{i}')
        all_components.append(components)

        # Score clarity
        score, reason = score_title_clarity(title, components)
        clarity_scores.append({
            'item_id': product.get('item_id', f'product_{i}'),
            'title': title,
            'clarity_score': score,
            'reason': reason
        })

        # Track vague titles
        if score <= 4:
            vague_titles.append({
                'title': title,
                'score': score,
                'reason': reason,
                'components': components
            })

        # Track keyword usage
        if components['product_type']:
            keyword_usage[components['product_type']] += 1

    # Find keywords from data
    print("Extracting product type keywords from data...")
    data_keywords = find_product_type_keywords_in_data(products)

    # ========================================================================
    # GENERATE OUTPUTS
    # ========================================================================

    print("\nGenerating output files...")

    # 1. Title patterns JSON
    patterns_output = {
        'pattern_counts': dict(pattern_counts),
        'pattern_examples': {
            pattern: examples
            for pattern, examples in pattern_examples.items()
        },
        'total_products': len(products)
    }

    with open('data/title_patterns.json', 'w') as f:
        json.dump(patterns_output, f, indent=2)
    print("✓ Created data/title_patterns.json")

    # 2. Product type keywords JSON
    keywords_output = {
        'predefined_keywords': PRODUCT_TYPE_KEYWORDS,
        'keyword_usage_in_data': dict(keyword_usage.most_common(30)),
        'frequently_appearing_words': dict(sorted(data_keywords.items(), key=lambda x: x[1], reverse=True)[:50])
    }

    with open('data/product_type_keywords.json', 'w') as f:
        json.dump(keywords_output, f, indent=2)
    print("✓ Created data/product_type_keywords.json")

    # 3. Title clarity scores
    with open('outputs/title_clarity_scores.json', 'w') as f:
        json.dump(clarity_scores, f, indent=2)
    print("✓ Created outputs/title_clarity_scores.json")

    # 4. Generate markdown report
    generate_report(
        products,
        pattern_counts,
        pattern_examples,
        all_components,
        clarity_scores,
        vague_titles,
        keyword_usage,
        data_keywords
    )
    print("✓ Created reports/title_analysis.md")

    print("\n✅ Analysis complete!")
    return clarity_scores


def generate_report(products, pattern_counts, pattern_examples, all_components,
                   clarity_scores, vague_titles, keyword_usage, data_keywords):
    """
    Generate comprehensive markdown report.
    """

    with open('reports/title_analysis.md', 'w') as f:
        f.write("# Product Title Intelligence Analysis\n\n")
        f.write(f"**Analysis Date:** 2025-11-13\n")
        f.write(f"**Total Products Analyzed:** {len(products)}\n\n")
        f.write("---\n\n")

        # SECTION 1: Title Pattern Analysis
        f.write("## 1. Title Pattern Analysis\n\n")
        f.write("### Pattern Distribution\n\n")
        f.write("| Pattern Type | Count | Percentage |\n")
        f.write("|--------------|-------|------------|\n")
        total = len(products)
        for pattern, count in pattern_counts.most_common():
            pct = (count / total) * 100
            f.write(f"| {pattern} | {count} | {pct:.1f}% |\n")

        f.write("\n### Pattern Examples (15 samples)\n\n")
        for pattern, examples in pattern_examples.items():
            f.write(f"#### {pattern}\n\n")
            for ex in examples:
                f.write(f"- **Product #{ex['product_id']}:** {ex['title']}\n")
            f.write("\n")

        # SECTION 2: Component Extraction Examples
        f.write("## 2. Component Extraction Results\n\n")
        f.write("### Sample Extractions (20 random products)\n\n")

        import random
        sample_components = random.sample(all_components, min(20, len(all_components)))

        for comp in sample_components:
            f.write(f"**Title:** {comp['title']}\n\n")
            f.write(f"- **Brand:** {comp['brand'] or 'Not detected'}\n")
            f.write(f"- **Product Type:** {comp['product_type'] or 'Not detected'}\n")
            f.write(f"- **Model:** {comp['model'] or 'Not detected'}\n")
            f.write(f"- **Size:** {comp['size'] or 'Not detected'}\n")
            f.write(f"- **Wattage:** {comp['wattage'] or 'Not detected'}\n")
            f.write(f"- **Color:** {comp['color'] or 'Not detected'}\n")
            f.write(f"- **Pack Size:** {comp['pack_size'] or 'Not detected'}\n")
            f.write("\n---\n\n")

        # SECTION 3: Product Type Keywords
        f.write("## 3. Product Type Keywords Dictionary\n\n")
        f.write("### Top 20 Keywords Found in Data\n\n")
        f.write("| Keyword | Product Count | What It Means |\n")
        f.write("|---------|---------------|---------------|\n")

        for keyword, count in keyword_usage.most_common(20):
            f.write(f"| {keyword} | {count} | {keyword} |\n")

        f.write("\n### All Keywords in Dictionary\n\n")
        f.write(f"Total keywords defined: {len(PRODUCT_TYPE_KEYWORDS)}\n\n")

        # Group by category
        categories = {
            'Lighting': ['bulb', 'led', 'chandelier', 'sconce', 'lamp', 'fixture', 'lighting'],
            'Fans': ['fan', 'ceiling fan', 'exhaust fan'],
            'Tools': ['drill', 'saw', 'sander', 'grinder', 'wrench', 'hammer'],
            'Hardware': ['screw', 'nail', 'bolt', 'hinge', 'lock'],
            'Plumbing': ['faucet', 'sink', 'toilet', 'shower', 'pipe'],
            'Outdoor': ['hose', 'sprinkler', 'mower', 'trimmer', 'blower'],
        }

        for category, keywords in categories.items():
            f.write(f"**{category}:**\n")
            for kw in keywords:
                if kw in PRODUCT_TYPE_KEYWORDS:
                    f.write(f"- `{kw}` → {PRODUCT_TYPE_KEYWORDS[kw]}\n")
            f.write("\n")

        # SECTION 4: Vague Titles
        f.write("## 4. Vague Title Analysis\n\n")
        f.write("### Titles That Don't Clearly State Product Type\n\n")
        f.write(f"Found {len(vague_titles)} titles with clarity score ≤ 4/10\n\n")

        f.write("#### Top 10 Hardest Titles to Parse\n\n")
        hardest = sorted(vague_titles, key=lambda x: x['score'])[:10]
        for i, vague in enumerate(hardest, 1):
            f.write(f"**{i}. Clarity Score: {vague['score']}/10**\n\n")
            f.write(f"- **Title:** {vague['title']}\n")
            f.write(f"- **Issue:** {vague['reason']}\n")
            f.write(f"- **Detected Type:** {vague['components']['product_type'] or 'None - needs description analysis'}\n")
            f.write("\n")

        # SECTION 5: Title Clarity Distribution
        f.write("## 5. Title Clarity Distribution\n\n")

        # Count by score
        score_dist = Counter([s['clarity_score'] for s in clarity_scores])

        f.write("### Score Distribution\n\n")
        f.write("| Clarity Score | Count | Percentage |\n")
        f.write("|---------------|-------|------------|\n")
        for score in range(10, 0, -1):
            count = score_dist[score]
            pct = (count / len(clarity_scores)) * 100
            f.write(f"| {score}/10 | {count} | {pct:.1f}% |\n")

        # Summary stats
        avg_score = statistics.mean([s['clarity_score'] for s in clarity_scores])
        median_score = statistics.median([s['clarity_score'] for s in clarity_scores])

        f.write(f"\n**Average Clarity Score:** {avg_score:.1f}/10\n")
        f.write(f"**Median Clarity Score:** {median_score}/10\n\n")

        # Clear vs vague
        clear_titles = len([s for s in clarity_scores if s['clarity_score'] >= 7])
        moderate_titles = len([s for s in clarity_scores if 4 < s['clarity_score'] < 7])
        vague_titles_count = len([s for s in clarity_scores if s['clarity_score'] <= 4])

        f.write("### Summary\n\n")
        f.write(f"- **Clear titles (7-10):** {clear_titles} ({(clear_titles/len(clarity_scores)*100):.1f}%)\n")
        f.write(f"- **Moderate titles (5-6):** {moderate_titles} ({(moderate_titles/len(clarity_scores)*100):.1f}%)\n")
        f.write(f"- **Vague titles (1-4):** {vague_titles_count} ({(vague_titles_count/len(clarity_scores)*100):.1f}%)\n\n")

        # SECTION 6: Key Findings
        f.write("## 6. Key Findings & Recommendations\n\n")

        f.write("### What We Learned\n\n")
        f.write("1. **Title Clarity:** Most titles include product type information, but some are model-heavy\n")
        f.write("2. **Pattern Diversity:** Multiple title formats used across products\n")
        f.write("3. **Component Extraction:** Brand and product type are most reliably extracted\n")
        f.write("4. **Vague Titles:** Some products require description/specs analysis for identification\n\n")

        f.write("### Next Steps\n\n")
        f.write("1. For clear titles (7-10 score): Product type can be identified from title alone\n")
        f.write("2. For moderate titles (5-6): Combine title with description keywords\n")
        f.write("3. For vague titles (1-4): Must analyze full description and specifications\n")
        f.write("4. Build a multi-stage classifier that uses title clarity score to determine analysis depth\n\n")

        # SECTION 7: 20 Hardest Titles
        f.write("## 7. The 20 Hardest Titles to Parse\n\n")
        f.write("These titles require the most help from descriptions and specs:\n\n")

        hardest_20 = sorted(vague_titles, key=lambda x: x['score'])[:20]
        for i, title in enumerate(hardest_20, 1):
            f.write(f"{i}. **Score {title['score']}/10:** {title['title']}\n")

        f.write("\n---\n\n")
        f.write("*End of Report*\n")


if __name__ == '__main__':
    analyze_all_titles()
