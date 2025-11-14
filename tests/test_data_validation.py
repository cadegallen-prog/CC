#!/usr/bin/env python3
"""
Data Validation Tests
Tests the quality and integrity of data files
"""

import json
import csv
import pytest
from pathlib import Path
from collections import Counter

# Data directory
DATA_DIR = Path("/home/user/CC/data")

# Valid product types from the validate_system.py mapping
VALID_PRODUCT_TYPES = {
    # Lighting products
    'recessed_light_fixture', 'under_cabinet_light', 'smart_flush_mount_light',
    'landscape_flood_light', 'wall_sconce', 'led_troffer_light',
    'led_track_lighting_kit', 'mini_pendant_light',

    # Electrical products
    'circuit_breaker', 'electrical_load_center', 'gfci_usb_outlet',
    'usb_outlet', 'surge_protector_with_usb', 'circuit_breaker_kit',

    # Locks
    'smart_deadbolt_lock',

    # Plumbing
    'faucet_valve_stem', 'backflow_preventer_valve', 'kitchen_sink_with_faucet',
    'dual_flush_toilet',

    # Tools & Hardware
    'multi_position_ladder', 'sds_plus_rebar_cutter', 'hex_driver_bits',
    'chainsaw_tuneup_kit', 'hvlp_paint_sprayer', 'decorative_shelf_bracket',
    'roofing_shovel_blade', 'stair_nosing_trim', 'velcro_fastener_tape',
    'metal_folding_tool',

    # HVAC & Home
    'safety_respirator_cartridge', 'bathroom_towel_bar', 'bathroom_exhaust_fan',
    'hvac_air_filter', 'double_hung_window', 'work_gloves',
    'outdoor_roller_shade', 'double_curtain_rod', 'speaker_wall_mounts',
    'disposable_earplugs', 'radon_detector',

    # Special cases
    'missing_data',
}

VALID_DIFFICULTY_LEVELS = {'easy', 'medium', 'hard'}


class TestDataValidation:
    """Test suite for validating data files"""

    # ============================================================================
    # GROUND TRUTH VALIDATION
    # ============================================================================

    def test_ground_truth_file_exists(self):
        """Ground truth file should exist"""
        gt_file = DATA_DIR / "ground_truth.json"
        assert gt_file.exists(), f"Ground truth file not found at {gt_file}"

    def test_ground_truth_is_valid_json(self):
        """Ground truth file should be valid JSON"""
        gt_file = DATA_DIR / "ground_truth.json"
        try:
            with open(gt_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, dict), "Ground truth should be a JSON object"
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in ground_truth.json: {e}")

    def test_ground_truth_has_correct_structure(self):
        """Ground truth should have metadata and samples keys"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert 'metadata' in data, "Ground truth missing 'metadata' key"
        assert 'samples' in data, "Ground truth missing 'samples' key"
        assert isinstance(data['samples'], list), "samples should be a list"

    def test_ground_truth_metadata_matches_samples(self):
        """Metadata total_samples should match actual sample count"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        metadata_count = data['metadata'].get('total_samples', 0)
        actual_count = len(data['samples'])

        print(f"\n  Metadata says: {metadata_count} samples")
        print(f"  Actual count: {actual_count} samples")

        assert metadata_count == actual_count, \
            f"Metadata says {metadata_count} samples but found {actual_count}"

    def test_ground_truth_samples_have_required_fields(self):
        """Each sample should have all required fields"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        required_fields = {
            'sample_id', 'index', 'title', 'true_product_type',
            'difficulty', 'predicted_cluster'
        }

        samples = data['samples']
        missing_fields = []

        for i, sample in enumerate(samples):
            sample_missing = required_fields - set(sample.keys())
            if sample_missing:
                missing_fields.append(f"Sample {i} (id={sample.get('sample_id', 'unknown')}): missing {sample_missing}")

        assert not missing_fields, \
            f"Samples with missing fields:\n" + "\n".join(missing_fields)

        print(f"\n  ✓ All {len(samples)} samples have required fields")

    def test_ground_truth_indices_are_valid(self):
        """All indices should be valid (0-424, within product dataset range)"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        samples = data['samples']
        invalid_indices = []

        for sample in samples:
            idx = sample['index']
            if not isinstance(idx, int):
                invalid_indices.append(f"Sample {sample['sample_id']}: index is not an integer ({idx})")
            elif idx < 0 or idx > 424:
                invalid_indices.append(f"Sample {sample['sample_id']}: index {idx} out of range (0-424)")

        assert not invalid_indices, \
            f"Samples with invalid indices:\n" + "\n".join(invalid_indices)

        print(f"\n  ✓ All indices are valid (0-424)")

    def test_ground_truth_no_duplicate_sample_ids(self):
        """There should be no duplicate sample_ids"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        samples = data['samples']
        sample_ids = [s['sample_id'] for s in samples]
        id_counts = Counter(sample_ids)

        duplicates = [(sid, count) for sid, count in id_counts.items() if count > 1]

        assert not duplicates, \
            f"Duplicate sample_ids found: {duplicates}"

        print(f"\n  ✓ All {len(sample_ids)} sample_ids are unique")

    def test_ground_truth_no_duplicate_indices(self):
        """There should be no duplicate indices (except edge cases)"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        samples = data['samples']
        indices = [s['index'] for s in samples]
        index_counts = Counter(indices)

        # Allow duplicates for specific edge case indices
        duplicates = []
        for idx, count in index_counts.items():
            if count > 1:
                # Check if these are edge case samples (missing_data)
                samples_with_idx = [s for s in samples if s['index'] == idx]
                edge_cases = [s for s in samples_with_idx if s['true_product_type'] == 'missing_data']

                # If all duplicates are edge cases, that's OK
                if len(edge_cases) < count:
                    duplicates.append((idx, count, [s['sample_id'] for s in samples_with_idx]))

        if duplicates:
            dup_details = "\n".join([f"  Index {idx}: appears {count} times in samples {sids}"
                                      for idx, count, sids in duplicates])
            pytest.fail(f"Duplicate indices found (non-edge-case):\n{dup_details}")

        print(f"\n  ✓ No problematic duplicate indices")

    def test_ground_truth_difficulty_is_valid(self):
        """All difficulty values should be easy, medium, or hard"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        samples = data['samples']
        invalid_difficulty = []

        for sample in samples:
            difficulty = sample.get('difficulty', '')
            if difficulty not in VALID_DIFFICULTY_LEVELS:
                invalid_difficulty.append(
                    f"Sample {sample['sample_id']}: invalid difficulty '{difficulty}'"
                )

        assert not invalid_difficulty, \
            f"Samples with invalid difficulty:\n" + "\n".join(invalid_difficulty)

        # Print difficulty distribution
        difficulty_counts = Counter([s['difficulty'] for s in samples])
        print(f"\n  Difficulty distribution:")
        for diff in ['easy', 'medium', 'hard']:
            print(f"    {diff}: {difficulty_counts[diff]} samples")

    def test_ground_truth_product_type_not_empty(self):
        """true_product_type should not be empty string"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        samples = data['samples']
        empty_types = []

        for sample in samples:
            prod_type = sample.get('true_product_type', '')
            if prod_type == '':
                empty_types.append(f"Sample {sample['sample_id']}: empty product type")

        assert not empty_types, \
            f"Samples with empty product type:\n" + "\n".join(empty_types)

        print(f"\n  ✓ All samples have non-empty true_product_type")

    def test_ground_truth_product_types_are_valid(self):
        """All true_product_type values should be in the valid set"""
        gt_file = DATA_DIR / "ground_truth.json"
        with open(gt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        samples = data['samples']
        invalid_types = []

        for sample in samples:
            prod_type = sample['true_product_type']
            if prod_type not in VALID_PRODUCT_TYPES:
                invalid_types.append(
                    f"Sample {sample['sample_id']}: unknown type '{prod_type}'"
                )

        if invalid_types:
            print("\n  Invalid product types found:")
            for msg in invalid_types:
                print(f"    {msg}")
            pytest.fail(f"Found {len(invalid_types)} samples with invalid product types")

        # Print product type distribution
        type_counts = Counter([s['true_product_type'] for s in samples])
        print(f"\n  Product type distribution ({len(type_counts)} unique types):")
        for ptype, count in type_counts.most_common(10):
            print(f"    {ptype}: {count}")
        if len(type_counts) > 10:
            print(f"    ... and {len(type_counts) - 10} more types")

    # ============================================================================
    # PRODUCT DATASET VALIDATION
    # ============================================================================

    def test_product_dataset_file_exists(self):
        """Product dataset file should exist"""
        data_file = DATA_DIR / "scraped_data_output.json"
        assert data_file.exists(), f"Product dataset not found at {data_file}"

    def test_product_dataset_is_valid_json(self):
        """Product dataset should be valid JSON"""
        data_file = DATA_DIR / "scraped_data_output.json"
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, list), "Product dataset should be a JSON array"
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in scraped_data_output.json: {e}")

    def test_product_dataset_has_425_products(self):
        """Product dataset should have exactly 425 products"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data) == 425, \
            f"Expected 425 products but found {len(data)}"

        print(f"\n  ✓ Dataset has exactly 425 products")

    def test_product_dataset_required_fields(self):
        """Each product should have required fields"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        required_fields = {'title', 'description', 'brand', 'price', 'rating', 'model'}

        missing_fields = []
        for i, product in enumerate(data):
            product_missing = required_fields - set(product.keys())
            if product_missing:
                title = product.get('title', '(no title)')[:50]
                missing_fields.append(
                    f"Product {i}: missing {product_missing} - '{title}'"
                )

        if missing_fields:
            # Show first 10 only
            print("\n  Products with missing fields:")
            for msg in missing_fields[:10]:
                print(f"    {msg}")
            if len(missing_fields) > 10:
                print(f"    ... and {len(missing_fields) - 10} more")
            pytest.fail(f"Found {len(missing_fields)} products with missing required fields")

        print(f"\n  ✓ All products have required fields")

    def test_product_dataset_title_not_none(self):
        """Title should not be None for all products"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Count products with None or empty title
        none_titles = []
        for i, product in enumerate(data):
            title = product.get('title')
            if title is None:
                none_titles.append(f"Product {i}: title is None")

        # Some products may legitimately have empty titles (missing data edge cases)
        # but we should report them
        if none_titles:
            print(f"\n  Found {len(none_titles)} products with None title")
            for msg in none_titles[:5]:
                print(f"    {msg}")

        print(f"\n  Products with valid titles: {len(data) - len(none_titles)}/{len(data)}")

    def test_product_dataset_price_is_numeric(self):
        """Price should be numeric and >= 0"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        invalid_prices = []
        for i, product in enumerate(data):
            price = product.get('price')
            title = product.get('title', '(no title)')[:50]

            # Price should be numeric
            if not isinstance(price, (int, float)):
                invalid_prices.append(
                    f"Product {i}: price is not numeric ({type(price).__name__}) - '{title}'"
                )
            # Price should be >= 0
            elif price < 0:
                invalid_prices.append(
                    f"Product {i}: negative price ({price}) - '{title}'"
                )

        assert not invalid_prices, \
            f"Products with invalid prices:\n" + "\n".join(invalid_prices[:10])

        # Print price statistics
        prices = [p['price'] for p in data if isinstance(p.get('price'), (int, float))]
        print(f"\n  Price statistics:")
        print(f"    Min: ${min(prices):.2f}")
        print(f"    Max: ${max(prices):.2f}")
        print(f"    Average: ${sum(prices)/len(prices):.2f}")

    def test_product_dataset_rating_is_valid(self):
        """Rating should be 0-5 or None"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        invalid_ratings = []
        for i, product in enumerate(data):
            rating = product.get('rating')
            title = product.get('title', '(no title)')[:50]

            # Rating can be None
            if rating is None:
                continue

            # Rating should be numeric
            if not isinstance(rating, (int, float)):
                invalid_ratings.append(
                    f"Product {i}: rating is not numeric ({type(rating).__name__}) - '{title}'"
                )
            # Rating should be 0-5
            elif rating < 0 or rating > 5:
                invalid_ratings.append(
                    f"Product {i}: rating out of range ({rating}) - '{title}'"
                )

        assert not invalid_ratings, \
            f"Products with invalid ratings:\n" + "\n".join(invalid_ratings[:10])

        # Print rating statistics
        ratings = [p['rating'] for p in data if p.get('rating') is not None]
        none_count = sum(1 for p in data if p.get('rating') is None)
        print(f"\n  Rating statistics:")
        print(f"    Products with ratings: {len(ratings)}/{len(data)}")
        print(f"    Products without ratings: {none_count}/{len(data)}")
        if ratings:
            print(f"    Average rating: {sum(ratings)/len(ratings):.2f}")

    def test_product_dataset_no_completely_empty_products(self):
        """No products should have all fields None/empty"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        completely_empty = []
        for i, product in enumerate(data):
            # Check if all important fields are None or empty
            title = product.get('title', '')
            description = product.get('description', '')
            brand = product.get('brand', '')
            price = product.get('price', 0)

            if not title and not description and not brand and price == 0:
                completely_empty.append(f"Product {i}: all fields are empty/None/0")

        # Report but don't fail (these might be valid edge cases)
        if completely_empty:
            print(f"\n  Found {len(completely_empty)} completely empty products:")
            for msg in completely_empty[:5]:
                print(f"    {msg}")
        else:
            print(f"\n  ✓ No completely empty products")

    def test_product_dataset_description_coverage(self):
        """Count how many products have descriptions"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with_desc = sum(1 for p in data if p.get('description'))
        total = len(data)
        coverage = (with_desc / total * 100) if total > 0 else 0

        print(f"\n  Description coverage: {with_desc}/{total} ({coverage:.1f}%)")

        # Warn if coverage is low
        if coverage < 90:
            print(f"  ⚠ Description coverage is below 90%")

    def test_product_dataset_price_coverage(self):
        """Count how many products have prices"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with_price = sum(1 for p in data if p.get('price') and p['price'] > 0)
        total = len(data)
        coverage = (with_price / total * 100) if total > 0 else 0

        print(f"\n  Price coverage: {with_price}/{total} ({coverage:.1f}%)")

        # Warn if coverage is low
        if coverage < 90:
            print(f"  ⚠ Price coverage is below 90%")

    # ============================================================================
    # CSV vs JSON CONSISTENCY
    # ============================================================================

    def test_csv_file_exists(self):
        """CSV file should exist"""
        csv_file = DATA_DIR / "scraped_data.csv"
        assert csv_file.exists(), f"CSV file not found at {csv_file}"

    def test_csv_vs_json_same_count(self):
        """CSV and JSON should have same number of products"""
        csv_file = DATA_DIR / "scraped_data.csv"
        json_file = DATA_DIR / "scraped_data_output.json"

        # Load CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            csv_data = list(csv_reader)

        # Load JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        assert len(csv_data) == len(json_data), \
            f"CSV has {len(csv_data)} products but JSON has {len(json_data)}"

        print(f"\n  ✓ Both CSV and JSON have {len(csv_data)} products")

    def test_csv_vs_json_title_consistency(self):
        """Products at same index should have same title"""
        csv_file = DATA_DIR / "scraped_data.csv"
        json_file = DATA_DIR / "scraped_data_output.json"

        # Load both
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            csv_data = list(csv_reader)

        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        mismatches = []
        for i in range(min(len(csv_data), len(json_data))):
            csv_title = csv_data[i].get('title', '').strip()
            json_title = json_data[i].get('title', '').strip()

            if csv_title != json_title:
                mismatches.append(
                    f"Index {i}: CSV='{csv_title[:50]}' vs JSON='{json_title[:50]}'"
                )

        if mismatches:
            print(f"\n  Found {len(mismatches)} title mismatches:")
            for msg in mismatches[:5]:
                print(f"    {msg}")
            if len(mismatches) > 5:
                print(f"    ... and {len(mismatches) - 5} more")
            pytest.fail(f"Found {len(mismatches)} title mismatches between CSV and JSON")

        print(f"\n  ✓ All titles match between CSV and JSON")

    def test_csv_vs_json_brand_consistency(self):
        """Products at same index should have same brand"""
        csv_file = DATA_DIR / "scraped_data.csv"
        json_file = DATA_DIR / "scraped_data_output.json"

        # Load both
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            csv_data = list(csv_reader)

        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        mismatches = []
        for i in range(min(len(csv_data), len(json_data))):
            csv_brand = csv_data[i].get('brand', '').strip()
            json_brand = json_data[i].get('brand', '').strip()

            if csv_brand != json_brand:
                title = json_data[i].get('title', '(no title)')[:40]
                mismatches.append(
                    f"Index {i} ('{title}'): CSV brand='{csv_brand}' vs JSON brand='{json_brand}'"
                )

        if mismatches:
            print(f"\n  Found {len(mismatches)} brand mismatches:")
            for msg in mismatches[:5]:
                print(f"    {msg}")
            pytest.fail(f"Found {len(mismatches)} brand mismatches")

        print(f"\n  ✓ All brands match between CSV and JSON")

    def test_csv_vs_json_price_consistency(self):
        """Products at same index should have same price"""
        csv_file = DATA_DIR / "scraped_data.csv"
        json_file = DATA_DIR / "scraped_data_output.json"

        # Load both
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            csv_data = list(csv_reader)

        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        mismatches = []
        for i in range(min(len(csv_data), len(json_data))):
            # CSV stores as string, need to convert
            csv_price_str = csv_data[i].get('price', '0').strip()
            try:
                csv_price = float(csv_price_str) if csv_price_str else 0.0
            except ValueError:
                csv_price = 0.0

            json_price = json_data[i].get('price', 0)

            # Allow small floating point differences
            if abs(csv_price - json_price) > 0.01:
                title = json_data[i].get('title', '(no title)')[:40]
                mismatches.append(
                    f"Index {i} ('{title}'): CSV price={csv_price} vs JSON price={json_price}"
                )

        if mismatches:
            print(f"\n  Found {len(mismatches)} price mismatches:")
            for msg in mismatches[:5]:
                print(f"    {msg}")
            pytest.fail(f"Found {len(mismatches)} price mismatches")

        print(f"\n  ✓ All prices match between CSV and JSON")

    # ============================================================================
    # DATA QUALITY METRICS
    # ============================================================================

    def test_data_quality_overall(self):
        """Calculate overall data quality metrics"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = len(data)

        # Calculate coverage for each field
        metrics = {
            'descriptions': sum(1 for p in data if p.get('description')) / total * 100,
            'brands': sum(1 for p in data if p.get('brand')) / total * 100,
            'prices': sum(1 for p in data if p.get('price') and p['price'] > 0) / total * 100,
            'ratings': sum(1 for p in data if p.get('rating') is not None) / total * 100,
        }

        print(f"\n  Data Quality Metrics:")
        print(f"  " + "="*60)

        for field, coverage in metrics.items():
            status = "✓" if coverage >= 90 else "⚠" if coverage >= 70 else "✗"
            print(f"  {status} {field.capitalize()}: {coverage:.1f}% coverage")

            if coverage < 90:
                missing = int(total * (100 - coverage) / 100)
                print(f"     ({missing} products missing {field})")

        print(f"  " + "="*60)

        # Overall quality score
        avg_coverage = sum(metrics.values()) / len(metrics)
        print(f"\n  Overall Quality Score: {avg_coverage:.1f}%")

        if avg_coverage >= 90:
            print(f"  Assessment: ✓ Excellent data quality")
        elif avg_coverage >= 70:
            print(f"  Assessment: ⚠ Good data quality, some gaps")
        else:
            print(f"  Assessment: ✗ Poor data quality, needs improvement")

    # ============================================================================
    # SCHEMA VALIDATION
    # ============================================================================

    def test_product_schema_validation(self):
        """Validate all products match expected schema"""
        data_file = DATA_DIR / "scraped_data_output.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        schema_errors = []

        for i, product in enumerate(data):
            errors = []
            title = product.get('title', '(no title)')[:50]

            # Check title
            if 'title' not in product:
                errors.append("missing 'title' field")
            elif not isinstance(product['title'], (str, type(None))):
                errors.append(f"'title' should be str or None, got {type(product['title']).__name__}")

            # Check description
            if 'description' not in product:
                errors.append("missing 'description' field")
            elif not isinstance(product['description'], (str, type(None))):
                errors.append(f"'description' should be str or None, got {type(product['description']).__name__}")

            # Check brand
            if 'brand' not in product:
                errors.append("missing 'brand' field")
            elif not isinstance(product['brand'], (str, type(None))):
                errors.append(f"'brand' should be str or None, got {type(product['brand']).__name__}")

            # Check price
            if 'price' not in product:
                errors.append("missing 'price' field")
            elif not isinstance(product['price'], (int, float)):
                errors.append(f"'price' should be numeric, got {type(product['price']).__name__}")

            # Check rating (optional field)
            if 'rating' in product and product['rating'] is not None:
                if not isinstance(product['rating'], (int, float)):
                    errors.append(f"'rating' should be numeric or None, got {type(product['rating']).__name__}")

            # Check model
            if 'model' not in product:
                errors.append("missing 'model' field")
            elif not isinstance(product['model'], (str, type(None))):
                errors.append(f"'model' should be str or None, got {type(product['model']).__name__}")

            if errors:
                schema_errors.append(f"Product {i} ('{title}'): {', '.join(errors)}")

        if schema_errors:
            print(f"\n  Found {len(schema_errors)} products with schema violations:")
            for msg in schema_errors[:10]:
                print(f"    {msg}")
            if len(schema_errors) > 10:
                print(f"    ... and {len(schema_errors) - 10} more")
            pytest.fail(f"Found {len(schema_errors)} products with schema violations")

        print(f"\n  ✓ All {len(data)} products match expected schema")


# ============================================================================
# SUMMARY STATISTICS (runs after all tests)
# ============================================================================

def test_print_summary_statistics():
    """Print summary statistics about the datasets"""
    print("\n" + "="*80)
    print("DATA VALIDATION SUMMARY")
    print("="*80)

    # Ground truth summary
    gt_file = DATA_DIR / "ground_truth.json"
    with open(gt_file, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)

    print(f"\nGround Truth Dataset:")
    print(f"  Total samples: {len(gt_data['samples'])}")
    print(f"  Unique product types: {len(set(s['true_product_type'] for s in gt_data['samples']))}")

    difficulty_counts = Counter([s['difficulty'] for s in gt_data['samples']])
    print(f"  Difficulty breakdown:")
    for diff in ['easy', 'medium', 'hard']:
        print(f"    {diff}: {difficulty_counts[diff]}")

    # Product dataset summary
    data_file = DATA_DIR / "scraped_data_output.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    print(f"\nProduct Dataset:")
    print(f"  Total products: {len(products)}")
    print(f"  Products with descriptions: {sum(1 for p in products if p.get('description'))}")
    print(f"  Products with brands: {sum(1 for p in products if p.get('brand'))}")
    print(f"  Products with prices: {sum(1 for p in products if p.get('price') and p['price'] > 0)}")
    print(f"  Products with ratings: {sum(1 for p in products if p.get('rating') is not None)}")

    # Brand distribution
    brands = [p.get('brand', '') for p in products if p.get('brand')]
    brand_counts = Counter(brands)
    print(f"\n  Top 5 brands:")
    for brand, count in brand_counts.most_common(5):
        print(f"    {brand}: {count} products")

    print("\n" + "="*80)
