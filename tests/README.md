# Test Suite Documentation

## Overview

This directory contains comprehensive automated tests for the CC Product Classification system. The test suite ensures the classifier correctly identifies product types, handles edge cases, and maintains high accuracy.

### Test Statistics

- **Total Tests**: 210 test functions
- **Test Files**: 6 test modules
- **Coverage Target**: 80%+ code coverage
- **Test Categories**: Unit tests, integration tests, validation tests

### What the Test Suite Covers

1. **Core Utilities** - Text normalization and keyword matching functions
2. **Scoring System** - Product classification scoring and keyword weighting
3. **Product Patterns** - Pattern matching for 20 most common product types
4. **Validation System** - Ground truth comparison and accuracy metrics
5. **Integration Pipeline** - End-to-end classification workflow
6. **Edge Cases** - Chandelier bulbs, pendant bulbs, negative keyword handling

---

## Quick Start

### Run All Tests

```bash
# Run all tests with verbose output
make test

# Or use pytest directly
python3 -m pytest tests -v
```

### Run Tests with Coverage

```bash
# Generate coverage report (HTML + terminal)
make test-coverage

# View HTML coverage report
make coverage-open
```

### Run Specific Test File

```bash
# Run specific test module
pytest tests/test_scoring_system.py -v

# Or use make
make test-specific TEST_FILE=tests/test_scoring_system.py
```

### Run Specific Test Function

```bash
# Run a single test function
pytest tests/test_scoring_system.py::TestScoringSystem::test_strong_keyword_in_title -v

# Run all tests in a class
pytest tests/test_scoring_system.py::TestScoringSystem -v
```

### Run Only Fast Tests (Skip Slow Ones)

```bash
# Skip slow integration tests
pytest tests -m "not slow" -v

# Or use make
make test-not-slow
```

### Run Only Slow Tests

```bash
# Run only tests marked as slow (integration tests with full dataset)
pytest tests -m slow -v
```

---

## Test Organization

### Test Files and What They Test

#### 1. `test_product_classifier_core.py` - Core Utility Functions
**Focus**: Tests fundamental text processing and keyword matching

**Test Classes**:
- `TestNormalizeText` (9 tests) - Tests text normalization (lowercase, whitespace, special chars)
- `TestContainsKeyword` (32 tests) - Tests word boundary keyword matching
- `TestKeywordMatchingIntegration` (3 tests) - Tests combined normalize + search workflow

**Key Tests**:
- ✓ Basic text normalization with mixed case
- ✓ Multiple spaces and whitespace handling
- ✓ Single-word keyword matching with word boundaries
- ✓ Multi-word keyword matching
- ✓ Prevention of false matches (e.g., "brush" not matching "brushed")
- ✓ Real-world examples: chandelier bulbs, pendant bulbs, ceiling fans
- ✓ Case-insensitive workflow

**Example**:
```bash
pytest tests/test_product_classifier_core.py::TestContainsKeyword::test_contains_prevents_false_match_brush -v
```

---

#### 2. `test_scoring_system.py` - Scoring Calculations and Keyword Weighting
**Focus**: Tests the `calculate_match_score()` function for accurate product scoring

**Test Classes**:
- `TestScoringSystem` (17 tests) - Main scoring algorithm tests
- `TestScoringEdgeCases` (6 tests) - Edge case handling
- `test_scoring_summary` - Comprehensive scoring report

**Key Tests**:
- ✓ Strong keyword in title (+80 points)
- ✓ Strong keyword in description only (+50 points)
- ✓ Weak keywords accumulation (+5 each, max 30)
- ✓ Negative keyword blocking (score = 0)
- ✓ **Chandelier bulb exception** (should NOT be blocked)
- ✓ **Pendant bulb exception** (should NOT be blocked)
- ✓ Score capping at 100 max
- ✓ Spec boost for products with detailed specifications
- ✓ Description hints adding points

**Critical Bug Fix Tests**:
```bash
# Test chandelier bulbs are NOT blocked by negative keyword
pytest tests/test_scoring_system.py::TestScoringSystem::test_chandelier_bulb_exception -v

# Test pendant bulbs are NOT blocked
pytest tests/test_scoring_system.py::TestScoringSystem::test_pendant_bulb_exception -v
```

---

#### 3. `test_product_patterns.py` - Product Type Pattern Matching
**Focus**: Tests the top 20 most common product types with 3 test cases each

**Product Types Tested** (60 tests total):
1. **LED Light Bulb** (3 tests) - Perfect match, good match, chandelier bulb edge case
2. **Ceiling Fan** (3 tests) - Indoor, outdoor, minimal description
3. **Circuit Breaker** (3 tests) - Standard, GFCI, AFCI variants
4. **Light Switch** (3 tests) - Dimmer, 3-way, smart switch
5. **Electrical Outlet** (3 tests) - GFCI, receptacle, USB outlet
6. **Faucet** (3 tests) - Kitchen, bathroom, with drain
7. **Toilet** (3 tests) - 2-piece, dual flush, comfort height
8. **Door Lock** (3 tests) - Keyed entry, deadbolt, smart lock
9. **Drill** (3 tests) - Cordless, hammer drill, impact driver
10. **Saw** (3 tests) - Circular, miter, jigsaw
11. **Fastener** (3 tests) - Screws, bolts, wall anchors
12. **Paint** (3 tests) - Interior, exterior, primer
13. **Pendant Light** (3 tests) - Standard, industrial, mini-pendant
14. **Wall Sconce** (3 tests) - Standard, vanity, bath light
15. **Recessed Light** (3 tests) - Standard, retrofit, canless
16. **Exhaust Fan** (3 tests) - Bathroom, ventilation, with light
17. **Sink** (3 tests) - Kitchen, bathroom, vessel sink
18. **Drill Bit** (3 tests) - Titanium, cobalt, driver bits
19. **Ladder** (3 tests) - Step, extension, multi-position
20. **Window** (3 tests) - Double-hung, sliding, casement

**Test Pattern for Each Product Type**:
1. **Perfect match** - Strong keyword in title (confidence ≥70%)
2. **Good match** - Strong keyword in description with weak keywords (confidence ≥50%)
3. **Edge case** - Borderline match that should still work

**Example**:
```bash
# Test all LED bulb patterns
pytest tests/test_product_patterns.py -k "led_bulb" -v

# Test all ceiling fan patterns
pytest tests/test_product_patterns.py -k "ceiling_fan" -v
```

---

#### 4. `test_validation_system.py` - Validation and Ground Truth Comparison
**Focus**: Tests validation functions that compare classifier predictions to manually labeled ground truth

**Test Classes**:
- `TestGroundTruthMapping` (44 tests) - Tests mapping from ground truth types to classifier types
- `TestAccuracyMetrics` (5 tests) - Tests accuracy calculation functions
- `TestConfusionMatrix` (4 tests) - Tests confusion matrix building
- `TestErrorAnalysis` (4 tests) - Tests error identification and reporting
- `TestEndToEndValidation` (6 tests) - Integration tests with actual data
- `TestValidationEdgeCases` (2 tests) - Tests edge case handling

**Key Tests**:
- ✓ Ground truth type mappings (e.g., `recessed_light_fixture` → `Recessed Light`)
- ✓ Accuracy calculation with filtering of missing data
- ✓ Accuracy breakdown by difficulty level (easy/medium/hard)
- ✓ Confusion matrix generation and sorting
- ✓ Error analysis with low confidence identification
- ✓ Validation on actual ground truth data

**Example**:
```bash
# Test validation with actual ground truth
pytest tests/test_validation_system.py::TestEndToEndValidation::test_validation_on_actual_ground_truth -v

# Test confusion matrix building
pytest tests/test_validation_system.py::TestConfusionMatrix -v
```

---

#### 5. `test_integration_pipeline.py` - End-to-End Pipeline Tests
**Focus**: Tests the complete classification pipeline from data loading to statistics generation

**Test Classes**:
- `TestIntegrationPipeline` - Complete integration test suite

**Test Categories**:
1. **Data Loading Tests** (2 tests) - Load and validate dataset structure
2. **Small Subset Tests** (2 tests) - Quick classification tests with 10 products
3. **Full Dataset Tests** (6 tests, marked `@slow`) - Complete 425-product classification
4. **Output Format Tests** (3 tests) - Verify result structure and formatting
5. **Performance Tests** (2 tests, marked `@slow`) - Benchmark classification speed
6. **Statistics Generation Tests** (4 tests) - Test statistics calculation
7. **Edge Case Tests** (6 tests) - Empty products, special characters, long descriptions
8. **End-to-End Smoke Test** (1 test, marked `@slow`) - Complete pipeline simulation

**Key Tests**:
- ✓ Load and validate 425 products from dataset
- ✓ Classify all products without crashes
- ✓ Validate result structure (index, title, product_type, confidence, etc.)
- ✓ Confidence scores in valid range (0-100)
- ✓ Performance benchmarks (< 1 second per product)
- ✓ Handle empty title/description gracefully
- ✓ Handle very long descriptions (10,000+ chars)
- ✓ Handle special characters and Unicode

**Example**:
```bash
# Run quick integration test (10 products)
pytest tests/test_integration_pipeline.py::TestIntegrationPipeline::test_classify_small_subset -v

# Run full integration test (425 products, slow)
pytest tests/test_integration_pipeline.py::TestIntegrationPipeline::test_classify_full_dataset -v

# Run end-to-end pipeline test
pytest tests/test_integration_pipeline.py::TestIntegrationPipeline::test_end_to_end_pipeline -v
```

---

#### 6. `test_classifier.py` - Basic Classifier Tests
**Focus**: Tests basic clustering and classification logic

**Test Classes**:
- `TestClassifier` - Automated test suite for product clustering

**Test Methods**:
- `test_lighting_products` (3 tests) - LED bulbs, ceiling fans, fixtures
- `test_electrical_products` (3 tests) - Circuit breakers, outlets, switches
- `test_plumbing_products` (6 tests) - Faucets, toilets, valves
- `test_tools_products` (2 tests) - Drills, saws
- `test_locks_products` (2 tests) - Deadbolts, door locks
- `test_hardware_products` (2 tests) - Screws, nails
- `test_paint_products` (3 tests) - Interior paint, primer, stain
- `test_word_boundary_matching` (2 tests) - Prevent false matches
- `test_empty_products` (2 tests) - Handle invalid products
- `test_confidence_scores` (2 tests) - Verify scoring
- `test_ambiguous_products` (1 test) - Multi-cluster matches

**Example**:
```bash
# Test plumbing classification
pytest tests/test_classifier.py::TestClassifier::test_plumbing_products -v

# Test word boundary matching (prevents "stain" matching "stainless")
pytest tests/test_classifier.py::TestClassifier::test_word_boundary_matching -v
```

---

## Test Fixtures (conftest.py)

The `conftest.py` file provides reusable fixtures that are automatically available to all tests.

### Path Fixtures
- `project_root` - Project root directory
- `data_dir` - Data directory path
- `scripts_dir` - Scripts directory path

### Data Loading Fixtures
- `ground_truth_data` - Ground truth JSON data (metadata + samples)
- `ground_truth_samples` - Just the samples array
- `full_dataset` - All 425 products from scraped_data_output.json
- `small_dataset` - First 10 products (for quick tests)

### Sample Product Fixtures
- `sample_led_bulb` - Realistic LED bulb with specs
- `sample_ceiling_fan` - Ceiling fan with remote
- `sample_circuit_breaker` - 20A circuit breaker
- `sample_faucet` - Kitchen pull-down faucet
- `sample_drill` - Cordless drill with batteries
- `all_sample_products` - List of all 5 sample products

### Edge Case Fixtures
- `edge_case_chandelier_bulb` - LED bulb FOR chandeliers (tests negative keyword fix)
- `edge_case_pendant_bulb` - LED bulb FOR pendants (tests negative keyword fix)
- `all_edge_cases` - List of all edge case products

### Classifier Fixtures
- `classifier` - Fresh ProductClassifier instance for each test (function scope)
- `classifier_session` - Shared ProductClassifier instance (session scope, faster)

### Validation Fixtures
- `expected_classifications` - Expected product types for sample products

---

## Coverage Summary

### Current Coverage Status

To check current coverage:
```bash
make test-coverage
```

This generates:
- **HTML Report**: `reports/coverage/index.html` (detailed line-by-line coverage)
- **Terminal Report**: Shows coverage % and missing lines
- **JSON Report**: `reports/coverage.json` (for CI/CD)

### Coverage Target: 80%+

The test suite is configured to fail if coverage drops below 80% (see `pytest.ini`).

### What's Covered

✅ **Well-Covered (80%+ coverage)**:
- Core utility functions (normalize_text, contains_keyword)
- Scoring calculations (calculate_match_score)
- Product pattern matching
- Classification workflow (classify_product, classify_all_products)
- Validation functions (accuracy metrics, confusion matrix, error analysis)
- Ground truth mapping

✅ **Thoroughly Tested**:
- Edge cases (chandelier bulbs, pendant bulbs, empty products)
- Negative keyword handling and exceptions
- Word boundary matching
- Case-insensitive keyword matching
- Multi-word keyword matching

### What's NOT Covered (If Anything)

To see what's missing:
```bash
# View terminal coverage report with missing lines
make coverage-report

# Open detailed HTML coverage report
make coverage-open
```

The HTML report shows:
- Green lines = covered by tests
- Red lines = not covered by tests
- Yellow lines = partially covered

---

## Running Tests - Command Reference

### Basic Commands

```bash
# Run all tests
make test
pytest tests -v

# Run with coverage
make test-coverage

# Run fast (stop on first failure)
make test-fast
pytest tests -v -x

# Run quietly
make test-quiet
pytest tests -q
```

### Run Specific Tests

```bash
# Run specific test file
pytest tests/test_scoring_system.py -v

# Run specific test class
pytest tests/test_scoring_system.py::TestScoringSystem -v

# Run specific test function
pytest tests/test_scoring_system.py::TestScoringSystem::test_strong_keyword_in_title -v

# Run tests matching keyword
pytest tests -k "chandelier" -v
pytest tests -k "scoring" -v
```

### Filter by Test Markers

```bash
# Run only fast tests (exclude slow integration tests)
pytest tests -m "not slow" -v
make test-not-slow

# Run only slow tests (integration tests with full dataset)
pytest tests -m slow -v

# Run only unit tests
pytest tests -m unit -v
make test-unit

# Run only integration tests
pytest tests -m integration -v
make test-integration
```

### Advanced Options

```bash
# Run in parallel (requires pytest-xdist)
make test-parallel
pytest tests -v -n auto

# Show local variables in tracebacks
pytest tests -v -l

# Show print statements
pytest tests -v -s

# Extra verbose with full tracebacks
pytest tests -vv -s --tb=long

# Debug mode (drop into debugger on failure)
make test-debug
pytest tests -vv -s --pdb

# Run only previously failed tests
make test-last-failed
pytest tests -v --lf

# Show test durations (slowest 10)
pytest tests -v --durations=10
```

### Coverage Commands

```bash
# Generate coverage report (HTML + terminal)
make coverage
make test-coverage

# Generate HTML coverage report only
make coverage-html

# Show terminal coverage report
make coverage-report

# Open HTML coverage report in browser
make coverage-open
```

### Information Commands

```bash
# List all available tests
make list-tests
pytest tests --collect-only -q

# Show all test markers
make test-markers
pytest --markers

# Show all fixtures
make test-fixtures
pytest --fixtures
```

### Cleanup

```bash
# Clean test artifacts and cache
make clean

# Clean coverage reports
make clean-coverage

# Clean everything
make clean-all
```

---

## Test Markers

Tests can be marked with custom markers for organization and filtering.

### Available Markers

- `@pytest.mark.slow` - Tests that take longer to run (uses full 425-product dataset)
- `@pytest.mark.integration` - Integration tests (end-to-end pipeline)
- `@pytest.mark.unit` - Unit tests (isolated function tests)
- `@pytest.mark.classifier` - Tests for product classifier
- `@pytest.mark.validation` - Tests for validation scripts

### Using Markers

```bash
# Run only fast tests
pytest tests -m "not slow" -v

# Run only unit tests
pytest tests -m unit -v

# Run integration and slow tests
pytest tests -m "integration or slow" -v

# Run everything except slow tests
pytest tests -m "not slow" -v
```

### How to Mark Tests

```python
import pytest

@pytest.mark.slow
def test_full_dataset_classification(classifier, full_dataset):
    """This test uses all 425 products - slow but comprehensive"""
    results = classifier.classify_all_products(full_dataset)
    assert len(results) == 425

@pytest.mark.unit
def test_normalize_text(classifier):
    """Fast unit test for text normalization"""
    result = classifier.normalize_text("LED Light Bulb")
    assert result == "led light bulb"
```

---

## Writing New Tests

### Test File Naming Convention

- Test files must start with `test_` (e.g., `test_new_feature.py`)
- Test files must be in the `tests/` directory
- Test classes must start with `Test` (e.g., `class TestNewFeature`)
- Test functions must start with `test_` (e.g., `def test_something()`)

### Basic Test Template

```python
import pytest
from classify_products import ProductClassifier


class TestNewFeature:
    """Test suite for new feature."""

    def test_basic_functionality(self, classifier):
        """Test basic functionality of new feature."""
        # Arrange
        product = {
            'title': 'LED Light Bulb',
            'description': 'Energy efficient bulb',
            'brand': 'Test Brand',
            'price': 9.97
        }

        # Act
        result = classifier.classify_product(product)

        # Assert
        assert result['product_type'] == 'LED Light Bulb'
        assert result['confidence'] >= 70

    @pytest.mark.slow
    def test_with_full_dataset(self, classifier, full_dataset):
        """Test with complete dataset (marked as slow)."""
        results = classifier.classify_all_products(full_dataset)
        assert len(results) == 425
```

### Using Fixtures

```python
def test_with_sample_led_bulb(classifier, sample_led_bulb):
    """Test uses the sample_led_bulb fixture from conftest.py"""
    result = classifier.classify_product(sample_led_bulb)
    assert result['product_type'] == 'LED Light Bulb'
    assert result['confidence'] >= 80
```

### Adding New Fixtures

Add to `conftest.py`:
```python
@pytest.fixture
def sample_new_product():
    """Sample product for testing."""
    return {
        'title': 'New Product Type',
        'description': 'Description of new product',
        'brand': 'Test Brand',
        'price': 19.97
    }
```

---

## Continuous Integration

### CI Commands

```bash
# Full CI pipeline (clean + test with coverage)
make ci

# Fast CI pipeline (clean + fast tests only)
make ci-fast
```

### GitHub Actions / CI Configuration

Example `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          make install
          make install-test
      - name: Run tests with coverage
        run: make test-coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./reports/coverage.json
```

---

## Troubleshooting

### Common Issues

**Issue**: `pytest: command not found`
```bash
# Solution: Install pytest
make install-test
# Or manually:
pip install pytest pytest-cov
```

**Issue**: `ModuleNotFoundError: No module named 'classify_products'`
```bash
# Solution: Run tests from project root directory
cd /home/user/CC
pytest tests -v
```

**Issue**: Tests are too slow
```bash
# Solution: Run only fast tests
make test-not-slow
pytest tests -m "not slow" -v
```

**Issue**: Coverage below 80%
```bash
# Solution: View coverage report to see what's missing
make coverage-open

# Or show in terminal
make coverage-report
```

**Issue**: All tests failing
```bash
# Solution: Check if data files exist
ls data/scraped_data_output.json
ls data/ground_truth.json

# Run a single simple test to debug
pytest tests/test_product_classifier_core.py::TestNormalizeText::test_normalize_basic_text -v
```

---

## Test Results and Reports

### Test Execution Output

When you run tests, you'll see:
```
tests/test_scoring_system.py::TestScoringSystem::test_strong_keyword_in_title PASSED [ 1%]
tests/test_scoring_system.py::TestScoringSystem::test_chandelier_bulb_exception PASSED [ 2%]
...
===================== 210 passed in 45.23s ======================
```

### Coverage Report Output

```
---------- coverage: platform linux, python 3.11.x -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
scripts/classify_products.py        450     45    90%   123-145, 234-256
scripts/validate_system.py          200     15    92%   45-60
---------------------------------------------------------------
TOTAL                               650     60    91%
```

### HTML Coverage Report

Open `reports/coverage/index.html` to see:
- Overall coverage percentage
- Coverage by file
- Line-by-line coverage highlighting
- Branch coverage
- Functions not covered

---

## Contributing Tests

When adding new features or fixing bugs:

1. **Write tests first** (TDD approach)
2. **Test both success and failure cases**
3. **Add edge cases** (empty values, special characters, boundary conditions)
4. **Use descriptive test names** (`test_chandelier_bulb_not_blocked_by_negative_keyword`)
5. **Add docstrings** explaining what the test validates
6. **Mark slow tests** with `@pytest.mark.slow`
7. **Run full test suite** before committing: `make test-coverage`
8. **Ensure coverage doesn't drop** below 80%

---

## References

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-cov Documentation**: https://pytest-cov.readthedocs.io/
- **Project Scripts**: `/home/user/CC/scripts/`
- **Test Fixtures**: `/home/user/CC/tests/conftest.py`
- **Test Configuration**: `/home/user/CC/pytest.ini`
- **Makefile**: `/home/user/CC/Makefile`

---

## Summary

The CC Product Classification test suite provides comprehensive coverage of:
- ✅ 210 test functions across 6 test modules
- ✅ Core utilities, scoring system, product patterns
- ✅ Validation against ground truth
- ✅ End-to-end integration pipeline
- ✅ Edge cases and bug fixes (chandelier bulbs, pendant bulbs)
- ✅ 80%+ code coverage target
- ✅ Fast tests and slow integration tests
- ✅ Reusable fixtures for common test scenarios

**Quick Commands**:
```bash
make test                 # Run all tests
make test-coverage        # Run with coverage
make test-not-slow        # Run only fast tests
pytest tests -k "keyword" # Run tests matching keyword
make coverage-open        # View coverage report
```

For questions or issues, refer to the test files themselves - they contain detailed docstrings and examples.
