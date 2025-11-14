#!/usr/bin/env python3
"""
Manually label the expanded ground truth dataset.
Goes through each product and assigns the correct product type based on title and description.
"""

import json


def manually_label_product(title: str, description: str) -> tuple:
    """
    Manually determine the true product type for a product.
    Returns (product_type, notes)
    """
    title_lower = title.lower()
    desc_lower = description.lower()

    # Missing data
    if not title or title == "":
        return 'missing_data', 'No title'

    # LIGHTING - String Lights
    if 'string light' in title_lower:
        return 'led_string_light', 'String light fixture'

    # LIGHTING - Bulbs
    if any(term in title_lower for term in ['led bulb', 'led light bulb']):
        if 'chandelier' in title_lower or 'candelabra' in title_lower:
            return 'led_light_bulb_decorative', 'Decorative LED bulb'
        return 'led_light_bulb', 'LED light bulb'
    if 'light bulb' in title_lower or ' bulb ' in title_lower:
        return 'light_bulb', 'General light bulb'

    # LIGHTING - Lamps
    if 'table lamp' in title_lower:
        return 'table_lamp', 'Table lamp'
    if 'floor lamp' in title_lower:
        return 'floor_lamp', 'Floor lamp'

    # LIGHTING - Outdoor Landscape
    if 'path light' in title_lower:
        return 'landscape_path_light', 'Outdoor path light'
    if any(term in title_lower for term in ['spotlight', 'spot light']) and 'outdoor' in title_lower:
        return 'landscape_spotlight', 'Outdoor spotlight'
    if 'landscape light' in title_lower or 'landscape flood' in title_lower:
        return 'landscape_flood_light', 'Landscape lighting'

    # LIGHTING - Fixtures
    if 'sconce' in title_lower:
        return 'wall_sconce', 'Wall sconce light fixture'
    if 'pendant' in title_lower and 'fan' not in title_lower:
        return 'pendant_light', 'Pendant light fixture'
    if 'chandelier' in title_lower and 'bulb' not in title_lower:
        return 'chandelier', 'Chandelier fixture'
    if 'flush mount' in title_lower or 'ceiling light' in title_lower:
        return 'ceiling_light_fixture', 'Ceiling mounted light'
    if 'recessed light' in title_lower or 'recessed lighting' in title_lower or 'canless' in title_lower or 'downlight' in title_lower:
        return 'recessed_light_fixture', 'Recessed lighting fixture'
    if 'track light' in title_lower or 'track lighting' in title_lower:
        return 'track_lighting_kit', 'Track lighting system'
    if 'under cabinet light' in title_lower or 'undercabinet' in title_lower:
        return 'under_cabinet_light', 'Under cabinet lighting'
    if 'troffer' in title_lower:
        return 'led_troffer_light', 'Commercial troffer light'

    # ELECTRICAL - Outlets
    if 'gfci' in title_lower and ('outlet' in title_lower or 'receptacle' in title_lower):
        return 'gfci_outlet', 'GFCI electrical outlet'
    if 'usb' in title_lower and ('outlet' in title_lower or 'receptacle' in title_lower or 'charger' in title_lower) and 'surge' not in title_lower:
        return 'usb_outlet', 'USB charging outlet'
    if ('outlet splitter' in title_lower or 'wall tap' in title_lower) and 'surge' in title_lower:
        return 'surge_protector', 'Surge protector outlet splitter'

    # ELECTRICAL - Breakers & Panels
    if 'circuit breaker' in title_lower or ('breaker' in title_lower and 'load center' not in title_lower):
        return 'circuit_breaker', 'Electrical circuit breaker'
    if 'load center' in title_lower or 'breaker panel' in title_lower or ('panel' in title_lower and 'amp' in title_lower):
        return 'electrical_load_center', 'Electrical panel/load center'

    # ELECTRICAL - Wire & Conduit
    if 'wire' in title_lower and 'by-the-foot' in title_lower:
        return 'electrical_wire', 'Electrical wire'
    if 'conduit' in title_lower and 'flexible' in title_lower:
        return 'flexible_conduit', 'Flexible electrical conduit'

    # SAFETY - Detectors
    if 'smoke' in title_lower and 'carbon monoxide' in title_lower:
        return 'smoke_co_detector_combo', 'Combination smoke and CO detector'
    if 'smoke detector' in title_lower or 'smoke alarm' in title_lower:
        return 'smoke_detector', 'Smoke detector'
    if 'carbon monoxide' in title_lower:
        return 'carbon_monoxide_detector', 'Carbon monoxide detector'

    # SAFETY - PPE
    if 'work gloves' in title_lower or 'gloves' in title_lower:
        return 'work_gloves', 'Work gloves'

    # SMART HOME & TRANSFORMERS
    if 'transformer' in title_lower and 'lighting' in title_lower:
        return 'lighting_transformer', 'Low voltage lighting transformer'

    # DOORS & LOCKS
    if 'door lock' in title_lower or 'deadbolt' in title_lower or 'keypad' in title_lower:
        if 'smart' in title_lower or 'wifi' in title_lower or 'electronic' in title_lower:
            return 'smart_door_lock', 'Electronic smart door lock'
        return 'door_lock', 'Door lock/deadbolt'
    if 'door knob' in title_lower or 'doorknob' in title_lower:
        return 'door_knob', 'Door knob'
    if 'doorbell' in title_lower:
        return 'wireless_doorbell', 'Wireless doorbell kit'
    if 'barn door' in title_lower and 'slab' in title_lower:
        return 'barn_door_slab', 'Barn door slab'
    if 'retractable screen door' in title_lower:
        return 'retractable_screen_door', 'Retractable screen door'

    # HARDWARE
    if 'framing nails' in title_lower or 'framing nail' in title_lower:
        return 'framing_nails', 'Framing nails'
    if 'screwdriving bit' in title_lower or 'driver bit' in title_lower or 'impact bit' in title_lower:
        return 'screwdriver_bits', 'Screwdriver/driver bits'
    if 'curtain rod' in title_lower:
        return 'curtain_rod', 'Curtain rod'
    if 'towel bar' in title_lower:
        return 'bathroom_towel_bar', 'Bathroom towel bar'

    # TOOLS & ACCESSORIES
    if 'nut driver' in title_lower:
        return 'nut_driver_set', 'Nut driver tool set'
    if 'multi-bit screwdriver' in title_lower:
        return 'multi_bit_screwdriver', 'Multi-bit screwdriver'
    if 'socket set' in title_lower:
        return 'socket_set', 'Socket wrench set'
    if 'saw blade' in title_lower or 'sawzall' in title_lower and 'blade' in title_lower:
        return 'saw_blade', 'Saw blade'
    if 'drill bit' in title_lower or 'coring drill' in title_lower:
        return 'drill_bit', 'Drill bit'
    if 'sanding' in title_lower and ('sheet' in title_lower or 'sandnet' in title_lower):
        return 'sandpaper_sheets', 'Sandpaper/sanding sheets'
    if 'aviation snips' in title_lower:
        return 'aviation_snips', 'Metal cutting snips'
    if 'voltage tester' in title_lower:
        return 'voltage_tester', 'Electrical voltage tester'

    # PLUMBING
    if 'water heater' in title_lower:
        return 'gas_water_heater', 'Gas water heater'
    if 'water filtration' in title_lower or 'water filter' in title_lower:
        return 'water_filtration_system', 'Water filtration system'
    if 'bathroom faucet' in title_lower or 'sink faucet' in title_lower:
        return 'bathroom_faucet', 'Bathroom faucet'
    if 'tub faucet' in title_lower or 'tub and shower' in title_lower or 'tub/shower' in title_lower:
        return 'tub_shower_faucet', 'Tub and shower faucet'
    if 'shower head' in title_lower or 'showerhead' in title_lower:
        return 'shower_head', 'Shower head'
    if 'shower pan' in title_lower or 'shower base' in title_lower:
        return 'shower_base', 'Shower pan/base'
    if 'vanity top' in title_lower:
        return 'bathroom_vanity_top', 'Bathroom vanity top'
    if 'toilet paper holder' in title_lower:
        return 'toilet_paper_holder', 'Toilet paper holder'
    if 'grab bar' in title_lower or 'assist bar' in title_lower:
        return 'bathroom_grab_bar', 'Bathroom grab bar'
    if 'riser pipe' in title_lower or 'abs' in title_lower and 'pipe' in title_lower:
        return 'drainage_pipe', 'Drainage pipe'

    # HOME PRODUCTS
    if 'water pitcher' in title_lower or 'water filter pitcher' in title_lower:
        return 'water_filter_pitcher', 'Water filter pitcher'
    if 'shop vacuum' in title_lower or 'wet dry vac' in title_lower or 'shop vac' in title_lower:
        return 'shop_vacuum', 'Shop vacuum'
    if 'vacuum attachment' in title_lower or 'extension wand' in title_lower:
        return 'vacuum_attachment', 'Vacuum attachment'
    if 'workbench' in title_lower:
        return 'workbench', 'Workbench'
    if 'trash can' in title_lower:
        return 'trash_can', 'Trash can'
    if 'bungee' in title_lower:
        return 'bungee_cord', 'Bungee cord'

    # BUILDING MATERIALS
    if 'skylight' in title_lower:
        return 'skylight', 'Skylight'
    if 'vinyl flooring' in title_lower or 'vinyl plank' in title_lower:
        return 'vinyl_plank_flooring', 'Vinyl plank flooring'
    if 'marble tile' in title_lower or 'floor and wall tile' in title_lower:
        return 'floor_wall_tile', 'Floor and wall tile'
    if 'corner bead' in title_lower:
        return 'drywall_corner_bead_tool', 'Drywall corner bead tool'
    if 'finishing trowel' in title_lower:
        return 'finishing_trowel', 'Finishing trowel'
    if 'deck railing' in title_lower:
        return 'deck_railing_connector', 'Deck railing connector'

    # TAPE & ADHESIVES
    if ('tape' in title_lower and 'velcro' not in title_lower) or 'splicing tape' in title_lower:
        return 'adhesive_tape', 'Adhesive tape'
    if 'velcro' in title_lower:
        if 'tape' in title_lower:
            return 'velcro_tape', 'Velcro fastener tape'
        return 'velcro_fasteners', 'Velcro hook and loop fasteners'

    # WINDOW TREATMENTS
    if 'faux wood blind' in title_lower:
        return 'faux_wood_blinds', 'Faux wood window blinds'
    if 'outdoor roller shade' in title_lower or 'exterior roller shade' in title_lower:
        return 'outdoor_roller_shade', 'Outdoor roller shade'
    if 'barn door' in title_lower and 'track' in title_lower:
        return 'barn_door_hardware', 'Barn door track hardware'

    # OTHER HOME ITEMS
    if 'lawn mower' in title_lower:
        return 'cordless_lawn_mower', 'Battery-powered lawn mower'
    if 'wall plate' in title_lower and 'recessed box' in title_lower:
        return 'tv_cable_box', 'TV cable management box'
    if 'area rug' in title_lower:
        return 'area_rug', 'Area rug'
    if 'screen' in title_lower and 'roll' in title_lower:
        return 'window_screen_material', 'Window screen material'
    if 'landscape fabric' in title_lower:
        return 'landscape_fabric', 'Landscape weed control fabric'
    if 'dvi cable' in title_lower or 'video cable' in title_lower:
        return 'video_cable', 'DVI video cable'

    # ELECTRICAL - Switches
    if 'switch' in title_lower and 'rocker' in title_lower:
        return 'light_switch', 'Rocker light switch'

    # If still no match
    return 'unknown', 'Unable to determine specific type'


def main():
    """Main execution - load, manually label, and save."""
    print("Loading expanded ground truth...")
    with open('/home/user/CC/data/ground_truth_expanded.json', 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data['samples'])} samples")
    print("\nManually labeling all products...")

    corrections = 0
    for sample in data['samples']:
        old_type = sample['true_product_type']
        new_type, new_notes = manually_label_product(
            sample['title'],
            sample['description']
        )

        if new_type != old_type:
            corrections += 1
            sample['true_product_type'] = new_type
            sample['notes'] = new_notes

    print(f"Made {corrections} corrections")

    # Update metadata
    data['metadata']['sampling_strategy'] = 'stratified by category with manual labeling'
    data['metadata']['labeling_method'] = 'manual review of each product'

    # Save corrected version
    with open('/home/user/CC/data/ground_truth_expanded.json', 'w') as f:
        json.dump(data, f, indent=2)

    print("✓ Saved corrected ground truth")

    # Print statistics
    from collections import Counter
    type_counts = Counter(s['true_product_type'] for s in data['samples'])
    difficulty_counts = Counter(s['difficulty'] for s in data['samples'])

    print("\nDifficulty distribution:")
    for difficulty, count in difficulty_counts.most_common():
        print(f"  {difficulty}: {count}")

    print(f"\nProduct type distribution (top 15):")
    for ptype, count in list(type_counts.most_common())[:15]:
        print(f"  {ptype}: {count}")

    print(f"\nTotal unique product types: {len(type_counts)}")
    print(f"Unknown products: {type_counts.get('unknown', 0)}")


if __name__ == '__main__':
    main()
