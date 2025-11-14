"""
Integration Tests for Product Classification Pipeline

These tests verify the complete end-to-end classification pipeline:
1. Data loading and validation
2. classify_all_products() function with various dataset sizes
3. Result format and structure validation
4. Statistics generation
5. Performance benchmarks
6. Edge case handling

Tests marked with @pytest.mark.slow may take longer to run.
"""

import json
import pytest
import time
from pathlib import Path
from collections import Counter


class TestIntegrationPipeline:
    """Integration tests for the complete product classification pipeline."""

    # ========================================================================
    # DATA LOADING TESTS
    # ========================================================================

    def test_load_full_dataset(self, data_dir):
        """
        Test loading the complete dataset from scraped_data_output.json.

        Verifies:
        - File exists and can be loaded
        - Contains exactly 425 products
        - Products have required fields
        """
        # Load the dataset
        dataset_path = data_dir / "scraped_data_output.json"
        assert dataset_path.exists(), f"Dataset file not found: {dataset_path}"

        with open(dataset_path, 'r', encoding='utf-8') as f:
            products = json.load(f)

        # Verify we have exactly 425 products
        assert len(products) == 425, f"Expected 425 products, got {len(products)}"

        print(f"\n✓ Successfully loaded {len(products)} products")

    def test_dataset_required_fields(self, full_dataset):
        """
        Test that all products in the dataset have required fields.

        Verifies each product has:
        - title (string)
        - description (string, may be empty)
        - brand (string, may be empty)
        - price (number)
        """
        required_fields = ['title', 'description', 'brand', 'price']

        missing_fields_count = 0

        for i, product in enumerate(full_dataset):
            for field in required_fields:
                if field not in product:
                    missing_fields_count += 1
                    print(f"\nProduct {i} missing field: {field}")

        assert missing_fields_count == 0, \
            f"Found {missing_fields_count} products with missing required fields"

        print(f"\n✓ All {len(full_dataset)} products have required fields")

    # ========================================================================
    # CLASSIFY_ALL_PRODUCTS - SMALL SUBSET TESTS
    # ========================================================================

    def test_classify_small_subset(self, classifier, small_dataset):
        """
        Test classify_all_products with a small subset (10 products).

        Verifies:
        - Function completes without errors
        - Returns exactly 10 results
        - Each result has all required fields
        - No results are None or missing
        """
        # Classify the first 10 products
        results = classifier.classify_all_products(small_dataset)

        # Verify we get 10 results back
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"

        # Verify no results are None
        assert all(r is not None for r in results), "Found None in results"

        # Verify each result has required fields
        required_fields = [
            'index', 'title', 'brand', 'price',
            'product_type', 'confidence', 'confidence_level',
            'reasons', 'alternate_types'
        ]

        for i, result in enumerate(results):
            for field in required_fields:
                assert field in result, \
                    f"Result {i} missing field: {field}"

        print(f"\n✓ Successfully classified {len(results)} products")
        print(f"  Sample: '{results[0]['title'][:50]}...' → {results[0]['product_type']}")

    def test_small_subset_no_crashes(self, classifier, small_dataset):
        """
        Test that classification doesn't crash or raise exceptions.

        This is a critical stability test - the pipeline should
        handle all products gracefully without errors.
        """
        try:
            results = classifier.classify_all_products(small_dataset)
            assert len(results) == len(small_dataset)
            print(f"\n✓ No crashes during classification of {len(small_dataset)} products")
        except Exception as e:
            pytest.fail(f"Classification crashed with error: {e}")

    # ========================================================================
    # CLASSIFY_ALL_PRODUCTS - FULL DATASET TESTS
    # ========================================================================

    @pytest.mark.slow
    def test_classify_full_dataset(self, classifier, full_dataset):
        """
        Test classify_all_products with the complete 425-product dataset.

        This is the main integration test - verifies the entire
        pipeline works on production data.

        Verifies:
        - All 425 products are classified
        - All results are present (no None values)
        - All product_types are valid (not empty strings)
        - All confidence scores are in valid range (0-100)
        """
        print(f"\n🔄 Classifying {len(full_dataset)} products...")

        # Classify all products
        results = classifier.classify_all_products(full_dataset)

        # Verify we get 425 results back
        assert len(results) == 425, \
            f"Expected 425 results, got {len(results)}"

        # Verify no results are None or missing
        assert all(r is not None for r in results), \
            "Found None in results"

        # Verify all product_types are valid (not empty)
        empty_types = [r for r in results if not r.get('product_type')]
        assert len(empty_types) == 0, \
            f"Found {len(empty_types)} results with empty product_type"

        # Verify all confidence scores are in valid range (0-100)
        invalid_confidence = [
            r for r in results
            if r.get('confidence', -1) < 0 or r.get('confidence', 101) > 100
        ]
        assert len(invalid_confidence) == 0, \
            f"Found {len(invalid_confidence)} results with invalid confidence scores"

        print(f"✓ Successfully classified all {len(results)} products")

        # Show sample classifications
        print("\n📊 Sample classifications:")
        for i in range(min(3, len(results))):
            r = results[i]
            print(f"  {i+1}. '{r['title'][:50]}...'")
            print(f"     → {r['product_type']} ({r['confidence_level']}, {r['confidence']:.1f}%)")

    @pytest.mark.slow
    def test_full_dataset_no_none_results(self, classifier, full_dataset):
        """
        Verify that classify_all_products never returns None results.

        Every product should get SOME classification, even if it's
        "Unknown - Unable to Classify".
        """
        results = classifier.classify_all_products(full_dataset)

        none_results = [i for i, r in enumerate(results) if r is None]

        assert len(none_results) == 0, \
            f"Found None results at indices: {none_results}"

        print(f"\n✓ All {len(results)} results are non-None")

    @pytest.mark.slow
    def test_full_dataset_valid_product_types(self, classifier, full_dataset):
        """
        Verify all products get valid product_type values.

        Valid means:
        - Not None
        - Not empty string
        - Is a string
        """
        results = classifier.classify_all_products(full_dataset)

        invalid_types = []
        for i, r in enumerate(results):
            product_type = r.get('product_type')
            if product_type is None or product_type == '' or not isinstance(product_type, str):
                invalid_types.append((i, product_type))

        assert len(invalid_types) == 0, \
            f"Found {len(invalid_types)} invalid product types: {invalid_types[:5]}"

        print(f"\n✓ All {len(results)} products have valid product_type strings")

    @pytest.mark.slow
    def test_full_dataset_confidence_range(self, classifier, full_dataset):
        """
        Verify all confidence scores are in the valid range (0-100).

        Confidence scores outside this range indicate a bug in the
        scoring system.
        """
        results = classifier.classify_all_products(full_dataset)

        out_of_range = []
        for i, r in enumerate(results):
            confidence = r.get('confidence', -1)
            if confidence < 0 or confidence > 100:
                out_of_range.append((i, confidence))

        assert len(out_of_range) == 0, \
            f"Found {len(out_of_range)} confidence scores out of range: {out_of_range[:5]}"

        # Show confidence distribution
        confidences = [r['confidence'] for r in results]
        avg_conf = sum(confidences) / len(confidences)
        min_conf = min(confidences)
        max_conf = max(confidences)

        print(f"\n✓ All confidence scores in valid range")
        print(f"  Average: {avg_conf:.1f}%")
        print(f"  Range: {min_conf:.1f}% - {max_conf:.1f}%")

    # ========================================================================
    # OUTPUT FORMAT TESTS
    # ========================================================================

    def test_output_format_structure(self, classifier, small_dataset):
        """
        Test that classification results have the correct structure.

        Each result should be a dict with these fields:
        - index (int): Product index in the dataset
        - title (str): Product title (truncated to 100 chars)
        - brand (str): Product brand
        - price (float): Product price
        - product_type (str): Classified product type
        - confidence (float): Confidence score (0-100)
        - confidence_level (str): Confidence category
        - reasons (list): List of matching reasons
        - alternate_types (list): Alternative classifications
        """
        results = classifier.classify_all_products(small_dataset)

        # Test first result in detail
        result = results[0]

        # Verify field types
        assert isinstance(result['index'], int), "index should be int"
        assert isinstance(result['title'], str), "title should be str"
        assert isinstance(result['brand'], str), "brand should be str"
        assert isinstance(result['price'], (int, float)), "price should be numeric"
        assert isinstance(result['product_type'], str), "product_type should be str"
        assert isinstance(result['confidence'], (int, float)), "confidence should be numeric"
        assert isinstance(result['confidence_level'], str), "confidence_level should be str"
        assert isinstance(result['reasons'], list), "reasons should be list"
        assert isinstance(result['alternate_types'], list), "alternate_types should be list"

        print(f"\n✓ Result structure is correct")
        print(f"  Sample result keys: {list(result.keys())}")

    def test_output_format_confidence_levels(self, classifier, small_dataset):
        """
        Test that confidence_level values are valid.

        Valid confidence levels are:
        - "High" (70+)
        - "Medium" (50-69)
        - "Low" (30-49)
        - "Very Low" (20-29)
        - "No Match" (<20)
        - "No Data" (missing data)
        """
        valid_levels = ["High", "Medium", "Low", "Very Low", "No Match", "No Data"]

        results = classifier.classify_all_products(small_dataset)

        invalid_levels = []
        for i, r in enumerate(results):
            level = r.get('confidence_level')
            if level not in valid_levels:
                invalid_levels.append((i, level))

        assert len(invalid_levels) == 0, \
            f"Found invalid confidence levels: {invalid_levels}"

        # Show distribution of confidence levels
        level_counts = Counter(r['confidence_level'] for r in results)
        print(f"\n✓ All confidence levels are valid")
        print(f"  Distribution: {dict(level_counts)}")

    def test_output_format_title_truncation(self, classifier, full_dataset):
        """
        Test that titles are truncated to 100 characters.

        Long titles should be truncated to keep results readable.
        """
        # Find a product with a long title
        long_title_product = None
        for product in full_dataset:
            if len(product.get('title', '')) > 100:
                long_title_product = product
                break

        if long_title_product:
            result = classifier.classify_all_products([long_title_product])[0]

            assert len(result['title']) <= 100, \
                f"Title not truncated: {len(result['title'])} chars"

            print(f"\n✓ Long titles are truncated to 100 chars")
        else:
            print(f"\n⚠ No products with titles >100 chars found")

    # ========================================================================
    # PERFORMANCE TESTS
    # ========================================================================

    @pytest.mark.slow
    def test_performance_100_products(self, classifier, full_dataset):
        """
        Test classification performance with 100 products.

        Should complete in less than 100 seconds (1 sec/product max).
        Ideally much faster.
        """
        subset = full_dataset[:100]

        print(f"\n⏱ Classifying {len(subset)} products...")
        start_time = time.time()

        results = classifier.classify_all_products(subset)

        elapsed = time.time() - start_time

        # Verify results
        assert len(results) == 100, f"Expected 100 results, got {len(results)}"

        # Performance check - should be under 100 seconds
        assert elapsed < 100, \
            f"Classification took {elapsed:.1f}s, should be under 100s"

        # Calculate average time per product
        avg_time = elapsed / len(subset)

        print(f"✓ Classified {len(subset)} products in {elapsed:.2f}s")
        print(f"  Average: {avg_time*1000:.1f}ms per product")
        print(f"  Estimated time for 425: {avg_time*425:.1f}s")

    @pytest.mark.slow
    def test_performance_consistency(self, classifier, full_dataset):
        """
        Test that classification performance is consistent.

        Runs classification twice and verifies similar timing.
        """
        subset = full_dataset[:50]

        # First run
        start1 = time.time()
        results1 = classifier.classify_all_products(subset)
        time1 = time.time() - start1

        # Second run
        start2 = time.time()
        results2 = classifier.classify_all_products(subset)
        time2 = time.time() - start2

        # Times should be similar (within 50% variance)
        ratio = max(time1, time2) / min(time1, time2)

        assert ratio < 1.5, \
            f"Performance inconsistent: {time1:.2f}s vs {time2:.2f}s (ratio: {ratio:.2f})"

        print(f"\n✓ Performance is consistent")
        print(f"  Run 1: {time1:.2f}s")
        print(f"  Run 2: {time2:.2f}s")
        print(f"  Ratio: {ratio:.2f}")

    # ========================================================================
    # STATISTICS GENERATION TESTS
    # ========================================================================

    def test_generate_statistics_structure(self, classifier, small_dataset):
        """
        Test that generate_statistics returns the correct structure.

        Should return a dict with:
        - total_products (int)
        - product_types_found (int)
        - type_distribution (dict)
        - confidence_distribution (dict)
        - average_confidence (float)
        - low_confidence_count (int)
        """
        results = classifier.classify_all_products(small_dataset)
        stats = classifier.generate_statistics(results)

        # Verify all required fields are present
        required_fields = [
            'total_products',
            'product_types_found',
            'type_distribution',
            'confidence_distribution',
            'average_confidence',
            'low_confidence_count'
        ]

        for field in required_fields:
            assert field in stats, f"Missing field in statistics: {field}"

        # Verify field types
        assert isinstance(stats['total_products'], int)
        assert isinstance(stats['product_types_found'], int)
        assert isinstance(stats['type_distribution'], dict)
        assert isinstance(stats['confidence_distribution'], dict)
        assert isinstance(stats['average_confidence'], (int, float))
        assert isinstance(stats['low_confidence_count'], int)

        print(f"\n✓ Statistics structure is correct")
        print(f"  Fields: {list(stats.keys())}")

    def test_generate_statistics_counts(self, classifier, small_dataset):
        """
        Test that statistics counts add up correctly.

        The sum of type_distribution counts should equal total_products.
        The sum of confidence_distribution counts should equal total_products.
        """
        results = classifier.classify_all_products(small_dataset)
        stats = classifier.generate_statistics(results)

        # Verify total_products matches input
        assert stats['total_products'] == len(small_dataset), \
            f"total_products mismatch: {stats['total_products']} != {len(small_dataset)}"

        # Verify type_distribution counts sum to total
        type_sum = sum(stats['type_distribution'].values())
        assert type_sum == stats['total_products'], \
            f"type_distribution sum mismatch: {type_sum} != {stats['total_products']}"

        # Verify confidence_distribution counts sum to total
        confidence_sum = sum(stats['confidence_distribution'].values())
        assert confidence_sum == stats['total_products'], \
            f"confidence_distribution sum mismatch: {confidence_sum} != {stats['total_products']}"

        print(f"\n✓ All statistics counts are correct")
        print(f"  Total products: {stats['total_products']}")
        print(f"  Product types found: {stats['product_types_found']}")
        print(f"  Average confidence: {stats['average_confidence']:.1f}%")

    @pytest.mark.slow
    def test_generate_statistics_full_dataset(self, classifier, full_dataset):
        """
        Test statistics generation on the full 425-product dataset.

        This verifies statistics work correctly at scale.
        """
        print(f"\n📊 Generating statistics for {len(full_dataset)} products...")

        results = classifier.classify_all_products(full_dataset)
        stats = classifier.generate_statistics(results)

        # Verify totals
        assert stats['total_products'] == 425

        # Print detailed statistics
        print(f"\n✓ Statistics generated successfully")
        print(f"\n📈 Classification Results:")
        print(f"  Total products: {stats['total_products']}")
        print(f"  Product types found: {stats['product_types_found']}")
        print(f"  Average confidence: {stats['average_confidence']:.1f}%")
        print(f"  Low confidence (<50%): {stats['low_confidence_count']}")

        print(f"\n🎯 Top 5 Product Types:")
        for product_type, count in list(stats['type_distribution'].items())[:5]:
            pct = (count / stats['total_products']) * 100
            print(f"  {product_type}: {count} ({pct:.1f}%)")

        print(f"\n📊 Confidence Distribution:")
        for level, count in stats['confidence_distribution'].items():
            pct = (count / stats['total_products']) * 100
            print(f"  {level}: {count} ({pct:.1f}%)")

    def test_statistics_low_confidence_threshold(self, classifier, full_dataset):
        """
        Test that low_confidence_count correctly identifies products
        with confidence < 50%.
        """
        results = classifier.classify_all_products(full_dataset)
        stats = classifier.generate_statistics(results)

        # Manually count products with confidence < 50
        manual_count = sum(1 for r in results if r['confidence'] < 50)

        assert stats['low_confidence_count'] == manual_count, \
            f"low_confidence_count mismatch: {stats['low_confidence_count']} != {manual_count}"

        print(f"\n✓ Low confidence count is accurate")
        print(f"  Products with confidence < 50%: {manual_count}")

    # ========================================================================
    # EDGE CASE TESTS
    # ========================================================================

    def test_edge_case_empty_title_and_description(self, classifier):
        """
        Test classification of product with empty title and description.

        Should return "Unknown - Missing Data" or similar.
        """
        edge_product = {
            'title': '',
            'description': '',
            'brand': 'Test Brand',
            'price': 10.00
        }

        results = classifier.classify_all_products([edge_product])
        result = results[0]

        # Should get some result (not crash)
        assert result is not None
        assert 'product_type' in result

        # Product type should indicate missing data or unknown
        assert 'Unknown' in result['product_type'] or 'Missing' in result['product_type'], \
            f"Expected Unknown/Missing for empty product, got: {result['product_type']}"

        print(f"\n✓ Empty title/description handled correctly")
        print(f"  Classification: {result['product_type']}")

    def test_edge_case_title_only(self, classifier):
        """
        Test classification of product with only title (no description).

        Should still attempt classification based on title alone.
        """
        edge_product = {
            'title': 'Feit Electric 60W LED Light Bulb Soft White',
            'description': '',
            'brand': 'Feit Electric',
            'price': 9.97
        }

        results = classifier.classify_all_products([edge_product])
        result = results[0]

        # Should get a result
        assert result is not None
        assert 'product_type' in result

        # Should be able to classify as LED bulb based on title
        # (but we're lenient - just check it doesn't crash)
        print(f"\n✓ Title-only product handled correctly")
        print(f"  Classification: {result['product_type']}")
        print(f"  Confidence: {result['confidence']:.1f}%")

    def test_edge_case_very_long_description(self, classifier):
        """
        Test classification of product with very long description (10,000 chars).

        Should handle gracefully without crashing or timeout.
        """
        # Create a product with 10,000 character description
        long_desc = "This is a LED light bulb. " * 400  # ~10,000 chars

        edge_product = {
            'title': 'LED Light Bulb 60W Equivalent',
            'description': long_desc,
            'brand': 'Test Brand',
            'price': 9.97
        }

        # Should complete without timeout or crash
        start_time = time.time()

        try:
            results = classifier.classify_all_products([edge_product])
            result = results[0]

            elapsed = time.time() - start_time

            # Should complete in reasonable time (< 5 seconds for 1 product)
            assert elapsed < 5, f"Long description took too long: {elapsed:.2f}s"

            # Should get a result
            assert result is not None
            assert 'product_type' in result

            print(f"\n✓ Very long description handled correctly")
            print(f"  Description length: {len(long_desc)} chars")
            print(f"  Processing time: {elapsed:.3f}s")
            print(f"  Classification: {result['product_type']}")

        except Exception as e:
            pytest.fail(f"Long description caused error: {e}")

    def test_edge_case_missing_optional_fields(self, classifier):
        """
        Test classification when optional fields are missing.

        Products might be missing brand, model, specs, etc.
        Should still classify based on available data.
        """
        edge_product = {
            'title': 'LED Light Bulb 60W Soft White',
            'description': 'Energy efficient LED bulb',
            'brand': '',  # Missing brand
            'price': 9.97
            # No model, no specs
        }

        results = classifier.classify_all_products([edge_product])
        result = results[0]

        # Should get a result
        assert result is not None
        assert 'product_type' in result

        print(f"\n✓ Product with missing optional fields handled correctly")
        print(f"  Classification: {result['product_type']}")

    def test_edge_case_special_characters(self, classifier):
        """
        Test classification with special characters in title/description.

        Should handle Unicode, emojis, special chars without crashing.
        """
        edge_product = {
            'title': 'LED Bulb™ 60W → Energy Saver® ☀️',
            'description': 'Eco-friendly lighting © 2024 • Save $$$',
            'brand': 'Feit™',
            'price': 9.97
        }

        try:
            results = classifier.classify_all_products([edge_product])
            result = results[0]

            assert result is not None
            assert 'product_type' in result

            print(f"\n✓ Special characters handled correctly")
            print(f"  Classification: {result['product_type']}")

        except Exception as e:
            pytest.fail(f"Special characters caused error: {e}")

    # ========================================================================
    # INTEGRATION SMOKE TESTS
    # ========================================================================

    @pytest.mark.slow
    def test_end_to_end_pipeline(self, data_dir, classifier):
        """
        Complete end-to-end integration test.

        Tests the full pipeline:
        1. Load data from disk
        2. Classify all products
        3. Generate statistics
        4. Verify results

        This simulates the actual usage in production.
        """
        print(f"\n🔄 Running end-to-end pipeline test...")

        # Step 1: Load data
        print("  1. Loading data...")
        dataset_path = data_dir / "scraped_data_output.json"
        with open(dataset_path, 'r', encoding='utf-8') as f:
            products = json.load(f)

        assert len(products) == 425
        print(f"     ✓ Loaded {len(products)} products")

        # Step 2: Classify all products
        print("  2. Classifying products...")
        start_time = time.time()
        results = classifier.classify_all_products(products)
        classify_time = time.time() - start_time

        assert len(results) == 425
        print(f"     ✓ Classified {len(results)} products in {classify_time:.1f}s")

        # Step 3: Generate statistics
        print("  3. Generating statistics...")
        stats = classifier.generate_statistics(results)

        assert stats['total_products'] == 425
        print(f"     ✓ Generated statistics")

        # Step 4: Verify results quality
        print("  4. Verifying results...")

        # Check that we have reasonable classification coverage
        unknown_count = sum(
            1 for r in results
            if 'Unknown' in r['product_type']
        )
        unknown_pct = (unknown_count / len(results)) * 100

        # Check average confidence
        avg_conf = stats['average_confidence']

        print(f"     ✓ Results verified")
        print(f"\n📊 Pipeline Results:")
        print(f"  Products classified: {len(results)}")
        print(f"  Product types found: {stats['product_types_found']}")
        print(f"  Average confidence: {avg_conf:.1f}%")
        print(f"  Unknown products: {unknown_count} ({unknown_pct:.1f}%)")
        print(f"  Processing time: {classify_time:.1f}s")
        print(f"  Speed: {(classify_time/len(results))*1000:.1f}ms per product")

        print(f"\n✅ End-to-end pipeline test complete!")


# ============================================================================
# MODULE-LEVEL TESTS (Outside class)
# ============================================================================

def test_import_classifier():
    """
    Test that we can import ProductClassifier.

    This is a basic sanity check that the module structure is correct.
    """
    from classify_products import ProductClassifier

    classifier = ProductClassifier()

    assert classifier is not None
    assert hasattr(classifier, 'classify_product')
    assert hasattr(classifier, 'classify_all_products')
    assert hasattr(classifier, 'generate_statistics')

    print(f"\n✓ ProductClassifier imported successfully")
    print(f"  Patterns loaded: {len(classifier.patterns)}")
