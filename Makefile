# Makefile for CC Product Classification Project
# Provides convenient commands for testing, coverage, and development

# ============================================================================
# VARIABLES
# ============================================================================

# Python interpreter (use the one in venv)
PYTHON := python3
PYTEST := $(PYTHON) -m pytest
PIP := $(PYTHON) -m pip

# Directories
SCRIPTS_DIR := scripts
TESTS_DIR := tests
REPORTS_DIR := reports
COVERAGE_DIR := reports/coverage

# Test files
TEST_FILE ?= tests/

# ============================================================================
# MAIN TARGETS
# ============================================================================

.PHONY: help
help:
	@echo "CC Product Classification - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests with standard output"
	@echo "  make test-coverage     - Run tests with coverage report"
	@echo "  make test-fast         - Run tests, stop on first failure"
	@echo "  make test-specific     - Run specific test file (usage: make test-specific TEST_FILE=tests/test_classifier.py)"
	@echo "  make test-verbose      - Run tests with extra verbose output"
	@echo "  make test-quiet        - Run tests with minimal output"
	@echo ""
	@echo "Coverage:"
	@echo "  make coverage          - Generate coverage report (HTML + terminal)"
	@echo "  make coverage-html     - Generate HTML coverage report only"
	@echo "  make coverage-report   - Show terminal coverage report"
	@echo "  make coverage-open     - Open HTML coverage report in browser"
	@echo ""
	@echo "Test Organization:"
	@echo "  make test-unit         - Run only unit tests"
	@echo "  make test-integration  - Run only integration tests"
	@echo "  make test-classifier   - Run only classifier tests"
	@echo "  make test-not-slow     - Run all tests except slow ones"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean             - Remove test artifacts and cache"
	@echo "  make clean-coverage    - Remove coverage reports"
	@echo "  make clean-all         - Remove all generated files"
	@echo ""
	@echo "Development:"
	@echo "  make install           - Install development dependencies"
	@echo "  make install-test      - Install test dependencies"
	@echo "  make lint              - Run code linters"
	@echo ""

# ============================================================================
# TESTING TARGETS
# ============================================================================

.PHONY: test
test:
	@echo "Running all tests..."
	$(PYTEST) $(TESTS_DIR) -v

.PHONY: test-coverage
test-coverage:
	@echo "Running tests with coverage analysis..."
	$(PYTEST) $(TESTS_DIR) -v \
		--cov=$(SCRIPTS_DIR) \
		--cov-report=html:$(COVERAGE_DIR) \
		--cov-report=term-missing \
		--cov-report=json:reports/coverage.json
	@echo ""
	@echo "Coverage reports generated:"
	@echo "  - HTML: $(COVERAGE_DIR)/index.html"
	@echo "  - JSON: reports/coverage.json"

.PHONY: test-fast
test-fast:
	@echo "Running tests (stop on first failure)..."
	$(PYTEST) $(TESTS_DIR) -v -x --tb=short

.PHONY: test-specific
test-specific:
	@echo "Running specific test file: $(TEST_FILE)"
	$(PYTEST) $(TEST_FILE) -v

.PHONY: test-verbose
test-verbose:
	@echo "Running tests with verbose output..."
	$(PYTEST) $(TESTS_DIR) -vv -s

.PHONY: test-quiet
test-quiet:
	@echo "Running tests (quiet mode)..."
	$(PYTEST) $(TESTS_DIR) -q

# ============================================================================
# COVERAGE TARGETS
# ============================================================================

.PHONY: coverage
coverage: test-coverage

.PHONY: coverage-html
coverage-html:
	@echo "Generating HTML coverage report..."
	$(PYTEST) $(TESTS_DIR) --cov=$(SCRIPTS_DIR) --cov-report=html:$(COVERAGE_DIR) --quiet
	@echo "HTML coverage report: $(COVERAGE_DIR)/index.html"

.PHONY: coverage-report
coverage-report:
	@echo "Showing coverage report..."
	$(PYTEST) $(TESTS_DIR) --cov=$(SCRIPTS_DIR) --cov-report=term-missing --quiet

.PHONY: coverage-open
coverage-open: coverage-html
	@echo "Opening coverage report in browser..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(COVERAGE_DIR)/index.html; \
	elif command -v open > /dev/null; then \
		open $(COVERAGE_DIR)/index.html; \
	else \
		echo "Could not open browser. Please open $(COVERAGE_DIR)/index.html manually"; \
	fi

# ============================================================================
# TEST ORGANIZATION TARGETS
# ============================================================================

.PHONY: test-unit
test-unit:
	@echo "Running unit tests only..."
	$(PYTEST) $(TESTS_DIR) -v -m unit

.PHONY: test-integration
test-integration:
	@echo "Running integration tests only..."
	$(PYTEST) $(TESTS_DIR) -v -m integration

.PHONY: test-classifier
test-classifier:
	@echo "Running classifier tests only..."
	$(PYTEST) $(TESTS_DIR) -v -m classifier

.PHONY: test-not-slow
test-not-slow:
	@echo "Running fast tests (excluding slow tests)..."
	$(PYTEST) $(TESTS_DIR) -v -m "not slow"

# ============================================================================
# CLEANUP TARGETS
# ============================================================================

.PHONY: clean
clean:
	@echo "Cleaning test artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage 2>/dev/null || true
	@echo "Cleanup complete!"

.PHONY: clean-coverage
clean-coverage:
	@echo "Cleaning coverage reports..."
	rm -rf $(REPORTS_DIR)/coverage 2>/dev/null || true
	rm -f $(REPORTS_DIR)/coverage.json 2>/dev/null || true
	rm -f $(REPORTS_DIR)/coverage.xml 2>/dev/null || true
	rm -f .coverage 2>/dev/null || true
	@echo "Coverage reports cleaned!"

.PHONY: clean-all
clean-all: clean clean-coverage
	@echo "All generated files cleaned!"

# ============================================================================
# DEVELOPMENT TARGETS
# ============================================================================

.PHONY: install
install:
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements_product_identifier.txt
	@echo "Dependencies installed!"

.PHONY: install-test
install-test:
	@echo "Installing test dependencies..."
	$(PIP) install pytest pytest-cov pytest-timeout pytest-xdist
	@echo "Test dependencies installed!"

.PHONY: lint
lint:
	@echo "Running linters..."
	@if command -v flake8 > /dev/null; then \
		flake8 $(SCRIPTS_DIR) --max-line-length=120 --exclude=__pycache__; \
	else \
		echo "flake8 not installed. Run: pip install flake8"; \
	fi

# ============================================================================
# ADVANCED TEST TARGETS
# ============================================================================

.PHONY: test-parallel
test-parallel:
	@echo "Running tests in parallel..."
	$(PYTEST) $(TESTS_DIR) -v -n auto

.PHONY: test-debug
test-debug:
	@echo "Running tests in debug mode..."
	$(PYTEST) $(TESTS_DIR) -vv -s --tb=long --pdb

.PHONY: test-last-failed
test-last-failed:
	@echo "Running only previously failed tests..."
	$(PYTEST) $(TESTS_DIR) -v --lf

.PHONY: test-failed-first
test-failed-first:
	@echo "Running failed tests first, then all tests..."
	$(PYTEST) $(TESTS_DIR) -v --ff

# ============================================================================
# CONTINUOUS INTEGRATION TARGETS
# ============================================================================

.PHONY: ci
ci: clean test-coverage
	@echo "CI pipeline complete!"

.PHONY: ci-fast
ci-fast: clean test-not-slow
	@echo "Fast CI pipeline complete!"

# ============================================================================
# INFORMATION TARGETS
# ============================================================================

.PHONY: list-tests
list-tests:
	@echo "Available tests:"
	$(PYTEST) $(TESTS_DIR) --collect-only -q

.PHONY: test-markers
test-markers:
	@echo "Available test markers:"
	$(PYTEST) --markers

.PHONY: test-fixtures
test-fixtures:
	@echo "Available fixtures:"
	$(PYTEST) --fixtures

# ============================================================================
# DEFAULT TARGET
# ============================================================================

.DEFAULT_GOAL := help
