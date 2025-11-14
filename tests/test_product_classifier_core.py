#!/usr/bin/env python3
"""
Unit tests for ProductClassifier core utility functions

Tests the fundamental text processing and keyword matching functions
that form the foundation of the classification system.
"""

import pytest
from classify_products import ProductClassifier


class TestNormalizeText:
    """Tests for the normalize_text utility function"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_normalize_basic_text(self, classifier):
        """Test basic text normalization with mixed case"""
        result = classifier.normalize_text("LED Light Bulb")
        assert result == "led light bulb", \
            f"Expected 'led light bulb', got '{result}'"

    def test_normalize_multiple_spaces(self, classifier):
        """Test normalization removes extra spaces"""
        result = classifier.normalize_text("  Multiple   Spaces  ")
        assert result == "multiple spaces", \
            f"Expected 'multiple spaces', got '{result}'"

    def test_normalize_empty_string(self, classifier):
        """Test normalization of empty string returns empty string"""
        result = classifier.normalize_text("")
        assert result == "", \
            f"Expected empty string, got '{result}'"

    def test_normalize_none_input(self, classifier):
        """Test normalization of None returns empty string"""
        result = classifier.normalize_text(None)
        assert result == "", \
            f"Expected empty string for None input, got '{result}'"

    def test_normalize_tabs_and_newlines(self, classifier):
        """Test normalization handles tabs and newlines"""
        result = classifier.normalize_text("Text\twith\ttabs\nand\nnewlines")
        assert result == "text with tabs and newlines", \
            f"Expected normalized text, got '{result}'"

    def test_normalize_mixed_whitespace(self, classifier):
        """Test normalization handles various whitespace characters"""
        result = classifier.normalize_text("  \t LED  \n  Light   Bulb  \t ")
        assert result == "led light bulb", \
            f"Expected 'led light bulb', got '{result}'"

    def test_normalize_already_normalized(self, classifier):
        """Test normalization of already normalized text"""
        result = classifier.normalize_text("already normalized text")
        assert result == "already normalized text", \
            f"Expected 'already normalized text', got '{result}'"

    def test_normalize_uppercase_only(self, classifier):
        """Test normalization converts all uppercase to lowercase"""
        result = classifier.normalize_text("CEILING FAN")
        assert result == "ceiling fan", \
            f"Expected 'ceiling fan', got '{result}'"

    def test_normalize_special_characters(self, classifier):
        """Test normalization preserves special characters"""
        result = classifier.normalize_text("LED-Light $19.99 (50% off)")
        assert result == "led-light $19.99 (50% off)", \
            f"Expected special characters preserved, got '{result}'"


class TestContainsKeyword:
    """Tests for the contains_keyword utility function"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    # Single-word keyword tests
    def test_contains_single_word_keyword_found(self, classifier):
        """Test finding a single-word keyword in text"""
        result = classifier.contains_keyword("led light bulb", "bulb")
        assert result is True, \
            "Expected 'bulb' to be found in 'led light bulb'"

    def test_contains_single_word_at_start(self, classifier):
        """Test finding keyword at the start of text"""
        result = classifier.contains_keyword("ceiling fan light", "ceiling")
        assert result is True, \
            "Expected 'ceiling' to be found at start of text"

    def test_contains_single_word_at_end(self, classifier):
        """Test finding keyword at the end of text"""
        result = classifier.contains_keyword("ceiling fan", "fan")
        assert result is True, \
            "Expected 'fan' to be found at end of text"

    def test_contains_prevents_false_match_brush(self, classifier):
        """Test that 'brush' doesn't match 'brushed nickel'"""
        result = classifier.contains_keyword("brushed nickel", "brush")
        assert result is False, \
            "Expected 'brush' NOT to match within 'brushed nickel'"

    def test_contains_prevents_false_match_fantastic(self, classifier):
        """Test that 'fan' doesn't match within 'fantastic'"""
        result = classifier.contains_keyword("fantastic", "fan")
        assert result is False, \
            "Expected 'fan' NOT to match within 'fantastic'"

    def test_contains_prevents_false_match_pendant(self, classifier):
        """Test that 'pend' doesn't match within 'pendant'"""
        result = classifier.contains_keyword("pendant light", "pend")
        assert result is False, \
            "Expected 'pend' NOT to match within 'pendant'"

    # Multi-word keyword tests
    def test_contains_multi_word_keyword_found(self, classifier):
        """Test finding a multi-word keyword"""
        result = classifier.contains_keyword("led light bulb", "led light")
        assert result is True, \
            "Expected 'led light' to be found in 'led light bulb'"

    def test_contains_multi_word_exact_match(self, classifier):
        """Test multi-word keyword matching entire text"""
        result = classifier.contains_keyword("ceiling fan", "ceiling fan")
        assert result is True, \
            "Expected 'ceiling fan' to match 'ceiling fan'"

    def test_contains_multi_word_not_found(self, classifier):
        """Test multi-word keyword not found"""
        result = classifier.contains_keyword("led bulb", "ceiling fan")
        assert result is False, \
            "Expected 'ceiling fan' NOT to be found in 'led bulb'"

    def test_contains_multi_word_partial_words(self, classifier):
        """Test multi-word keyword matches if substring present (no word boundaries for multi-word)"""
        # Note: Multi-word keywords use simple substring matching (line 716 in classify_products.py)
        # So "bulb fix" WILL match in "bulb fixture" since it's a substring
        result = classifier.contains_keyword("light bulb fixture", "bulb fix")
        assert result is True, \
            "Expected 'bulb fix' to match as substring in 'bulb fixture'"

    # Edge cases
    def test_contains_keyword_empty_text(self, classifier):
        """Test searching in empty text"""
        result = classifier.contains_keyword("", "bulb")
        assert result is False, \
            "Expected no match in empty text"

    def test_contains_keyword_only_keyword(self, classifier):
        """Test when text is exactly the keyword"""
        result = classifier.contains_keyword("bulb", "bulb")
        assert result is True, \
            "Expected 'bulb' to match 'bulb' exactly"

    def test_contains_keyword_with_punctuation(self, classifier):
        """Test keyword matching with punctuation boundaries"""
        result = classifier.contains_keyword("led, light, bulb", "light")
        assert result is True, \
            "Expected 'light' to be found even with punctuation"

    def test_contains_keyword_with_hyphen(self, classifier):
        """Test keyword matching with hyphenated words"""
        result = classifier.contains_keyword("led-light bulb", "light")
        assert result is True, \
            "Expected 'light' to be found in hyphenated word"

    def test_contains_case_sensitive(self, classifier):
        """Test that keyword matching is case-sensitive"""
        result = classifier.contains_keyword("LED Light Bulb", "led")
        assert result is False, \
            "Expected case-sensitive match to fail for 'led' vs 'LED'"

    def test_contains_case_match(self, classifier):
        """Test keyword matching with matching case"""
        result = classifier.contains_keyword("led light bulb", "led")
        assert result is True, \
            "Expected 'led' to be found in lowercase text"

    # Real-world product examples
    def test_contains_real_world_chandelier_bulb(self, classifier):
        """Test real-world case: chandelier LED light bulbs"""
        text = "chandelier led light bulbs soft white"

        # Note: "bulb" (singular) won't match "bulbs" (plural) due to word boundaries
        # Need to search for the actual word form in the text
        assert classifier.contains_keyword(text, "bulbs") is True, \
            "Expected 'bulbs' to be found in chandelier bulb product"
        assert classifier.contains_keyword(text, "led") is True, \
            "Expected 'led' to be found in chandelier bulb product"

        # Should match 'chandelier' as a complete word
        assert classifier.contains_keyword(text, "chandelier") is True, \
            "Expected 'chandelier' to be found as complete word"

        # Demonstrate that singular 'bulb' does NOT match plural 'bulbs' (word boundary behavior)
        assert classifier.contains_keyword(text, "bulb") is False, \
            "Expected 'bulb' NOT to match 'bulbs' due to word boundaries"

    def test_contains_real_world_pendant_bulb(self, classifier):
        """Test real-world case: pendant light bulbs"""
        text = "pendant light bulbs dimmable led"

        # Should match individual keywords (using correct word form)
        assert classifier.contains_keyword(text, "bulbs") is True, \
            "Expected 'bulbs' to be found in pendant bulb product"
        assert classifier.contains_keyword(text, "pendant") is True, \
            "Expected 'pendant' to be found as complete word"

        # Multi-word keyword with substring match
        assert classifier.contains_keyword(text, "light bulb") is True, \
            "Expected 'light bulb' to be found as substring in 'light bulbs'"

        # Demonstrate singular vs plural word boundary behavior
        assert classifier.contains_keyword(text, "bulb") is False, \
            "Expected 'bulb' NOT to match 'bulbs' due to word boundaries"

    def test_contains_real_world_ceiling_fan(self, classifier):
        """Test real-world case: ceiling fan products"""
        text = "modern ceiling fan with light"

        # Should match both single and multi-word
        assert classifier.contains_keyword(text, "fan") is True, \
            "Expected 'fan' to be found"
        assert classifier.contains_keyword(text, "ceiling fan") is True, \
            "Expected 'ceiling fan' to be found"

        # Should NOT match partial words
        assert classifier.contains_keyword(text, "ceil") is False, \
            "Expected 'ceil' NOT to match within 'ceiling'"

    def test_contains_real_world_brushed_nickel(self, classifier):
        """Test real-world case: brushed nickel products"""
        text = "brushed nickel door handle"

        # Should NOT match 'brush' (the key test case from requirements)
        assert classifier.contains_keyword(text, "brush") is False, \
            "Expected 'brush' NOT to match within 'brushed'"

        # Should match 'brushed' as complete word
        assert classifier.contains_keyword(text, "brushed") is True, \
            "Expected 'brushed' to be found as complete word"

        # Should match 'nickel'
        assert classifier.contains_keyword(text, "nickel") is True, \
            "Expected 'nickel' to be found"


class TestKeywordMatchingIntegration:
    """Integration tests combining normalize_text and contains_keyword"""

    @pytest.fixture
    def classifier(self):
        """Create a ProductClassifier instance for testing"""
        return ProductClassifier()

    def test_normalize_then_search(self, classifier):
        """Test typical workflow: normalize text then search for keywords"""
        raw_text = "  LED Light BULB  Soft White  "
        normalized = classifier.normalize_text(raw_text)

        assert normalized == "led light bulb soft white", \
            f"Expected normalized text, got '{normalized}'"

        assert classifier.contains_keyword(normalized, "bulb") is True, \
            "Expected 'bulb' to be found in normalized text"
        assert classifier.contains_keyword(normalized, "led light") is True, \
            "Expected 'led light' to be found in normalized text"

    def test_normalize_handles_edge_cases_for_search(self, classifier):
        """Test that normalization prepares text correctly for keyword search"""
        # Text with extra spaces that could break word boundary detection
        raw_text = "ceiling   fan   light"
        normalized = classifier.normalize_text(raw_text)

        # After normalization, keywords should be properly detectable
        assert classifier.contains_keyword(normalized, "fan") is True, \
            "Expected 'fan' to be found after normalization"
        assert classifier.contains_keyword(normalized, "ceiling fan") is True, \
            "Expected 'ceiling fan' to be found after normalization"

    def test_case_insensitive_workflow(self, classifier):
        """Test that normalize_text enables case-insensitive keyword matching"""
        # Different case variations
        texts = [
            "LED Light Bulb",
            "led light bulb",
            "LED LIGHT BULB",
            "Led Light Bulb"
        ]

        for text in texts:
            normalized = classifier.normalize_text(text)
            assert classifier.contains_keyword(normalized, "led") is True, \
                f"Expected 'led' to be found in normalized '{text}'"
            assert classifier.contains_keyword(normalized, "bulb") is True, \
                f"Expected 'bulb' to be found in normalized '{text}'"
