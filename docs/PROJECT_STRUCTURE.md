# Product Type Identifier - Project Structure Overview

## Quick Summary (30-second version)

**What is this?** A machine learning project to automatically classify ~425 Home Depot products into product types with 98%+ accuracy.

**What data do you have?**
- 425 real product records (JSON format)
- 373 taxonomy categories (reference)
- Product details: titles, descriptions, prices, ratings, images, specifications

**What's built?** Foundation files and 4 commits worth of analysis scripts (need to pull from origin/main)

**What's missing?** Beginner-friendly guides, examples, and setup instructions

---

## File Structure (Current Working Directory)

```
product_type_identifier_repo/
│
├── README.md                                    [Project overview & roadmap]
├── requirements_product_identifier.txt          [Python dependencies]
├── WORKSPACE_ANALYSIS.md                        [This detailed analysis]
├── PROJECT_STRUCTURE.md                         [This file]
│
├── .gitignore                                   [Standard Python ignores]
├── .vscode/
│   └── settings.json                            [VSCode Python path config]
│
├── data/
│   ├── scraped_data_output.json                 [425 products - 1.2 MB]
│   └── taxonomy_paths.txt                       [373 categories]
│
├── venv/                                        [Python virtual environment]
└── .git/                                        [Git repository & history]
```

---

## What Files SHOULD Exist (on origin/main branch)

These files are in git history but not in your working directory:

```
MISSING - Run: git pull origin main

notebooks/
└── baseline_product_type.ipynb                  [ML baseline analysis notebook]

scripts/
├── data_audit.py                                [Data quality & completeness check]
├── data_profile.py                              [Data profiling with CLI]
├── pattern_discovery.py                         [Find product clusters]
└── validation_methodology.py                    [Confidence scoring system]
```

---

## Data Breakdown

### Product Records (425 items)

**Each product has 14 fields:**

1. **title** - Product name
   - Example: "Feit Electric 60-Watt Equivalent B10 E26 Base Dim White Filament Clear Glass Chandelier LED Light Bulb..."

2. **description** - Detailed marketing copy
   - Usually 200-500 words with features, specs, use cases

3. **brand** - Manufacturer name
   - Most common: Hampton Bay (33), Commercial Electric (30), Home Decorators Collection (23)

4. **model** - Product model number
   - Example: "ETC60927CAWFILHDRP/3"

5. **price** - Current retail price in USD
   - Range: $0.00 to $1,510.11
   - Average: $86.90

6. **sale_price** - Discounted price (if applicable)

7. **images** - Array of product photo URLs
   - 10-12 images per product

8. **rating** - Star rating (0-5)
   - Example: 4.5 stars

9. **reviews** - Number of customer reviews
   - Example: 52 reviews

10. **sku** - Stock keeping unit (internal identifier)

11. **internet_sku** - Online-specific identifier

12. **sku_description** - Text description of SKU

13. **structured_specifications** - Rich structured data
    ```
    {
      "wattage": {"value": 5.5, "unit": "W"},
      "lumens": {"value": 500, "unit": "lm"},
      "color_temp": {"value": 2700, "unit": "K"},
      "lifespan": {"value": 15000, "unit": "hours"},
      "cri": {"value": 90, "unit": "CRI"},
      ... more fields
    }
    ```

14. **structured_details** - Additional specs
    ```
    {
      "Color": "No Color",
      "Product ID": "327568545",
      "Height": "3.85 in",
      ... more fields
    }
    ```

### Taxonomy Reference (373 categories)

**Format:** Hierarchical paths using "//" delimiter

**Structure:** Department // Category // Subcategory // Type

**Examples:**
```
Home & Kitchen//Bath//Bath Accessories//Mirrors
Home & Kitchen//Bath//Bath Accessories//Plungers
Home & Kitchen//Bath//Bath Storage//Bath Caddies
Home & Kitchen//Furniture//Outdoor Furniture//Outdoor Chairs, Benches & Swings
Home & Kitchen//Home Decor//Holiday & Seasonal Decor//Christmas Lights
Home & Kitchen//Household Supplies & Cleaning//General Cleaning Supplies//Cleaning Products
```

**Key Philosophy:** DON'T force-fit products into this taxonomy initially. Let product types emerge organically from the data first.

---

## Development Stack

### Core Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| pandas | Data manipulation & analysis | >=2.2 |
| scikit-learn | Machine learning models | >=1.5 |
| sentence-transformers | Text embeddings | >=3.0 |
| spacy | NLP (noun chunks, entity extraction) | latest |
| rapidfuzz | Fuzzy string matching | latest |
| numpy | Numerical computing | latest |
| scipy | Scientific computing | latest |

### Environment

- **Python:** 3.11 or 3.12
- **Virtual Environment:** Located in `./venv/`
- **Package Manager:** pip (venv/bin/pip)
- **Editor:** VSCode (pre-configured)

### Optional Additions Needed

```
jupyter                     # Run .ipynb notebooks
notebook                    # Jupyter notebook interface
black                      # Code formatting
isort                      # Import sorting
pytest                     # Testing
mlflow                     # Experiment tracking
weights-and-biases         # Experiment tracking (alternative)
```

---

## Development Workflow

### Phase 1: Data Understanding (Do first!)
```
1. Load data/scraped_data_output.json
2. Explore structure, schema, quality
3. Identify data cleaning needs
4. Understand product diversity
```

**Tools:** data_audit.py, data_profile.py, Jupyter notebooks

### Phase 2: Feature Engineering
```
1. Extract text features (embeddings, keywords, n-grams)
2. Parse structured_specifications into features
3. Create brand-category mappings
4. Store in DuckDB or Parquet for reproducibility
```

### Phase 3: Organic Label Discovery
```
1. Don't use taxonomy yet - discover types from data
2. Use heuristics: titles, brands, specs, descriptions
3. Create product clusters
4. Assign confidence scores
```

**Tools:** pattern_discovery.py

### Phase 4: Model Training
```
1. Use discovered types as training labels
2. Train classifiers (SentenceTransformers or sklearn)
3. Use cross-validation (80/20 or stratified split)
4. Track experiments in MLflow/W&B
```

### Phase 5: Evaluation
```
1. Achieve >=98% macro accuracy
2. Achieve >=0.95 recall per category
3. Hold out 15% test set
4. Create spot-check report of errors
```

### Phase 6: Deployment
```
1. Package as FastAPI/Flask microservice
2. Add taxonomy validation logic
3. Add confidence thresholds
4. Deploy with monitoring
```

---

## Git Status

### Current Situation

```
Local: master branch
  - 4 commits behind origin/main
  - Has modified files not committed
  - Missing scripts and notebooks

Remote: origin/main
  - 4 commits ahead (f95fb6d, 07b6701, fb312c6, 9f6b7c8)
  - Contains all analytical scripts
  - Contains notebooks with analysis
```

### How to Sync

```bash
# See what's different
git log --oneline master..origin/main

# Pull the work from origin
git pull origin main

# This will bring in:
# - scripts/ directory with 4 Python analysis tools
# - notebooks/ directory with baseline ML notebook
# - Updated documentation
```

### Modified Files to Handle

Currently modified but not committed:
- `.gitignore`
- `README.md`
- `data/scraped_data_output.json`
- `data/taxonomy_paths.txt`
- `requirements_product_identifier.txt`

**Decision:** Either commit these changes or discard them before pulling.

---

## Key Statistics

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Products** | 425 | Real Home Depot listings |
| **Data Completeness** | 97.6% | Core fields populated |
| **Taxonomy Categories** | 373 | 4-level hierarchy |
| **Top Brand** | Hampton Bay | 33 products |
| **Avg Product Price** | $86.90 | Range: $0 - $1,510 |
| **Images Per Product** | 10-12 | Product photography |
| **Python Version** | 3.11+ | 3.12 installed locally |

---

## For Someone Who Doesn't Code Yet

**What you need to understand:**

1. **This is a classification project**
   - You give it a product (title, description, specs)
   - The machine learns to predict which category it belongs to
   - Goal: 98%+ accuracy

2. **You have raw ingredients:**
   - 425 sample products with known information
   - A list of 373 possible categories
   - Python code that will analyze this

3. **The workflow is:**
   ```
   Raw Products → Learn Patterns → Build Model → Predict Categories
   ```

4. **You're missing:**
   - Step-by-step instructions on how to start
   - Examples showing what each tool does
   - Explanations of what the data fields mean
   - Confirmation steps to check everything works

5. **What would help:**
   - A "Getting Started" guide (5-10 minutes)
   - Sample scripts showing how to load and explore data
   - Video walkthrough or detailed documentation
   - A Jupyter notebook showing analysis step-by-step

---

## Common Questions

### Q: Where's the magic ML code?
A: It's on the origin/main branch. Run `git pull origin main` to get it. The analysis is in:
- `scripts/data_audit.py` - Analyzes data quality
- `scripts/data_profile.py` - Interactive data exploration
- `scripts/pattern_discovery.py` - Finds product patterns/clusters
- `notebooks/baseline_product_type.ipynb` - Full ML example

### Q: What do I do first?
A: 
1. Activate virtual environment: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements_product_identifier.txt`
3. Run: `python scripts/data_audit.py` (once you pull from origin/main)

### Q: Can I run Jupyter notebooks?
A: Yes, but you need to:
1. Add jupyter: `pip install jupyter notebook`
2. Run: `jupyter notebook`
3. Open the .ipynb files from the browser

### Q: What if I'm not a programmer?
A: You can still use this! The Jupyter notebooks are visual and step-by-step. Just:
1. Install Jupyter
2. Run Jupyter
3. Open notebooks
4. Click "Run Cell" to execute code blocks
5. Read the output and explanations

### Q: Is the data private?
A: It's scraped public data from Home Depot, but treat carefully:
- Don't upload to public repos without permission
- Don't share with unauthorized people
- Keep in .gitignore (currently it is)

---

## Next Steps

### Immediate (Today)
- [ ] Read WORKSPACE_ANALYSIS.md for full details
- [ ] Understand what's on the origin/main branch
- [ ] Decide whether to pull origin/main or create beginner guides first

### Short Term (This Week)
- [ ] Sync with origin/main
- [ ] Run the data_audit.py script
- [ ] Explore the Jupyter notebook
- [ ] Understand the product data

### Medium Term (This Month)
- [ ] Feature engineering (extract patterns)
- [ ] Train baseline models
- [ ] Evaluate accuracy
- [ ] Document findings

### Longer Term (Ongoing)
- [ ] Improve model performance
- [ ] Package as microservice
- [ ] Deploy to production
- [ ] Monitor performance

---

## File Locations

**Absolute paths in this project:**

```
/home/cadegallen/Projects/product_type_identifier_repo/
├── README.md
├── WORKSPACE_ANALYSIS.md                        [Detailed analysis - read this!]
├── PROJECT_STRUCTURE.md                         [This file]
├── requirements_product_identifier.txt
├── data/
│   ├── scraped_data_output.json                 [425 products]
│   └── taxonomy_paths.txt                       [373 categories]
├── venv/bin/python                              [Python executable]
└── venv/bin/pip                                 [Package installer]
```

---

## Resources

- **Main README:** `/home/cadegallen/Projects/product_type_identifier_repo/README.md`
- **This Analysis:** `/home/cadegallen/Projects/product_type_identifier_repo/WORKSPACE_ANALYSIS.md`
- **Data Files:** `/home/cadegallen/Projects/product_type_identifier_repo/data/`
- **Git History:** Run `git log --oneline --all`
- **Remote Info:** `git remote -v`

