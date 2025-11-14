"""
Performance Benchmark Tests for Product Classification System

Tests performance requirements:
- Single product: < 50ms average
- 100 products: < 100 seconds
- 425 products: < 425 seconds
- Data loading: < 5 seconds
- Memory usage: < 500MB
- Initialization: < 1 second

Results are saved to outputs/performance_baseline.json for tracking.
"""

import json
import time
import tracemalloc
import pytest
from pathlib import Path
from datetime import datetime


class TestPerformance:
    """Performance benchmarks for the product classification system."""

    def test_classifier_initialization(self, classifier):
        """
        Test ProductClassifier initialization time.

        Requirements:
        - Should initialize in < 1 second
        - Should load all patterns successfully
        """
        start_time = time.time()

        # Create a new classifier instance
        from classify_products import ProductClassifier
        new_classifier = ProductClassifier()

        end_time = time.time()
        init_time = end_time - start_time

        # Verify patterns loaded
        pattern_count = len(new_classifier.patterns)
        assert pattern_count > 0, "No patterns loaded"

        # Check initialization time
        assert init_time < 1.0, f"SLOW: Initialization took {init_time:.3f}s (expected <1s)"

        print(f"\n✓ Initialized in {init_time:.3f}s with {pattern_count} patterns")

    def test_single_product_classification_speed(self, classifier, sample_led_bulb):
        """
        Test single product classification speed.

        Requirements:
        - Average time per classification: < 50ms
        - Tests 100 iterations to get stable average
        """
        iterations = 100

        # Warm up (first run might be slower due to caching)
        classifier.classify_product(sample_led_bulb)

        # Measure performance
        start_time = time.time()
        for _ in range(iterations):
            result = classifier.classify_product(sample_led_bulb)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_ms = (total_time / iterations) * 1000

        # Verify results
        assert result is not None, "Classification returned None"
        assert result['product_type'] != '', "No product type identified"

        # Check performance requirement
        assert avg_time_ms < 50, f"SLOW: Single classification took {avg_time_ms:.2f}ms (expected <50ms)"

        print(f"\n✓ Single product: {avg_time_ms:.2f}ms average ({iterations} iterations)")
        print(f"  Classifications per second: {1000/avg_time_ms:.1f}")

    def test_batch_classification_speed_10_products(self, classifier, full_dataset):
        """
        Test batch classification speed on 10 products (quick test).

        This is a faster version to run during normal test runs.
        """
        batch_size = 10
        products = full_dataset[:batch_size]

        start_time = time.time()
        results = classifier.classify_all_products(products)
        end_time = time.time()

        total_time = end_time - start_time
        products_per_sec = batch_size / total_time

        # Verify results
        assert len(results) == batch_size, f"Expected {batch_size} results, got {len(results)}"
        assert all(r['product_type'] for r in results), "Some products not classified"

        print(f"\n✓ Classified {batch_size} products in {total_time:.2f}s ({products_per_sec:.1f} products/sec)")

    def test_batch_classification_speed_100_products(self, classifier, full_dataset):
        """
        Test batch classification speed on 100 products.

        Requirements:
        - 100 products: < 100 seconds
        - Should maintain reasonable throughput
        """
        batch_size = 100
        products = full_dataset[:batch_size]

        start_time = time.time()
        results = classifier.classify_all_products(products)
        end_time = time.time()

        total_time = end_time - start_time
        products_per_sec = batch_size / total_time
        avg_time_per_product = total_time / batch_size

        # Verify results
        assert len(results) == batch_size, f"Expected {batch_size} results, got {len(results)}"
        assert all(r['product_type'] for r in results), "Some products not classified"

        # Check performance requirement
        assert total_time < 100, f"SLOW: Classified {batch_size} products in {total_time:.2f}s (expected <100s)"

        print(f"\n✓ Classified {batch_size} products in {total_time:.2f}s ({products_per_sec:.1f} products/sec)")
        print(f"  Average per product: {avg_time_per_product:.3f}s")

    @pytest.mark.slow
    def test_full_dataset_classification_speed(self, classifier, full_dataset):
        """
        Test full dataset classification speed (425 products).

        Requirements:
        - 425 products: < 425 seconds (1 sec/product max)
        - Should complete successfully for all products

        Note: Marked as @pytest.mark.slow because it takes >60 seconds
        """
        total_products = len(full_dataset)

        print(f"\n⏱ Classifying {total_products} products (this may take a few minutes)...")

        start_time = time.time()
        results = classifier.classify_all_products(full_dataset)
        end_time = time.time()

        total_time = end_time - start_time
        products_per_sec = total_products / total_time
        avg_time_per_product = total_time / total_products

        # Verify results
        assert len(results) == total_products, f"Expected {total_products} results, got {len(results)}"
        assert all(r['product_type'] for r in results), "Some products not classified"

        # Check performance requirement
        max_allowed_time = total_products  # 1 second per product
        assert total_time < max_allowed_time, \
            f"SLOW: Classified {total_products} products in {total_time:.2f}s (expected <{max_allowed_time}s)"

        # Count classification quality
        unknown_count = sum(1 for r in results if 'Unknown' in r['product_type'])
        high_confidence = sum(1 for r in results if r['confidence_level'] == 'High')

        print(f"\n✓ Classified {total_products} products in {total_time:.2f}s ({products_per_sec:.1f} products/sec)")
        print(f"  Average per product: {avg_time_per_product:.3f}s")
        print(f"  High confidence: {high_confidence}/{total_products} ({high_confidence/total_products*100:.1f}%)")
        print(f"  Unknown: {unknown_count}/{total_products} ({unknown_count/total_products*100:.1f}%)")

    def test_data_loading_speed(self, data_dir):
        """
        Test data loading speed.

        Requirements:
        - Load scraped_data_output.json in < 5 seconds
        - Verify data integrity
        """
        data_file = data_dir / 'scraped_data_output.json'

        # Get file size
        file_size_mb = data_file.stat().st_size / (1024 * 1024)

        # Measure load time
        start_time = time.time()
        with open(data_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        end_time = time.time()

        load_time = end_time - start_time

        # Verify data
        assert len(products) > 0, "No products loaded"
        assert isinstance(products, list), "Products should be a list"

        # Check performance requirement
        assert load_time < 5.0, f"SLOW: Data loading took {load_time:.2f}s (expected <5s)"

        print(f"\n✓ Loaded {len(products)} products in {load_time:.2f}s")
        print(f"  File size: {file_size_mb:.2f}MB")
        print(f"  Load speed: {file_size_mb/load_time:.2f}MB/s")

    @pytest.mark.slow
    def test_memory_usage_full_dataset(self, classifier, full_dataset):
        """
        Test memory usage when classifying full dataset.

        Requirements:
        - Peak memory usage: < 500MB
        - No memory leaks
        """
        # Start memory tracking
        tracemalloc.start()

        # Get baseline memory
        baseline_current, baseline_peak = tracemalloc.get_traced_memory()

        # Classify all products
        results = classifier.classify_all_products(full_dataset)

        # Get peak memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Calculate memory used (subtract baseline)
        memory_used_mb = (peak - baseline_peak) / (1024 * 1024)

        # Verify results
        assert len(results) == len(full_dataset), "Not all products classified"

        # Check memory requirement
        max_memory_mb = 500
        assert memory_used_mb < max_memory_mb, \
            f"HIGH MEMORY: Used {memory_used_mb:.2f}MB (expected <{max_memory_mb}MB)"

        print(f"\n✓ Memory usage: {memory_used_mb:.2f}MB (peak)")
        print(f"  Products classified: {len(results)}")
        print(f"  Memory per product: {memory_used_mb/len(results)*1024:.2f}KB")

    def test_pattern_matching_performance(self, classifier, sample_led_bulb):
        """
        Test individual pattern matching performance.

        This helps identify if specific pattern types are slow.
        """
        iterations = 100

        # Test calculate_match_score performance
        start_time = time.time()
        for _ in range(iterations):
            score, reasons = classifier.calculate_match_score(sample_led_bulb, 'LED Light Bulb')
        end_time = time.time()

        avg_time_ms = ((end_time - start_time) / iterations) * 1000

        # Verify results
        assert score > 0, "Match score should be positive for LED bulb"
        assert len(reasons) > 0, "Should have reasons for match"

        # Pattern matching should be fast (< 10ms)
        assert avg_time_ms < 10, f"SLOW: Pattern matching took {avg_time_ms:.2f}ms (expected <10ms)"

        print(f"\n✓ Pattern matching: {avg_time_ms:.2f}ms average")
        print(f"  Score: {score:.1f}")
        print(f"  Reasons: {len(reasons)}")


class TestPerformanceBaseline:
    """
    Save performance baseline results to JSON for tracking over time.
    """

    @pytest.mark.slow
    def test_save_performance_baseline(self, classifier, full_dataset, data_dir, project_root):
        """
        Run comprehensive performance tests and save baseline.

        This creates a JSON file with all performance metrics for comparison.
        """
        print("\n" + "="*60)
        print("PERFORMANCE BASELINE TEST")
        print("="*60)

        baseline = {
            "timestamp": datetime.now().isoformat(),
            "dataset_size": len(full_dataset),
        }

        # Test 1: Initialization
        print("\n1. Testing initialization...")
        from classify_products import ProductClassifier
        start = time.time()
        test_classifier = ProductClassifier()
        init_time = time.time() - start
        baseline['initialization_seconds'] = round(init_time, 4)
        print(f"   ✓ {init_time:.4f}s")

        # Test 2: Single product (100 iterations)
        print("\n2. Testing single product classification...")
        sample = full_dataset[0]
        classifier.classify_product(sample)  # Warm up

        iterations = 100
        start = time.time()
        for _ in range(iterations):
            classifier.classify_product(sample)
        single_time_ms = ((time.time() - start) / iterations) * 1000
        baseline['single_product_ms'] = round(single_time_ms, 2)
        print(f"   ✓ {single_time_ms:.2f}ms average")

        # Test 3: Batch 100 products
        print("\n3. Testing 100 product batch...")
        batch_100 = full_dataset[:100]
        start = time.time()
        results_100 = classifier.classify_all_products(batch_100)
        batch_100_time = time.time() - start
        baseline['batch_100_seconds'] = round(batch_100_time, 2)
        print(f"   ✓ {batch_100_time:.2f}s ({100/batch_100_time:.1f} products/sec)")

        # Test 4: Full dataset (425 products)
        print(f"\n4. Testing full dataset ({len(full_dataset)} products)...")
        start = time.time()
        results_full = classifier.classify_all_products(full_dataset)
        full_time = time.time() - start
        baseline['full_425_seconds'] = round(full_time, 2)
        print(f"   ✓ {full_time:.2f}s ({len(full_dataset)/full_time:.1f} products/sec)")

        # Test 5: Data loading
        print("\n5. Testing data loading...")
        data_file = data_dir / 'scraped_data_output.json'
        start = time.time()
        with open(data_file, 'r', encoding='utf-8') as f:
            json.load(f)
        load_time = time.time() - start
        baseline['data_load_seconds'] = round(load_time, 4)
        file_size_mb = data_file.stat().st_size / (1024 * 1024)
        baseline['data_file_size_mb'] = round(file_size_mb, 2)
        print(f"   ✓ {load_time:.4f}s ({file_size_mb:.2f}MB)")

        # Test 6: Memory usage
        print("\n6. Testing memory usage...")
        tracemalloc.start()
        baseline_mem = tracemalloc.get_traced_memory()[1]

        # Classify all products
        classifier.classify_all_products(full_dataset)

        peak_mem = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()

        memory_mb = (peak_mem - baseline_mem) / (1024 * 1024)
        baseline['memory_mb'] = round(memory_mb, 2)
        print(f"   ✓ {memory_mb:.2f}MB peak")

        # Calculate throughput
        baseline['throughput_products_per_second'] = round(len(full_dataset) / full_time, 2)

        # Save baseline to JSON
        outputs_dir = project_root / 'outputs'
        outputs_dir.mkdir(exist_ok=True)

        baseline_file = outputs_dir / 'performance_baseline.json'
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2)

        print("\n" + "="*60)
        print("PERFORMANCE BASELINE SAVED")
        print("="*60)
        print(f"File: {baseline_file}")
        print(f"\nSummary:")
        print(f"  Single product:     {single_time_ms:.2f}ms")
        print(f"  100 products:       {batch_100_time:.2f}s")
        print(f"  425 products:       {full_time:.2f}s")
        print(f"  Data loading:       {load_time:.4f}s")
        print(f"  Memory usage:       {memory_mb:.2f}MB")
        print(f"  Throughput:         {baseline['throughput_products_per_second']:.2f} products/sec")
        print("="*60)

        # Verify all requirements met
        assert single_time_ms < 50, f"Single product too slow: {single_time_ms:.2f}ms"
        assert batch_100_time < 100, f"Batch 100 too slow: {batch_100_time:.2f}s"
        assert full_time < 425, f"Full dataset too slow: {full_time:.2f}s"
        assert load_time < 5, f"Data loading too slow: {load_time:.4f}s"
        assert memory_mb < 500, f"Memory usage too high: {memory_mb:.2f}MB"

        print("\n✓ All performance requirements met!")
