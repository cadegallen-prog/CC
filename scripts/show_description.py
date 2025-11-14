#!/usr/bin/env python3
import csv
from pathlib import Path

csv_path = Path(__file__).parent.parent / 'data' / 'scraped_data.csv'
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row['index']) == 0:
            print(f"Title: {row['title']}\n")
            print(f"Description:\n{row['description']}")
            break
