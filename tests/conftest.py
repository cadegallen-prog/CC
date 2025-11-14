"""
Pytest Configuration and Fixtures for CC Product Classification Tests

This file provides reusable fixtures for testing the product classification system.
Fixtures provide sample data, test products, and classifier instances.
"""

import json
import pytest
from pathlib import Path
import sys

# Add scripts directory to path so we can import from it
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Import after adding to path
from classify_products import ProductClassifier


# ============================================================================
# PATH FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Returns the project root directory path."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir(project_root):
    """Returns the data directory path."""
    return project_root / "data"


@pytest.fixture(scope="session")
def scripts_dir(project_root):
    """Returns the scripts directory path."""
    return project_root / "scripts"


# ============================================================================
# DATA LOADING FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def ground_truth_data(data_dir):
    """
    Loads ground truth data from ground_truth.json.

    Returns:
        dict: Ground truth data with 'metadata' and 'samples' keys
    """
    ground_truth_path = data_dir / "ground_truth.json"
    if not ground_truth_path.exists():
        pytest.skip(f"Ground truth file not found: {ground_truth_path}")

    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def ground_truth_samples(ground_truth_data):
    """
    Returns just the samples array from ground truth data.

    Returns:
        list: List of manually labeled product samples
    """
    return ground_truth_data.get('samples', [])


@pytest.fixture(scope="session")
def full_dataset(data_dir):
    """
    Loads the full dataset from scraped_data_output.json.

    Returns:
        list: All 425 products with complete data
    """
    dataset_path = data_dir / "scraped_data_output.json"
    if not dataset_path.exists():
        pytest.skip(f"Dataset file not found: {dataset_path}")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="function")
def small_dataset(full_dataset):
    """
    Returns a small subset of the full dataset for quick tests.

    Returns:
        list: First 10 products from the dataset
    """
    return full_dataset[:10]


# ============================================================================
# SAMPLE PRODUCT FIXTURES
# ============================================================================

@pytest.fixture
def sample_led_bulb():
    """
    Sample LED light bulb product for testing.

    Returns:
        dict: LED bulb product with realistic data
    """
    return {
        "title": "Feit Electric 60-Watt Equivalent A19 Dimmable LED Light Bulb Soft White (8-Pack)",
        "description": "Upgrade your lighting to Feit Electric's elegant LED bulbs. These dimmable A19 bulbs provide 800 lumens of soft white light while using just 8.8 watts of electricity, up to 85% less energy than standard 60-watt incandescent bulbs. A 90+ CRI infuses vibrance into your space, bringing out truer colors and more natural skin tones. Get up to 15,000 hours of life with an estimated energy cost of only $1.06 per year.",
        "brand": "Feit Electric",
        "model": "A800/827/10KLED/2",
        "price": 19.97,
        "rating": 4.6,
        "reviews": 1234,
        "structured_specifications": {
            "wattage": {"value": 8.8, "unit": "W"},
            "lumens": {"value": 800, "unit": "lm"},
            "color_temp": {"value": 2700, "unit": "K"},
            "base_type": "E26",
            "dimmable": True,
            "lifespan": {"value": 15000, "unit": "hours"}
        }
    }


@pytest.fixture
def sample_ceiling_fan():
    """
    Sample ceiling fan product for testing.

    Returns:
        dict: Ceiling fan product with realistic data
    """
    return {
        "title": "Home Decorators Collection Mercer 52 in. LED Indoor Brushed Nickel Ceiling Fan with Light Kit and Remote Control",
        "description": "The Mercer 52 in. LED Indoor Ceiling Fan in Brushed Nickel brings modern style and efficient cooling to any room. This ceiling fan features a powerful DC motor that delivers superior air circulation while using up to 70% less energy than traditional fans. The integrated LED light kit provides bright, energy-efficient illumination. Includes a handheld remote control for convenient operation.",
        "brand": "Home Decorators Collection",
        "model": "YG493-BN",
        "price": 149.00,
        "rating": 4.3,
        "reviews": 892,
        "structured_specifications": {
            "fan_blades": 5,
            "blade_span": {"value": 52, "unit": "in"},
            "cfm": {"value": 5200, "unit": "CFM"},
            "motor_type": "DC Motor",
            "remote_control": True,
            "reversible": True
        }
    }


@pytest.fixture
def sample_circuit_breaker():
    """
    Sample circuit breaker product for testing.

    Returns:
        dict: Circuit breaker product with realistic data
    """
    return {
        "title": "Square D Homeline 20 Amp Single-Pole Circuit Breaker HOM120CP",
        "description": "The Square D Homeline 20 Amp Single-Pole Circuit Breaker is the workhorse of the Homeline load center. It's UL-listed and ANSI-certified. The Homeline circuit breaker fits every Homeline load center and CSED. It provides overload and short-circuit protection to your electrical system. The circuit breaker is also rated for 120/240 Volt AC and 10,000 AIR.",
        "brand": "Square D",
        "model": "HOM120CP",
        "price": 4.87,
        "rating": 4.8,
        "reviews": 2156,
        "structured_specifications": {
            "amperage": {"value": 20, "unit": "A"},
            "voltage": {"value": 120, "unit": "V"},
            "poles": 1,
            "circuit_type": "Standard",
            "trip_type": "Thermal-Magnetic"
        }
    }


@pytest.fixture
def sample_faucet():
    """
    Sample kitchen faucet product for testing.

    Returns:
        dict: Faucet product with realistic data
    """
    return {
        "title": "Delta Leland Single-Handle Pull-Down Sprayer Kitchen Faucet with MagnaTite Docking in Venetian Bronze",
        "description": "Delta's Leland Kitchen Faucet combines timeless design with innovative technology. The pull-down spray wand comes free with a gentle tug and gives you total flexibility. MagnaTite Docking uses a powerful integrated magnet to snap your faucet spray wand precisely into place and hold it there. Touch-Clean spray holes allow you to easily wipe away calcium and lime build-up.",
        "brand": "Delta",
        "model": "9178-RB-DST",
        "price": 298.00,
        "rating": 4.5,
        "reviews": 3421,
        "structured_specifications": {
            "faucet_type": "Pull-Down",
            "handle_type": "Single Handle",
            "finish": "Venetian Bronze",
            "spray_modes": 2,
            "flow_rate": {"value": 1.8, "unit": "GPM"}
        }
    }


@pytest.fixture
def sample_drill():
    """
    Sample power drill product for testing.

    Returns:
        dict: Power drill product with realistic data
    """
    return {
        "title": "DEWALT 20V MAX Cordless Drill/Driver Kit with 2 Batteries and Charger (DCD771C2)",
        "description": "The DEWALT 20V MAX Cordless Drill/Driver Kit is compact and lightweight, designed for small spaces and overhead work. The high-speed transmission delivers 2 speeds (0-450 & 0-1,500 RPM) for a range of drilling and fastening applications. The 1/2 in. ratcheting chuck provides tight bit gripping strength. Includes 2 compact 1.3Ah batteries, charger, and contractor bag.",
        "brand": "DEWALT",
        "model": "DCD771C2",
        "price": 99.00,
        "rating": 4.7,
        "reviews": 5678,
        "structured_specifications": {
            "voltage": {"value": 20, "unit": "V"},
            "battery_type": "Lithium-Ion",
            "battery_capacity": {"value": 1.3, "unit": "Ah"},
            "chuck_size": {"value": 0.5, "unit": "in"},
            "max_torque": {"value": 300, "unit": "in-lbs"},
            "speeds": 2
        }
    }


@pytest.fixture
def all_sample_products(sample_led_bulb, sample_ceiling_fan, sample_circuit_breaker,
                        sample_faucet, sample_drill):
    """
    Returns all sample products in a list for batch testing.

    Returns:
        list: All 5 sample products (bulb, fan, breaker, faucet, drill)
    """
    return [
        sample_led_bulb,
        sample_ceiling_fan,
        sample_circuit_breaker,
        sample_faucet,
        sample_drill
    ]


# ============================================================================
# CLASSIFIER FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def classifier():
    """
    Creates a fresh ProductClassifier instance for each test.

    Returns:
        ProductClassifier: Initialized classifier instance
    """
    return ProductClassifier()


@pytest.fixture(scope="session")
def classifier_session():
    """
    Creates a ProductClassifier instance that persists for the entire test session.
    Use this for read-only tests to improve performance.

    Returns:
        ProductClassifier: Initialized classifier instance
    """
    return ProductClassifier()


# ============================================================================
# EDGE CASE FIXTURES
# ============================================================================

@pytest.fixture
def edge_case_chandelier_bulb():
    """
    Edge case: LED bulb FOR chandeliers (should be classified as bulb, not chandelier).
    This tests the negative keyword bug fix.

    Returns:
        dict: Chandelier LED bulb product
    """
    return {
        "title": "Feit Electric Chandelier LED Light Bulb Soft White 60W Equivalent",
        "description": "Elegant chandelier LED light bulbs designed for use in chandelier fixtures. These decorative bulbs provide 500 lumens of soft white light while using just 5.5 watts. Perfect for chandeliers, sconces, and decorative lighting.",
        "brand": "Feit Electric",
        "model": "CHANDELIERLED60",
        "price": 12.97,
        "rating": 4.4,
        "structured_specifications": {
            "wattage": {"value": 5.5, "unit": "W"},
            "lumens": {"value": 500, "unit": "lm"},
            "color_temp": {"value": 2700, "unit": "K"},
            "base_type": "E12",
            "bulb_type": "Candelabra"
        }
    }


@pytest.fixture
def edge_case_pendant_bulb():
    """
    Edge case: LED bulb FOR pendants (should be classified as bulb, not pendant light).

    Returns:
        dict: Pendant LED bulb product
    """
    return {
        "title": "Philips Pendant LED Light Bulb Vintage Style 40W Equivalent",
        "description": "Vintage-style LED bulbs ideal for pendant light fixtures. These Edison-style bulbs provide warm amber light with visible LED filaments. Perfect for modern pendant lights and exposed bulb fixtures.",
        "brand": "Philips",
        "model": "PENDANTLED40",
        "price": 9.97,
        "rating": 4.6,
        "structured_specifications": {
            "wattage": {"value": 4.5, "unit": "W"},
            "lumens": {"value": 350, "unit": "lm"},
            "color_temp": {"value": 2200, "unit": "K"},
            "base_type": "E26",
            "bulb_shape": "ST19"
        }
    }


@pytest.fixture
def all_edge_cases(edge_case_chandelier_bulb, edge_case_pendant_bulb):
    """
    Returns all edge case products for comprehensive testing.

    Returns:
        list: All edge case products
    """
    return [
        edge_case_chandelier_bulb,
        edge_case_pendant_bulb
    ]


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

@pytest.fixture
def expected_classifications():
    """
    Returns expected classifications for sample products.
    Used for validation testing.

    Returns:
        dict: Mapping of product fixture names to expected product types
    """
    return {
        'sample_led_bulb': 'LED Light Bulb',
        'sample_ceiling_fan': 'Ceiling Fan',
        'sample_circuit_breaker': 'Circuit Breaker',
        'sample_faucet': 'Kitchen Faucet',
        'sample_drill': 'Power Drill',
        'edge_case_chandelier_bulb': 'LED Light Bulb',  # Should be bulb, not chandelier!
        'edge_case_pendant_bulb': 'LED Light Bulb'  # Should be bulb, not pendant!
    }


# ============================================================================
# SESSION CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """
    Pytest configuration hook.
    Adds custom markers and configuration.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.
    """
    for item in items:
        # Auto-mark tests based on their names
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if "full_dataset" in item.fixturenames:
            item.add_marker(pytest.mark.slow)
