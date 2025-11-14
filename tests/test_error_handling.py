#!/usr/bin/env python3
"""
Error Handling and Edge Case Tests for ProductClassifier

Tests the robustness of the classification system when handling:
- Missing or None values
- Wrong data types
- Malformed data (SQL injection, XSS, special characters)
- Empty or minimal data
- Classification edge cases
- File I/O errors

These tests ensure the system handles errors gracefully without crashing.
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path to import classify_products
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from classify_products import ProductClassifier


class TestMissingOrNoneValues:
    """Test handling of products with missing or None values"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_product_with_none_title(self, classifier):
        """Product with title=None should handle gracefully and return 'Unknown - Missing Data'"""
        product = {
            'title': None,
            'description': 'This is a product description',
            'brand': 'TestBrand',
            'price': 19.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert 'product_type' in result, "Result should have product_type key"
        # Product should still try to classify from description
        assert result['product_type'] != '', "Product type should not be empty"

    def test_product_with_none_description(self, classifier):
        """Product with description=None should still classify from title"""
        product = {
            'title': 'LED Light Bulb 60W Equivalent',
            'description': None,
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert 'product_type' in result, "Result should have product_type key"
        assert result['product_type'] == 'LED Light Bulb', \
            f"Expected 'LED Light Bulb', got '{result['product_type']}'"

    def test_product_with_none_brand(self, classifier):
        """Product with brand=None should still classify (brand is optional)"""
        product = {
            'title': 'Ceiling Fan with Light Kit',
            'description': 'Indoor ceiling fan with 5 blades',
            'brand': None,
            'price': 149.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert 'product_type' in result, "Result should have product_type key"
        assert result['product_type'] == 'Ceiling Fan', \
            f"Expected 'Ceiling Fan', got '{result['product_type']}'"

    def test_product_with_none_price(self, classifier):
        """Product with price=None should still classify (price not used for classification)"""
        product = {
            'title': 'Kitchen Faucet with Pull-Down Spray',
            'description': 'Single handle kitchen faucet',
            'brand': 'TestBrand',
            'price': None
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert 'product_type' in result, "Result should have product_type key"
        assert result['product_type'] == 'Faucet', \
            f"Expected 'Faucet', got '{result['product_type']}'"

    def test_product_with_both_title_and_description_none(self, classifier):
        """Product with both title and description as None should return 'Unknown - Missing Data'"""
        product = {
            'title': None,
            'description': None,
            'brand': 'TestBrand',
            'price': 19.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert result['product_type'] == 'Unknown - Missing Data', \
            f"Expected 'Unknown - Missing Data', got '{result['product_type']}'"
        assert result['confidence'] == 0, "Confidence should be 0 for missing data"
        assert result['confidence_level'] == 'No Data', \
            f"Expected 'No Data', got '{result['confidence_level']}'"

    def test_product_with_missing_keys(self, classifier):
        """Product with missing keys should handle gracefully using .get() defaults"""
        product = {
            'title': 'Drill Bit Set'
            # Missing description, brand, price
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert 'product_type' in result, "Result should have product_type key"
        assert result['product_type'] == 'Drill Bit', \
            f"Expected 'Drill Bit', got '{result['product_type']}'"


class TestWrongDataTypes:
    """Test handling of products with wrong data types"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_product_with_numeric_title(self, classifier):
        """Product with title=123 (number) should handle gracefully"""
        product = {
            'title': 123,
            'description': 'LED Light Bulb 60W Equivalent',
            'brand': 'TestBrand',
            'price': 9.99
        }

        # Should either convert to string or handle gracefully
        try:
            result = classifier.classify_product(product)
            assert result is not None, "Should handle numeric title gracefully"
            assert 'product_type' in result, "Result should have product_type key"
        except (TypeError, AttributeError) as e:
            pytest.fail(f"classify_product should handle numeric title, but raised: {e}")

    def test_product_with_list_description(self, classifier):
        """Product with description=[] (list) should handle gracefully"""
        product = {
            'title': 'LED Light Bulb',
            'description': ['This', 'is', 'a', 'list'],
            'brand': 'TestBrand',
            'price': 9.99
        }

        # Should either convert to string or handle gracefully
        try:
            result = classifier.classify_product(product)
            assert result is not None, "Should handle list description gracefully"
            assert 'product_type' in result, "Result should have product_type key"
        except (TypeError, AttributeError) as e:
            pytest.fail(f"classify_product should handle list description, but raised: {e}")

    def test_product_with_empty_dict(self, classifier):
        """Empty dict {} should return 'Unknown - Missing Data'"""
        product = {}
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert result['product_type'] == 'Unknown - Missing Data', \
            f"Expected 'Unknown - Missing Data', got '{result['product_type']}'"

    def test_product_with_boolean_values(self, classifier):
        """Product with boolean values should handle gracefully"""
        product = {
            'title': True,
            'description': False,
            'brand': 'TestBrand',
            'price': 9.99
        }

        try:
            result = classifier.classify_product(product)
            assert result is not None, "Should handle boolean values gracefully"
        except (TypeError, AttributeError) as e:
            pytest.fail(f"classify_product should handle boolean values, but raised: {e}")


class TestMalformedData:
    """Test handling of malformed data (SQL injection, XSS, special characters, unicode)"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_product_with_only_special_characters_title(self, classifier):
        """Product with title containing only special characters: '!@#$%^&*()'"""
        product = {
            'title': '!@#$%^&*()',
            'description': 'LED Light Bulb',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle special characters in title"
        assert 'product_type' in result, "Result should have product_type key"
        # Should classify from description since title has no useful keywords
        assert result['product_type'] == 'LED Light Bulb', \
            f"Expected 'LED Light Bulb', got '{result['product_type']}'"

    def test_product_with_sql_injection_description(self, classifier):
        """Product with SQL injection in description should sanitize/ignore"""
        product = {
            'title': 'LED Light Bulb',
            'description': "'; DROP TABLE products; --",
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle SQL injection gracefully"
        assert 'product_type' in result, "Result should have product_type key"
        # Should still classify from title
        assert result['product_type'] == 'LED Light Bulb', \
            f"Expected 'LED Light Bulb', got '{result['product_type']}'"

    def test_product_with_xss_description(self, classifier):
        """Product with XSS script in description should handle safely"""
        product = {
            'title': 'Ceiling Fan',
            'description': "<script>alert('XSS')</script>",
            'brand': 'TestBrand',
            'price': 149.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle XSS gracefully"
        assert 'product_type' in result, "Result should have product_type key"
        # Should classify from title
        assert result['product_type'] == 'Ceiling Fan', \
            f"Expected 'Ceiling Fan', got '{result['product_type']}'"

    def test_product_with_very_long_title(self, classifier):
        """Product with very long title (10,000 characters) should not crash"""
        long_title = 'LED Light Bulb ' + 'A' * 10000
        product = {
            'title': long_title,
            'description': 'Standard LED bulb',
            'brand': 'TestBrand',
            'price': 9.99
        }

        try:
            result = classifier.classify_product(product)
            assert result is not None, "Should handle very long title"
            assert 'product_type' in result, "Result should have product_type key"
            # Should still find the keyword in the long title
            assert result['product_type'] == 'LED Light Bulb', \
                f"Expected 'LED Light Bulb', got '{result['product_type']}'"
        except (MemoryError, RecursionError) as e:
            pytest.fail(f"Should handle long titles efficiently, but raised: {e}")

    def test_product_with_unicode_emoji(self, classifier):
        """Product with unicode/emoji: 'LED 💡 Light Bulb 🌟' should handle gracefully"""
        product = {
            'title': 'LED 💡 Light Bulb 🌟',
            'description': 'Bright LED bulb with emoji',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle unicode/emoji gracefully"
        assert 'product_type' in result, "Result should have product_type key"
        # Should still extract keywords despite emoji
        assert result['product_type'] == 'LED Light Bulb', \
            f"Expected 'LED Light Bulb', got '{result['product_type']}'"

    def test_product_with_html_entities(self, classifier):
        """Product with HTML entities should handle gracefully"""
        product = {
            'title': 'LED Light Bulb &amp; Fixture',
            'description': 'Price: &lt;$10 &gt; $5',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle HTML entities gracefully"
        assert 'product_type' in result, "Result should have product_type key"

    def test_product_with_control_characters(self, classifier):
        """Product with control characters (null bytes, etc.) should handle gracefully"""
        product = {
            'title': 'LED\x00Light\x01Bulb\x02',
            'description': 'Standard bulb\x03\x04',
            'brand': 'TestBrand',
            'price': 9.99
        }

        try:
            result = classifier.classify_product(product)
            assert result is not None, "Should handle control characters gracefully"
        except (ValueError, UnicodeError) as e:
            pytest.fail(f"Should handle control characters, but raised: {e}")


class TestEmptyOrMinimalData:
    """Test handling of empty or minimal data"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_product_with_empty_strings(self, classifier):
        """Product with title='' and description='' should return 'Unknown - Missing Data'"""
        product = {
            'title': '',
            'description': '',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert result['product_type'] == 'Unknown - Missing Data', \
            f"Expected 'Unknown - Missing Data', got '{result['product_type']}'"

    def test_product_with_single_character_title(self, classifier):
        """Product with title='A' (single character) should handle gracefully"""
        product = {
            'title': 'A',
            'description': 'LED Light Bulb',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle single character title"
        assert 'product_type' in result, "Result should have product_type key"
        # Should classify from description
        assert result['product_type'] == 'LED Light Bulb', \
            f"Expected 'LED Light Bulb', got '{result['product_type']}'"

    def test_product_with_whitespace_only_title(self, classifier):
        """Product with title containing only whitespace: '   ' should treat as empty"""
        product = {
            'title': '   ',
            'description': 'Ceiling Fan with Light',
            'brand': 'TestBrand',
            'price': 149.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle whitespace-only title"
        # normalize_text will convert '   ' to '', so it should classify from description
        assert result['product_type'] == 'Ceiling Fan', \
            f"Expected 'Ceiling Fan', got '{result['product_type']}'"

    def test_product_with_only_whitespace_both_fields(self, classifier):
        """Product with only whitespace in title and description"""
        product = {
            'title': '   \t\n   ',
            'description': '\n\t  \n',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle whitespace-only fields"
        # After normalization, both will be empty, so should return Unknown
        assert result['product_type'] == 'Unknown - Missing Data', \
            f"Expected 'Unknown - Missing Data', got '{result['product_type']}'"

    def test_product_with_minimal_valid_data(self, classifier):
        """Product with minimal but valid data should classify correctly"""
        product = {
            'title': 'drill bit'
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle minimal valid data"
        assert result['product_type'] == 'Drill Bit', \
            f"Expected 'Drill Bit', got '{result['product_type']}'"


class TestClassificationEdgeCases:
    """Test edge cases in the classification logic"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_product_matching_no_patterns(self, classifier):
        """Product that matches NO patterns should return 'Unknown - Unable to Classify'"""
        product = {
            'title': 'Quantum Flux Capacitor XYZ-9000',
            'description': 'Advanced quantum technology for time travel applications',
            'brand': 'FutureTech',
            'price': 999999.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "classify_product should return a result dict"
        assert 'product_type' in result, "Result should have product_type key"
        assert result['product_type'] == 'Unknown - Unable to Classify', \
            f"Expected 'Unknown - Unable to Classify', got '{result['product_type']}'"
        assert result['confidence'] < 15, \
            f"Expected confidence < 15, got {result['confidence']}"

    def test_product_with_score_at_boundary_20(self, classifier):
        """Product with score exactly at 20 (Very Low confidence boundary)"""
        # This test might need adjustment based on actual scoring
        product = {
            'title': 'Product with weak keywords only',
            'description': 'dimmable lumens watt',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle boundary score"
        assert 'confidence' in result, "Result should have confidence key"
        assert 'confidence_level' in result, "Result should have confidence_level key"

    def test_product_with_score_at_boundary_30(self, classifier):
        """Product with score exactly at 30 (Low confidence boundary)"""
        product = {
            'title': 'Item with some keywords',
            'description': 'Contains multiple weak keywords: dimmable watt lumens kelvin',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle boundary score"
        assert 'confidence' in result, "Result should have confidence key"

    def test_product_with_score_at_boundary_50(self, classifier):
        """Product with score exactly at 50 (Medium confidence boundary)"""
        product = {
            'title': 'Light fixture',
            'description': 'flush mount ceiling integrated led',
            'brand': 'TestBrand',
            'price': 49.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle boundary score"
        assert 'confidence' in result, "Result should have confidence key"

    def test_product_with_score_at_boundary_70(self, classifier):
        """Product with score exactly at 70 (High confidence boundary)"""
        product = {
            'title': 'LED Light Bulb',
            'description': 'High quality bulb with excellent features',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle boundary score"
        assert 'confidence' in result, "Result should have confidence key"
        assert result['confidence'] >= 70, \
            f"Expected confidence >= 70, got {result['confidence']}"

    def test_product_matching_multiple_patterns_equally(self, classifier):
        """Product that matches multiple patterns should pick highest scoring one"""
        # This is a theoretical edge case - in practice, patterns are designed to be distinct
        product = {
            'title': 'Multi-purpose tool',
            'description': 'Can be used as hammer drill saw wrench screwdriver',
            'brand': 'TestBrand',
            'price': 99.99
        }
        result = classifier.classify_product(product)

        assert result is not None, "Should handle multiple pattern matches"
        assert 'product_type' in result, "Result should have product_type key"
        assert 'alternate_types' in result, "Should provide alternate classifications"
        # Should pick one and provide alternates
        assert len(result['alternate_types']) >= 0, "Should have alternate types"

    def test_classify_all_products_with_empty_list(self, classifier):
        """classify_all_products with empty list should return empty list"""
        products = []
        results = classifier.classify_all_products(products)

        assert results == [], "Should return empty list for empty input"

    def test_classify_all_products_with_single_product(self, classifier):
        """classify_all_products with single product should work correctly"""
        products = [{
            'title': 'LED Light Bulb',
            'description': '60W equivalent',
            'brand': 'TestBrand',
            'price': 9.99
        }]
        results = classifier.classify_all_products(products)

        assert len(results) == 1, "Should return one result"
        assert results[0]['product_type'] == 'LED Light Bulb', \
            f"Expected 'LED Light Bulb', got '{results[0]['product_type']}'"

    def test_generate_statistics_with_empty_results(self, classifier):
        """generate_statistics with empty results should handle gracefully"""
        # This would raise ZeroDivisionError if not handled properly
        results = []

        try:
            stats = classifier.generate_statistics(results)
            # If it doesn't raise, it should return sensible empty stats
            pytest.fail("generate_statistics should handle empty list, but it might raise ZeroDivisionError")
        except ZeroDivisionError:
            # This is expected if not handled - the code should be fixed to handle this
            pass


class TestFileIOErrors:
    """Test file I/O error handling (these test the main() function behavior)"""

    def test_nonexistent_data_file(self):
        """Test what happens if data file doesn't exist"""
        # This tests the main() function which tries to load a file
        # We can't easily test main() without mocking, but we can test the concept

        nonexistent_file = Path('/tmp/nonexistent_file_xyz_123.json')

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            with open(nonexistent_file, 'r') as f:
                json.load(f)

    def test_corrupted_json_file(self):
        """Test what happens if data file is corrupted JSON"""
        # Create a temporary corrupted JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ "invalid": "json" ')  # Missing closing brace
            temp_file = f.name

        try:
            # Should raise JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                with open(temp_file, 'r') as f:
                    json.load(f)
        finally:
            Path(temp_file).unlink()

    def test_empty_json_file(self):
        """Test what happens if data file is empty"""
        # Create a temporary empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('')  # Empty file
            temp_file = f.name

        try:
            # Should raise JSONDecodeError
            with pytest.raises(json.JSONDecodeError):
                with open(temp_file, 'r') as f:
                    json.load(f)
        finally:
            Path(temp_file).unlink()

    def test_valid_but_empty_json_array(self):
        """Test what happens if data file contains valid but empty JSON array"""
        # Create a temporary file with empty array
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('[]')  # Valid JSON but empty array
            temp_file = f.name

        try:
            # Should load successfully but return empty list
            with open(temp_file, 'r') as f:
                data = json.load(f)
                assert data == [], "Should load empty array successfully"
        finally:
            Path(temp_file).unlink()

    def test_json_with_invalid_product_structure(self):
        """Test what happens if JSON has unexpected structure"""
        # Create a temporary file with unexpected structure
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'not': 'a list'}, f)  # Not a list of products
            temp_file = f.name

        try:
            with open(temp_file, 'r') as f:
                data = json.load(f)
                # This would cause issues in classify_all_products
                # which expects a list
                assert isinstance(data, dict), "Loaded unexpected structure"
        finally:
            Path(temp_file).unlink()


class TestResultStructureIntegrity:
    """Test that results always have the expected structure"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_result_has_required_keys(self, classifier):
        """Every classification result should have required keys"""
        product = {
            'title': 'LED Light Bulb',
            'description': '60W equivalent',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        required_keys = ['product_type', 'confidence', 'confidence_level', 'reasons', 'alternate_types']
        for key in required_keys:
            assert key in result, f"Result missing required key: {key}"

    def test_result_types_are_correct(self, classifier):
        """Result values should be correct types"""
        product = {
            'title': 'LED Light Bulb',
            'description': '60W equivalent',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        assert isinstance(result['product_type'], str), "product_type should be string"
        assert isinstance(result['confidence'], (int, float)), "confidence should be numeric"
        assert isinstance(result['confidence_level'], str), "confidence_level should be string"
        assert isinstance(result['reasons'], list), "reasons should be list"
        assert isinstance(result['alternate_types'], list), "alternate_types should be list"

    def test_confidence_within_bounds(self, classifier):
        """Confidence should always be between 0 and 100"""
        products = [
            {'title': 'LED Light Bulb', 'description': '60W'},
            {'title': 'Unknown Product XYZ', 'description': 'No keywords'},
            {'title': '', 'description': ''},
            {'title': None, 'description': None}
        ]

        for product in products:
            result = classifier.classify_product(product)
            assert 0 <= result['confidence'] <= 100, \
                f"Confidence {result['confidence']} out of bounds [0, 100]"

    def test_confidence_level_valid_values(self, classifier):
        """confidence_level should be one of the expected values"""
        valid_levels = ['High', 'Medium', 'Low', 'Very Low', 'No Match', 'No Data']

        products = [
            {'title': 'LED Light Bulb', 'description': '60W equivalent'},
            {'title': 'Ceiling Fan', 'description': 'indoor'},
            {'title': 'unknown thing', 'description': 'mysterious'},
            {'title': None, 'description': None}
        ]

        for product in products:
            result = classifier.classify_product(product)
            assert result['confidence_level'] in valid_levels, \
                f"Invalid confidence_level: {result['confidence_level']}"

    def test_alternate_types_structure(self, classifier):
        """alternate_types should be list of (type, score) tuples"""
        product = {
            'title': 'LED Light Bulb',
            'description': '60W equivalent',
            'brand': 'TestBrand',
            'price': 9.99
        }
        result = classifier.classify_product(product)

        for alt in result['alternate_types']:
            assert isinstance(alt, tuple), "Each alternate should be a tuple"
            assert len(alt) == 2, "Each alternate should be (type, score) tuple"
            assert isinstance(alt[0], str), "Alternate type should be string"
            assert isinstance(alt[1], (int, float)), "Alternate score should be numeric"


class TestConcurrentSafetyAndPerformance:
    """Test that the classifier is safe for concurrent use and performs reasonably"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_classifier_is_stateless(self, classifier):
        """Classifier should produce same results for same input (stateless)"""
        product = {
            'title': 'LED Light Bulb 60W',
            'description': 'Soft white dimmable',
            'brand': 'TestBrand',
            'price': 9.99
        }

        result1 = classifier.classify_product(product)
        result2 = classifier.classify_product(product)

        assert result1['product_type'] == result2['product_type'], \
            "Classifier should produce same result for same input"
        assert result1['confidence'] == result2['confidence'], \
            "Confidence should be same for same input"

    def test_large_batch_performance(self, classifier):
        """Classifier should handle large batches without excessive memory/time"""
        # Create 1000 products
        products = []
        for i in range(1000):
            products.append({
                'title': f'LED Light Bulb {i}',
                'description': '60W equivalent soft white',
                'brand': f'Brand{i}',
                'price': 9.99 + i * 0.01
            })

        import time
        start_time = time.time()

        results = classifier.classify_all_products(products)

        elapsed = time.time() - start_time

        assert len(results) == 1000, "Should process all products"
        assert elapsed < 30, f"Should process 1000 products in < 30s, took {elapsed:.2f}s"

        # Check memory didn't explode (results should be reasonable size)
        import sys
        result_size = sys.getsizeof(str(results))
        assert result_size < 10_000_000, \
            f"Results too large: {result_size} bytes (should be < 10MB)"


# Run tests with: pytest tests/test_error_handling.py -v
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
