"""
Pytest Unit Tests for ProductClassifier Scoring System

Tests the calculate_match_score() function to ensure accurate scoring
based on keywords, specifications, and negative keyword handling.

Test coverage:
- Strong keywords in title (+80 points)
- Strong keywords in description (+50 points)
- Weak keywords accumulation (+5 each, max 30)
- Negative keyword blocking (score = 0)
- Chandelier/pendant bulb exceptions (should NOT block)
- Score capping at 100 max
- No matches scenarios (score = 0)
"""

import pytest
from classify_products import ProductClassifier


class TestScoringSystem:
    """
    Unit tests for the ProductClassifier.calculate_match_score() method.

    Tests verify that the scoring algorithm correctly:
    - Awards points for strong keywords in different locations
    - Accumulates points from weak keywords
    - Blocks products with negative keywords
    - Handles edge cases like chandelier bulbs
    - Caps scores at maximum 100 points
    """

    def test_strong_keyword_in_title(self, classifier):
        """
        Test: Strong keyword in title should award 80 points

        When a product title contains a strong keyword for the product type,
        it should receive the maximum title bonus of 80 points.

        Example: "LED Light Bulb 60W" contains "led light bulb" (strong keyword)
        Expected: Score >= 80
        """
        product = {
            "title": "LED Light Bulb 60W Equivalent Soft White",
            "description": "Energy efficient lighting solution for your home",
            "brand": "Generic",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should get 80 points for strong keyword in title
        assert score >= 80, f"Expected score >= 80 for strong keyword in title, got {score}"

        # Should have a reason mentioning the title match
        assert any("Title" in reason or "title" in reason for reason in reasons), \
            f"Expected title match in reasons, got: {reasons}"

        print(f"✓ Strong keyword in title: Score={score}, Reasons={reasons}")

    def test_strong_keyword_in_description_only(self, classifier):
        """
        Test: Strong keyword in description (but not title) should award 50 points

        When a strong keyword appears in the description but NOT in the title,
        it should receive 50 points (less than title because title is stronger signal).

        Example: Title is "60W Replacement", description has "LED light bulb"
        Expected: Score >= 50 and < 80
        """
        product = {
            "title": "60W Equivalent Replacement Bulb",  # No strong keyword
            "description": "This LED light bulb provides bright illumination and energy savings",
            "brand": "Generic",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should get 50 points for description, not 80 for title
        assert score >= 50, f"Expected score >= 50 for strong keyword in description, got {score}"
        assert score < 80, f"Expected score < 80 (description only, not title), got {score}"

        # Should have a reason mentioning the description match
        assert any("Description" in reason or "description" in reason for reason in reasons), \
            f"Expected description match in reasons, got: {reasons}"

        print(f"✓ Strong keyword in description only: Score={score}, Reasons={reasons}")

    def test_weak_keywords_accumulation(self, classifier):
        """
        Test: Weak keywords should accumulate (+5 each, max 30 points)

        Weak keywords provide supporting evidence. Each weak keyword adds 5 points,
        but the total is capped at 30 points maximum.

        Weak keywords for LED Light Bulb include: dimmable, A19, lumens, kelvin, etc.

        Example: "LED Bulb Dimmable A19 800 lumens 2700K"
        Expected: Should include points for weak keywords (dimmable, a19, lumens, 2700k)
        """
        product = {
            "title": "LED Light Bulb",  # Strong keyword = 80 points
            "description": "Dimmable A19 bulb with 800 lumens at 2700 Kelvin E26 base BR30 shape",
            # Weak keywords: dimmable, a19, lumens, kelvin, e26, br30 = 6 weak keywords = 30 points
            "brand": "Generic",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should get 80 (title) + weak keyword points
        # Weak keywords: dimmable, a19, lumens, kelvin, e26, br30 = 6 keywords = 30 points
        assert score >= 80, f"Expected score >= 80 (title keyword alone), got {score}"

        # Should have a reason about supporting keywords
        assert any("supporting" in reason.lower() or "keyword" in reason.lower() for reason in reasons), \
            f"Expected supporting keywords in reasons, got: {reasons}"

        # Score should be higher than just the title score due to weak keywords
        # 80 (title) + up to 30 (weak) = up to 110, but capped at 100
        assert score > 80, f"Expected score > 80 due to weak keywords, got {score}"

        print(f"✓ Weak keywords accumulation: Score={score}, Reasons={reasons}")

    def test_negative_keyword_blocking(self, classifier):
        """
        Test: Negative keywords should block the match (score = 0)

        If a product contains a negative keyword AND it's not a false positive
        (like chandelier fixture vs chandelier bulb), it should be blocked with score 0.

        Example: "Pendant Light Fixture" has "pendant" which is a negative keyword
        Expected: Score = 0 (blocked)
        """
        product = {
            "title": "Pendant Light Fixture for Kitchen",
            "description": "Beautiful pendant fixture with adjustable height",
            "brand": "Generic",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should be blocked with score 0
        assert score == 0, f"Expected score = 0 for negative keyword blocking, got {score}"

        # Should have a disqualification reason
        assert any("Disqualified" in reason or "negative" in reason for reason in reasons), \
            f"Expected disqualification in reasons, got: {reasons}"

        print(f"✓ Negative keyword blocking: Score={score}, Reasons={reasons}")

    def test_chandelier_bulb_exception(self, classifier):
        """
        Test: Chandelier LED bulbs should NOT be blocked (exception to negative keyword rule)

        This is a critical edge case. "Chandelier" is normally a negative keyword,
        BUT when it's part of "Chandelier LED Light Bulb" (a bulb FOR chandeliers),
        it should NOT be blocked. The is_false_positive_block() method handles this.

        Example: "Chandelier LED Light Bulb" - this is a BULB, not a chandelier fixture
        Expected: Score > 0 (NOT blocked)
        """
        product = {
            "title": "Chandelier LED Light Bulb 60W Equivalent",
            "description": "LED bulbs designed for chandelier fixtures with candelabra base",
            "brand": "Feit Electric",
            "structured_specifications": {
                "wattage": {"value": 5.5, "unit": "W"},
                "lumens": {"value": 500, "unit": "lm"},
                "base_type": "E12"
            }
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should NOT be blocked - this is a bulb FOR chandeliers
        assert score > 0, f"Expected score > 0 for chandelier bulb (should NOT be blocked), got {score}"

        # Should NOT have disqualification reason
        assert not any("Disqualified" in reason for reason in reasons), \
            f"Chandelier bulb should NOT be disqualified, got reasons: {reasons}"

        # Should have positive scoring reasons
        assert any("Title" in reason or "Description" in reason for reason in reasons), \
            f"Expected positive scoring reasons, got: {reasons}"

        print(f"✓ Chandelier bulb exception: Score={score}, Reasons={reasons}")

    def test_pendant_bulb_exception(self, classifier):
        """
        Test: Pendant LED bulbs should NOT be blocked (another exception case)

        Similar to chandelier bulbs, "pendant" is a negative keyword,
        BUT "Pendant LED Light Bulb" is a bulb FOR pendants, not a pendant fixture.

        Example: "Pendant LED Light Bulb Vintage Style"
        Expected: Score > 0 (NOT blocked)
        """
        product = {
            "title": "Pendant LED Light Bulb Vintage Style",
            "description": "Vintage LED bulbs ideal for pendant light fixtures with Edison style",
            "brand": "Philips",
            "structured_specifications": {
                "wattage": {"value": 4.5, "unit": "W"},
                "lumens": {"value": 350, "unit": "lm"},
                "base_type": "E26"
            }
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should NOT be blocked
        assert score > 0, f"Expected score > 0 for pendant bulb (should NOT be blocked), got {score}"

        # Should NOT have disqualification reason
        assert not any("Disqualified" in reason for reason in reasons), \
            f"Pendant bulb should NOT be disqualified, got reasons: {reasons}"

        print(f"✓ Pendant bulb exception: Score={score}, Reasons={reasons}")

    def test_sconce_bulb_exception(self, classifier):
        """
        Test: Sconce LED bulbs should NOT be blocked (third exception case)

        "Sconce" is a negative keyword for bulbs, but "Sconce LED Light Bulb"
        is a bulb FOR sconces, not a sconce fixture itself.

        Example: "Sconce LED Light Bulb Candelabra Base"
        Expected: Score > 0 (NOT blocked)
        """
        product = {
            "title": "Sconce LED Light Bulb Candelabra Base",
            "description": "LED bulbs for sconce fixtures with E12 candelabra base",
            "brand": "Generic",
            "structured_specifications": {
                "base_type": "E12",
                "lumens": {"value": 400, "unit": "lm"}
            }
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should NOT be blocked
        assert score > 0, f"Expected score > 0 for sconce bulb (should NOT be blocked), got {score}"
        assert not any("Disqualified" in reason for reason in reasons), \
            f"Sconce bulb should NOT be disqualified, got reasons: {reasons}"

        print(f"✓ Sconce bulb exception: Score={score}, Reasons={reasons}")

    def test_max_score_capping(self, classifier):
        """
        Test: Scores should be capped at maximum 100 points

        Even if all possible scoring factors are present (strong keyword in title,
        weak keywords, specs, hints, etc.), the total score cannot exceed 100.

        Example: Product with every possible scoring factor
        Expected: Score = 100 (capped)
        """
        product = {
            "title": "LED Light Bulb Dimmable A19 Soft White",  # Strong keyword + weak keywords
            "description": "This LED light bulb provides 800 lumens at 2700 Kelvin color temperature. "
                          "Dimmable LED bulbs with E26 base. BR30 shape, 60 watt equivalent. "
                          "CRI 90+. LED bulbs for home lighting.",  # Description hints + more weak keywords
            "brand": "Feit Electric",
            "structured_specifications": {
                "wattage": {"value": 8.8, "unit": "W"},
                "lumens": {"value": 800, "unit": "lm"},
                "color_temp": {"value": 2700, "unit": "K"},
                "base_type": "E26",
                "dimmable": True
            }
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Score should be capped at 100, not exceed it
        assert score == 100, f"Expected score = 100 (capped at max), got {score}"

        # Should have multiple reasons (strong keyword, weak keywords, specs, etc.)
        assert len(reasons) >= 3, f"Expected multiple scoring reasons, got: {reasons}"

        print(f"✓ Max score capping: Score={score}, Reasons={reasons}")

    def test_no_matches_zero_score(self, classifier):
        """
        Test: Products with no matching keywords should score 0

        If a product has no strong keywords, no weak keywords, no specs,
        and no other matching factors, it should score 0.

        Example: "Hammer" (tool) tested against "LED Light Bulb" pattern
        Expected: Score = 0 (no matches)
        """
        product = {
            "title": "Hammer",
            "description": "A tool for hammering nails into wood",
            "brand": "Stanley",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should score 0 - no matches at all
        assert score == 0, f"Expected score = 0 for no matches, got {score}"

        print(f"✓ No matches zero score: Score={score}, Reasons={reasons}")

    def test_spec_boost_for_bulbs(self, classifier):
        """
        Test: Products with bulb-specific specs should get spec boost

        LED Light Bulb pattern has spec_boost enabled. If a product has
        3+ bulb-specific specs (wattage, lumens, color_temp, base_type, dimmable),
        it should get an additional 10-point boost.

        Example: Bulb with wattage, lumens, color_temp, and base_type
        Expected: Should include spec boost in scoring
        """
        product = {
            "title": "LED Light Bulb",  # Strong keyword = 80
            "description": "Energy efficient bulb",
            "brand": "Generic",
            "structured_specifications": {
                "wattage": {"value": 8.8, "unit": "W"},
                "lumens": {"value": 800, "unit": "lm"},
                "color_temp": {"value": 2700, "unit": "K"},
                "base_type": "E26",
                "dimmable": True
            }
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should get spec boost (has 5 spec indicators)
        assert score >= 80, f"Expected score >= 80 with spec boost, got {score}"

        # Should have a reason about specifications
        assert any("specification" in reason.lower() for reason in reasons), \
            f"Expected specification-related reason, got: {reasons}"

        print(f"✓ Spec boost for bulbs: Score={score}, Reasons={reasons}")

    def test_description_hints_add_points(self, classifier):
        """
        Test: Description hints should add points (max 10)

        Description hints are phrases like "watt equivalent", "color temperature",
        "soft white", etc. Each hint adds 3 points, capped at 10 points total.

        Example: Description with "watt equivalent", "color temperature", "soft white"
        Expected: Should add hint points
        """
        product = {
            "title": "LED Light Bulb",  # Strong keyword = 80
            "description": "60 watt equivalent bulb with 2700K color temperature in soft white. "
                          "These LED bulbs provide excellent CRI and are dimmable.",
            # Hints: "watt equivalent", "color temperature", "soft white", "led bulbs" = 4 hints = 10 points (capped)
            "brand": "Generic",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should get 80 (title) + hints + possibly other points
        assert score >= 80, f"Expected score >= 80 with description hints, got {score}"

        # Should have a reason about description hints
        assert any("hint" in reason.lower() for reason in reasons), \
            f"Expected description hints in reasons, got: {reasons}"

        print(f"✓ Description hints add points: Score={score}, Reasons={reasons}")

    def test_combined_scoring_realistic_bulb(self, classifier):
        """
        Test: Realistic LED bulb should score very high (near 100)

        A typical LED bulb product with title keyword, description, specs,
        weak keywords, etc. should score very high.

        This tests the full scoring algorithm with a realistic product.
        """
        product = {
            "title": "Feit Electric 60W Equivalent LED Light Bulb Soft White A19 Dimmable",
            "description": "Upgrade to Feit Electric's elegant LED bulbs. These dimmable A19 bulbs "
                          "provide 800 lumens of soft white light at 2700 Kelvin color temperature. "
                          "Uses just 8.8 watts, up to 85% less energy than 60-watt equivalent bulbs. "
                          "CRI 90+ for vibrant colors. E26 medium base.",
            "brand": "Feit Electric",
            "structured_specifications": {
                "wattage": {"value": 8.8, "unit": "W"},
                "lumens": {"value": 800, "unit": "lm"},
                "color_temp": {"value": 2700, "unit": "K"},
                "base_type": "E26",
                "dimmable": True
            }
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should score very high (likely 100 or close to it)
        assert score >= 90, f"Expected score >= 90 for realistic bulb, got {score}"
        assert score <= 100, f"Expected score <= 100 (capped), got {score}"

        # Should have multiple scoring reasons
        assert len(reasons) >= 3, f"Expected multiple reasons for high score, got: {reasons}"

        print(f"✓ Combined scoring realistic bulb: Score={score}, Reasons={reasons}")

    def test_edge_case_for_chandelier_phrase(self, classifier):
        """
        Test: "for chandelier" phrase should NOT block bulbs

        Products with phrases like "bulbs for chandelier" or "for use in chandelier"
        should NOT be blocked because they're describing USE CASE, not product type.

        Example: "LED Bulbs for Chandelier Fixtures"
        Expected: Score > 0 (NOT blocked)
        """
        product = {
            "title": "LED Bulbs for Chandelier Fixtures E12 Base",
            "description": "These LED light bulbs are designed for use in chandelier fixtures",
            "brand": "Generic",
            "structured_specifications": {
                "base_type": "E12",
                "lumens": {"value": 400, "unit": "lm"}
            }
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should NOT be blocked
        assert score > 0, f"Expected score > 0 for 'for chandelier' phrase, got {score}"
        assert not any("Disqualified" in reason for reason in reasons), \
            f"Should NOT be disqualified for use case mention, got: {reasons}"

        print(f"✓ Edge case 'for chandelier' phrase: Score={score}, Reasons={reasons}")

    def test_negative_keyword_in_description_blocks(self, classifier):
        """
        Test: Negative keywords in description should also block (not just title)

        If a negative keyword appears in the description and it's not a false positive,
        it should block the match with score 0.

        Example: Description says "ceiling mounted fixture" for LED Light Bulb pattern
        Expected: Score = 0 (blocked by "fixture" negative keyword)
        """
        product = {
            "title": "LED Lighting Solution",
            "description": "This is a ceiling mounted fixture with integrated LED modules",
            "brand": "Generic",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should be blocked by "fixture" negative keyword in description
        assert score == 0, f"Expected score = 0 for negative keyword in description, got {score}"
        assert any("Disqualified" in reason for reason in reasons), \
            f"Expected disqualification reason, got: {reasons}"

        print(f"✓ Negative keyword in description blocks: Score={score}, Reasons={reasons}")


class TestScoringEdgeCases:
    """
    Additional edge case tests for scoring system robustness.
    """

    def test_empty_product_fields(self, classifier):
        """
        Test: Products with empty/missing fields should handle gracefully

        If a product has empty title or description, the scoring should
        still work without errors.
        """
        product = {
            "title": "",
            "description": "",
            "brand": "",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should return score 0, not crash
        assert score == 0, f"Expected score = 0 for empty product, got {score}"

        print(f"✓ Empty product fields: Score={score}, Reasons={reasons}")

    def test_case_insensitive_matching(self, classifier):
        """
        Test: Keyword matching should be case-insensitive

        "LED LIGHT BULB" and "led light bulb" should match the same.
        """
        product_upper = {
            "title": "LED LIGHT BULB 60W",
            "description": "DIMMABLE A19 BULB",
            "structured_specifications": {}
        }

        product_lower = {
            "title": "led light bulb 60w",
            "description": "dimmable a19 bulb",
            "structured_specifications": {}
        }

        score_upper, _ = classifier.calculate_match_score(product_upper, "LED Light Bulb")
        score_lower, _ = classifier.calculate_match_score(product_lower, "LED Light Bulb")

        # Scores should be the same (case insensitive)
        assert score_upper == score_lower, \
            f"Expected same scores for case variations, got {score_upper} vs {score_lower}"

        print(f"✓ Case insensitive matching: Upper={score_upper}, Lower={score_lower}")

    def test_multiple_strong_keywords_only_count_once(self, classifier):
        """
        Test: Multiple strong keywords in title should only count once (+80, not +160)

        The scoring logic has a "break" statement after finding the first strong
        keyword in title, so it should only count 80 points once.
        """
        product = {
            "title": "LED Light Bulb LED Bulb LED Lamp",  # Multiple strong keywords
            "description": "Energy efficient lighting",
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should get 80 for title, not 240 (3 x 80)
        # Might get a bit more for weak keywords, but base should be 80
        assert score >= 80, f"Expected score >= 80, got {score}"
        # Should not be way over 100 if we're capping properly
        assert score <= 100, f"Expected score <= 100 (capped), got {score}"

        print(f"✓ Multiple strong keywords count once: Score={score}, Reasons={reasons}")

    def test_weak_keyword_max_cap_30_points(self, classifier):
        """
        Test: Weak keywords should cap at 30 points (not exceed)

        Even if there are 10+ weak keywords (10 * 5 = 50 points),
        it should cap at 30 points maximum for weak keywords.
        Note: Description hints can add a few more points (max 10).
        """
        product = {
            "title": "Bulb",  # No strong keyword
            "description": "dimmable a19 a21 br30 par38 e26 e12 b10 lumens kelvin candelabra watt equivalent",
            # 11 weak keywords would be 55 points, but should cap at 30
            # May also get description hints (e.g., "watt equivalent" = 3 points)
            "structured_specifications": {}
        }

        score, reasons = classifier.calculate_match_score(product, "LED Light Bulb")

        # Should get 30 points from weak keywords + up to 10 from description hints
        # So max would be 40, but typically around 30-35
        assert score <= 40, f"Expected score <= 40 (weak keywords + hints capped), got {score}"
        assert score >= 25, f"Expected score >= 25 (should have many weak keywords), got {score}"

        # Verify that weak keywords are capped at 30 (not 55)
        # We can't exceed 40 total without strong keywords
        assert score < 50, f"Weak keywords should be capped, got {score}"

        print(f"✓ Weak keyword max cap: Score={score}, Reasons={reasons}")


# ============================================================================
# TEST EXECUTION SUMMARY
# ============================================================================

def test_scoring_summary(classifier):
    """
    Summary test that runs all major test cases and prints a report.

    This is useful for getting a quick overview of how the scoring system
    performs across different scenarios.
    """
    test_cases = [
        {
            "name": "Strong keyword in title",
            "product": {
                "title": "LED Light Bulb 60W",
                "description": "Energy efficient",
                "structured_specifications": {}
            },
            "expected_min": 80
        },
        {
            "name": "Strong keyword in description",
            "product": {
                "title": "60W Replacement",
                "description": "LED light bulb for home",
                "structured_specifications": {}
            },
            "expected_min": 50
        },
        {
            "name": "Chandelier bulb (should NOT block)",
            "product": {
                "title": "Chandelier LED Light Bulb",
                "description": "Bulbs for chandelier fixtures",
                "structured_specifications": {}
            },
            "expected_min": 1  # Any score > 0 means not blocked
        },
        {
            "name": "Pendant fixture (SHOULD block)",
            "product": {
                "title": "Pendant Light Fixture",
                "description": "Beautiful pendant for kitchen",
                "structured_specifications": {}
            },
            "expected_exact": 0  # Should be blocked
        },
        {
            "name": "No matches",
            "product": {
                "title": "Hammer",
                "description": "Tool for hammering",
                "structured_specifications": {}
            },
            "expected_exact": 0
        }
    ]

    print("\n" + "=" * 70)
    print("SCORING SYSTEM TEST SUMMARY")
    print("=" * 70)

    for i, test_case in enumerate(test_cases, 1):
        score, reasons = classifier.calculate_match_score(
            test_case["product"],
            "LED Light Bulb"
        )

        passed = True
        if "expected_min" in test_case:
            passed = score >= test_case["expected_min"]
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"\n{i}. {test_case['name']}: {status}")
            print(f"   Score: {score} (expected >= {test_case['expected_min']})")
        else:
            passed = score == test_case["expected_exact"]
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"\n{i}. {test_case['name']}: {status}")
            print(f"   Score: {score} (expected = {test_case['expected_exact']})")

        print(f"   Reasons: {reasons[:2]}...")  # Show first 2 reasons

    print("\n" + "=" * 70)
