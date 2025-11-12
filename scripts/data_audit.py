#!/usr/bin/env python3
"""
Data Audit Script for scraped_data_output.json
Analyzes schema, records, duplicates, null patterns, and text cleaning needs
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

def load_data(file_path):
    """Load JSON data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def analyze_schema(data):
    """Analyze data schema and structure"""
    print("=" * 80)
    print("SCHEMA ANALYSIS")
    print("=" * 80)

    if isinstance(data, list):
        print(f"Data Type: List of {len(data)} records")
        if data:
            print(f"\nSample Record Structure:")
            sample = data[0]
            for key, value in sample.items():
                value_type = type(value).__name__
                value_preview = str(value)[:100] if value else "None"
                print(f"  - {key}: {value_type}")
                print(f"    Preview: {value_preview}")

            # Get all unique keys across all records
            all_keys = set()
            for record in data:
                if isinstance(record, dict):
                    all_keys.update(record.keys())
            print(f"\nAll Unique Keys Found ({len(all_keys)}): {sorted(all_keys)}")

    elif isinstance(data, dict):
        print(f"Data Type: Dictionary with {len(data)} keys")
        print(f"Keys: {list(data.keys())}")

    return data

def analyze_records(data):
    """Analyze record counts and basic statistics"""
    print("\n" + "=" * 80)
    print("RECORD COUNT ANALYSIS")
    print("=" * 80)

    if not isinstance(data, list):
        print("Data is not a list of records")
        return data

    print(f"Total Records: {len(data)}")

    # Get all keys
    all_keys = set()
    for record in data:
        if isinstance(record, dict):
            all_keys.update(record.keys())

    print(f"Total Unique Keys: {len(all_keys)}")
    print(f"\nKeys: {sorted(all_keys)}")

    # Analyze key presence
    key_counts = defaultdict(int)
    for record in data:
        if isinstance(record, dict):
            for key in record.keys():
                key_counts[key] += 1

    print(f"\nKey Presence:")
    for key in sorted(key_counts.keys()):
        count = key_counts[key]
        pct = (count / len(data)) * 100
        print(f"  - {key}: {count} ({pct:.2f}%)")

    return data

def analyze_duplicates(data):
    """Analyze duplicates in the data"""
    print("\n" + "=" * 80)
    print("DUPLICATE ANALYSIS")
    print("=" * 80)

    if not isinstance(data, list):
        return data

    # Check for key columns
    key_columns = ['title', 'product_url', 'asin', 'product_id']

    for col in key_columns:
        values = []
        for record in data:
            if isinstance(record, dict) and col in record:
                values.append(record[col])

        if values:
            total = len(values)
            unique = len(set(values))
            dupes = total - unique
            none_count = values.count(None) + values.count('')

            print(f"\n{col}:")
            print(f"  - Total Values: {total}")
            print(f"  - Unique Values: {unique}")
            print(f"  - Duplicates: {dupes}")
            print(f"  - None/Empty: {none_count}")

            # Show most common duplicates
            if dupes > 0:
                counter = Counter(values)
                most_common = [item for item, count in counter.most_common(3) if count > 1]
                if most_common:
                    print(f"  - Most Duplicated (top 3):")
                    for item in most_common[:3]:
                        count = counter[item]
                        preview = str(item)[:60]
                        print(f"    * '{preview}' (x{count})")

    return data

def analyze_nulls(data):
    """Analyze null/missing patterns"""
    print("\n" + "=" * 80)
    print("NULL/MISSING VALUE ANALYSIS")
    print("=" * 80)

    if not isinstance(data, list):
        return data

    total_records = len(data)

    # Get all keys
    all_keys = set()
    for record in data:
        if isinstance(record, dict):
            all_keys.update(record.keys())

    # Count nulls/missing for each key
    null_stats = {}
    for key in all_keys:
        null_count = 0
        empty_count = 0
        missing_count = 0

        for record in data:
            if isinstance(record, dict):
                if key not in record:
                    missing_count += 1
                elif record[key] is None:
                    null_count += 1
                elif record[key] == '':
                    empty_count += 1

        null_stats[key] = {
            'null': null_count,
            'empty': empty_count,
            'missing': missing_count,
            'total_invalid': null_count + empty_count + missing_count
        }

    print(f"\nMissing/Null Values by Key:")
    for key in sorted(null_stats.keys()):
        stats = null_stats[key]
        total_invalid = stats['total_invalid']
        pct = (total_invalid / total_records) * 100
        print(f"\n  {key}:")
        print(f"    - Missing Key: {stats['missing']}")
        print(f"    - Null Values: {stats['null']}")
        print(f"    - Empty Strings: {stats['empty']}")
        print(f"    - TOTAL INVALID: {total_invalid} ({pct:.2f}%)")

    return data

def analyze_text_cleaning_needs(data):
    """Identify text cleaning requirements"""
    print("\n" + "=" * 80)
    print("TEXT CLEANING REQUIREMENTS")
    print("=" * 80)

    if not isinstance(data, list):
        return data

    # Focus on text fields
    text_fields = ['title', 'description', 'brand', 'category', 'product_name']

    for field in text_fields:
        values = []
        for record in data:
            if isinstance(record, dict) and field in record and record[field]:
                values.append(str(record[field]))

        if not values:
            continue

        print(f"\n{field.upper()}:")
        print(f"  Total Non-Empty Values: {len(values)}")

        # Check for common issues
        has_html = sum(1 for v in values if re.search(r'<[^>]+>', v))
        has_extra_spaces = sum(1 for v in values if re.search(r'\s{2,}', v))
        has_special_chars = sum(1 for v in values if re.search(r'[^\w\s\-.,!?()&/]', v))
        has_newlines = sum(1 for v in values if re.search(r'[\n\r]', v))
        has_brackets = sum(1 for v in values if '[' in v or ']' in v)
        has_pipes = sum(1 for v in values if '|' in v)

        print(f"  Issues Found:")
        print(f"    - HTML Tags: {has_html}")
        print(f"    - Extra Spaces: {has_extra_spaces}")
        print(f"    - Special Characters: {has_special_chars}")
        print(f"    - Newlines: {has_newlines}")
        print(f"    - Brackets: {has_brackets}")
        print(f"    - Pipes: {has_pipes}")

        # Length statistics
        lengths = [len(v) for v in values]
        avg_length = sum(lengths) / len(lengths)
        min_length = min(lengths)
        max_length = max(lengths)

        print(f"  Length Statistics:")
        print(f"    - Avg: {avg_length:.1f} chars")
        print(f"    - Min: {min_length} chars")
        print(f"    - Max: {max_length} chars")

        # Show samples
        print(f"  Sample Values (first 3):")
        for i, val in enumerate(values[:3], 1):
            preview = val[:120].replace('\n', ' ')
            print(f"    {i}. {preview}")

    return data

def main():
    # File path
    data_file = Path("/home/user/CC/data/scraped_data_output.json")

    print("Loading data...")
    data = load_data(data_file)

    # Schema analysis
    data = analyze_schema(data)

    # Record analysis
    data = analyze_records(data)

    # Duplicate analysis
    data = analyze_duplicates(data)

    # Null analysis
    data = analyze_nulls(data)

    # Text cleaning analysis
    data = analyze_text_cleaning_needs(data)

    print("\n" + "=" * 80)
    print("DATA AUDIT COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
