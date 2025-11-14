#!/usr/bin/env python3
"""
Comprehensive Test Cases for Context-Aware Negative Keyword Logic
Tests the is_false_positive_block() function with real and synthetic examples
"""

import sys
from pathlib import Path

# Import the classifier
sys.path.append(str(Path(__file__).parent))
from classify_products import ProductClassifier


class NegativeKeywordTester:
    """Test suite for negative keyword logic"""

    def __init__(self):
        self.classifier = ProductClassifier()
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def test_case(self, description: str, text: str, negative_kw: str, pattern_name: str,
                  expected_is_false_positive: bool, location: str = 'title'):
        """
        Run a single test case

        Args:
            description: Human-readable test description
            text: The text to test (normalized)
            negative_kw: The negative keyword to check
            pattern_name: Name of the pattern (e.g., 'LED Light Bulb')
            expected_is_false_positive: True if we expect this to be a false positive (should NOT block)
            location: 'title' or 'description'
        """
        pattern = self.classifier.patterns[pattern_name]
        text_normalized = self.classifier.normalize_text(text)

        result = self.classifier.is_false_positive_block(
            text_normalized, negative_kw, pattern, location
        )

        passed = (result == expected_is_false_positive)

        if passed:
            self.passed += 1
            status = "✓ PASS"
        else:
            self.failed += 1
            status = "✗ FAIL"

        self.test_results.append({
            'status': status,
            'description': description,
            'text': text[:80],
            'negative_kw': negative_kw,
            'pattern': pattern_name,
            'expected': 'FALSE_POSITIVE (don\'t block)' if expected_is_false_positive else 'TRUE_BLOCK (block)',
            'actual': 'FALSE_POSITIVE (don\'t block)' if result else 'TRUE_BLOCK (block)',
            'passed': passed
        })

        return passed

    def print_result(self, test_num: int, test: dict):
        """Print a single test result"""
        print(f"\n{test['status']} Test {test_num}: {test['description']}")
        print(f"   Text: \"{test['text']}...\"")
        print(f"   Negative Keyword: '{test['negative_kw']}' in pattern '{test['pattern']}'")
        print(f"   Expected: {test['expected']}")
        print(f"   Actual:   {test['actual']}")

    def run_all_tests(self):
        """Run comprehensive test suite"""

        print("="*80)
        print("NEGATIVE KEYWORD CONTEXT-AWARE LOGIC TEST SUITE")
        print("="*80)

        print("\n" + "="*80)
        print("CATEGORY 1: FIXTURE BULBS (False Positives - Should NOT Block)")
        print("="*80)

        # Test 1: Chandelier LED Light Bulb
        self.test_case(
            "Chandelier LED Light Bulb - bulb FOR chandelier",
            "Feit Electric 60-Watt Equivalent B10 E26 Base Dim White Filament Clear Glass Chandelier LED Light Bulb Soft White 2700K",
            "light bulb",
            "Chandelier",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 2: Pendant Light Bulb
        self.test_case(
            "Pendant Light Bulb - bulb FOR pendant",
            "40-Watt Equivalent G16.5 Pendant LED Light Bulb Soft White",
            "light bulb",
            "Pendant Light",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 3: Sconce Light Bulb
        self.test_case(
            "Sconce LED Bulb - bulb FOR sconce",
            "Candelabra Base Sconce LED Bulb 60W Equivalent",
            "led bulb",
            "Wall Sconce",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 4: Ceiling Fan Light Bulb
        self.test_case(
            "Ceiling Fan Light Bulb - bulb FOR ceiling fan",
            "Ceiling Fan LED Light Bulb 60W Equivalent A15",
            "ceiling fan",
            "LED Light Bulb",
            expected_is_false_positive=True,
            location='title'
        )

        print("\n" + "="*80)
        print("CATEGORY 2: INTEGRATED COMPONENTS (False Positives - Should NOT Block)")
        print("="*80)

        # Test 5: Faucet with Drain
        self.test_case(
            "Faucet with integrated drain",
            "Pfister Brea Single Handle Bathroom Faucet with Push and Seal Drain",
            "drain",
            "Faucet",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 6: Tub/Shower Faucet with Showerhead
        self.test_case(
            "Tub and Shower Faucet includes showerhead",
            "KOHLER Capilano Single-Handle 3-Spray Tub and Shower Faucet in Vibrant Brushed Nickel (Showerhead Included)",
            "showerhead",
            "Faucet",
            expected_is_false_positive=True,
            location='description'
        )

        # Test 7: Wall Sconce with Switch
        self.test_case(
            "Wall Sconce with integrated switch",
            "Hampton Bay Ashhurst 1-Light ORB Wall Sconce with Switch",
            "switch",
            "Wall Sconce",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 8: Vanity Top (sold without cabinet)
        self.test_case(
            "Vanity Top for vanity cabinet",
            "Home Decorators Collection 37 in. W x 22 in D Quartz white Rectangular Single Sink Vanity Top for 37 in. Vanity Cabinet",
            "vanity cabinet",
            "Vanity Top",
            expected_is_false_positive=True,
            location='description'
        )

        print("\n" + "="*80)
        print("CATEGORY 3: ACCESSORIES & COMPATIBLE PRODUCTS (False Positives)")
        print("="*80)

        # Test 9: Door Handle Set with Knob
        self.test_case(
            "Door Handle Set includes knob option",
            "Schlage Parthenon Antique Brass Single Cylinder Door Handle set with Georgian Knob",
            "knob",
            "Door Handle",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 10: Dimmer Switch for LED Bulbs
        self.test_case(
            "Dimmer Switch for LED bulbs (compatible)",
            "Lutron Skylark Contour LED+ Dimmer Switch for LED and Incandescent Bulbs, 150-Watt",
            "led bulb",
            "Light Switch",
            expected_is_false_positive=True,
            location='description'
        )

        # Test 11: Paint Sprayer (product is sprayer, not paint)
        self.test_case(
            "Paint Sprayer - sprayer is the product",
            "TITAN EP 60X Fine Finishing HVLP Paint Sprayer",
            "sprayer",
            "Paint",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 12: Drill Bit with screwdriver function
        self.test_case(
            "Screwdriver Drill Bit - bit is the product",
            "DEWALT MAXFIT Impact Rated 2 in. #2 Philips Steel Screwdriver Drill Bit",
            "drill",
            "Screwdriver",
            expected_is_false_positive=True,
            location='title'
        )

        print("\n" + "="*80)
        print("CATEGORY 4: TRUE BLOCKS (Should Block - Preserve Existing Logic)")
        print("="*80)

        # Test 13: Actual Chandelier (should be blocked from LED Light Bulb pattern)
        self.test_case(
            "Crystal Chandelier with LED bulbs included",
            "Crystal Chandelier 5-Light with LED Bulbs Included",
            "chandelier",
            "LED Light Bulb",
            expected_is_false_positive=False,  # Should block - it's a chandelier, not a bulb
            location='title'
        )

        # Test 14: Pendant Light Fixture (should be blocked from LED Light Bulb pattern)
        self.test_case(
            "Pendant Light Fixture",
            "Home Decorators Collection Orbit 1-Light Black Mini Pendant Light Fixture",
            "pendant",
            "LED Light Bulb",
            expected_is_false_positive=False,  # Should block - it's a pendant, not a bulb
            location='title'
        )

        # Test 15: Light Switch (should be blocked from LED Light Bulb pattern)
        self.test_case(
            "Light Switch product",
            "Lutron Diva Dimmer Light Switch for Dimmable LED Halogen",
            "switch",
            "LED Light Bulb",
            expected_is_false_positive=False,  # Should block - it's a switch, not a bulb
            location='title'
        )

        # Test 16: Wall Sconce Fixture (should be blocked from LED Light Bulb pattern)
        self.test_case(
            "Wall Sconce Fixture",
            "Hampton Bay Industrial Wall Sconce Light Fixture in Bronze",
            "sconce",
            "LED Light Bulb",
            expected_is_false_positive=False,  # Should block - it's a sconce, not a bulb
            location='title'
        )

        # Test 17: Ceiling Fan (should be blocked from LED Light Bulb pattern)
        self.test_case(
            "Ceiling Fan product",
            "Hunter 52 in. Indoor Ceiling Fan with Light Kit and Remote",
            "ceiling fan",
            "LED Light Bulb",
            expected_is_false_positive=False,  # Should block - it's a fan, not a bulb
            location='title'
        )

        print("\n" + "="*80)
        print("CATEGORY 5: EDGE CASES")
        print("="*80)

        # Test 18: Track Pendant Adapter (pendant in name, but not a pendant fixture)
        self.test_case(
            "Track Pendant Adapter - for converting track to pendant",
            "Hampton Bay 120-Volt 150-Watt Black Single Circuit Linear Track Pendant Adapter",
            "pendant",
            "LED Light Bulb",
            expected_is_false_positive=True,  # Should NOT block - it's an adapter
            location='title'
        )

        # Test 19: Lamp (floor lamp, not a light bulb)
        self.test_case(
            "Floor Lamp product - actual lamp fixture",
            "Hampton Bay Wesleigh 59 in. Aged Brass Standard LED Indoor Floor Lamp",
            "lamp",
            "Light Switch",
            expected_is_false_positive=False,  # Should block - it's a lamp fixture
            location='title'
        )

        # Test 20: LED Lamp Light Bulbs (lamp used as synonym for bulb)
        self.test_case(
            "LED Lamp Bulbs - lamp = bulb in this context",
            "BEYOND BRIGHT 25-Watt LED Lamp Light Bulbs 6500K 3700-Lumens",
            "lamp",
            "Light Switch",
            expected_is_false_positive=True,  # Should NOT block - lamp = bulb here
            location='title'
        )

        # Test 21: Nut Driver (driver is part of product name, not impact driver)
        self.test_case(
            "Nut Driver tool - driver in compound name",
            "Commercial Electric 4-Piece Nut Driver Set",
            "driver",
            "Fastener",
            expected_is_false_positive=True,  # Should NOT block - it's a tool, not a fastener
            location='title'
        )

        # Test 22: Refrigerator Water Filter (should block from HVAC Air Filter pattern)
        self.test_case(
            "Refrigerator Water Filter - water filter blocks HVAC pattern",
            "HDX FMS-1-S Standard Refrigerator Water Filter Replacement",
            "water filter",
            "HVAC Air Filter",
            expected_is_false_positive=False,  # Should block - it's a water filter, not HVAC
            location='title'
        )

        print("\n" + "="*80)
        print("CATEGORY 6: REAL DATASET EXAMPLES")
        print("="*80)

        # Test 23: Product #0 from dataset
        self.test_case(
            "Real Product #0: Chandelier LED Light Bulb",
            "Feit Electric 60-Watt Equivalent B10 E26 Base Dim White Filament Clear Glass Chandelier LED Light Bulb Soft White 2700K (3-Pack)",
            "bulb soft",
            "Chandelier",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 24: Product #343 - Another chandelier bulb
        self.test_case(
            "Real Product #343: Chandelier Bulb",
            "Feit Electric 40-Watt Equivalent B10 E12 Candelabra Dim White Filament Clear Glass Chandelier LED Light Bulb",
            "light bulb",
            "Chandelier",
            expected_is_false_positive=True,
            location='title'
        )

        # Test 25: Product #167 - Sink with drain
        self.test_case(
            "Real Product #167: Kitchen Sink with drain assembly",
            "Glacier Bay 33 in. Drop-In Single Bowl 18 Gauge Stainless Steel Kitchen Sink with Drain Assembly",
            "drain",
            "Faucet",
            expected_is_false_positive=True,
            location='description'
        )

        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed}")

        if self.failed > 0:
            print("\n" + "="*80)
            print("FAILED TESTS")
            print("="*80)

            for i, test in enumerate(self.test_results, 1):
                if not test['passed']:
                    self.print_result(i, test)

        return self.passed, self.failed


def main():
    tester = NegativeKeywordTester()
    passed, failed = tester.run_all_tests()

    print("\n" + "="*80)

    if failed == 0:
        print("✓ ALL TESTS PASSED!")
        print("="*80)
        return 0
    else:
        print(f"✗ {failed} TESTS FAILED")
        print("="*80)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
