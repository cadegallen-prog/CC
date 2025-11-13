#!/usr/bin/env python3
"""
Final boost: Add patterns for the remaining 13 identifiable products.
"""

import json

def add_final_patterns_to_title_extraction(title: str) -> str:
    """Add final extraction patterns for edge cases."""
    if not title:
        return None

    title_lower = title.lower()

    # Additional patterns for the remaining products
    final_patterns = [
        # Tools and accessories
        ('rebar cutter', 'rebar_cutter_tool'),
        ('socket set', 'socket_set'),
        ('nut driver', 'nut_driver'),
        ('driver bit', 'screw_driver_bits'),
        ('bit set', 'screw_driver_bits'),
        ('trowel', 'trowel'),
        ('finishing trowel', 'finishing_trowel'),

        # Hardware and fasteners
        ('towel bar', 'towel_bar'),
        ('fasteners', 'fasteners'),
        ('adhesive', 'adhesive'),
        ('spray adhesive', 'spray_adhesive'),

        # Tape products
        ('patch and seal', 'waterproof_tape'),
        ('waterproof tape', 'waterproof_tape'),
        ('seal tape', 'sealant_tape'),

        # Safety equipment
        ('earplugs', 'earplugs'),
        ('ear plugs', 'earplugs'),
    ]

    for pattern, product_type in final_patterns:
        if pattern in title_lower:
            return product_type

    return None

def apply_final_boost():
    """Apply final pattern matching to remaining products."""
    print("Loading improved results...")
    with open('outputs/extracted_signals_improved.json', 'r') as f:
        results = json.load(f)

    print(f"Total products: {len(results)}")

    # Find products that need help
    need_help = [r for r in results if r['confidence'] in ['low', 'unknown']]
    print(f"Products needing help: {len(need_help)}")

    # Apply final patterns
    boosted_count = 0
    for r in results:
        if r['confidence'] in ['low', 'unknown'] and r['title']:
            # Try final patterns
            final_type = add_final_patterns_to_title_extraction(r['title'])
            if final_type:
                r['identified_type'] = final_type
                r['title_type'] = final_type
                r['confidence'] = 'high'  # Specific pattern match
                boosted_count += 1
                print(f"  ✓ Boosted: {r['title'][:70]} -> {final_type}")

    print(f"\nBoosted {boosted_count} products to high confidence!")

    # Recalculate stats
    from collections import Counter
    confidence_counts = Counter([r['confidence'] for r in results])

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    print(f"\n📊 Final Confidence Distribution:")
    print(f"  • Very High Confidence: {confidence_counts['very_high']} products ({confidence_counts['very_high']/len(results)*100:.1f}%)")
    print(f"  • High Confidence:      {confidence_counts['high']} products ({confidence_counts['high']/len(results)*100:.1f}%)")
    print(f"  • Medium Confidence:    {confidence_counts['medium']} products ({confidence_counts['medium']/len(results)*100:.1f}%)")
    print(f"  • Low Confidence:       {confidence_counts['low']} products ({confidence_counts['low']/len(results)*100:.1f}%)")
    print(f"  • Unknown:              {confidence_counts['unknown']} products ({confidence_counts['unknown']/len(results)*100:.1f}%)")

    successful = confidence_counts['very_high'] + confidence_counts['high'] + confidence_counts['medium']
    total_identifiable = len([r for r in results if r['title'] and r['title'].strip()])  # Products with actual titles

    print(f"\n✅ Successfully Identified: {successful}/{len(results)} ({successful/len(results)*100:.1f}% of all)")
    print(f"✅ Success Rate (identifiable products): {successful}/{total_identifiable} ({successful/total_identifiable*100:.1f}%)")

    remaining = confidence_counts['low'] + confidence_counts['unknown']
    empty_products = len([r for r in results if not r['title'] or not r['title'].strip()])

    print(f"\n⚠️  Need Review: {remaining} products ({remaining/len(results)*100:.1f}%)")
    print(f"    • Empty/Bad Data: {empty_products} products")
    print(f"    • Genuinely Difficult: {remaining - empty_products} products")

    # Save final results
    with open('outputs/extracted_signals_final.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print("\n✓ Saved extracted_signals_final.json")

    # List remaining difficult products
    truly_difficult = [r for r in results if r['confidence'] in ['low', 'unknown'] and r['title'] and r['title'].strip()]

    if truly_difficult:
        print(f"\n" + "="*70)
        print(f"REMAINING {len(truly_difficult)} DIFFICULT PRODUCTS")
        print("="*70)
        for r in truly_difficult:
            print(f"\n  • {r['title'][:75]}")
            print(f"    Current: {r['identified_type']}")
            print(f"    Category: {r['top_category']}")

    return results

if __name__ == '__main__':
    apply_final_boost()
