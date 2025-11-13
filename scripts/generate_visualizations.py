#!/usr/bin/env python3
"""
Product Visualization Dashboard Generator
Generates comprehensive visualizations and reports for product type identification
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import re
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Paths
BASE_DIR = Path("/home/user/CC")
DATA_FILE = BASE_DIR / "data/scraped_data_output.json"
PATTERN_FILE = BASE_DIR / "data/pattern_discovery_results.json"
OUTPUT_DIR = BASE_DIR / "outputs/visualizations"
EXPORTS_DIR = BASE_DIR / "exports"
REPORTS_DIR = BASE_DIR / "reports"

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load product data and pattern results"""
    print("Loading data...")
    with open(DATA_FILE) as f:
        products = json.load(f)

    with open(PATTERN_FILE) as f:
        patterns = json.load(f)

    return products, patterns

def extract_product_type(product):
    """
    Extract detailed product type from title and description
    Returns a more specific product type than just category
    """
    title = product.get('title', '').lower()
    description = product.get('description', '').lower()

    # Define product type patterns (order matters - more specific first)
    type_patterns = {
        # Lighting
        'LED Light Bulb': r'\bled\s+(?:light\s+)?bulb',
        'Ceiling Fan': r'ceiling\s+fan',
        'Chandelier': r'chandelier',
        'Pendant Light': r'pendant\s+light',
        'Recessed Light': r'recessed\s+(?:light|lighting)',
        'Track Light': r'track\s+light',
        'Vanity Light': r'vanity\s+light',
        'Wall Sconce': r'wall\s+sconce',
        'Flush Mount Light': r'flush\s+mount',
        'Table Lamp': r'table\s+lamp',
        'Floor Lamp': r'floor\s+lamp',
        'String Lights': r'string\s+lights',
        'Light Fixture': r'light\s+fixture',
        'Light Bulb': r'(?:incandescent|halogen|cfl)\s+bulb',

        # Electrical
        'Electrical Outlet': r'(?:electrical\s+)?outlet|receptacle',
        'Light Switch': r'light\s+switch|wall\s+switch',
        'Dimmer Switch': r'dimmer\s+switch',
        'GFCI Outlet': r'gfci\s+outlet',
        'USB Outlet': r'usb\s+outlet',
        'Electrical Wire': r'electrical\s+wire|copper\s+wire',
        'Extension Cord': r'extension\s+cord',
        'Power Strip': r'power\s+strip',
        'Junction Box': r'junction\s+box',
        'Circuit Breaker': r'circuit\s+breaker',

        # Locks & Hardware
        'Door Lock': r'door\s+lock',
        'Deadbolt': r'deadbolt',
        'Smart Lock': r'smart\s+lock',
        'Padlock': r'padlock',
        'Door Knob': r'door\s+knob|door\s+handle',
        'Door Hinge': r'door\s+hinge',
        'Cabinet Lock': r'cabinet\s+lock',

        # Plumbing
        'Faucet': r'faucet',
        'Showerhead': r'shower\s*head',
        'Toilet': r'toilet(?!\s+paper)',
        'Sink': r'\bsink\b',
        'Bathtub': r'bathtub|bath\s+tub',
        'Water Heater': r'water\s+heater',
        'Pipe': r'\bpipe\b|piping',
        'Drain': r'drain',
        'Valve': r'valve',

        # Tools
        'Drill': r'\bdrill\b',
        'Saw': r'\bsaw\b',
        'Hammer': r'hammer',
        'Screwdriver': r'screwdriver',
        'Wrench': r'wrench',
        'Pliers': r'pliers',
        'Tool Set': r'tool\s+(?:set|kit)',
        'Power Tool': r'power\s+tool',
        'Drill Bit': r'drill\s+bit',
        'Saw Blade': r'saw\s+blade',

        # Paint
        'Paint': r'\bpaint\b',
        'Primer': r'primer',
        'Stain': r'stain',
        'Paint Brush': r'paint\s+brush',
        'Paint Roller': r'paint\s+roller',

        # Smart Home
        'Smart Thermostat': r'smart\s+thermostat',
        'Smart Switch': r'smart\s+switch',
        'Smart Plug': r'smart\s+plug',
        'Smart Doorbell': r'smart\s+doorbell',
        'Security Camera': r'security\s+camera',
    }

    # Check patterns
    for product_type, pattern in type_patterns.items():
        if re.search(pattern, title) or re.search(pattern, description):
            return product_type

    # Fallback to generic categories
    if 'light' in title or 'bulb' in title or 'lamp' in title:
        return 'Lighting (Other)'
    elif 'electrical' in title or 'outlet' in title or 'switch' in title:
        return 'Electrical (Other)'
    elif 'lock' in title or 'key' in title:
        return 'Lock/Hardware'
    elif 'faucet' in title or 'plumbing' in title or 'water' in title:
        return 'Plumbing (Other)'
    elif 'tool' in title:
        return 'Tool (Other)'
    elif 'paint' in title:
        return 'Paint (Other)'
    else:
        return 'Other/Uncategorized'

def calculate_confidence_score(product):
    """
    Calculate confidence score based on data completeness and quality
    Higher score = better data quality
    """
    score = 0
    max_score = 100

    # Title exists and is descriptive (0-20 points)
    title = product.get('title', '')
    if title:
        score += 10
        if len(title) > 30:  # Detailed title
            score += 10

    # Description exists (0-20 points)
    description = product.get('description', '')
    if description:
        score += 10
        if len(description) > 100:  # Detailed description
            score += 10

    # Brand exists (0-10 points)
    if product.get('brand'):
        score += 10

    # Price exists (0-10 points)
    if product.get('price') or product.get('sale_price'):
        score += 10

    # Specifications exist (0-20 points)
    specs = product.get('structured_specifications', {})
    if specs:
        score += 10
        if len(specs) >= 3:  # Multiple specs
            score += 10

    # Images exist (0-10 points)
    images = product.get('images', [])
    if images:
        score += 10

    # Ratings/reviews exist (0-10 points)
    if product.get('rating') or product.get('reviews'):
        score += 10

    return min(score, max_score)

def get_category_from_type(product_type):
    """Map detailed product type back to broad category"""
    type_lower = product_type.lower()

    if any(word in type_lower for word in ['light', 'bulb', 'lamp', 'fixture', 'chandelier', 'sconce', 'fan']):
        return 'lighting'
    elif any(word in type_lower for word in ['electrical', 'outlet', 'switch', 'wire', 'cord', 'breaker']):
        return 'electrical'
    elif any(word in type_lower for word in ['lock', 'deadbolt', 'knob', 'hinge', 'hardware']):
        return 'locks'
    elif any(word in type_lower for word in ['faucet', 'shower', 'toilet', 'sink', 'plumbing', 'pipe', 'drain', 'valve']):
        return 'plumbing'
    elif any(word in type_lower for word in ['drill', 'saw', 'hammer', 'tool', 'wrench', 'blade']):
        return 'tools'
    elif 'paint' in type_lower or 'primer' in type_lower or 'stain' in type_lower:
        return 'paint'
    elif 'smart' in type_lower or 'camera' in type_lower:
        return 'smart_home'
    else:
        return 'uncategorized'

def analyze_products(products):
    """Analyze all products and extract insights"""
    print("Analyzing products...")

    results = []
    for i, product in enumerate(products):
        product_type = extract_product_type(product)
        confidence = calculate_confidence_score(product)
        category = get_category_from_type(product_type)

        # Extract price
        price = product.get('price') or product.get('sale_price') or 0
        if isinstance(price, str):
            price = float(re.sub(r'[^\d.]', '', price)) if re.sub(r'[^\d.]', '', price) else 0

        # Extract rating
        rating = product.get('rating', 0)
        if isinstance(rating, str):
            rating = float(rating) if rating else 0

        result = {
            'product_id': i + 1,
            'title': product.get('title', ''),
            'brand': product.get('brand', 'Unknown'),
            'product_type': product_type,
            'category': category,
            'price': price,
            'rating': rating,
            'confidence_score': confidence,
            'has_description': bool(product.get('description')),
            'has_specs': bool(product.get('structured_specifications')),
            'has_images': bool(product.get('images')),
            'review_count': product.get('reviews', 0) if isinstance(product.get('reviews'), (int, float)) else 0,
        }
        results.append(result)

    df = pd.DataFrame(results)
    print(f"Analyzed {len(df)} products")
    print(f"Found {df['product_type'].nunique()} unique product types")

    return df

def create_product_type_distribution(df):
    """Create product type distribution charts"""
    print("Creating product type distribution charts...")

    # Count products by type
    type_counts = df['product_type'].value_counts()

    # Chart 1: Top 20 product types
    plt.figure(figsize=(14, 8))
    top_20 = type_counts.head(20)
    colors = sns.color_palette("husl", len(top_20))
    bars = plt.barh(range(len(top_20)), top_20.values, color=colors)
    plt.yticks(range(len(top_20)), top_20.index)
    plt.xlabel('Number of Products', fontsize=12, fontweight='bold')
    plt.title('Top 20 Product Types by Count', fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_20.values)):
        plt.text(val + 0.5, i, str(val), va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'product_type_distribution_top20.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 2: Long tail visualization
    plt.figure(figsize=(14, 6))
    all_counts = type_counts.values
    plt.plot(range(1, len(all_counts) + 1), all_counts, linewidth=2, color='#2E86AB')
    plt.fill_between(range(1, len(all_counts) + 1), all_counts, alpha=0.3, color='#2E86AB')
    plt.xlabel('Product Type Rank', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
    plt.title('Product Type Distribution: The Long Tail', fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3)

    # Add annotation for long tail
    plt.axvline(x=20, color='red', linestyle='--', alpha=0.7, linewidth=2)
    plt.text(22, max(all_counts) * 0.8, 'Top 20 Types', fontsize=11, fontweight='bold', color='red')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'product_type_long_tail.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 3: Category distribution with confidence colors
    plt.figure(figsize=(12, 8))

    # Group by type and get average confidence
    type_conf = df.groupby('product_type')['confidence_score'].mean()
    type_counts_with_conf = pd.DataFrame({
        'count': type_counts.head(20),
        'confidence': type_conf[type_counts.head(20).index]
    })

    # Create color map based on confidence
    norm = plt.Normalize(vmin=60, vmax=100)
    colors = plt.cm.RdYlGn(norm(type_counts_with_conf['confidence'].values))

    bars = plt.barh(range(len(type_counts_with_conf)), type_counts_with_conf['count'].values, color=colors)
    plt.yticks(range(len(type_counts_with_conf)), type_counts_with_conf.index)
    plt.xlabel('Number of Products', fontsize=12, fontweight='bold')
    plt.title('Top 20 Product Types (Color = Confidence Level)', fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca(), orientation='vertical', pad=0.01)
    cbar.set_label('Average Confidence Score', fontsize=11, fontweight='bold')

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, type_counts_with_conf['count'].values)):
        plt.text(val + 0.5, i, str(val), va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'product_type_by_confidence.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_data_quality_visualizations(df):
    """Create data quality visualization charts"""
    print("Creating data quality charts...")

    # Chart 1: Field completeness
    plt.figure(figsize=(10, 6))

    completeness = {
        'Title': (df['title'] != '').sum() / len(df) * 100,
        'Brand': (df['brand'] != 'Unknown').sum() / len(df) * 100,
        'Price': (df['price'] > 0).sum() / len(df) * 100,
        'Description': df['has_description'].sum() / len(df) * 100,
        'Specifications': df['has_specs'].sum() / len(df) * 100,
        'Images': df['has_images'].sum() / len(df) * 100,
        'Rating': (df['rating'] > 0).sum() / len(df) * 100,
    }

    colors = ['#2E7D32' if v >= 80 else '#F57C00' if v >= 50 else '#C62828' for v in completeness.values()]
    bars = plt.bar(completeness.keys(), completeness.values(), color=colors, edgecolor='black', linewidth=1.5)
    plt.ylabel('Completeness (%)', fontsize=12, fontweight='bold')
    plt.title('Data Field Completeness Across All Products', fontsize=16, fontweight='bold', pad=20)
    plt.ylim(0, 105)
    plt.xticks(rotation=45, ha='right')

    # Add value labels
    for bar, val in zip(bars, completeness.values()):
        plt.text(bar.get_x() + bar.get_width()/2, val + 2, f'{val:.1f}%',
                ha='center', va='bottom', fontweight='bold')

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2E7D32', label='Good (≥80%)'),
        Patch(facecolor='#F57C00', label='Fair (50-80%)'),
        Patch(facecolor='#C62828', label='Poor (<50%)')
    ]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'data_completeness.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 2: Confidence score distribution
    plt.figure(figsize=(12, 6))

    # Create bins for confidence scores
    bins = [0, 50, 70, 85, 100]
    labels = ['Low (0-50)', 'Medium (50-70)', 'High (70-85)', 'Very High (85-100)']
    df['confidence_bin'] = pd.cut(df['confidence_score'], bins=bins, labels=labels)

    confidence_counts = df['confidence_bin'].value_counts().sort_index()
    colors = ['#C62828', '#F57C00', '#FBC02D', '#2E7D32']

    bars = plt.bar(range(len(confidence_counts)), confidence_counts.values,
                   color=colors, edgecolor='black', linewidth=1.5, width=0.7)
    plt.xticks(range(len(confidence_counts)), confidence_counts.index, rotation=0)
    plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
    plt.title('Product Confidence Score Distribution', fontsize=16, fontweight='bold', pad=20)

    # Add value labels
    for bar, val in zip(bars, confidence_counts.values):
        plt.text(bar.get_x() + bar.get_width()/2, val + 3, str(val),
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'confidence_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 3: Correlation between data completeness and confidence
    plt.figure(figsize=(10, 6))

    # Calculate completeness score for each product
    df['completeness_score'] = (
        (df['title'] != '').astype(int) * 20 +
        (df['brand'] != 'Unknown').astype(int) * 15 +
        (df['price'] > 0).astype(int) * 15 +
        df['has_description'].astype(int) * 20 +
        df['has_specs'].astype(int) * 15 +
        df['has_images'].astype(int) * 10 +
        (df['rating'] > 0).astype(int) * 5
    )

    plt.scatter(df['completeness_score'], df['confidence_score'],
               alpha=0.5, s=50, c='#2E86AB', edgecolors='black', linewidth=0.5)
    plt.xlabel('Data Completeness Score', fontsize=12, fontweight='bold')
    plt.ylabel('Confidence Score', fontsize=12, fontweight='bold')
    plt.title('Correlation: Data Completeness vs Confidence Score', fontsize=16, fontweight='bold', pad=20)

    # Add trend line
    z = np.polyfit(df['completeness_score'], df['confidence_score'], 1)
    p = np.poly1d(z)
    plt.plot(df['completeness_score'].sort_values(),
            p(df['completeness_score'].sort_values()),
            "r--", linewidth=2, alpha=0.8, label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'completeness_vs_confidence.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_price_analysis(df):
    """Create price analysis charts by product type"""
    print("Creating price analysis charts...")

    # Filter out products without price
    df_with_price = df[df['price'] > 0].copy()

    # Chart 1: Price range by top product types
    plt.figure(figsize=(14, 8))

    # Get top 15 types by count
    top_types = df['product_type'].value_counts().head(15).index
    df_top = df_with_price[df_with_price['product_type'].isin(top_types)]

    # Create box plot
    type_order = df_top.groupby('product_type')['price'].median().sort_values(ascending=False).index

    box_plot = df_top.boxplot(column='price', by='product_type',
                              figsize=(14, 8), rot=45, patch_artist=True)

    plt.suptitle('')  # Remove default title
    plt.title('Price Ranges by Product Type (Top 15)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Product Type', fontsize=12, fontweight='bold')
    plt.ylabel('Price ($)', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'price_ranges_by_type.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 2: Average price by type (bar chart)
    plt.figure(figsize=(14, 8))

    avg_prices = df_top.groupby('product_type')['price'].mean().sort_values(ascending=True).tail(20)
    colors = sns.color_palette("viridis", len(avg_prices))

    bars = plt.barh(range(len(avg_prices)), avg_prices.values, color=colors, edgecolor='black', linewidth=1)
    plt.yticks(range(len(avg_prices)), avg_prices.index)
    plt.xlabel('Average Price ($)', fontsize=12, fontweight='bold')
    plt.title('Average Price by Product Type (Top 20)', fontsize=16, fontweight='bold', pad=20)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, avg_prices.values)):
        plt.text(val + 1, i, f'${val:.2f}', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'average_price_by_type.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 3: Price distribution histogram
    plt.figure(figsize=(12, 6))

    plt.hist(df_with_price['price'], bins=50, color='#2E86AB', edgecolor='black', linewidth=1, alpha=0.7)
    plt.xlabel('Price ($)', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
    plt.title('Overall Price Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.axvline(df_with_price['price'].median(), color='red', linestyle='--',
               linewidth=2, label=f'Median: ${df_with_price["price"].median():.2f}')
    plt.axvline(df_with_price['price'].mean(), color='green', linestyle='--',
               linewidth=2, label=f'Mean: ${df_with_price["price"].mean():.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'price_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_brand_analysis(df):
    """Create brand analysis charts"""
    print("Creating brand analysis charts...")

    # Chart 1: Top brands by product count
    plt.figure(figsize=(12, 8))

    top_brands = df['brand'].value_counts().head(20)
    colors = sns.color_palette("Set2", len(top_brands))

    bars = plt.barh(range(len(top_brands)), top_brands.values, color=colors, edgecolor='black', linewidth=1)
    plt.yticks(range(len(top_brands)), top_brands.index)
    plt.xlabel('Number of Products', fontsize=12, fontweight='bold')
    plt.title('Top 20 Brands by Product Count', fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, top_brands.values)):
        plt.text(val + 0.5, i, str(val), va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'top_brands.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 2: Brand distribution by category
    plt.figure(figsize=(14, 8))

    # Get top 10 brands and top 6 categories
    top_10_brands = df['brand'].value_counts().head(10).index
    top_categories = df['category'].value_counts().head(6).index

    df_filtered = df[(df['brand'].isin(top_10_brands)) & (df['category'].isin(top_categories))]

    # Create pivot table
    brand_cat_matrix = df_filtered.pivot_table(
        index='brand',
        columns='category',
        values='product_id',
        aggfunc='count',
        fill_value=0
    )

    # Create heatmap
    sns.heatmap(brand_cat_matrix, annot=True, fmt='d', cmap='YlOrRd',
               cbar_kws={'label': 'Number of Products'}, linewidths=0.5, linecolor='gray')
    plt.title('Brand-Category Matrix (Top 10 Brands, Top 6 Categories)',
             fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Category', fontsize=12, fontweight='bold')
    plt.ylabel('Brand', fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'brand_category_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 3: Average price by brand
    plt.figure(figsize=(12, 8))

    df_with_price = df[(df['price'] > 0) & (df['brand'].isin(top_brands.head(15).index))]
    avg_price_by_brand = df_with_price.groupby('brand')['price'].mean().sort_values(ascending=True)

    colors = sns.color_palette("coolwarm", len(avg_price_by_brand))
    bars = plt.barh(range(len(avg_price_by_brand)), avg_price_by_brand.values,
                   color=colors, edgecolor='black', linewidth=1)
    plt.yticks(range(len(avg_price_by_brand)), avg_price_by_brand.index)
    plt.xlabel('Average Price ($)', fontsize=12, fontweight='bold')
    plt.title('Average Price by Brand (Top 15 Brands)', fontsize=16, fontweight='bold', pad=20)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, avg_price_by_brand.values)):
        plt.text(val + 1, i, f'${val:.2f}', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'average_price_by_brand.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_confidence_analysis(df):
    """Create confidence analysis charts"""
    print("Creating confidence analysis charts...")

    # Chart 1: Confidence by product type
    plt.figure(figsize=(14, 8))

    top_types = df['product_type'].value_counts().head(20).index
    df_top = df[df['product_type'].isin(top_types)]

    avg_conf_by_type = df_top.groupby('product_type')['confidence_score'].mean().sort_values(ascending=True)

    # Color by confidence level
    colors = ['#C62828' if x < 70 else '#F57C00' if x < 85 else '#2E7D32'
             for x in avg_conf_by_type.values]

    bars = plt.barh(range(len(avg_conf_by_type)), avg_conf_by_type.values,
                   color=colors, edgecolor='black', linewidth=1)
    plt.yticks(range(len(avg_conf_by_type)), avg_conf_by_type.index)
    plt.xlabel('Average Confidence Score', fontsize=12, fontweight='bold')
    plt.title('Average Confidence Score by Product Type (Top 20)', fontsize=16, fontweight='bold', pad=20)
    plt.xlim(0, 105)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, avg_conf_by_type.values)):
        plt.text(val + 1, i, f'{val:.1f}', va='center', fontweight='bold')

    # Add vertical lines for thresholds
    plt.axvline(x=70, color='orange', linestyle='--', alpha=0.5, linewidth=1.5)
    plt.axvline(x=85, color='green', linestyle='--', alpha=0.5, linewidth=1.5)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'confidence_by_type.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 2: Products needing manual review (low confidence)
    plt.figure(figsize=(12, 6))

    low_conf_products = df[df['confidence_score'] < 70]
    low_conf_by_type = low_conf_products['product_type'].value_counts().head(15)

    colors = sns.color_palette("Reds_r", len(low_conf_by_type))
    bars = plt.barh(range(len(low_conf_by_type)), low_conf_by_type.values,
                   color=colors, edgecolor='black', linewidth=1)
    plt.yticks(range(len(low_conf_by_type)), low_conf_by_type.index)
    plt.xlabel('Number of Products Needing Review', fontsize=12, fontweight='bold')
    plt.title(f'Products Requiring Manual Review (Confidence < 70) - Total: {len(low_conf_products)}',
             fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, low_conf_by_type.values)):
        plt.text(val + 0.3, i, str(val), va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'products_needing_review.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Chart 3: Confidence score histogram
    plt.figure(figsize=(12, 6))

    plt.hist(df['confidence_score'], bins=20, color='#2E86AB', edgecolor='black',
            linewidth=1, alpha=0.7)
    plt.xlabel('Confidence Score', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Products', fontsize=12, fontweight='bold')
    plt.title('Confidence Score Distribution', fontsize=16, fontweight='bold', pad=20)

    # Add vertical lines for average and median
    plt.axvline(df['confidence_score'].mean(), color='red', linestyle='--',
               linewidth=2, label=f'Mean: {df["confidence_score"].mean():.1f}')
    plt.axvline(df['confidence_score'].median(), color='green', linestyle='--',
               linewidth=2, label=f'Median: {df["confidence_score"].median():.1f}')

    # Add shaded regions
    plt.axvspan(0, 70, alpha=0.2, color='red', label='Low Confidence')
    plt.axvspan(70, 85, alpha=0.2, color='yellow', label='Medium Confidence')
    plt.axvspan(85, 100, alpha=0.2, color='green', label='High Confidence')

    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'confidence_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_category_overview(df):
    """Create broad category overview chart"""
    print("Creating category overview chart...")

    plt.figure(figsize=(12, 8))

    category_counts = df['category'].value_counts()
    colors = sns.color_palette("husl", len(category_counts))

    # Create pie chart
    wedges, texts, autotexts = plt.pie(category_counts.values,
                                        labels=category_counts.index,
                                        autopct='%1.1f%%',
                                        colors=colors,
                                        startangle=90,
                                        textprops={'fontsize': 11, 'fontweight': 'bold'})

    # Enhance text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')

    plt.title('Product Distribution by Category', fontsize=16, fontweight='bold', pad=20)

    # Add legend with counts
    legend_labels = [f'{cat}: {count}' for cat, count in zip(category_counts.index, category_counts.values)]
    plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'category_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def export_to_csv(df):
    """Export results to CSV"""
    print("Exporting to CSV...")

    export_df = df[[
        'product_id', 'title', 'brand', 'product_type', 'category',
        'price', 'rating', 'confidence_score'
    ]].copy()

    export_df.to_csv(EXPORTS_DIR / 'product_classifications.csv', index=False)
    print(f"Exported to {EXPORTS_DIR / 'product_classifications.csv'}")

def export_to_excel(df, products):
    """Export results to Excel with multiple sheets"""
    print("Exporting to Excel...")

    with pd.ExcelWriter(EXPORTS_DIR / 'product_classifications.xlsx', engine='openpyxl') as writer:
        # Sheet 1: All products with classifications
        export_df = df[[
            'product_id', 'title', 'brand', 'product_type', 'category',
            'price', 'rating', 'confidence_score', 'has_description', 'has_specs'
        ]].copy()
        export_df.to_excel(writer, sheet_name='All Products', index=False)

        # Sheet 2: Product type summary
        type_summary = df.groupby('product_type').agg({
            'product_id': 'count',
            'price': ['mean', 'min', 'max'],
            'confidence_score': 'mean',
            'rating': 'mean'
        }).round(2)
        type_summary.columns = ['Count', 'Avg Price', 'Min Price', 'Max Price', 'Avg Confidence', 'Avg Rating']
        type_summary = type_summary.sort_values('Count', ascending=False)
        type_summary.to_excel(writer, sheet_name='Type Summary')

        # Sheet 3: Category summary
        category_summary = df.groupby('category').agg({
            'product_id': 'count',
            'price': 'mean',
            'confidence_score': 'mean'
        }).round(2)
        category_summary.columns = ['Count', 'Avg Price', 'Avg Confidence']
        category_summary = category_summary.sort_values('Count', ascending=False)
        category_summary.to_excel(writer, sheet_name='Category Summary')

        # Sheet 4: Brand summary
        brand_summary = df.groupby('brand').agg({
            'product_id': 'count',
            'price': 'mean',
            'confidence_score': 'mean'
        }).round(2)
        brand_summary.columns = ['Count', 'Avg Price', 'Avg Confidence']
        brand_summary = brand_summary.sort_values('Count', ascending=False).head(30)
        brand_summary.to_excel(writer, sheet_name='Brand Summary')

        # Sheet 5: Products needing review
        review_df = df[df['confidence_score'] < 70][[
            'product_id', 'title', 'brand', 'product_type', 'confidence_score'
        ]].sort_values('confidence_score')
        review_df.to_excel(writer, sheet_name='Needs Review', index=False)

    print(f"Exported to {EXPORTS_DIR / 'product_classifications.xlsx'}")

def export_to_json(df, products):
    """Export results to JSON"""
    print("Exporting to JSON...")

    output = {
        'metadata': {
            'total_products': len(df),
            'unique_types': df['product_type'].nunique(),
            'unique_categories': df['category'].nunique(),
            'unique_brands': df['brand'].nunique(),
            'average_confidence': float(df['confidence_score'].mean()),
            'products_needing_review': int((df['confidence_score'] < 70).sum())
        },
        'products': df.to_dict('records'),
        'summary': {
            'by_type': df.groupby('product_type').size().to_dict(),
            'by_category': df.groupby('category').size().to_dict(),
            'by_brand': df.groupby('brand').size().to_dict()
        }
    }

    with open(EXPORTS_DIR / 'product_classifications.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Exported to {EXPORTS_DIR / 'product_classifications.json'}")

def generate_html_dashboard(df):
    """Generate interactive HTML dashboard"""
    print("Generating HTML dashboard...")

    # Calculate statistics
    stats = {
        'total_products': len(df),
        'unique_types': df['product_type'].nunique(),
        'unique_brands': df['brand'].nunique(),
        'avg_confidence': df['confidence_score'].mean(),
        'avg_price': df[df['price'] > 0]['price'].mean(),
        'products_with_reviews': (df['review_count'] > 0).sum(),
        'high_confidence': (df['confidence_score'] >= 85).sum(),
        'needs_review': (df['confidence_score'] < 70).sum(),
    }

    # Get sample products for each type
    type_samples = {}
    for ptype in df['product_type'].value_counts().head(10).index:
        samples = df[df['product_type'] == ptype].head(3)[['title', 'brand', 'price', 'confidence_score']].to_dict('records')
        type_samples[ptype] = samples

    # Create HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Type Identification Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}

        .stat-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}

        .stat-card .label {{
            color: #666;
            font-size: 0.95em;
            margin-top: 5px;
        }}

        .content {{
            padding: 40px;
        }}

        .section {{
            margin-bottom: 50px;
        }}

        .section h2 {{
            color: #667eea;
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}

        .visualization {{
            margin: 30px 0;
            text-align: center;
        }}

        .visualization img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}

        .visualization img:hover {{
            transform: scale(1.02);
        }}

        .visualization h3 {{
            margin-top: 15px;
            color: #333;
            font-size: 1.2em;
        }}

        .samples {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}

        .samples h3 {{
            color: #667eea;
            margin-bottom: 15px;
        }}

        .sample-item {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .sample-item strong {{
            color: #333;
        }}

        .sample-item span {{
            color: #666;
            font-size: 0.9em;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }}

        .badge-high {{
            background: #d4edda;
            color: #155724;
        }}

        .badge-medium {{
            background: #fff3cd;
            color: #856404;
        }}

        .badge-low {{
            background: #f8d7da;
            color: #721c24;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}

        footer {{
            background: #333;
            color: white;
            padding: 30px;
            text-align: center;
        }}

        footer p {{
            margin: 5px 0;
        }}

        .download-section {{
            background: #e8f4f8;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
            text-align: center;
        }}

        .download-section h3 {{
            color: #667eea;
            margin-bottom: 20px;
        }}

        .download-links {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .download-btn {{
            display: inline-block;
            padding: 15px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: background 0.3s, transform 0.2s;
        }}

        .download-btn:hover {{
            background: #5568d3;
            transform: translateY(-2px);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Product Type Identification Dashboard</h1>
            <p>Comprehensive Analysis of 425 Home Depot Products</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Products</h3>
                <div class="value">{stats['total_products']}</div>
                <div class="label">Products Analyzed</div>
            </div>

            <div class="stat-card">
                <h3>Product Types</h3>
                <div class="value">{stats['unique_types']}</div>
                <div class="label">Unique Types Identified</div>
            </div>

            <div class="stat-card">
                <h3>Brands</h3>
                <div class="value">{stats['unique_brands']}</div>
                <div class="label">Different Brands</div>
            </div>

            <div class="stat-card">
                <h3>Avg Confidence</h3>
                <div class="value">{stats['avg_confidence']:.1f}%</div>
                <div class="label">Data Quality Score</div>
            </div>

            <div class="stat-card">
                <h3>High Confidence</h3>
                <div class="value">{stats['high_confidence']}</div>
                <div class="label">Products (≥85% confidence)</div>
            </div>

            <div class="stat-card">
                <h3>Needs Review</h3>
                <div class="value">{stats['needs_review']}</div>
                <div class="label">Low Confidence Products</div>
            </div>

            <div class="stat-card">
                <h3>With Reviews</h3>
                <div class="value">{stats['products_with_reviews']}</div>
                <div class="label">Products Have Ratings</div>
            </div>

            <div class="stat-card">
                <h3>Avg Price</h3>
                <div class="value">${stats['avg_price']:.2f}</div>
                <div class="label">Average Product Price</div>
            </div>
        </div>

        <div class="content">
            <section class="section">
                <h2>📈 Product Type Distribution</h2>

                <div class="visualization">
                    <img src="../outputs/visualizations/category_distribution.png" alt="Category Distribution">
                    <h3>Product Distribution by Category</h3>
                </div>

                <div class="grid-2">
                    <div class="visualization">
                        <img src="../outputs/visualizations/product_type_distribution_top20.png" alt="Top 20 Product Types">
                        <h3>Top 20 Most Common Product Types</h3>
                    </div>

                    <div class="visualization">
                        <img src="../outputs/visualizations/product_type_long_tail.png" alt="Long Tail">
                        <h3>The Long Tail of Product Types</h3>
                    </div>
                </div>

                <div class="visualization">
                    <img src="../outputs/visualizations/product_type_by_confidence.png" alt="Types by Confidence">
                    <h3>Product Types Colored by Confidence Level</h3>
                </div>
            </section>

            <section class="section">
                <h2>✅ Data Quality Analysis</h2>

                <div class="grid-2">
                    <div class="visualization">
                        <img src="../outputs/visualizations/data_completeness.png" alt="Data Completeness">
                        <h3>Field Completeness Across Products</h3>
                    </div>

                    <div class="visualization">
                        <img src="../outputs/visualizations/confidence_distribution.png" alt="Confidence Distribution">
                        <h3>Confidence Score Distribution</h3>
                    </div>
                </div>

                <div class="visualization">
                    <img src="../outputs/visualizations/completeness_vs_confidence.png" alt="Completeness vs Confidence">
                    <h3>Data Completeness vs Confidence Correlation</h3>
                </div>
            </section>

            <section class="section">
                <h2>💰 Price Analysis</h2>

                <div class="visualization">
                    <img src="../outputs/visualizations/price_distribution.png" alt="Price Distribution">
                    <h3>Overall Price Distribution</h3>
                </div>

                <div class="grid-2">
                    <div class="visualization">
                        <img src="../outputs/visualizations/price_ranges_by_type.png" alt="Price Ranges">
                        <h3>Price Ranges by Product Type</h3>
                    </div>

                    <div class="visualization">
                        <img src="../outputs/visualizations/average_price_by_type.png" alt="Average Price">
                        <h3>Average Price by Type</h3>
                    </div>
                </div>
            </section>

            <section class="section">
                <h2>🏷️ Brand Analysis</h2>

                <div class="visualization">
                    <img src="../outputs/visualizations/top_brands.png" alt="Top Brands">
                    <h3>Top 20 Brands by Product Count</h3>
                </div>

                <div class="grid-2">
                    <div class="visualization">
                        <img src="../outputs/visualizations/brand_category_matrix.png" alt="Brand-Category Matrix">
                        <h3>Brand-Category Heat Map</h3>
                    </div>

                    <div class="visualization">
                        <img src="../outputs/visualizations/average_price_by_brand.png" alt="Price by Brand">
                        <h3>Average Price by Brand</h3>
                    </div>
                </div>
            </section>

            <section class="section">
                <h2>🎯 Confidence Analysis</h2>

                <div class="visualization">
                    <img src="../outputs/visualizations/confidence_histogram.png" alt="Confidence Histogram">
                    <h3>Confidence Score Histogram</h3>
                </div>

                <div class="grid-2">
                    <div class="visualization">
                        <img src="../outputs/visualizations/confidence_by_type.png" alt="Confidence by Type">
                        <h3>Average Confidence by Product Type</h3>
                    </div>

                    <div class="visualization">
                        <img src="../outputs/visualizations/products_needing_review.png" alt="Needs Review">
                        <h3>Products Requiring Manual Review</h3>
                    </div>
                </div>
            </section>

            <section class="section">
                <h2>📋 Sample Products by Type</h2>
                <p style="margin-bottom: 20px; color: #666;">Here are examples of products for the top product types:</p>
"""

    # Add sample products
    for ptype, samples in list(type_samples.items())[:5]:
        html += f"""
                <div class="samples">
                    <h3>{ptype} ({df[df['product_type'] == ptype].shape[0]} products)</h3>
"""
        for sample in samples:
            conf_class = 'badge-high' if sample['confidence_score'] >= 85 else 'badge-medium' if sample['confidence_score'] >= 70 else 'badge-low'
            html += f"""
                    <div class="sample-item">
                        <strong>{sample['title'][:100]}...</strong><br>
                        <span>Brand: {sample['brand']} | Price: ${sample['price']:.2f}</span>
                        <span class="badge {conf_class}">Confidence: {sample['confidence_score']:.0f}%</span>
                    </div>
"""
        html += """
                </div>
"""

    html += f"""
            </section>

            <div class="download-section">
                <h3>📥 Download Full Results</h3>
                <div class="download-links">
                    <a href="../exports/product_classifications.csv" class="download-btn">📊 Download CSV</a>
                    <a href="../exports/product_classifications.xlsx" class="download-btn">📊 Download Excel</a>
                    <a href="../exports/product_classifications.json" class="download-btn">📊 Download JSON</a>
                    <a href="executive_summary.md" class="download-btn">📄 View Summary</a>
                </div>
            </div>
        </div>

        <footer>
            <p><strong>Product Type Identification Dashboard</strong></p>
            <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>425 Home Depot Products | {stats['unique_types']} Product Types Identified</p>
        </footer>
    </div>
</body>
</html>
"""

    # Save HTML
    with open(REPORTS_DIR / 'visualization_dashboard.html', 'w') as f:
        f.write(html)

    print(f"Dashboard saved to {REPORTS_DIR / 'visualization_dashboard.html'}")

def main():
    """Main execution function"""
    print("="*60)
    print("PRODUCT VISUALIZATION DASHBOARD GENERATOR")
    print("="*60)
    print()

    # Load data
    products, patterns = load_data()

    # Analyze products
    df = analyze_products(products)

    # Create all visualizations
    print("\nGenerating visualizations...")
    create_category_overview(df)
    create_product_type_distribution(df)
    create_data_quality_visualizations(df)
    create_price_analysis(df)
    create_brand_analysis(df)
    create_confidence_analysis(df)

    # Export data
    print("\nExporting data...")
    export_to_csv(df)
    export_to_excel(df, products)
    export_to_json(df, products)

    # Generate dashboard
    print("\nGenerating dashboard...")
    generate_html_dashboard(df)

    print()
    print("="*60)
    print("✅ ALL VISUALIZATIONS AND EXPORTS COMPLETE!")
    print("="*60)
    print()
    print("📊 Generated Files:")
    print(f"   - Dashboard: {REPORTS_DIR / 'visualization_dashboard.html'}")
    print(f"   - Visualizations: {OUTPUT_DIR}/ (13 charts)")
    print(f"   - CSV Export: {EXPORTS_DIR / 'product_classifications.csv'}")
    print(f"   - Excel Export: {EXPORTS_DIR / 'product_classifications.xlsx'}")
    print(f"   - JSON Export: {EXPORTS_DIR / 'product_classifications.json'}")
    print()
    print("📈 Key Statistics:")
    print(f"   - Total Products: {len(df)}")
    print(f"   - Unique Product Types: {df['product_type'].nunique()}")
    print(f"   - Average Confidence: {df['confidence_score'].mean():.1f}%")
    print(f"   - Products Needing Review: {(df['confidence_score'] < 70).sum()}")
    print()

if __name__ == "__main__":
    main()
