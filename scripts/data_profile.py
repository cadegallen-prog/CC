#!/usr/bin/env python3
"""
Data Profiling Tool for Product Data Analysis

This script provides comprehensive statistical analysis of scraped product data
without interacting with taxonomy systems. It's designed for extensibility and
reusability across different data analysis workflows.

USAGE:
    # Basic profiling (prints to console)
    python scripts/data_profile.py

    # Export metrics to JSON file
    python scripts/data_profile.py --export-metrics output/metrics.json

    # Future feature: Brand normalization analysis
    python scripts/data_profile.py --brand-normalization

CORE FUNCTIONALITY:
    - Record count and unique brand/model statistics
    - Title and description length analysis
    - Price quartile analysis (Q1, median, Q3)
    - Missing field detection and reporting
    - JSON export capability for metrics

REQUIREMENTS:
    - Input: data/scraped_data_output.json
    - Python 3.7+
    - Standard library only (json, argparse, statistics)

EXTENSIBILITY HOOKS:
    - Brand normalization (placeholder)
    - Custom field analysis (placeholder)
    - Data quality scoring (placeholder)
"""

import json
import argparse
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter


class DataProfiler:
    """Main class for profiling scraped product data."""

    def __init__(self, data_path: str = "data/scraped_data_output.json"):
        """
        Initialize the data profiler.

        Args:
            data_path: Path to the JSON data file
        """
        self.data_path = Path(data_path)
        self.data: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}

    def load_data(self) -> None:
        """Load JSON data from file."""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✓ Loaded {len(self.data)} records from {self.data_path}")
        except FileNotFoundError:
            print(f"✗ Error: Data file not found at {self.data_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON format - {e}")
            raise

    def analyze_record_counts(self) -> Dict[str, Any]:
        """Analyze basic record counts and uniqueness."""
        brands = [record.get('brand', '') for record in self.data if record.get('brand')]
        models = [record.get('model', '') for record in self.data if record.get('model')]

        metrics = {
            'total_records': len(self.data),
            'unique_brands': len(set(brands)),
            'unique_models': len(set(models)),
            'top_brands': dict(Counter(brands).most_common(10))
        }

        return metrics

    def analyze_text_fields(self) -> Dict[str, Any]:
        """Analyze title and description length statistics."""
        title_lengths = [
            len(record.get('title', ''))
            for record in self.data
            if record.get('title')
        ]

        desc_lengths = [
            len(record.get('description', ''))
            for record in self.data
            if record.get('description')
        ]

        def get_stats(lengths: List[int], field_name: str) -> Dict[str, Any]:
            """Calculate statistics for a list of lengths."""
            if not lengths:
                return {
                    f'{field_name}_count': 0,
                    f'{field_name}_min': None,
                    f'{field_name}_max': None,
                    f'{field_name}_mean': None,
                    f'{field_name}_median': None
                }

            return {
                f'{field_name}_count': len(lengths),
                f'{field_name}_min': min(lengths),
                f'{field_name}_max': max(lengths),
                f'{field_name}_mean': round(statistics.mean(lengths), 2),
                f'{field_name}_median': round(statistics.median(lengths), 2)
            }

        metrics = {
            **get_stats(title_lengths, 'title_length'),
            **get_stats(desc_lengths, 'description_length')
        }

        return metrics

    def analyze_prices(self) -> Dict[str, Any]:
        """Analyze price quartiles and statistics."""
        prices = [
            record.get('price')
            for record in self.data
            if record.get('price') is not None
        ]

        if not prices:
            return {
                'price_count': 0,
                'price_q1': None,
                'price_median': None,
                'price_q3': None,
                'price_min': None,
                'price_max': None,
                'price_mean': None
            }

        sorted_prices = sorted(prices)

        metrics = {
            'price_count': len(prices),
            'price_q1': round(statistics.quantiles(sorted_prices, n=4)[0], 2),
            'price_median': round(statistics.median(sorted_prices), 2),
            'price_q3': round(statistics.quantiles(sorted_prices, n=4)[2], 2),
            'price_min': round(min(prices), 2),
            'price_max': round(max(prices), 2),
            'price_mean': round(statistics.mean(prices), 2)
        }

        return metrics

    def analyze_missing_fields(self) -> Dict[str, Any]:
        """Analyze missing fields and return indices/IDs of affected records."""
        fields_to_check = ['title', 'description', 'brand', 'model', 'price', 'images']
        missing_report: Dict[str, List[int]] = {field: [] for field in fields_to_check}

        for idx, record in enumerate(self.data):
            for field in fields_to_check:
                value = record.get(field)
                # Check if field is missing, None, empty string, or empty list
                if value is None or value == '' or (isinstance(value, list) and len(value) == 0):
                    missing_report[field].append(idx)

        # Calculate percentages
        total_records = len(self.data)
        missing_summary = {
            f'{field}_missing_count': len(indices)
            for field, indices in missing_report.items()
        }

        missing_summary.update({
            f'{field}_missing_percentage': round((len(indices) / total_records * 100), 2)
            for field, indices in missing_report.items()
        })

        metrics = {
            'missing_field_summary': missing_summary,
            'missing_field_indices': missing_report
        }

        return metrics

    def generate_full_profile(self) -> Dict[str, Any]:
        """Generate complete data profile with all metrics."""
        print("\n" + "=" * 70)
        print("DATA PROFILING REPORT")
        print("=" * 70)

        # Record counts
        print("\n📊 RECORD STATISTICS")
        print("-" * 70)
        record_metrics = self.analyze_record_counts()
        print(f"Total Records:     {record_metrics['total_records']:,}")
        print(f"Unique Brands:     {record_metrics['unique_brands']:,}")
        print(f"Unique Models:     {record_metrics['unique_models']:,}")

        print("\nTop 10 Brands by Product Count:")
        for brand, count in list(record_metrics['top_brands'].items())[:10]:
            print(f"  • {brand}: {count}")

        # Text field analysis
        print("\n📝 TEXT FIELD STATISTICS")
        print("-" * 70)
        text_metrics = self.analyze_text_fields()

        print("Title Lengths:")
        print(f"  Records with titles: {text_metrics['title_length_count']:,}")
        print(f"  Min length:          {text_metrics['title_length_min']}")
        print(f"  Max length:          {text_metrics['title_length_max']}")
        print(f"  Mean length:         {text_metrics['title_length_mean']}")
        print(f"  Median length:       {text_metrics['title_length_median']}")

        print("\nDescription Lengths:")
        print(f"  Records with descriptions: {text_metrics['description_length_count']:,}")
        print(f"  Min length:                {text_metrics['description_length_min']}")
        print(f"  Max length:                {text_metrics['description_length_max']}")
        print(f"  Mean length:               {text_metrics['description_length_mean']}")
        print(f"  Median length:             {text_metrics['description_length_median']}")

        # Price analysis
        print("\n💰 PRICE STATISTICS")
        print("-" * 70)
        price_metrics = self.analyze_prices()

        print(f"Records with prices: {price_metrics['price_count']:,}")
        print(f"Price Range:         ${price_metrics['price_min']} - ${price_metrics['price_max']}")
        print(f"Q1 (25th percentile): ${price_metrics['price_q1']}")
        print(f"Median (50th):        ${price_metrics['price_median']}")
        print(f"Q3 (75th percentile): ${price_metrics['price_q3']}")
        print(f"Mean:                 ${price_metrics['price_mean']}")

        # Missing fields
        print("\n⚠️  MISSING FIELD REPORT")
        print("-" * 70)
        missing_metrics = self.analyze_missing_fields()
        summary = missing_metrics['missing_field_summary']
        indices = missing_metrics['missing_field_indices']

        fields = ['title', 'description', 'brand', 'model', 'price', 'images']
        for field in fields:
            count = summary[f'{field}_missing_count']
            percentage = summary[f'{field}_missing_percentage']
            print(f"{field.capitalize():15} Missing: {count:5} ({percentage:5.2f}%)")

            # Show first few indices if any are missing
            if count > 0 and count <= 10:
                print(f"                 Indices: {indices[field]}")
            elif count > 10:
                print(f"                 First 10 indices: {indices[field][:10]}")

        # Compile all metrics
        self.metrics = {
            'record_statistics': record_metrics,
            'text_statistics': text_metrics,
            'price_statistics': price_metrics,
            'missing_fields': missing_metrics
        }

        print("\n" + "=" * 70)
        print("END OF REPORT")
        print("=" * 70 + "\n")

        return self.metrics

    def export_metrics(self, output_path: str) -> None:
        """
        Export metrics to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)

        print(f"✓ Metrics exported to {output_path}")

    # =========================================================================
    # EXTENSIBILITY HOOKS - Placeholder methods for future features
    # =========================================================================

    def analyze_brand_normalization(self) -> None:
        """
        [PLACEHOLDER] Analyze brand name variations and suggest normalizations.

        Future implementation will:
        - Detect brand name variations (e.g., "HP" vs "Hewlett-Packard")
        - Suggest normalization rules
        - Flag potential duplicates
        """
        print("\n🔧 BRAND NORMALIZATION ANALYSIS")
        print("-" * 70)
        print("TODO: Brand normalization feature not yet implemented")
        print("This will analyze brand name variations and suggest normalizations")
        print("-" * 70 + "\n")

    def analyze_data_quality_score(self) -> Dict[str, Any]:
        """
        [PLACEHOLDER] Calculate data quality score for each record.

        Future implementation will score based on:
        - Field completeness
        - Data consistency
        - Value validity
        """
        pass

    def analyze_custom_fields(self, field_names: List[str]) -> Dict[str, Any]:
        """
        [PLACEHOLDER] Analyze custom fields specified by user.

        Args:
            field_names: List of field names to analyze

        Returns:
            Dictionary of metrics for specified fields
        """
        pass


def main():
    """Main entry point for the data profiling tool."""
    parser = argparse.ArgumentParser(
        description="Data profiling tool for product data analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/data_profile.py
  python scripts/data_profile.py --export-metrics output/metrics.json
  python scripts/data_profile.py --brand-normalization
        """
    )

    parser.add_argument(
        '--data-path',
        default='data/scraped_data_output.json',
        help='Path to input JSON data file (default: data/scraped_data_output.json)'
    )

    parser.add_argument(
        '--export-metrics',
        metavar='OUTPUT_PATH',
        help='Export metrics to JSON file at specified path'
    )

    parser.add_argument(
        '--brand-normalization',
        action='store_true',
        help='[PLACEHOLDER] Analyze brand name variations (feature not yet implemented)'
    )

    args = parser.parse_args()

    # Initialize profiler
    profiler = DataProfiler(data_path=args.data_path)

    # Load data
    profiler.load_data()

    # Generate profile
    profiler.generate_full_profile()

    # Handle optional features
    if args.brand_normalization:
        profiler.analyze_brand_normalization()

    if args.export_metrics:
        profiler.export_metrics(args.export_metrics)


if __name__ == '__main__':
    main()
