#!/usr/bin/env python3
"""
Fix Ground Truth Labels
Manually corrects the product type labels for each of the 50 samples
"""

import json
from pathlib import Path

def determine_correct_product_type(sample):
    """
    Manually determine the correct product type for each sample
    based on title and description
    """

    title = sample['title'].lower()
    desc = sample.get('description', '').lower()

    # Product 1: 3M Organic Vapor Replacement Cartridges
    if '3m organic vapor' in title:
        return 'safety_respirator_cartridge'

    # Product 2: HALO LED Recessed Light Kit
    if 'recessed light' in title:
        return 'recessed_light_fixture'

    # Product 3: Delta Towel Bar
    if 'towel bar' in title:
        return 'bathroom_towel_bar'

    # Product 4: Hampton Bay Bathroom Exhaust Fan
    if 'exhaust fan' in title:
        return 'bathroom_exhaust_fan'

    # Product 5: Commercial Electric Under Cabinet Light
    if 'under cabinet light' in title:
        return 'under_cabinet_light'

    # Product 6: 360 Electrical Surge Protector with USB
    if 'surge protector' in title or 'revolve' in title:
        return 'surge_protector_with_usb'

    # Product 7: HDX Air Filter
    if 'air filter' in title:
        return 'hvac_air_filter'

    # Product 8: Leviton GFCI USB Outlet
    if 'gfci' in title and 'usb' in title and 'outlet' in title:
        return 'gfci_usb_outlet'

    # Product 9: Lithonia Lighting Troffer
    if 'troffer' in title:
        return 'led_troffer_light'

    # Product 10: Andersen Window
    if 'window' in title and 'andersen' in sample.get('brand', '').lower():
        return 'double_hung_window'

    # Product 11: Malco Folding Tool
    if 'folding tool' in title:
        return 'metal_folding_tool'

    # Product 12: StyleWell Shelf Bracket
    if 'shelf bracket' in title or 'bracket' in title:
        return 'decorative_shelf_bracket'

    # Product 13: Commercial Electric Smart Flush Mount
    if 'flush mount' in title:
        return 'smart_flush_mount_light'

    # Product 14: Hampton Bay LED Landscape Flood Light
    if 'landscape' in title and 'flood' in title:
        return 'landscape_flood_light'

    # Product 15: Milwaukee Earplugs
    if 'earplug' in title:
        return 'disposable_earplugs'

    # Product 16: Werner Multi Position Ladder
    if 'ladder' in title:
        return 'multi_position_ladder'

    # Product 17: Home Decorators Collection Wall Sconce
    if 'sconce' in title:
        return 'wall_sconce'

    # Product 18: Milwaukee Work Gloves
    if 'glove' in title:
        return 'work_gloves'

    # Product 19: GE PowerMark Circuit Breaker
    if 'circuit breaker' in title:
        return 'circuit_breaker'

    # Product 20: Square D Load Center
    if 'load center' in title:
        return 'electrical_load_center'

    # Product 21: Airthings Radon Detector
    if 'radon detector' in title:
        return 'radon_detector'

    # Product 22: Coolaroo Outdoor Roller Shade
    if 'roller shade' in title:
        return 'outdoor_roller_shade'

    # Product 23: Kwikset HALO Smart Lock Deadbolt
    if 'smart lock' in title or ('kwikset' in title and 'deadbolt' in title):
        return 'smart_deadbolt_lock'

    # Product 24: Pfister Valve Stem Assembly
    if 'valve stem' in title:
        return 'faucet_valve_stem'

    # Product 25: Watts Double Check Valve
    if 'check valve' in title or 'backflow' in title:
        return 'backflow_preventer_valve'

    # Product 26: Anvil Roofing Stripper Blade
    if 'blade' in title and 'roofing' in desc:
        return 'roofing_shovel_blade'

    # Product 27: TrimMaster Stair Nosing
    if 'stair nosing' in title:
        return 'stair_nosing_trim'

    # Product 28: Home Decorators Collection Curtain Rod
    if 'curtain rod' in title:
        return 'double_curtain_rod'

    # Product 29: DIABLO Rebar Cutter
    if 'rebar cutter' in title:
        return 'sds_plus_rebar_cutter'

    # Product 30: Leviton USB Charger Outlet (3-Pack)
    if 'usb charger' in title and '3-pack' in title:
        return 'usb_outlet'

    # Product 31: Leviton USB Charger Outlet (single)
    if 'usb' in title and 'outlet' in title:
        return 'usb_outlet'

    # Product 32: TITAN Paint Sprayer
    if 'paint sprayer' in title:
        return 'hvlp_paint_sprayer'

    # Product 33: Glacier Bay Kitchen Sink with Faucet
    if 'kitchen sink' in title:
        return 'kitchen_sink_with_faucet'

    # Empty products
    if not title or len(title.strip()) == 0:
        return 'missing_data'

    # Product 37: HDX Earplugs
    if 'hdx' in sample.get('brand', '').lower() and 'earplug' in title:
        return 'disposable_earplugs'

    # Product 39: RYOBI Chainsaw Tune-Up Kit
    if 'chainsaw' in title and 'tune-up' in title:
        return 'chainsaw_tuneup_kit'

    # Product 40: Milwaukee Hex Driver Bits
    if 'driver bit' in title or 'hex' in title:
        return 'hex_driver_bits'

    # Product 41: Delta Toilet
    if 'toilet' in title:
        return 'dual_flush_toilet'

    # Product 42: Commercial Electric Speaker Wall Mounts
    if 'speaker' in title and 'mount' in title:
        return 'speaker_wall_mounts'

    # Product 43: Commercial Electric Recessed Light 4-Pack
    if 'recessed' in title and '4-pack' in title:
        return 'recessed_light_fixture'

    # Product 44: Feit Electric Under Cabinet LED Strip
    if 'strip light' in title or ('under cabinet' in title and 'tape' in desc):
        return 'led_strip_light'

    # Product 45: GE PowerMark Load Center Value Kit
    if 'load center' in title or 'circuit breaker' in desc:
        return 'circuit_breaker_kit'

    # Product 46: VELCRO Sticky Back Tape
    if 'velcro' in title or 'sticky back' in title:
        return 'velcro_fastener_tape'

    # Product 47: Hampton Bay Track Lighting Kit
    if 'track lighting' in title:
        return 'led_track_lighting_kit'

    # Product 48: Home Decorators Collection Mini Pendant
    if 'pendant' in title:
        return 'mini_pendant_light'

    # Fallback - should not reach here
    return 'unknown'

def main():
    # Load ground truth
    gt_file = Path("/home/user/CC/data/ground_truth.json")
    with open(gt_file, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)

    # Fix each sample
    fixed_count = 0
    for sample in ground_truth['samples']:
        old_type = sample['true_product_type']
        new_type = determine_correct_product_type(sample)

        if old_type != new_type:
            sample['true_product_type'] = new_type
            fixed_count += 1
            print(f"Sample {sample['sample_id']}: {old_type} → {new_type}")

    # Save fixed ground truth
    with open(gt_file, 'w', encoding='utf-8') as f:
        json.dump(ground_truth, f, indent=2)

    print(f"\n{'='*80}")
    print(f"GROUND TRUTH FIXED")
    print(f"{'='*80}")
    print(f"Fixed {fixed_count} product type labels")
    print(f"Saved to: {gt_file}")

    # Print summary
    type_dist = {}
    for sample in ground_truth['samples']:
        ptype = sample['true_product_type']
        type_dist[ptype] = type_dist.get(ptype, 0) + 1

    print(f"\nTrue Product Type Distribution:")
    for ptype, count in sorted(type_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ptype}: {count}")

if __name__ == "__main__":
    main()
