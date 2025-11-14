# Integration Tests for Product Classification Pipeline

## Overview

The `test_integration_pipeline.py` file contains comprehensive integration tests for the complete product classification pipeline. These tests verify end-to-end functionality from data loading through classification to statistics generation.

## Test Coverage

### 1. Data Loading Tests (2 tests)
- ✅ Load full dataset (425 products)
- ✅ Verify all products have required fields (title, description, brand, price)

### 2. Small Subset Tests (2 tests)
- ✅ Classify 10 products successfully
- ✅ No crashes or exceptions during classification

### 3. Full Dataset Tests (4 tests)
- ✅ Classify all 425 products
- ✅ Verify no None results
- ✅ Verify all product_types are valid
- ✅ Verify all confidence scores are in range (0-100)

### 4. Output Format Tests (3 tests)
- ✅ Result structure validation (9 required fields)
- ✅ Confidence level validation (High/Medium/Low/Very Low/No Match/No Data)
- ✅ Title truncation to 100 characters

### 5. Performance Tests (2 tests)
- ✅ 100 products in <100 seconds
- ✅ Consistent performance across runs

### 6. Statistics Generation Tests (4 tests)
- ✅ Statistics structure validation
- ✅ Count verification (type_distribution, confidence_distribution)
- ✅ Full dataset statistics generation
- ✅ Low confidence threshold accuracy

### 7. Edge Case Tests (6 tests)
- ✅ Empty title and description → "Unknown - Missing Data"
- ✅ Title only (no description) → Still classifies
- ✅ Very long description (10,000 chars) → Handles gracefully
- ✅ Missing optional fields → Classifies based on available data
- ✅ Special characters (Unicode, emojis) → No crashes
- ✅ End-to-end pipeline test → Complete workflow

### 8. Module Tests (1 test)
- ✅ Import and initialization verification

**Total: 24 tests**

## Running the Tests

### Run All Tests (Including Slow)
```bash
python3 -m pytest tests/test_integration_pipeline.py -v
```

### Run Only Fast Tests (Skip Slow)
```bash
python3 -m pytest tests/test_integration_pipeline.py -m "not slow" -v
```

### Run Specific Test
```bash
python3 -m pytest tests/test_integration_pipeline.py::TestIntegrationPipeline::test_classify_small_subset -v
```

### Run with Output Showing
```bash
python3 -m pytest tests/test_integration_pipeline.py -v -s
```

### Run Without Coverage
```bash
python3 -m pytest tests/test_integration_pipeline.py -v --no-cov
```

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.slow` - Tests that take >5 seconds (full dataset tests)
- `@pytest.mark.integration` - Auto-applied to all integration tests

### Examples:

Run only slow tests:
```bash
python3 -m pytest tests/test_integration_pipeline.py -m "slow" -v
```

Run only fast tests:
```bash
python3 -m pytest tests/test_integration_pipeline.py -m "not slow" -v
```

## Expected Results

### Fast Tests (7 tests)
- Should complete in <1 second
- All tests should PASS

### Slow Tests (17 tests)
- Should complete in <30 seconds total
- All tests should PASS
- Full dataset (425 products) classification tests included

## Test Output

Each test provides helpful output:

```
✓ Successfully classified 10 products
  Sample: 'Feit Electric 60-Watt...' → LED Light Bulb

✓ Result structure is correct
  Sample result keys: ['index', 'title', 'brand', 'price', ...]

📊 Classification Results:
  Total products: 425
  Product types found: 78
  Average confidence: 75.3%
```

## What These Tests Verify

1. **Data Integrity**: All 425 products load correctly with required fields
2. **Classification Completeness**: Every product gets classified (no None results)
3. **Result Structure**: All results have the 9 required fields with correct types
4. **Confidence Scoring**: All scores are in valid range (0-100)
5. **Performance**: Classification completes in reasonable time
6. **Statistics Accuracy**: Counts and distributions are mathematically correct
7. **Edge Case Handling**: Graceful handling of missing data, long text, special chars
8. **End-to-End Flow**: Complete pipeline from load → classify → stats works

## Troubleshooting

### Import Errors
If you see import errors, make sure you're running from the project root:
```bash
cd /home/user/CC
python3 -m pytest tests/test_integration_pipeline.py
```

### Fixture Errors
The tests use fixtures from `tests/conftest.py`. Make sure that file exists.

### Data File Missing
Tests require `/home/user/CC/data/scraped_data_output.json` to exist.

## Integration with CI/CD

These tests are designed to run in continuous integration:

```yaml
# Example GitHub Actions workflow
- name: Run Integration Tests
  run: |
    python3 -m pytest tests/test_integration_pipeline.py -m "not slow" -v

- name: Run Full Test Suite (with slow tests)
  run: |
    python3 -m pytest tests/test_integration_pipeline.py -v
```

## Test Philosophy

These tests follow the **integration testing** philosophy:

- ✅ Test complete workflows (not isolated units)
- ✅ Use real data (425 actual products)
- ✅ Verify end-to-end behavior
- ✅ Catch regressions in the full pipeline
- ✅ Validate production-like scenarios

For unit tests (testing individual functions in isolation), see:
- `tests/test_product_classifier_core.py`
- `tests/test_scoring_system.py`
- `tests/test_product_patterns.py`

## Next Steps

After these integration tests pass, you can:

1. Run validation against ground truth:
   ```bash
   python3 scripts/validate_system.py
   ```

2. View coverage report:
   ```bash
   python3 -m pytest tests/ --cov=scripts --cov-report=html
   # Open reports/coverage/index.html
   ```

3. Run full test suite:
   ```bash
   python3 -m pytest tests/ -v
   ```

---

**Created**: 2025-11-14
**Last Updated**: 2025-11-14
**Test Count**: 24 tests
**Expected Pass Rate**: 100%
