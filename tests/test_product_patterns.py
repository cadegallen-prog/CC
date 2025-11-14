#!/usr/bin/env python3
"""
Comprehensive Pattern Tests for Product Classifier
Tests the top 20 most important product types with 3 test cases each:
- Perfect match (strong keyword in title)
- Good match (strong keyword in description, weak keywords)
- Edge case (borderline match that should still work)
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path to import classifier
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from classify_products import ProductClassifier


class TestProductPatterns:
    """Test suite for product type pattern matching"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup classifier for each test"""
        self.classifier = ProductClassifier()

    # ==================== LED LIGHT BULB TESTS ====================

    def test_led_bulb_perfect_match(self):
        """
        Test perfect match for LED Light Bulb
        Product has "LED Light Bulb" directly in title
        Expected: High confidence (≥70), classified as LED Light Bulb
        This tests the fix for the bug where literal "LED Light Bulb" was scoring low
        """
        product = {
            "title": "LED Light Bulb 60W Soft White",
            "description": "800 lumens energy efficient bulb",
            "brand": "Philips",
            "price": 5.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "LED Light Bulb", f"Expected LED Light Bulb, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_led_bulb_good_match(self):
        """
        Test good match for LED Light Bulb
        Product has "LED bulb" in description with weak keywords (lumens, A19)
        Expected: Medium confidence (≥50), classified as LED Light Bulb
        """
        product = {
            "title": "60W Replacement A19 Soft White",
            "description": "LED bulb with 800 lumens for any fixture",
            "brand": "GE",
            "price": 4.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "LED Light Bulb", f"Expected LED Light Bulb, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_led_bulb_edge_case_chandelier_bulb(self):
        """
        Test edge case: Chandelier LED Bulb should NOT be blocked by negative keyword
        This tests the critical bug fix where "chandelier" negative keyword
        was incorrectly blocking "chandelier bulbs" (which ARE bulbs FOR chandeliers)
        Expected: Classified as LED Light Bulb with confidence > 0
        """
        product = {
            "title": "Chandelier LED Bulb Candelabra Base",
            "description": "LED light for chandelier applications E12 base",
            "brand": "Feit Electric",
            "price": 3.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "LED Light Bulb", f"Expected LED Light Bulb, got {result['product_type']}"
        assert result['confidence'] > 0, f"Product should not be blocked by 'chandelier' negative keyword"
        assert result['confidence'] >= 50, f"Expected confidence ≥50 for clear bulb product, got {result['confidence']}"

    # ==================== CEILING FAN TESTS ====================

    def test_ceiling_fan_perfect_match(self):
        """
        Test perfect match for Ceiling Fan
        Product has "ceiling fan" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Indoor Ceiling Fan with Light Kit 52 in.",
            "description": "5-blade fan with remote control and reversible motor",
            "brand": "Hunter",
            "price": 149.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Ceiling Fan", f"Expected Ceiling Fan, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_ceiling_fan_good_match(self):
        """
        Test good match for Ceiling Fan
        Product has "ceiling fan" in description with weak keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "52 in. Indoor LED Light Kit with Remote",
            "description": "Ceiling fan features 5 blades, 3-speed reversible motor, 4200 CFM airflow",
            "brand": "Home Decorators Collection",
            "price": 199.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Ceiling Fan", f"Expected Ceiling Fan, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_ceiling_fan_edge_case_outdoor(self):
        """
        Test edge case: Outdoor ceiling fan with minimal description
        Expected: Still classified as Ceiling Fan
        """
        product = {
            "title": "Outdoor Ceiling Fan 60 in. Weathered Bronze",
            "description": "Damp rated for covered outdoor areas",
            "brand": "Westinghouse",
            "price": 179.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Ceiling Fan", f"Expected Ceiling Fan, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    # ==================== CIRCUIT BREAKER TESTS ====================

    def test_circuit_breaker_perfect_match(self):
        """
        Test perfect match for Circuit Breaker
        Product has "circuit breaker" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "20 Amp Circuit Breaker Single Pole",
            "description": "Thermal magnetic circuit breaker for residential panel",
            "brand": "Square D",
            "price": 8.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Circuit Breaker", f"Expected Circuit Breaker, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_circuit_breaker_good_match(self):
        """
        Test good match for Circuit Breaker
        Product has "breaker" with amp rating and pole count
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "GFCI 20A 2-Pole Breaker",
            "description": "Ground fault circuit breaker with arc fault protection",
            "brand": "Eaton",
            "price": 45.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Circuit Breaker", f"Expected Circuit Breaker, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_circuit_breaker_edge_case_afci(self):
        """
        Test edge case: AFCI breaker with technical terminology
        Expected: Still classified as Circuit Breaker
        """
        product = {
            "title": "15A AFCI Breaker Dual Function",
            "description": "Arc fault circuit interrupter protection",
            "brand": "Siemens",
            "price": 35.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Circuit Breaker", f"Expected Circuit Breaker, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== LIGHT SWITCH TESTS ====================

    def test_light_switch_perfect_match(self):
        """
        Test perfect match for Light Switch
        Product has "light switch" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Dimmer Light Switch Single Pole White",
            "description": "Decorator rocker switch with LED dimming",
            "brand": "Lutron",
            "price": 19.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Light Switch", f"Expected Light Switch, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_light_switch_good_match(self):
        """
        Test good match for Light Switch
        Product has "switch" with 3-way, decorator keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "3-Way Decorator Rocker Switch White",
            "description": "Wall switch for controlling lights from two locations",
            "brand": "Leviton",
            "price": 7.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Light Switch", f"Expected Light Switch, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_light_switch_edge_case_smart_dimmer(self):
        """
        Test edge case: Smart dimmer switch with minimal "switch" mention
        Expected: Still classified as Light Switch
        """
        product = {
            "title": "Smart Dimmer with WiFi White",
            "description": "Wall switch compatible with Alexa and Google Home",
            "brand": "TP-Link",
            "price": 29.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Light Switch", f"Expected Light Switch, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== ELECTRICAL OUTLET TESTS ====================

    def test_electrical_outlet_perfect_match(self):
        """
        Test perfect match for Electrical Outlet
        Product has "outlet" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "GFCI Outlet 20 Amp Tamper Resistant White",
            "description": "Duplex receptacle with ground fault protection",
            "brand": "Leviton",
            "price": 18.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Electrical Outlet", f"Expected Electrical Outlet, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_electrical_outlet_good_match(self):
        """
        Test good match for Electrical Outlet
        Product has "receptacle" with tamper resistant keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "15A Duplex Receptacle White",
            "description": "Tamper resistant grounded outlet for residential use",
            "brand": "Eaton",
            "price": 3.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Electrical Outlet", f"Expected Electrical Outlet, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_electrical_outlet_edge_case_usb_charger(self):
        """
        Test edge case: USB outlet with integrated charger
        Expected: Still classified as Electrical Outlet
        """
        product = {
            "title": "USB Charger 4.2A Type A and Type C White",
            "description": "In-wall charger with USB-A and USB-C ports for devices",
            "brand": "Legrand",
            "price": 24.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Electrical Outlet", f"Expected Electrical Outlet, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== FAUCET TESTS ====================

    def test_faucet_perfect_match(self):
        """
        Test perfect match for Faucet
        Product has "faucet" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Kitchen Faucet Single Handle Pulldown Spray",
            "description": "Stainless steel faucet with 1.8 GPM flow rate",
            "brand": "Delta",
            "price": 149.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Faucet", f"Expected Faucet, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_faucet_good_match(self):
        """
        Test good match for Faucet
        Product has "bathroom faucet" in description with handle/spout keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "Centerset 2-Handle Brushed Nickel",
            "description": "Bathroom faucet with popup drain and deck mount installation",
            "brand": "Moen",
            "price": 89.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Faucet", f"Expected Faucet, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_faucet_edge_case_with_drain(self):
        """
        Test edge case: Faucet with integrated drain (drain should not block)
        Expected: Still classified as Faucet, not blocked by "drain" negative keyword
        """
        product = {
            "title": "Lavatory Faucet with Push & Seal Drain Chrome",
            "description": "Single handle faucet includes drain assembly",
            "brand": "Pfister",
            "price": 79.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Faucet", f"Expected Faucet, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== TOILET TESTS ====================

    def test_toilet_perfect_match(self):
        """
        Test perfect match for Toilet
        Product has "toilet" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "2-Piece Elongated Toilet in White",
            "description": "Comfort height toilet with 1.28 GPF flush",
            "brand": "Kohler",
            "price": 299.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Toilet", f"Expected Toilet, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_toilet_good_match(self):
        """
        Test good match for Toilet
        Product has "toilet" in description with flush/bowl keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "1-Piece Elongated White",
            "description": "Toilet with dual flush system and soft close seat",
            "brand": "American Standard",
            "price": 399.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Toilet", f"Expected Toilet, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_toilet_edge_case_comfort_height(self):
        """
        Test edge case: Comfort height toilet with minimal description
        Expected: Still classified as Toilet
        """
        product = {
            "title": "Comfort Height Round Front White",
            "description": "Water closet with elongated bowl and 12-inch rough-in",
            "brand": "Glacier Bay",
            "price": 199.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Toilet", f"Expected Toilet, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== DOOR LOCK TESTS ====================

    def test_door_lock_perfect_match(self):
        """
        Test perfect match for Door Lock
        Product has "door lock" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Keyed Entry Door Lock Satin Nickel",
            "description": "Grade 2 security lock with deadbolt",
            "brand": "Schlage",
            "price": 39.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Door Lock", f"Expected Door Lock, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_door_lock_good_match(self):
        """
        Test good match for Door Lock
        Product has "deadbolt" with keyed entry keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "Single Cylinder Deadbolt Satin Nickel",
            "description": "Door security lock with Grade 1 rating and keyed entry",
            "brand": "Kwikset",
            "price": 29.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Door Lock", f"Expected Door Lock, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_door_lock_edge_case_smart_lock(self):
        """
        Test edge case: Smart lock should classify as Door Lock (not smart_home)
        This tests that smart locks are correctly identified as door security products
        Expected: Still classified as Door Lock
        """
        product = {
            "title": "Smart Lock Keyless Entry Touchscreen Satin Nickel",
            "description": "Electronic door lock with keypad and Bluetooth connectivity",
            "brand": "Yale",
            "price": 149.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Door Lock", f"Expected Door Lock, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== DRILL TESTS ====================

    def test_drill_perfect_match(self):
        """
        Test perfect match for Drill
        Product has "drill" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "18V Cordless Drill/Driver with Battery",
            "description": "Brushless drill with 1/2 in. chuck and 2-speed transmission",
            "brand": "DeWalt",
            "price": 129.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Drill", f"Expected Drill, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_drill_good_match(self):
        """
        Test good match for Drill
        Product has "hammer drill" in description with volt/battery keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "20V MAX Brushless with 2 Batteries",
            "description": "Hammer drill with 1/2 in. chuck for drilling and driving",
            "brand": "Milwaukee",
            "price": 179.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Drill", f"Expected Drill, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_drill_edge_case_impact_driver(self):
        """
        Test edge case: Impact driver should classify as Drill
        Expected: Still classified as Drill
        """
        product = {
            "title": "Impact Driver 18V Lithium-Ion Brushless",
            "description": "Compact power tool with 1500 in-lbs torque",
            "brand": "Makita",
            "price": 99.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Drill", f"Expected Drill, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== SAW TESTS ====================

    def test_saw_perfect_match(self):
        """
        Test perfect match for Saw
        Product has "circular saw" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "7-1/4 in. Circular Saw 15 Amp",
            "description": "Corded saw with carbide blade for cutting wood",
            "brand": "Ryobi",
            "price": 69.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Saw", f"Expected Saw, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_saw_good_match(self):
        """
        Test good match for Saw
        Product has "miter saw" in description with blade/cutting keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "12 in. Dual Bevel Sliding Compound",
            "description": "Miter saw with 15 amp motor and laser guide for cutting",
            "brand": "DeWalt",
            "price": 499.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Saw", f"Expected Saw, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_saw_edge_case_jigsaw(self):
        """
        Test edge case: Jigsaw with minimal description
        Expected: Still classified as Saw
        """
        product = {
            "title": "Jigsaw Variable Speed 6.5 Amp",
            "description": "Cutting tool with orbital action for curves",
            "brand": "Black+Decker",
            "price": 49.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Saw", f"Expected Saw, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== FASTENER TESTS ====================

    def test_fastener_perfect_match(self):
        """
        Test perfect match for Fastener
        Product has "screw" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "#8 x 1-1/2 in. Wood Screws (100-Pack)",
            "description": "Zinc plated Phillips drive screws for wood",
            "brand": "Grip-Rite",
            "price": 7.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Fastener", f"Expected Fastener, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_fastener_good_match(self):
        """
        Test good match for Fastener
        Product has "bolt" with nut/washer keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "1/4 in. x 2 in. Zinc Plated (25-Pack)",
            "description": "Hex bolt with nut and washer hardware pack",
            "brand": "Crown Bolt",
            "price": 5.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Fastener", f"Expected Fastener, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_fastener_edge_case_anchor(self):
        """
        Test edge case: Wall anchor should classify as Fastener
        Expected: Still classified as Fastener
        """
        product = {
            "title": "Self-Drilling Drywall Anchor 50 lb. (10-Pack)",
            "description": "Zinc anchor for hanging on walls",
            "brand": "Hillman",
            "price": 4.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Fastener", f"Expected Fastener, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== PAINT TESTS ====================

    def test_paint_perfect_match(self):
        """
        Test perfect match for Paint
        Product has "paint" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Interior Paint Semi-Gloss White 1 Gallon",
            "description": "Premium wall paint with primer for interior surfaces",
            "brand": "Behr",
            "price": 32.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Paint", f"Expected Paint, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_paint_good_match(self):
        """
        Test good match for Paint
        Product has "exterior paint" in description with gallon/finish keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "5 Gallon Satin Enamel Base",
            "description": "Exterior paint and primer for siding and trim",
            "brand": "Sherwin-Williams",
            "price": 149.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Paint", f"Expected Paint, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_paint_edge_case_primer(self):
        """
        Test edge case: Paint primer should classify as Paint
        Expected: Still classified as Paint
        """
        product = {
            "title": "Multi-Surface Primer Sealer 1 Gallon",
            "description": "Interior/exterior primer coating for walls",
            "brand": "Kilz",
            "price": 24.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Paint", f"Expected Paint, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== PENDANT LIGHT TESTS ====================

    def test_pendant_light_perfect_match(self):
        """
        Test perfect match for Pendant Light
        Product has "pendant light" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "1-Light Mini Pendant Light Brushed Nickel",
            "description": "Hanging pendant with glass shade and adjustable height",
            "brand": "Progress Lighting",
            "price": 79.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Pendant Light", f"Expected Pendant Light, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_pendant_light_good_match(self):
        """
        Test good match for Pendant Light
        Product has "pendant" in description with hanging/suspension keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "Industrial Hanging Light Bronze",
            "description": "Pendant with metal shade and adjustable chain suspension",
            "brand": "Kichler",
            "price": 99.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Pendant Light", f"Expected Pendant Light, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_pendant_light_edge_case_mini_pendant(self):
        """
        Test edge case: Mini-pendant with minimal description
        Expected: Still classified as Pendant Light
        """
        product = {
            "title": "Mini-Pendant Glass Shade Chrome",
            "description": "Decorative lighting fixture for kitchen island",
            "brand": "Sea Gull Lighting",
            "price": 69.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Pendant Light", f"Expected Pendant Light, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== WALL SCONCE TESTS ====================

    def test_wall_sconce_perfect_match(self):
        """
        Test perfect match for Wall Sconce
        Product has "wall sconce" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "1-Light Wall Sconce Brushed Nickel",
            "description": "Vanity sconce with glass shade for bathroom lighting",
            "brand": "Progress Lighting",
            "price": 49.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Wall Sconce", f"Expected Wall Sconce, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_wall_sconce_good_match(self):
        """
        Test good match for Wall Sconce
        Product has "sconce" in description with wall mount keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "2-Light Bath Vanity Light Matte Black",
            "description": "Wall sconce features glass shades and wall mounted design",
            "brand": "Kichler",
            "price": 89.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Wall Sconce", f"Expected Wall Sconce, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_wall_sconce_edge_case_vanity_light(self):
        """
        Test edge case: Vanity light should classify as Wall Sconce
        Expected: Still classified as Wall Sconce
        """
        product = {
            "title": "3-Light Vanity Light Chrome",
            "description": "Bath light with wall mount and accent lighting",
            "brand": "Globe Electric",
            "price": 39.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Wall Sconce", f"Expected Wall Sconce, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== RECESSED LIGHT TESTS ====================

    def test_recessed_light_perfect_match(self):
        """
        Test perfect match for Recessed Light
        Product has "recessed" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "6 in. Recessed LED Downlight Trim Kit",
            "description": "Retrofit recessed light with integrated LED",
            "brand": "Commercial Electric",
            "price": 19.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Recessed Light", f"Expected Recessed Light, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_recessed_light_good_match(self):
        """
        Test good match for Recessed Light
        Product has "recessed lighting" in description with retrofit/baffle keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "4 in. Ultra Slim LED Downlight White",
            "description": "Recessed lighting with color selectable and baffle trim",
            "brand": "Halo",
            "price": 14.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Recessed Light", f"Expected Recessed Light, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_recessed_light_edge_case_canless(self):
        """
        Test edge case: Canless downlight should classify as Recessed Light
        Expected: Still classified as Recessed Light
        """
        product = {
            "title": "5/6 in. Canless LED Downlight 90 CRI",
            "description": "Slim downlight with integrated housing for ceiling recess",
            "brand": "Lithonia Lighting",
            "price": 24.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Recessed Light", f"Expected Recessed Light, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== EXHAUST FAN TESTS ====================

    def test_exhaust_fan_perfect_match(self):
        """
        Test perfect match for Exhaust Fan
        Product has "exhaust fan" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Bathroom Exhaust Fan 50 CFM 1.5 Sone",
            "description": "Ventilation fan with quiet operation for bathroom",
            "brand": "Broan-NuTone",
            "price": 39.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Exhaust Fan", f"Expected Exhaust Fan, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_exhaust_fan_good_match(self):
        """
        Test good match for Exhaust Fan
        Product has "ventilation fan" in description with CFM/sone keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "110 CFM Ceiling Mount White",
            "description": "Bathroom fan with ventilation and 2.0 sone rating",
            "brand": "Delta Breez",
            "price": 49.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Exhaust Fan", f"Expected Exhaust Fan, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_exhaust_fan_edge_case_with_light(self):
        """
        Test edge case: Exhaust fan with integrated light
        Expected: Still classified as Exhaust Fan (not Ceiling Fan)
        """
        product = {
            "title": "Bathroom Fan with LED Light 80 CFM",
            "description": "Air exhaust and lighting combo unit with 0.8 sone",
            "brand": "Panasonic",
            "price": 89.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Exhaust Fan", f"Expected Exhaust Fan, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== SINK TESTS ====================

    def test_sink_perfect_match(self):
        """
        Test perfect match for Sink
        Product has "sink" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Undermount Kitchen Sink Stainless Steel 32 in.",
            "description": "Double bowl sink 18 gauge stainless for kitchen",
            "brand": "Kraus",
            "price": 249.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Sink", f"Expected Sink, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_sink_good_match(self):
        """
        Test good match for Sink
        Product has "bathroom sink" in description with basin/bowl keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "Oval Drop-In White Vitreous China",
            "description": "Bathroom sink with overflow and undermount basin",
            "brand": "Kohler",
            "price": 129.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Sink", f"Expected Sink, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_sink_edge_case_vessel_sink(self):
        """
        Test edge case: Vessel sink with minimal description
        Expected: Still classified as Sink
        """
        product = {
            "title": "Vessel Round Glass Clear 16 in.",
            "description": "Wash basin for bathroom vanity with modern design",
            "brand": "Vigo",
            "price": 179.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Sink", f"Expected Sink, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== DRILL BIT TESTS ====================

    def test_drill_bit_perfect_match(self):
        """
        Test perfect match for Drill Bit
        Product has "drill bit" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Titanium Drill Bit Set 29-Piece",
            "description": "Impact rated drill bits for metal and wood",
            "brand": "DeWalt",
            "price": 29.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Drill Bit", f"Expected Drill Bit, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_drill_bit_good_match(self):
        """
        Test good match for Drill Bit
        Product has "bit set" in description with titanium/cobalt keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "21-Piece Cobalt Steel Set",
            "description": "Drill bit set for drilling metal, wood, and plastic",
            "brand": "Bosch",
            "price": 39.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Drill Bit", f"Expected Drill Bit, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_drill_bit_edge_case_driver_bits(self):
        """
        Test edge case: Driver bits should classify as Drill Bit
        Expected: Still classified as Drill Bit
        """
        product = {
            "title": "Impact Driver Bit Set Philips/Torx 40-Piece",
            "description": "Driver bits with impact rating for screw driving",
            "brand": "Milwaukee",
            "price": 19.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Drill Bit", f"Expected Drill Bit, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== LADDER TESTS ====================

    def test_ladder_perfect_match(self):
        """
        Test perfect match for Ladder
        Product has "ladder" directly in title
        Expected: High confidence (≥70)
        """
        product = {
            "title": "6 ft. Fiberglass Step Ladder 250 lb. Capacity",
            "description": "Type I ladder with anti-slip feet for climbing",
            "brand": "Werner",
            "price": 89.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Ladder", f"Expected Ladder, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_ladder_good_match(self):
        """
        Test good match for Ladder
        Product has "extension ladder" in description with reach/feet keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "20 ft. Aluminum 225 lb. Type II",
            "description": "Extension ladder with 17 ft. reach height access",
            "brand": "Louisville",
            "price": 149.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Ladder", f"Expected Ladder, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_ladder_edge_case_multi_position(self):
        """
        Test edge case: Multi-position ladder with minimal description
        Expected: Still classified as Ladder
        """
        product = {
            "title": "Multi-Position 22 ft. Aluminum 300 lb. IAA",
            "description": "Telescoping ladder for height access and climbing",
            "brand": "Little Giant",
            "price": 299.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Ladder", f"Expected Ladder, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    # ==================== WINDOW TESTS ====================

    def test_window_perfect_match(self):
        """
        Test perfect match for Window
        Product has "window" directly in title with window type
        Expected: High confidence (≥70)
        """
        product = {
            "title": "Double-Hung Window Vinyl White 36 in. x 48 in.",
            "description": "Insulated glass window with low-e coating energy efficient",
            "brand": "American Craftsman",
            "price": 249.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Window", f"Expected Window, got {result['product_type']}"
        assert result['confidence'] >= 70, f"Expected confidence ≥70, got {result['confidence']}"

    def test_window_good_match(self):
        """
        Test good match for Window
        Product has "sliding window" in description with glass/vinyl keywords
        Expected: Medium confidence (≥50)
        """
        product = {
            "title": "48 in. x 36 in. Vinyl White Low-E",
            "description": "Sliding window with insulated glass and wood clad sash",
            "brand": "JELD-WEN",
            "price": 299.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Window", f"Expected Window, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"

    def test_window_edge_case_casement(self):
        """
        Test edge case: Casement window with minimal description
        Expected: Still classified as Window (not window treatment)
        """
        product = {
            "title": "Casement 24 in. x 40 in. White Vinyl",
            "description": "Window features low-e glass and energy efficient construction",
            "brand": "Pella",
            "price": 349.99
        }
        result = self.classifier.classify_product(product)
        assert result['product_type'] == "Window", f"Expected Window, got {result['product_type']}"
        assert result['confidence'] >= 50, f"Expected confidence ≥50, got {result['confidence']}"
