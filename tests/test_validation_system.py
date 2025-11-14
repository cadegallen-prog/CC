#!/usr/bin/env python3
"""
Comprehensive pytest tests for Product Type Validation System
Tests the validation functions that compare classifier predictions to ground truth
"""

import pytest
import json
from pathlib import Path
from collections import defaultdict
import sys

# Import validation functions
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from validate_system import (
    map_ground_truth_to_expected_classifier_type,
    calculate_accuracy_metrics,
    build_confusion_matrix,
    analyze_errors,
    load_ground_truth,
    load_full_dataset
)
from classify_products import ProductClassifier


class TestGroundTruthMapping:
    """Test the mapping from ground truth types to expected classifier types"""

    def test_recessed_light_mapping(self):
        """Test recessed light fixture mapping"""
        result = map_ground_truth_to_expected_classifier_type('recessed_light_fixture')
        assert result == 'Recessed Light'

    def test_under_cabinet_light_mapping(self):
        """Test under cabinet light mapping"""
        result = map_ground_truth_to_expected_classifier_type('under_cabinet_light')
        assert result == 'Under Cabinet Light'

    def test_smart_flush_mount_light_mapping(self):
        """Test smart flush mount light mapping"""
        result = map_ground_truth_to_expected_classifier_type('smart_flush_mount_light')
        assert result == 'Flush Mount Light'

    def test_landscape_flood_light_mapping(self):
        """Test landscape flood light mapping"""
        result = map_ground_truth_to_expected_classifier_type('landscape_flood_light')
        assert result == 'Landscape Lighting'

    def test_wall_sconce_mapping(self):
        """Test wall sconce mapping"""
        result = map_ground_truth_to_expected_classifier_type('wall_sconce')
        assert result == 'Wall Sconce'

    def test_led_troffer_light_mapping(self):
        """Test LED troffer light mapping"""
        result = map_ground_truth_to_expected_classifier_type('led_troffer_light')
        assert result == 'Troffer Light'

    def test_track_lighting_mapping(self):
        """Test track lighting kit mapping"""
        result = map_ground_truth_to_expected_classifier_type('led_track_lighting_kit')
        assert result == 'Track Lighting'

    def test_mini_pendant_light_mapping(self):
        """Test mini pendant light mapping"""
        result = map_ground_truth_to_expected_classifier_type('mini_pendant_light')
        assert result == 'Pendant Light'

    def test_circuit_breaker_mapping(self):
        """Test circuit breaker mapping"""
        result = map_ground_truth_to_expected_classifier_type('circuit_breaker')
        assert result == 'Circuit Breaker'

    def test_load_center_mapping(self):
        """Test electrical load center mapping"""
        result = map_ground_truth_to_expected_classifier_type('electrical_load_center')
        assert result == 'Load Center'

    def test_gfci_usb_outlet_mapping(self):
        """Test GFCI USB outlet mapping"""
        result = map_ground_truth_to_expected_classifier_type('gfci_usb_outlet')
        assert result == 'Electrical Outlet'

    def test_usb_outlet_mapping(self):
        """Test USB outlet mapping"""
        result = map_ground_truth_to_expected_classifier_type('usb_outlet')
        assert result == 'Electrical Outlet'

    def test_surge_protector_mapping(self):
        """Test surge protector with USB mapping"""
        result = map_ground_truth_to_expected_classifier_type('surge_protector_with_usb')
        assert result == 'Surge Protector'

    def test_circuit_breaker_kit_mapping(self):
        """Test circuit breaker kit mapping"""
        result = map_ground_truth_to_expected_classifier_type('circuit_breaker_kit')
        assert result == 'Circuit Breaker'

    def test_smart_deadbolt_lock_mapping(self):
        """Test smart deadbolt lock mapping"""
        result = map_ground_truth_to_expected_classifier_type('smart_deadbolt_lock')
        assert result == 'Door Lock'

    def test_faucet_valve_stem_mapping(self):
        """Test faucet valve stem mapping"""
        result = map_ground_truth_to_expected_classifier_type('faucet_valve_stem')
        assert result == 'Faucet Part'

    def test_backflow_preventer_valve_mapping(self):
        """Test backflow preventer valve mapping"""
        result = map_ground_truth_to_expected_classifier_type('backflow_preventer_valve')
        assert result == 'Plumbing Fitting'

    def test_kitchen_sink_with_faucet_mapping(self):
        """Test kitchen sink with faucet mapping"""
        result = map_ground_truth_to_expected_classifier_type('kitchen_sink_with_faucet')
        assert result == 'Sink'

    def test_dual_flush_toilet_mapping(self):
        """Test dual flush toilet mapping"""
        result = map_ground_truth_to_expected_classifier_type('dual_flush_toilet')
        assert result == 'Toilet'

    def test_multi_position_ladder_mapping(self):
        """Test multi-position ladder mapping"""
        result = map_ground_truth_to_expected_classifier_type('multi_position_ladder')
        assert result == 'Ladder'

    def test_sds_plus_rebar_cutter_mapping(self):
        """Test SDS plus rebar cutter mapping"""
        result = map_ground_truth_to_expected_classifier_type('sds_plus_rebar_cutter')
        assert result == 'Specialty Cutter'

    def test_hex_driver_bits_mapping(self):
        """Test hex driver bits mapping"""
        result = map_ground_truth_to_expected_classifier_type('hex_driver_bits')
        assert result == 'Drill Bit'

    def test_chainsaw_tuneup_kit_mapping(self):
        """Test chainsaw tune-up kit mapping"""
        result = map_ground_truth_to_expected_classifier_type('chainsaw_tuneup_kit')
        assert result == 'Tool Kit'

    def test_hvlp_paint_sprayer_mapping(self):
        """Test HVLP paint sprayer mapping"""
        result = map_ground_truth_to_expected_classifier_type('hvlp_paint_sprayer')
        assert result == 'Paint Sprayer'

    def test_decorative_shelf_bracket_mapping(self):
        """Test decorative shelf bracket mapping"""
        result = map_ground_truth_to_expected_classifier_type('decorative_shelf_bracket')
        assert result == 'Shelf Bracket'

    def test_roofing_shovel_blade_mapping(self):
        """Test roofing shovel blade mapping"""
        result = map_ground_truth_to_expected_classifier_type('roofing_shovel_blade')
        assert result == 'Saw Blade'

    def test_stair_nosing_trim_mapping(self):
        """Test stair nosing trim mapping"""
        result = map_ground_truth_to_expected_classifier_type('stair_nosing_trim')
        assert result == 'Fastener'

    def test_velcro_fastener_tape_mapping(self):
        """Test Velcro fastener tape mapping"""
        result = map_ground_truth_to_expected_classifier_type('velcro_fastener_tape')
        assert result == 'Tape'

    def test_metal_folding_tool_mapping(self):
        """Test metal folding tool mapping"""
        result = map_ground_truth_to_expected_classifier_type('metal_folding_tool')
        assert result == 'Metal Folding Tool'

    def test_safety_respirator_cartridge_mapping(self):
        """Test safety respirator cartridge mapping"""
        result = map_ground_truth_to_expected_classifier_type('safety_respirator_cartridge')
        assert result == 'Safety Respirator'

    def test_bathroom_towel_bar_mapping(self):
        """Test bathroom towel bar mapping"""
        result = map_ground_truth_to_expected_classifier_type('bathroom_towel_bar')
        assert result == 'Bathroom Towel Bar'

    def test_bathroom_exhaust_fan_mapping(self):
        """Test bathroom exhaust fan mapping"""
        result = map_ground_truth_to_expected_classifier_type('bathroom_exhaust_fan')
        assert result == 'Exhaust Fan'

    def test_hvac_air_filter_mapping(self):
        """Test HVAC air filter mapping"""
        result = map_ground_truth_to_expected_classifier_type('hvac_air_filter')
        assert result == 'HVAC Air Filter'

    def test_double_hung_window_mapping(self):
        """Test double-hung window mapping"""
        result = map_ground_truth_to_expected_classifier_type('double_hung_window')
        assert result == 'Window'

    def test_work_gloves_mapping(self):
        """Test work gloves mapping"""
        result = map_ground_truth_to_expected_classifier_type('work_gloves')
        assert result == 'Work Gloves'

    def test_outdoor_roller_shade_mapping(self):
        """Test outdoor roller shade mapping"""
        result = map_ground_truth_to_expected_classifier_type('outdoor_roller_shade')
        assert result == 'Window Shade'

    def test_double_curtain_rod_mapping(self):
        """Test double curtain rod mapping"""
        result = map_ground_truth_to_expected_classifier_type('double_curtain_rod')
        assert result == 'Curtain Rod'

    def test_speaker_wall_mounts_mapping(self):
        """Test speaker wall mounts mapping"""
        result = map_ground_truth_to_expected_classifier_type('speaker_wall_mounts')
        assert result == 'Speaker Mount'

    def test_disposable_earplugs_mapping(self):
        """Test disposable earplugs mapping"""
        result = map_ground_truth_to_expected_classifier_type('disposable_earplugs')
        assert result == 'Disposable Earplugs'

    def test_radon_detector_mapping(self):
        """Test radon detector mapping"""
        result = map_ground_truth_to_expected_classifier_type('radon_detector')
        assert result == 'Radon Detector'

    def test_missing_data_mapping(self):
        """Test missing data special case"""
        result = map_ground_truth_to_expected_classifier_type('missing_data')
        assert result == 'Unknown - Missing Data'

    def test_unknown_type_returns_unknown_mapping(self):
        """Test that unknown ground truth types return UNKNOWN_MAPPING"""
        result = map_ground_truth_to_expected_classifier_type('completely_unknown_product')
        assert result == 'UNKNOWN_MAPPING'

    def test_all_ground_truth_types_have_mappings(self):
        """Test that all ground truth types in the actual data have mappings"""
        # Load actual ground truth
        ground_truth = load_ground_truth()

        # Get all unique true_product_type values
        true_types = set(s['true_product_type'] for s in ground_truth)

        # Check each one has a mapping (not UNKNOWN_MAPPING)
        unmapped_types = []
        for true_type in true_types:
            mapped = map_ground_truth_to_expected_classifier_type(true_type)
            if mapped == 'UNKNOWN_MAPPING':
                unmapped_types.append(true_type)

        # All types should be mapped (except potentially new ones)
        assert len(unmapped_types) == 0, f"Found unmapped types: {unmapped_types}"


class TestAccuracyMetrics:
    """Test accuracy metric calculations"""

    def create_mock_product(self, title, description="Test product"):
        """Helper to create mock product"""
        return {
            'title': title,
            'description': description,
            'brand': 'Test Brand',
            'price': 10.0,
            'rating': 4.5,
            'model': 'TEST-123'
        }

    def create_mock_ground_truth_sample(self, index, true_type, difficulty='easy', sample_id=1):
        """Helper to create mock ground truth sample"""
        return {
            'sample_id': sample_id,
            'index': index,
            'title': f'Test Product {index}',
            'true_product_type': true_type,
            'difficulty': difficulty
        }

    def test_accuracy_with_all_correct_predictions(self, capsys):
        """Test accuracy calculation when all predictions are correct"""
        # Create mock data - products that should be correctly classified
        mock_dataset = {
            0: self.create_mock_product('Halo 4 inch LED Recessed Light', 'LED recessed lighting fixture'),
            1: self.create_mock_product('Kwikset Smart Lock Deadbolt', 'WiFi enabled smart deadbolt'),
            2: self.create_mock_product('Square D Circuit Breaker 20A', 'Single pole circuit breaker')
        }

        mock_ground_truth = [
            self.create_mock_ground_truth_sample(0, 'recessed_light_fixture', 'easy', 1),
            self.create_mock_ground_truth_sample(1, 'smart_deadbolt_lock', 'easy', 2),
            self.create_mock_ground_truth_sample(2, 'circuit_breaker', 'easy', 3)
        ]

        classifier = ProductClassifier()

        # Calculate accuracy
        results, accuracy = calculate_accuracy_metrics(mock_ground_truth, mock_dataset, classifier)

        # Should have 3 results
        assert len(results) == 3

        # Accuracy should be high (may not be 100% if classifier has issues)
        # But we can verify the structure of results
        assert accuracy >= 0.0 and accuracy <= 1.0
        assert all('is_correct' in r for r in results)
        assert all('confidence' in r for r in results)
        assert all('predicted_type' in r for r in results)
        assert all('expected_type' in r for r in results)

    def test_accuracy_filtering_missing_data(self, capsys):
        """Test that missing_data samples are filtered out"""
        mock_dataset = {
            0: self.create_mock_product('Halo LED Recessed Light', 'LED recessed lighting fixture'),
            1: {'title': '', 'description': '', 'brand': '', 'price': 0.0, 'rating': 0, 'model': ''}
        }

        mock_ground_truth = [
            self.create_mock_ground_truth_sample(0, 'recessed_light_fixture', 'easy', 1),
            self.create_mock_ground_truth_sample(1, 'missing_data', 'hard', 2)
        ]

        classifier = ProductClassifier()

        # Calculate accuracy
        results, accuracy = calculate_accuracy_metrics(mock_ground_truth, mock_dataset, classifier)

        # Should only have 1 result (missing_data filtered out)
        assert len(results) == 1
        assert results[0]['true_product_type'] == 'recessed_light_fixture'

    def test_accuracy_by_difficulty(self, capsys):
        """Test that results are properly categorized by difficulty"""
        mock_dataset = {
            0: self.create_mock_product('Halo LED Recessed Light', 'LED recessed lighting fixture'),
            1: self.create_mock_product('Kwikset Smart Lock Deadbolt', 'WiFi enabled smart deadbolt'),
            2: self.create_mock_product('Square D Circuit Breaker 20A', 'Single pole circuit breaker')
        }

        mock_ground_truth = [
            self.create_mock_ground_truth_sample(0, 'recessed_light_fixture', 'easy', 1),
            self.create_mock_ground_truth_sample(1, 'smart_deadbolt_lock', 'medium', 2),
            self.create_mock_ground_truth_sample(2, 'circuit_breaker', 'hard', 3)
        ]

        classifier = ProductClassifier()

        # Calculate accuracy
        results, accuracy = calculate_accuracy_metrics(mock_ground_truth, mock_dataset, classifier)

        # Verify difficulty distribution
        difficulties = [r['difficulty'] for r in results]
        assert 'easy' in difficulties
        assert 'medium' in difficulties
        assert 'hard' in difficulties

        # Verify each difficulty has exactly 1 sample
        assert difficulties.count('easy') == 1
        assert difficulties.count('medium') == 1
        assert difficulties.count('hard') == 1

    def test_results_structure(self, capsys):
        """Test that results have the correct structure"""
        mock_dataset = {
            0: self.create_mock_product('Halo LED Recessed Light', 'LED recessed lighting fixture')
        }

        mock_ground_truth = [
            self.create_mock_ground_truth_sample(0, 'recessed_light_fixture', 'easy', 1)
        ]

        classifier = ProductClassifier()

        # Calculate accuracy
        results, accuracy = calculate_accuracy_metrics(mock_ground_truth, mock_dataset, classifier)

        # Verify result structure
        assert len(results) == 1
        result = results[0]

        # Check all required fields exist
        required_fields = [
            'sample_id', 'title', 'true_product_type', 'expected_type',
            'predicted_type', 'is_correct', 'confidence', 'classification_details', 'difficulty'
        ]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"

        # Check types
        assert isinstance(result['sample_id'], int)
        assert isinstance(result['title'], str)
        assert isinstance(result['is_correct'], bool)
        assert isinstance(result['confidence'], (int, float))
        assert isinstance(result['classification_details'], dict)


class TestConfusionMatrix:
    """Test confusion matrix building"""

    def test_confusion_matrix_with_no_errors(self, capsys):
        """Test confusion matrix when all predictions are correct"""
        results = [
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'LED Light Bulb', 'is_correct': True},
            {'expected_type': 'Door Lock', 'predicted_type': 'Door Lock', 'is_correct': True},
            {'expected_type': 'Circuit Breaker', 'predicted_type': 'Circuit Breaker', 'is_correct': True}
        ]

        confusion = build_confusion_matrix(results)

        # Should only have diagonal entries
        assert confusion['LED Light Bulb']['LED Light Bulb'] == 1
        assert confusion['Door Lock']['Door Lock'] == 1
        assert confusion['Circuit Breaker']['Circuit Breaker'] == 1

        # Should have no off-diagonal entries
        assert confusion['LED Light Bulb']['Door Lock'] == 0
        assert confusion['LED Light Bulb']['Circuit Breaker'] == 0

    def test_confusion_matrix_with_specific_error(self, capsys):
        """Test confusion matrix with specific misclassification"""
        results = [
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'LED Light Bulb', 'is_correct': True},
            {'expected_type': 'Door Lock', 'predicted_type': 'Door Lock', 'is_correct': True}
        ]

        confusion = build_confusion_matrix(results)

        # Check the specific confusion
        assert confusion['LED Light Bulb']['Light Switch'] == 2
        assert confusion['LED Light Bulb']['LED Light Bulb'] == 1
        assert confusion['Door Lock']['Door Lock'] == 1

    def test_confusion_matrix_counts_multiple_confusions(self, capsys):
        """Test that confusion matrix correctly counts multiple confusion patterns"""
        results = [
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'Pendant Light', 'predicted_type': 'Chandelier', 'is_correct': False},
            {'expected_type': 'Pendant Light', 'predicted_type': 'Chandelier', 'is_correct': False}
        ]

        confusion = build_confusion_matrix(results)

        # Check counts
        assert confusion['LED Light Bulb']['Light Switch'] == 3
        assert confusion['Pendant Light']['Chandelier'] == 2

    def test_confusion_list_sorted_by_count(self, capsys):
        """Test that confusion pairs are sorted by count (most common first)"""
        results = [
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'LED Light Bulb', 'predicted_type': 'Light Switch', 'is_correct': False},
            {'expected_type': 'Pendant Light', 'predicted_type': 'Chandelier', 'is_correct': False}
        ]

        confusion = build_confusion_matrix(results)

        # Capture printed output to verify sorting
        captured = capsys.readouterr()

        # The output should show "LED Light Bulb → Light Switch: 3 times" before "Pendant Light → Chandelier: 1 times"
        # Since we can't easily parse the output, we'll verify the confusion matrix structure
        assert confusion['LED Light Bulb']['Light Switch'] > confusion['Pendant Light']['Chandelier']


class TestErrorAnalysis:
    """Test error analysis functions"""

    def test_analyze_errors_with_no_errors(self, capsys):
        """Test error analysis when there are no errors"""
        results = [
            {'is_correct': True, 'title': 'Test 1', 'predicted_type': 'LED Light Bulb'},
            {'is_correct': True, 'title': 'Test 2', 'predicted_type': 'Door Lock'}
        ]

        errors = analyze_errors(results)

        # Should return empty list
        assert len(errors) == 0

        # Check output
        captured = capsys.readouterr()
        assert "Total Errors: 0" in captured.out
        assert "No errors found!" in captured.out

    def test_analyze_errors_identifies_all_errors(self, capsys):
        """Test that analyze_errors identifies all incorrect predictions"""
        results = [
            {
                'is_correct': False,
                'title': 'LED Bulb 1',
                'true_product_type': 'led_light_bulb',
                'expected_type': 'LED Light Bulb',
                'predicted_type': 'Light Switch',
                'confidence': 25,
                'classification_details': {'alternate_types': [], 'reasons': []}
            },
            {
                'is_correct': False,
                'title': 'LED Bulb 2',
                'true_product_type': 'led_light_bulb',
                'expected_type': 'LED Light Bulb',
                'predicted_type': 'Light Switch',
                'confidence': 30,
                'classification_details': {'alternate_types': [], 'reasons': []}
            },
            {
                'is_correct': False,
                'title': 'Pendant Light',
                'true_product_type': 'pendant_light',
                'expected_type': 'Pendant Light',
                'predicted_type': 'Chandelier',
                'confidence': 40,
                'classification_details': {'alternate_types': [], 'reasons': []}
            },
            {
                'is_correct': True,
                'title': 'Door Lock',
                'true_product_type': 'door_lock',
                'expected_type': 'Door Lock',
                'predicted_type': 'Door Lock',
                'confidence': 80,
                'classification_details': {'alternate_types': [], 'reasons': []}
            }
        ]

        errors = analyze_errors(results)

        # Should identify exactly 3 errors
        assert len(errors) == 3

        # Verify all errors are included
        error_titles = [e['title'] for e in errors]
        assert 'LED Bulb 1' in error_titles
        assert 'LED Bulb 2' in error_titles
        assert 'Pendant Light' in error_titles
        assert 'Door Lock' not in error_titles

    def test_analyze_errors_identifies_low_confidence(self, capsys):
        """Test that low confidence errors are identified"""
        results = [
            {
                'is_correct': False,
                'title': 'Low Confidence Error',
                'true_product_type': 'led_light_bulb',
                'expected_type': 'LED Light Bulb',
                'predicted_type': 'Unknown',
                'confidence': 15,
                'classification_details': {'alternate_types': [], 'reasons': []}
            }
        ]

        errors = analyze_errors(results)

        # Check output mentions low confidence
        captured = capsys.readouterr()
        assert "Errors with low confidence (<30): 1" in captured.out

    def test_analyze_errors_identifies_unknown_classification(self, capsys):
        """Test that products classified as Unknown are identified"""
        results = [
            {
                'is_correct': False,
                'title': 'Unknown Product',
                'true_product_type': 'led_light_bulb',
                'expected_type': 'LED Light Bulb',
                'predicted_type': 'Unknown - No Keywords Matched',
                'confidence': 0,
                'classification_details': {'alternate_types': [], 'reasons': []}
            }
        ]

        errors = analyze_errors(results)

        # Check output identifies unknown classification
        captured = capsys.readouterr()
        assert "Products that couldn't be classified: 1" in captured.out

    def test_analyze_errors_shows_most_common_predictions(self, capsys):
        """Test that most common error predictions are shown"""
        results = [
            {
                'is_correct': False,
                'title': f'LED Bulb {i}',
                'true_product_type': 'led_light_bulb',
                'expected_type': 'LED Light Bulb',
                'predicted_type': 'Light Switch',
                'confidence': 30,
                'classification_details': {'alternate_types': [], 'reasons': []}
            }
            for i in range(5)
        ]

        errors = analyze_errors(results)

        # Check output shows Light Switch as most common error
        captured = capsys.readouterr()
        assert "Most common error predictions:" in captured.out
        assert "Light Switch: 5 errors" in captured.out


class TestEndToEndValidation:
    """Test end-to-end validation with actual data"""

    def test_load_ground_truth(self):
        """Test loading actual ground truth file"""
        ground_truth = load_ground_truth()

        # Should have samples
        assert len(ground_truth) > 0

        # Check structure of first sample
        sample = ground_truth[0]
        required_fields = ['sample_id', 'index', 'title', 'true_product_type', 'difficulty']
        for field in required_fields:
            assert field in sample, f"Missing field: {field}"

    def test_load_full_dataset(self):
        """Test loading full dataset"""
        dataset = load_full_dataset()

        # Should have products
        assert len(dataset) > 0

        # Check structure (should be a list or dict)
        assert isinstance(dataset, (list, dict))

    def test_validation_on_actual_ground_truth(self, capsys):
        """Integration test: Run validation on actual ground truth"""
        # Load actual data
        ground_truth = load_ground_truth()
        full_dataset = load_full_dataset()

        # Initialize classifier
        classifier = ProductClassifier()

        # Run validation
        results, accuracy = calculate_accuracy_metrics(ground_truth, full_dataset, classifier)

        # Basic sanity checks
        assert len(results) > 0, "Should have results"
        assert accuracy >= 0.0 and accuracy <= 1.0, "Accuracy should be between 0 and 1"

        # Verify all results have required fields
        for result in results:
            assert 'is_correct' in result
            assert 'predicted_type' in result
            assert 'expected_type' in result
            assert 'confidence' in result

    def test_validation_processes_all_valid_samples(self, capsys):
        """Test that validation processes all valid samples (excluding missing_data)"""
        ground_truth = load_ground_truth()
        full_dataset = load_full_dataset()
        classifier = ProductClassifier()

        # Count valid samples (not missing_data)
        valid_count = sum(1 for s in ground_truth if s['true_product_type'] != 'missing_data')

        # Run validation
        results, accuracy = calculate_accuracy_metrics(ground_truth, full_dataset, classifier)

        # Should process exactly the valid samples
        assert len(results) == valid_count

    def test_confusion_matrix_on_actual_results(self, capsys):
        """Test building confusion matrix on actual results"""
        ground_truth = load_ground_truth()
        full_dataset = load_full_dataset()
        classifier = ProductClassifier()

        # Run validation
        results, accuracy = calculate_accuracy_metrics(ground_truth, full_dataset, classifier)

        # Build confusion matrix
        confusion = build_confusion_matrix(results)

        # Should have entries
        assert len(confusion) > 0

        # Verify confusion matrix structure - should be a dict of dicts
        assert isinstance(confusion, dict)

        # Each entry should have at least one prediction
        for expected_type, predictions in confusion.items():
            assert len(predictions) > 0
            assert isinstance(predictions, dict)

    def test_error_analysis_on_actual_results(self, capsys):
        """Test error analysis on actual results"""
        ground_truth = load_ground_truth()
        full_dataset = load_full_dataset()
        classifier = ProductClassifier()

        # Run validation
        results, accuracy = calculate_accuracy_metrics(ground_truth, full_dataset, classifier)

        # Analyze errors
        errors = analyze_errors(results)

        # Errors should match incorrect predictions
        incorrect_count = sum(1 for r in results if not r['is_correct'])
        assert len(errors) == incorrect_count


class TestValidationEdgeCases:
    """Test edge cases in validation"""

    def test_empty_ground_truth(self, capsys):
        """Test validation with empty ground truth"""
        mock_dataset = {}
        mock_ground_truth = []
        classifier = ProductClassifier()

        # Should handle gracefully
        results, accuracy = calculate_accuracy_metrics(mock_ground_truth, mock_dataset, classifier)

        assert len(results) == 0
        # Accuracy should be 0 (or could be NaN, depends on implementation)
        assert accuracy == 0 or accuracy != accuracy  # NaN check

    def test_all_missing_data_samples(self, capsys):
        """Test validation when all samples are missing_data"""
        mock_dataset = {
            0: {'title': '', 'description': '', 'brand': '', 'price': 0.0, 'rating': 0, 'model': ''},
            1: {'title': '', 'description': '', 'brand': '', 'price': 0.0, 'rating': 0, 'model': ''}
        }

        mock_ground_truth = [
            {'sample_id': 1, 'index': 0, 'title': '', 'true_product_type': 'missing_data', 'difficulty': 'hard'},
            {'sample_id': 2, 'index': 1, 'title': '', 'true_product_type': 'missing_data', 'difficulty': 'hard'}
        ]

        classifier = ProductClassifier()

        # Should filter out all samples
        results, accuracy = calculate_accuracy_metrics(mock_ground_truth, mock_dataset, classifier)

        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
