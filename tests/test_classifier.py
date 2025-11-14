#!/usr/bin/env python3
"""
Automated Test Suite for Product Type Classifier
Tests all major functions of the classification system
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_cluster_assignment(product):
    """Replicate the cluster assignment logic from pattern_discovery.py"""
    import re

    title = product.get('title', '').lower()
    description = product.get('description', '').lower()
    combined = f"{title} {description}"

    cluster_seeds = {
        'lighting': ['light', 'bulb', 'lamp', 'led', 'fixture', 'lumens', 'watt', 'filament'],
        'electrical': ['breaker', 'switch', 'outlet', 'electrical', 'circuit', 'amp', 'volt', 'wire'],
        'smart_home': ['smart', 'wifi', 'keypad', 'electronic', 'digital', 'bluetooth'],
        'locks': ['lock', 'deadbolt', 'door', 'keyless', 'security', 'latch'],
        'paint': ['paint', 'primer', 'coating', 'stain', 'semi-gloss', 'latex', 'enamel'],
        'tools': ['drill', 'saw', 'tool', 'impact', 'cordless', 'battery', 'driver'],
        'hardware': ['screw', 'screws', 'nail', 'nails', 'fastener', 'anchor', 'bolt', 'nut'],
        'plumbing': ['pipe', 'faucet', 'valve', 'plumbing', 'water', 'drain'],
    }

    cluster_scores = defaultdict(int)
    for cluster_name, keywords in cluster_seeds.items():
        for keyword in keywords:
            # Use word boundary matching to avoid partial matches (e.g., "stain" in "stainless")
            if re.search(r'\b' + re.escape(keyword) + r'\b', combined):
                cluster_scores[cluster_name] += 1

    if cluster_scores:
        best_cluster = max(cluster_scores.items(), key=lambda x: x[1])[0]
        confidence_score = cluster_scores[best_cluster]
        return best_cluster, confidence_score, cluster_scores
    else:
        return 'uncategorized', 0, {}

# Test Suite
class TestClassifier:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def assert_equal(self, actual, expected, test_name):
        """Assert that actual equals expected"""
        if actual == expected:
            self.passed += 1
            self.tests.append({'name': test_name, 'status': 'PASS', 'message': f'Expected {expected}, got {expected}'})
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            self.tests.append({'name': test_name, 'status': 'FAIL', 'message': f'Expected {expected}, got {actual}'})
            print(f"  ✗ {test_name}: Expected {expected}, got {actual}")

    def assert_true(self, condition, test_name):
        """Assert that condition is true"""
        if condition:
            self.passed += 1
            self.tests.append({'name': test_name, 'status': 'PASS', 'message': 'Condition is true'})
            print(f"  ✓ {test_name}")
        else:
            self.failed += 1
            self.tests.append({'name': test_name, 'status': 'FAIL', 'message': 'Condition is false'})
            print(f"  ✗ {test_name}: Condition is false")

    def test_lighting_products(self):
        """Test lighting product classification"""
        print("\n1. Testing Lighting Products:")

        # Test LED bulb
        product = {'title': 'LED Light Bulb 60W', 'description': 'Energy efficient LED bulb with 800 lumens'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'lighting', 'LED bulb should be classified as lighting')

        # Test ceiling fan
        product = {'title': 'Ceiling Fan with Light', 'description': 'Indoor ceiling fan with integrated LED light'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'lighting', 'Ceiling fan with light should be classified as lighting')

        # Test light fixture
        product = {'title': 'Pendant Light Fixture', 'description': 'Modern pendant light fixture for kitchen'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'lighting', 'Pendant fixture should be classified as lighting')

    def test_electrical_products(self):
        """Test electrical product classification"""
        print("\n2. Testing Electrical Products:")

        # Test circuit breaker
        product = {'title': '20 Amp Circuit Breaker', 'description': 'Single pole circuit breaker for residential use'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'electrical', 'Circuit breaker should be classified as electrical')

        # Test outlet
        product = {'title': 'GFCI Outlet', 'description': 'Ground fault circuit interrupter outlet'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'electrical', 'GFCI outlet should be classified as electrical')

        # Test switch
        product = {'title': 'Light Switch', 'description': 'Single pole electrical switch'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'electrical', 'Switch should be classified as electrical')

    def test_plumbing_products(self):
        """Test plumbing product classification"""
        print("\n3. Testing Plumbing Products:")

        # Test faucet
        product = {'title': 'Kitchen Faucet', 'description': 'Stainless steel kitchen faucet with pull-down spray'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'plumbing', 'Faucet should be classified as plumbing')
        self.assert_true(conf >= 1, 'Faucet should have confidence >= 1')

        # Test toilet
        product = {'title': 'Dual Flush Toilet', 'description': 'Water-efficient toilet with dual flush system'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'plumbing', 'Toilet should be classified as plumbing')

        # Test valve
        product = {'title': 'Shut-off Valve', 'description': 'Quarter turn shut-off valve for plumbing'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'plumbing', 'Valve should be classified as plumbing')

        # Test bathroom faucet
        product = {'title': 'Bathroom Faucet', 'description': 'Chrome bathroom sink faucet'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'plumbing', 'Bathroom faucet should be classified as plumbing')
        self.assert_true(conf >= 1, 'Bathroom faucet should have confidence >= 1')

        # Test lavatory faucet
        product = {'title': 'Lavatory Faucet', 'description': 'Single handle lavatory faucet'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'plumbing', 'Lavatory faucet should be classified as plumbing')
        self.assert_true(conf >= 1, 'Lavatory faucet should have confidence >= 1')

        # Test pull-down faucet
        product = {'title': 'Pull-Down Faucet', 'description': 'Kitchen pull-down spray faucet'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'plumbing', 'Pull-down faucet should be classified as plumbing')
        self.assert_true(conf >= 1, 'Pull-down faucet should have confidence >= 1')

    def test_tools_products(self):
        """Test tools product classification"""
        print("\n4. Testing Tools Products:")

        # Test drill
        product = {'title': 'Cordless Drill', 'description': '20V cordless drill with battery and charger'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'tools', 'Drill should be classified as tools')

        # Test saw
        product = {'title': 'Circular Saw', 'description': 'Electric circular saw for cutting wood'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'tools', 'Saw should be classified as tools')

    def test_locks_products(self):
        """Test locks product classification"""
        print("\n5. Testing Locks Products:")

        # Test deadbolt
        product = {'title': 'Smart Deadbolt Lock', 'description': 'Electronic deadbolt with keyless entry'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'locks', 'Smart deadbolt should be classified as locks')

        # Test door lock
        product = {'title': 'Door Lock Set', 'description': 'Entry door lock with keyed cylinder'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'locks', 'Door lock should be classified as locks')

    def test_hardware_products(self):
        """Test hardware product classification"""
        print("\n6. Testing Hardware Products:")

        # Test screws
        product = {'title': 'Wood Screws Pack', 'description': '100-pack of wood screws for construction'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'hardware', 'Screws should be classified as hardware')

        # Test nails
        product = {'title': 'Framing Nails', 'description': 'Galvanized framing nails for construction'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'hardware', 'Nails should be classified as hardware')

    def test_paint_products(self):
        """Test paint product classification"""
        print("\n7. Testing Paint Products:")

        # Test paint
        product = {'title': 'Interior Paint', 'description': 'Latex interior paint in semi-gloss finish'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'paint', 'Interior paint should be classified as paint')

        # Test primer
        product = {'title': 'Paint Primer', 'description': 'Multi-purpose primer for walls and ceilings'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'paint', 'Primer should be classified as paint')

        # Test wood stain (should be paint)
        product = {'title': 'Wood Stain', 'description': 'Oil-based wood stain for furniture'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'paint', 'Wood stain should be classified as paint')

    def test_word_boundary_matching(self):
        """Test that word boundary matching prevents false matches"""
        print("\n8. Testing Word Boundary Matching:")

        # Test stainless steel products (should NOT match "stain" keyword)
        product = {'title': 'Stainless Steel Sink', 'description': 'Undermount stainless steel kitchen sink'}
        cluster, conf, scores = get_cluster_assignment(product)
        # Should NOT be paint (stain is a paint keyword)
        self.assert_true(cluster != 'paint', 'Stainless steel sink should NOT be classified as paint')

        # Test that actual stain products still work
        product = {'title': 'Oak Wood Stain', 'description': 'Premium stain for wood surfaces'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'paint', 'Wood stain should be classified as paint')

    def test_empty_products(self):
        """Test empty/invalid products"""
        print("\n9. Testing Empty/Invalid Products:")

        # Test empty title
        product = {'title': '', 'description': ''}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_equal(cluster, 'uncategorized', 'Empty product should be uncategorized')

        # Test missing description
        product = {'title': 'Some Product', 'description': ''}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_true(cluster != '', 'Product with title should have a classification')

    def test_confidence_scores(self):
        """Test confidence scoring"""
        print("\n10. Testing Confidence Scores:")

        # Test high confidence (multiple matching keywords)
        product = {'title': 'LED Light Bulb', 'description': 'Energy efficient LED bulb with 800 lumens and 60-watt equivalent'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_true(conf >= 3, 'LED bulb should have high confidence')

        # Test low confidence (single keyword)
        product = {'title': 'Some Tool', 'description': 'A general purpose tool'}
        cluster, conf, _ = get_cluster_assignment(product)
        self.assert_true(conf >= 1, 'Product should have at least 1 confidence point')

    def test_ambiguous_products(self):
        """Test products that match multiple clusters"""
        print("\n11. Testing Ambiguous Products:")

        # Test product with both electrical and lighting keywords
        product = {'title': 'LED Switch', 'description': 'Smart light switch with LED indicator'}
        cluster, conf, scores = get_cluster_assignment(product)
        self.assert_true(len(scores) >= 2, 'Ambiguous product should match multiple clusters')

    def run_all_tests(self):
        """Run all test suites"""
        print("="*80)
        print("RUNNING AUTOMATED TEST SUITE")
        print("="*80)

        self.test_lighting_products()
        self.test_electrical_products()
        self.test_plumbing_products()
        self.test_tools_products()
        self.test_locks_products()
        self.test_hardware_products()
        self.test_paint_products()
        self.test_word_boundary_matching()
        self.test_empty_products()
        self.test_confidence_scores()
        self.test_ambiguous_products()

        print(f"\n{'='*80}")
        print(f"TEST RESULTS")
        print(f"{'='*80}")
        print(f"\nTotal Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")

        if self.failed == 0:
            print(f"\n✓ All tests passed!")
        else:
            print(f"\n✗ {self.failed} test(s) failed")

        return self.failed == 0

def main():
    """Main test runner"""
    tester = TestClassifier()
    success = tester.run_all_tests()

    # Save test results
    test_results_dir = Path("/home/user/CC/outputs")
    test_results_dir.mkdir(exist_ok=True)

    test_results_file = test_results_dir / 'test_results.json'
    with open(test_results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_tests': tester.passed + tester.failed,
            'passed': tester.passed,
            'failed': tester.failed,
            'success_rate': tester.passed / (tester.passed + tester.failed) if (tester.passed + tester.failed) > 0 else 0,
            'tests': tester.tests
        }, f, indent=2)

    print(f"\nTest results saved to: {test_results_file}")

    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
