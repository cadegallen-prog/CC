# 🚀 8 Copy-Paste Prompts with Auto-Next-Prompt Generation

Each prompt now includes a command at the end that automatically generates your NEXT prompt!

---

## 🎯 HIGH PRIORITY (Do These First)

### **Prompt 1: Run Classifier on All 425 Products** ⭐ CRITICAL

```
I have a product classifier at 93.2% accuracy. I need you to run it on all 425 products in my dataset and generate the final classification results.

Context:
- Classifier script: /home/user/CC/scripts/classify_products.py
- Product data: /home/user/CC/data/scraped_data_output.json (425 products)
- Current accuracy: 93.2% on ground truth samples
- Only 44 products have been validated so far

Your task:
1. Run the ProductClassifier on ALL 425 products (not just the 44 ground truth samples)

2. Create a script: /home/user/CC/scripts/run_full_classification.py that:
   - Loads all 425 products
   - Classifies each one using ProductClassifier
   - Saves results to /home/user/CC/outputs/final_product_types.json

3. The output JSON should include for each product:
   ```json
   {
     "index": 0,
     "title": "Product title here",
     "product_type": "LED Light Bulb",
     "confidence": 85.5,
     "confidence_level": "High",
     "reasons": ["Title contains 'light bulb'", "Found 3 supporting keywords"],
     "alternate_types": [
       {"type": "Pendant Light", "score": 42.0},
       {"type": "Wall Sconce", "score": 28.5}
     ]
   }
   ```

4. Generate summary statistics and save to /home/user/CC/outputs/classification_summary.json:
   - Total products: 425
   - Products classified by type (count per type)
   - Products by confidence level (High/Medium/Low/Very Low/Unknown)
   - Average confidence score
   - Top 10 most common product types
   - Products that couldn't be classified (Unknown)

5. Create a CSV export: /home/user/CC/outputs/classifications.csv with columns:
   - Index, Title, Product Type, Confidence, Confidence Level, Status

6. Print summary to console:
   - Total classified: X/425
   - Average confidence: X%
   - Top 5 product types with counts
   - Products needing review (confidence < 30)

7. Commit your changes with message: "Run classifier on all 425 products"

8. **IMPORTANT - Mark task complete and generate next prompt:**
   Run this Python command at the very end:
   ```python
   python -c "
   import sys, json
   sys.path.insert(0, '/home/user/CC/scripts')
   from workflow_engine import WorkflowEngine

   # Load the results you just generated
   with open('/home/user/CC/outputs/classification_summary.json', 'r') as f:
       summary = json.load(f)

   # Mark task complete with your results
   w = WorkflowEngine()
   w.mark_task_complete('classify_all_products', {
       'classified_count': summary.get('total_classified', 0),
       'unknown_count': summary.get('unknown_count', 0),
       'avg_confidence': summary.get('avg_confidence', 0)
   })
   "
   ```

This will:
- ✅ Mark the task as complete
- 📝 Log your results
- 🎯 Generate your NEXT prompt automatically
- 💾 Save it to: /home/user/CC/workflow/NEXT_PROMPT.txt

Expected outputs:
- final_product_types.json (all 425 products classified)
- classification_summary.json (statistics)
- classifications.csv (spreadsheet format)
- NEXT_PROMPT.txt (what to do next!)
```

---

### **Prompt 2: Start Stage 2 - Taxonomy Mapping** ⭐ CRITICAL

```
My product classifier identifies products into 77 specific types (like "LED Light Bulb", "Circuit Breaker", etc.) with 93.2% accuracy. Now I need to map these 77 types to Facebook's standardized 373-category taxonomy.

Context:
- I have 77 product types in: /home/user/CC/scripts/classify_products.py
- Facebook's taxonomy: /home/user/CC/data/taxonomy_paths.txt (373 categories)
- Strategy document: /home/user/CC/docs/mapping_strategy.md
- Current status: Stage 1 (identification) complete at 93.2%
- Next stage: Stage 2 (taxonomy mapping)

Your task:
1. Read the 77 product types from classify_products.py
   - They are the keys in the self.patterns dictionary
   - Extract all pattern names into a list

2. Read Facebook's 373 taxonomy categories from taxonomy_paths.txt
   - These are hierarchical paths like "Home & Garden > Lighting > Light Bulbs"

3. Create a mapping file: /home/user/CC/data/type_to_taxonomy_mapping.json

   For EACH of the 77 product types, find 1-3 best matching Facebook categories using:
   - Exact/semantic matching (e.g., "LED Light Bulb" → "Lighting > Light Bulbs")
   - Keyword overlap (shared words between type and category)
   - Parent category matching (e.g., "Wall Sconce" → "Lighting > Lamps")
   - Hierarchical logic (specific → general)

4. Format the JSON as:
   ```json
   {
     "LED Light Bulb": {
       "primary_match": "Home & Garden > Lighting > Light Bulbs",
       "confidence": "high",
       "match_reason": "Exact semantic match - both describe light bulbs",
       "alternate_matches": [
         "Home & Garden > Lighting > Lamps",
         "Electronics > Components > LEDs & Light Components"
       ],
       "keywords_matched": ["light", "bulb", "led"],
       "hierarchy_score": 95
     },
     "Circuit Breaker": {
       "primary_match": "Hardware > Electrical Equipment",
       "confidence": "medium",
       "match_reason": "Keyword match on 'electrical' - no exact category exists",
       "alternate_matches": [],
       "keywords_matched": ["electrical"],
       "hierarchy_score": 60,
       "notes": "No perfect FB category for circuit breakers - this is best approximation"
     }
   }
   ```

5. Generate a mapping quality report: /home/user/CC/reports/taxonomy_mapping_report.md

   Include:
   - Summary: X/77 types mapped successfully
   - High confidence mappings: X (>80 score)
   - Medium confidence: X (50-80 score)
   - Low confidence: X (<50 score) - need manual review
   - Unmapped types: X (if any)
   - Top 10 most confident mappings
   - Top 10 least confident (ambiguous) mappings
   - Recommendations for improving mappings

6. Create reverse index: /home/user/CC/data/taxonomy_to_types_index.json
   - Maps each FB category → list of my product types
   - Useful for seeing which FB categories cover multiple types

   Format:
   ```json
   {
     "Home & Garden > Lighting > Light Bulbs": [
       "LED Light Bulb",
       "CFL Bulb",
       "Halogen Bulb"
     ],
     "Home & Garden > Lighting > Lamps": [
       "Table Lamp",
       "Floor Lamp",
       "Pendant Light"
     ]
   }
   ```

7. Validation checks:
   - Ensure all 77 types have at least one mapping
   - Flag any FB categories that don't exist in taxonomy_paths.txt
   - Calculate overall mapping quality score (0-100)
   - Identify types that might need multiple FB categories

8. Generate statistics:
   - Average hierarchy score: X
   - Most common FB parent categories
   - Coverage: X% of my types have high-confidence mappings

9. Commit your changes with message: "Add Stage 2 taxonomy mappings for 77 product types"

10. **IMPORTANT - Mark task complete and generate next prompt:**
    ```python
    python -c "
    import sys, json
    sys.path.insert(0, '/home/user/CC/scripts')
    from workflow_engine import WorkflowEngine

    with open('/home/user/CC/data/type_to_taxonomy_mapping.json', 'r') as f:
        mappings = json.load(f)

    high_conf = sum(1 for m in mappings.values() if m.get('confidence') == 'high')
    needs_review = sum(1 for m in mappings.values() if m.get('confidence') == 'low')

    w = WorkflowEngine()
    w.mark_task_complete('taxonomy_mapping', {
        'mappings_created': len(mappings),
        'high_confidence': high_conf,
        'needs_review': needs_review
    })
    "
    ```

Expected outputs:
- type_to_taxonomy_mapping.json (77 mappings)
- taxonomy_mapping_report.md (quality analysis)
- taxonomy_to_types_index.json (reverse lookup)
- NEXT_PROMPT.txt (generated automatically!)
```

---

## ⚙️ MEDIUM PRIORITY (High Value)

### **Prompt 3: Expand Ground Truth Dataset**

```
My product classifier has 44 ground truth samples for validation. I need to expand this to 100+ samples to better validate the classifier.

Context:
- Current ground truth: /home/user/CC/data/ground_truth.json (44 samples)
- Full product dataset: /home/user/CC/data/scraped_data_output.json (425 products)
- Classification results: /home/user/CC/outputs/final_product_types.json
- Current accuracy: 93.2% on 44 samples
- Goal: 100+ samples for more robust validation

Your task:
1. Read the existing ground_truth.json to understand the format
   - Note the structure: sample_id, index, title, true_product_type, difficulty

2. Analyze which products to add for maximum validation value:
   - Products with confidence 20-50 (uncertain classifications)
   - Product types underrepresented in current ground truth
   - Products from diverse brands and categories
   - Edge cases (unusual products, combo products, etc.)

3. Select 60 ADDITIONAL products from scraped_data_output.json
   - Prioritize diversity and coverage
   - Include some easy, medium, and hard examples
   - Ensure all 77 product types represented (if possible)

4. For each of the 60 products, manually determine the correct product type by:
   - Reading the full title
   - Reading the full description
   - Checking structured_specifications
   - Using your best judgment as a human would

5. Add these 60 products to ground_truth.json following the exact format:
   ```json
   {
     "sample_id": 45,
     "index": 234,
     "title": "Product title here",
     "true_product_type": "led_light_bulb",
     "difficulty": "medium",
     "notes": "Clear LED bulb based on title and specs"
   }
   ```

6. Classify difficulty:
   - "easy": Product type is obvious from title alone
   - "medium": Need to read description or specs
   - "hard": Ambiguous, unusual, or combo product

7. Re-run validation with expanded dataset:
   ```bash
   python scripts/validate_system.py > outputs/validation_100plus.txt
   ```

8. Generate comparison report: /home/user/CC/reports/expanded_validation_report.md

   Compare metrics:
   - 44 samples: 93.2% accuracy (41/44 correct)
   - 100+ samples: X% accuracy (Y/Z correct)
   - Accuracy by difficulty (easy/medium/hard)
   - Accuracy by product type
   - New error patterns discovered
   - Recommendations based on larger sample

9. Identify any new problem areas:
   - Product types that perform poorly
   - Patterns that need improvement
   - Misclassification trends

10. Commit changes: "Expand ground truth from 44 to 100+ samples"

11. **Mark task complete:**
    ```python
    python -c "
    import sys, json
    sys.path.insert(0, '/home/user/CC/scripts')
    from workflow_engine import WorkflowEngine

    with open('/home/user/CC/data/ground_truth.json', 'r') as f:
        gt = json.load(f)

    total_samples = len(gt['samples'])

    # Parse validation output
    import re
    with open('/home/user/CC/outputs/validation_100plus.txt', 'r') as f:
        content = f.read()
        match = re.search(r'Overall Accuracy: (\d+)/(\d+) = ([\d.]+)%', content)
        if match:
            correct = int(match.group(1))
            total = int(match.group(2))
            accuracy = float(match.group(3))
        else:
            correct, total, accuracy = 0, 0, 0

    w = WorkflowEngine()
    w.mark_task_complete('expand_ground_truth', {
        'total_samples': total_samples,
        'new_samples_added': total_samples - 44,
        'new_accuracy': accuracy,
        'correct': correct,
        'total': total
    })
    "
    ```

Expected outputs:
- Updated ground_truth.json (100+ samples)
- validation_100plus.txt (new validation results)
- expanded_validation_report.md (comparison analysis)
- NEXT_PROMPT.txt (auto-generated!)
```

---

### **Prompt 4: Create Interactive Visualization Dashboard**

```
I need an HTML dashboard to visualize my product classification results. The dashboard should be easy to understand for non-technical users.

Context:
- Classification data: /home/user/CC/outputs/final_product_types.json
- Product data: /home/user/CC/data/scraped_data_output.json
- Accuracy: 93.2%
- 77 product types, 425 products total

Your task:
1. Create an interactive HTML dashboard: /home/user/CC/visualizations/classification_dashboard.html

2. Include these sections:

   **A. OVERVIEW PANEL** (Top of page)
   - Total products: 425
   - Total product types: 77
   - Average confidence: X%
   - Accuracy: 93.2%
   - Last updated: [timestamp]

   **B. PRODUCT TYPE DISTRIBUTION** (Bar Chart)
   - Interactive bar chart using Chart.js
   - Show count for each product type
   - Display top 20 types by default
   - Click to filter table below
   - Hover to see count and percentage

   **C. CONFIDENCE DISTRIBUTION** (Pie Chart)
   - High (70-100): X products
   - Medium (50-69): X products
   - Low (30-49): X products
   - Very Low (20-29): X products
   - Unknown (<20): X products
   - Click slice to filter table

   **D. CLASSIFICATION TABLE** (Searchable, Sortable)
   - All 425 products in a data table
   - Columns: Index, Title (truncated to 60 chars), Product Type, Confidence, Status
   - Sortable by any column
   - Searchable by title keywords
   - Filters:
     - By product type (dropdown)
     - By confidence level (dropdown)
     - By status (Classified / Unknown)
   - Pagination (25 products per page)
   - Export to CSV button

   **E. LOW CONFIDENCE ALERTS** (Warning Box)
   - List products with confidence < 30
   - Highlight in red
   - Show count: "X products need review"
   - Link to filter table to show only these

   **F. PRODUCT TYPE DETAILS** (Expandable Sections)
   - Click any product type name
   - Show all products in that category
   - Display pattern keywords used for classification
   - Show confidence distribution for that type
   - List alternate types that scored high

3. Styling requirements:
   - Professional, clean design
   - Use Bootstrap 5 for layout (CDN)
   - Use Chart.js for charts (CDN)
   - Responsive design (works on mobile, tablet, desktop)
   - Dark mode toggle switch
   - Color scheme:
     - High confidence: Green
     - Medium: Yellow/Orange
     - Low: Orange/Red
     - Unknown: Gray

4. Technical requirements:
   - Self-contained single HTML file
   - All CSS in <style> tag
   - All JavaScript in <script> tag
   - Load external libraries from CDN only:
     - Bootstrap 5 CSS/JS
     - Chart.js
     - (optional) DataTables for table features
   - Fast loading (< 2 seconds)
   - Works offline after first load
   - No server needed - opens directly in browser

5. Interactive features:
   - Click chart segments to filter table
   - Search box with instant filtering
   - Sort table by clicking column headers
   - Export filtered results to CSV
   - Dark mode persists to localStorage
   - Expand/collapse sections
   - Tooltips on hover for more info

6. Create usage guide: /home/user/CC/visualizations/DASHBOARD_GUIDE.md
   - How to open the dashboard
   - How to use each feature
   - How to filter and search
   - How to export data
   - Troubleshooting tips

7. Test the dashboard:
   - Open it in a browser
   - Verify all charts load
   - Test filtering and searching
   - Test dark mode toggle
   - Test CSV export
   - Check mobile responsiveness

8. Commit: "Add interactive classification dashboard"

9. **Mark task complete:**
   ```python
   python -c "
   import sys, os
   sys.path.insert(0, '/home/user/CC/scripts')
   from workflow_engine import WorkflowEngine

   dashboard_path = '/home/user/CC/visualizations/classification_dashboard.html'
   dashboard_exists = os.path.exists(dashboard_path)
   dashboard_size = os.path.getsize(dashboard_path) if dashboard_exists else 0

   w = WorkflowEngine()
   w.mark_task_complete('create_dashboard', {
       'dashboard_created': dashboard_exists,
       'dashboard_size_kb': dashboard_size / 1024,
       'guide_created': os.path.exists('/home/user/CC/visualizations/DASHBOARD_GUIDE.md')
   })
   "
   ```

Expected outputs:
- classification_dashboard.html (interactive dashboard)
- DASHBOARD_GUIDE.md (usage instructions)
- NEXT_PROMPT.txt (auto-generated!)

After completing, open the dashboard in your browser:
```bash
# Linux/Mac
xdg-open visualizations/classification_dashboard.html

# Or just double-click the HTML file
```
```

---

## 🔧 OPTIMIZATION (Polish & Improve)

### **Prompt 5: Fix the Remaining 3 Errors (93.2% → 95%+)**

```
My classifier is at 93.2% accuracy (41/44 correct). I want to fix the remaining 3 errors to push accuracy to 95%+.

Context:
- Current accuracy: 93.2% (3 errors remaining)
- Classifier: /home/user/CC/scripts/classify_products.py
- Validation: /home/user/CC/scripts/validate_system.py
- Ground truth: /home/user/CC/data/ground_truth.json

The 3 remaining errors are:
1. "TrimMaster Satin Nickel 5.5mm x 74 in. Aluminum Stair Nosing Floor Transition St"
   - Expected: Fastener
   - Got: Unknown (10 pts confidence)
   - Issue: Stair nosing trim not recognized

2. "Commercial Electric Bookshelf Speaker Wall Mounts, No Stud Required (Set of 2) M"
   - Expected: Speaker Mount
   - Got: Unknown (8 pts confidence)
   - Issue: Not scoring high enough

3. "Home Decorators Collection Orbit 1-Light Black Mini Pendant with Black Metal Str"
   - Expected: Pendant Light
   - Got: Unknown (6 pts confidence)
   - Issue: Very low score despite being a pendant

Your task:
1. For each error, read the full product details:
   ```python
   import json
   with open('/home/user/CC/data/scraped_data_output.json', 'r') as f:
       products = json.load(f)

   # Find products by searching title
   for i, p in enumerate(products):
       if 'TrimMaster' in p['title']:
           print(f"Index {i}:", json.dumps(p, indent=2))
   ```

2. Analyze WHY the classifier is missing these:
   - Check what keywords are in title/description
   - See what pattern SHOULD match
   - Identify what's preventing the match

3. Fix the patterns in classify_products.py:

   **For Error #1 (Stair Nosing):**
   - Option A: Add "Floor Transition" or "Stair Nosing" pattern
   - Option B: Strengthen "Fastener" pattern with "stair nosing", "transition strip", "trim"
   - Option C: Lower threshold even more (currently 20)

   **For Error #2 (Speaker Mount):**
   - Strengthen "Speaker Mount" keywords
   - Add: "bookshelf", "no stud", "stud required", "speaker display"
   - Increase weak keyword score if multiple match

   **For Error #3 (Mini Pendant):**
   - "Pendant Light" should catch "mini pendant"
   - Check if "mini pendant" is already a strong keyword
   - If not, add it
   - Add "orbit" as a weak keyword (brand/style)
   - Add "1-light" as weak keyword

4. Update validate_system.py ground truth mappings if you add new patterns
   - If you add "Floor Transition" pattern, map it in the validation

5. Re-run validation after each fix:
   ```bash
   python scripts/validate_system.py | grep "Overall Accuracy"
   ```

6. Iteratively fix until accuracy reaches 95%+ (42 or 43 out of 44 correct)

7. Generate improvement report: /home/user/CC/reports/accuracy_improvement_report.md

   Include:
   - Starting accuracy: 93.2%
   - Final accuracy: X%
   - Changes made to patterns
   - Before/after for each error
   - New patterns added (if any)
   - Validation output comparison

8. Run final full validation:
   ```bash
   python scripts/validate_system.py > outputs/validation_95percent.txt
   ```

9. Commit: "Fix remaining errors to achieve 95%+ accuracy"

10. **Mark task complete:**
    ```python
    python -c "
    import sys, re
    sys.path.insert(0, '/home/user/CC/scripts')
    from workflow_engine import WorkflowEngine

    with open('/home/user/CC/outputs/validation_95percent.txt', 'r') as f:
        content = f.read()
        match = re.search(r'Overall Accuracy: (\d+)/(\d+) = ([\d.]+)%', content)
        if match:
            correct = int(match.group(1))
            total = int(match.group(2))
            accuracy = float(match.group(3))
        else:
            correct, total, accuracy = 0, 0, 0

    w = WorkflowEngine()
    w.mark_task_complete('fix_remaining_errors', {
        'accuracy_achieved': accuracy,
        'correct': correct,
        'total': total,
        'errors_remaining': total - correct,
        'target_reached': accuracy >= 95.0
    })
    "
    ```

Expected outputs:
- Updated classify_products.py (fixed patterns)
- validation_95percent.txt (validation results)
- accuracy_improvement_report.md (analysis)
- NEXT_PROMPT.txt (auto-generated!)
```

---

### **Prompt 6: Quality Audit - Find Edge Cases**

```
I need a comprehensive quality audit of my product classifications to find edge cases, anomalies, and potential improvements.

Context:
- 425 products classified with 93.2% accuracy
- Classifications in: /home/user/CC/outputs/final_product_types.json
- Product data: /home/user/CC/data/scraped_data_output.json

Your task:
Analyze ALL 425 product classifications and find:

1. **CONFIDENCE RED FLAGS**
   - Products with confidence < 20 (shouldn't be classified at all)
   - Products with confidence 20-30 (very uncertain, need manual review)
   - Products where top 2 alternate types have scores within 10 points (ambiguous)
   - Example: Primary type scores 55, alternate scores 52 → very uncertain

2. **CLASSIFICATION ANOMALIES**
   - Products where title strongly contradicts classification
     - Example: Title says "LED Bulb" but classified as "Pendant Light"
   - Products with unusual brand/type combinations
     - Example: "DeWalt" classified as "Faucet" (DeWalt makes tools!)
   - Products where description contradicts classification
   - Price outliers for the product type
     - Example: "LED Bulb" costs $500 → probably wrong type

3. **MISSING PATTERNS**
   - Groups of 5+ similar products all classified as "Unknown"
   - These likely need a new product type pattern
   - Example: 10 products with "door hinge" in title, all Unknown
   - Identify the common keywords/patterns

4. **KEYWORD ISSUES**
   - Products classified with very generic reasoning
     - Example: Classified as "Wire" only because description mentions "wire"
   - Products where negative keywords might prevent false matches
   - Patterns that might be too broad or too narrow

5. **DATA QUALITY PROBLEMS**
   - Products with missing/incomplete titles
   - Products with missing/incomplete descriptions
   - Products with corrupted or weird text (encoding issues)
   - Duplicate products (same title, different index)
   - Outlier prices (< $1 or > $10,000 for Home Depot products)
   - Missing structured_specifications

Generate these outputs:

**A. Audit Report:** /home/user/CC/reports/quality_audit_report.md

Structure:
```markdown
# Product Classification Quality Audit

Date: [timestamp]
Total Products Audited: 425

## Executive Summary
- Total issues found: X
- High priority issues: X
- Medium priority: X
- Low priority: X

## Top 10 Findings
1. [Most critical issue]
2. [Second most critical]
...

## Detailed Findings

### 1. Confidence Red Flags (X products)
- Products < 20 confidence: X
  - [List examples]
- Products 20-30 confidence: X
  - [List examples]
- Ambiguous classifications: X
  - [List examples with scores]

### 2. Classification Anomalies (X products)
- Title/type contradictions: X
  - [List examples]
- Brand/type mismatches: X
  - [List examples]
- Price outliers: X
  - [List examples]

### 3. Missing Patterns (X groups)
- Group 1: [Pattern name] - X products
  - Common keywords: [list]
  - Example titles: [3 examples]
- Group 2: ...

### 4. Keyword Issues (X products)
- Overly generic classifications: X
  - [Examples]
- Patterns needing negative keywords: X
  - [Examples]

### 5. Data Quality (X products)
- Missing titles: X
- Missing descriptions: X
- Corrupted text: X
- Duplicates: X
- Price outliers: X

## Recommended Fixes

### High Priority (Do First)
1. [Fix description]
   - Products affected: X
   - Estimated effort: [time]
   - Impact: [benefit]

### Medium Priority
[...]

### Low Priority
[...]

## Statistics
- Overall quality score: X/100
- Products needing review: X (Y%)
- Products that could improve: X (Y%)
```

**B. Manual Review List:** /home/user/CC/outputs/manual_review_needed.json

Format:
```json
[
  {
    "index": 123,
    "title": "Product title",
    "current_classification": "LED Light Bulb",
    "confidence": 22.5,
    "priority": "high",
    "reason": "Very low confidence - ambiguous between LED Light Bulb (22.5) and Pendant Light (21.0)",
    "suggested_action": "Review product details and determine correct type"
  },
  ...
]
```

**C. Quality Metrics:** /home/user/CC/outputs/quality_metrics.json

```json
{
  "audit_date": "2025-01-15",
  "total_products": 425,
  "overall_quality_score": 87.3,
  "issues_by_category": {
    "confidence_red_flags": 23,
    "classification_anomalies": 5,
    "missing_patterns": 3,
    "keyword_issues": 12,
    "data_quality": 8
  },
  "products_needing_review": 51,
  "high_priority_issues": 8,
  "medium_priority_issues": 15,
  "low_priority_issues": 28
}
```

Commit: "Complete quality audit - identify issues and improvements"

**Mark task complete:**
```python
python -c "
import sys, json
sys.path.insert(0, '/home/user/CC/scripts')
from workflow_engine import WorkflowEngine

with open('/home/user/CC/outputs/quality_metrics.json', 'r') as f:
    metrics = json.load(f)

w = WorkflowEngine()
w.mark_task_complete('quality_audit', {
    'issues_found': sum(metrics['issues_by_category'].values()),
    'products_flagged': metrics['products_needing_review'],
    'quality_score': metrics['overall_quality_score'],
    'high_priority': metrics['high_priority_issues']
})
"
```

Expected outputs:
- quality_audit_report.md (comprehensive audit)
- manual_review_needed.json (flagged products)
- quality_metrics.json (statistics)
- NEXT_PROMPT.txt (auto-generated based on findings!)
```

---

## 📚 DOCUMENTATION & QUALITY

### **Prompt 7: Generate Comprehensive System Documentation**

```
I need complete documentation explaining my product classification system for someone who doesn't code.

Context:
- Product classifier at 93.2% accuracy
- 77 product types, 425 products
- Stage 1 (identification) complete
- Multiple Python scripts, outputs, and reports exist

Your task:
Create a comprehensive guide: /home/user/CC/docs/SYSTEM_GUIDE.md

Include these sections:

## 1. PROJECT OVERVIEW
- What problem does this solve?
- What are the stages? (Stage 1 vs Stage 2)
- Current status and achievements
- Timeline and milestones

## 2. HOW THE CLASSIFIER WORKS (Non-Technical)
- Explain in simple terms how products are classified
- Keyword-based pattern matching explained
- Confidence scoring (0-100 scale) explained
- What the 77 product types are
- Examples of classification in action

## 3. ACCURACY & VALIDATION
- Current accuracy: 93.2%
- How validation works (ground truth samples explained)
- What errors mean and how to interpret them
- Confidence levels explained (High/Medium/Low)

## 4. FILE STRUCTURE (Directory Guide)
Explain what each directory contains:
- **/data** - What data files are here and what they contain
- **/scripts** - What each Python script does (in simple terms)
- **/outputs** - What outputs are generated
- **/reports** - What reports are available
- **/visualizations** - Dashboards and visual tools
- **/workflow** - Workflow tracking files

## 5. KEY FILES EXPLAINED
For each major file, explain:
- What it is
- What it contains
- How to use it (or view it)
- When it was created/updated

Examples:
- classify_products.py - The main classifier with 77 product patterns
- final_product_types.json - Classifications for all 425 products
- classification_dashboard.html - Interactive visual dashboard

## 6. HOW TO USE THE SYSTEM (Step-by-Step)
As a non-coder, how do I:
- Classify new products?
- Run validation?
- View results?
- Update patterns?
- Generate reports?

## 7. UNDERSTANDING RESULTS
- How to read classification output
- How to interpret confidence scores
- What to do about "Unknown" classifications
- How to identify misclassifications

## 8. NEXT STEPS
- What is Stage 2 (taxonomy mapping)?
- How to improve accuracy further
- How to add new product types
- How to deploy to production

## 9. TROUBLESHOOTING
Common issues and solutions:
- "Product classified incorrectly" → How to fix
- "Low confidence classification" → What to do
- "Script won't run" → Basic troubleshooting

## 10. GLOSSARY
Define technical terms in simple language:
- Product Type
- Confidence Score
- Ground Truth
- Validation
- Taxonomy
- Pattern Matching
- Classification
- etc.

---

Also create: /home/user/CC/docs/QUICK_START.md (5-minute version)

Quick Start format:
```markdown
# Quick Start Guide (5 Minutes)

## What You Have
- 425 Home Depot products classified
- 93.2% accuracy
- 77 different product types identified

## Key Files
1. **Classification Results:** outputs/final_product_types.json
2. **Dashboard:** visualizations/classification_dashboard.html
3. **Summary:** outputs/classification_summary.json

## How to View Results

### Option 1: Interactive Dashboard (Easiest!)
1. Open: visualizations/classification_dashboard.html
2. Click around to explore
3. Search, filter, and export data

### Option 2: JSON File
1. Open: outputs/final_product_types.json
2. Each product has: type, confidence, reasons

### Option 3: CSV Spreadsheet
1. Open: outputs/classifications.csv
2. View in Excel or Google Sheets

## Next Steps
- Read: docs/SYSTEM_GUIDE.md for full details
- Run: workflow/NEXT_PROMPT.txt for what to do next
```

Requirements:
- Write in plain English - avoid jargon
- Use analogies to explain technical concepts
- Include examples wherever possible
- Make it suitable for someone with no coding experience
- Format with clear headers and sections
- Use bullets and numbered lists
- Include diagrams or ASCII art if helpful

Commit: "Add comprehensive system documentation for non-technical users"

**Mark task complete:**
```python
python -c "
import sys, os
sys.path.insert(0, '/home/user/CC/scripts')
from workflow_engine import WorkflowEngine

system_guide_exists = os.path.exists('/home/user/CC/docs/SYSTEM_GUIDE.md')
quick_start_exists = os.path.exists('/home/user/CC/docs/QUICK_START.md')

# Count words in system guide
word_count = 0
if system_guide_exists:
    with open('/home/user/CC/docs/SYSTEM_GUIDE.md', 'r') as f:
        word_count = len(f.read().split())

w = WorkflowEngine()
w.mark_task_complete('generate_documentation', {
    'system_guide_created': system_guide_exists,
    'quick_start_created': quick_start_exists,
    'word_count': word_count,
    'comprehensive': word_count > 2000
})
"
```

Expected outputs:
- SYSTEM_GUIDE.md (comprehensive documentation)
- QUICK_START.md (5-minute quick reference)
- NEXT_PROMPT.txt (auto-generated!)
```

---

### **Prompt 8: Add 10 New Product Type Patterns**

```
My classifier has 77 product types. I want to expand coverage by adding 10 more common Home Depot product types.

Context:
- Current classifier: /home/user/CC/scripts/classify_products.py (77 patterns)
- Product data: /home/user/CC/data/scraped_data_output.json (425 products)
- Classification results: /home/user/CC/outputs/final_product_types.json
- Current accuracy: 93.2%

Your task:

1. Analyze the 425 products to find product types NOT currently covered
   - Load final_product_types.json
   - Find products classified as "Unknown" or with very low confidence
   - Group them by common keywords/patterns in titles

2. Identify candidates for new patterns:
   - Look for groups of 3+ products with similar titles
   - Common keywords that appear in Unknown products
   - Product types missing from current 77

3. Choose 10 NEW product types to add

   Suggestions (choose best 10 from these or find others):
   - Area Rug / Rug
   - Mailbox / Mailbox Post
   - Doorbell / Video Doorbell
   - Ceiling Fan Light Kit
   - Cabinet Hardware (Knobs / Pulls)
   - Weatherstripping / Door Seal
   - Caulk / Sealant
   - Picture Frame / Wall Frame
   - Power Tool Battery / Charger
   - Extension Ladder
   - Hand Sanitizer Dispenser
   - Pet Door
   - Welcome Mat / Doormat
   - Garden Hose / Hose Reel
   - Concrete / Mortar Mix
   - Garage Door Opener
   - Light Timer / Smart Plug

4. For each new pattern, define in classify_products.py:

   ```python
   'Area Rug': {
       'strong_keywords': ['rug', 'area rug', 'runner rug', 'floor rug'],
       'weak_keywords': ['woven', 'pile', 'x', 'ft', 'indoor', 'outdoor', 'polypropylene'],
       'description_hints': ['floor covering', 'rug features', 'soft underfoot'],
       'domains': [],
       'negative_keywords': ['mat', 'doormat', 'welcome mat']
   },
   ```

   Requirements for each pattern:
   - At least 2 strong_keywords (high confidence matches)
   - At least 5 weak_keywords (supporting evidence)
   - At least 2 description_hints
   - Include negative_keywords to prevent false matches
   - Consider domains if applicable

5. Add all 10 patterns to the self.patterns dictionary in classify_products.py
   - Insert in appropriate section (organize by category)
   - Maintain alphabetical order within sections

6. Test the new patterns:
   - Re-run classification on all 425 products
   - See how many previously "Unknown" products now get classified
   - Check for any false positives (misclassifications)

7. Generate impact report: /home/user/CC/reports/new_patterns_report.md

   Include:
   ```markdown
   # New Product Type Patterns Report

   Date: [timestamp]

   ## Patterns Added: 10
   1. Area Rug
   2. Mailbox
   3. Doorbell
   ... (list all 10)

   ## Impact Analysis

   ### Before (77 patterns)
   - Unknown products: X
   - Average confidence: X%

   ### After (87 patterns)
   - Unknown products: Y
   - Average confidence: Y%
   - Improvement: Z fewer unknowns

   ## Products Reclassified

   ### Area Rug (X products newly classified)
   - Product 1: [title] - was Unknown, now Area Rug (confidence: X%)
   - Product 2: ...

   ### Mailbox (X products newly classified)
   - Product 1: ...

   ## Validation
   - No new false positives detected
   - All new classifications reviewed for accuracy

   ## Recommendations
   - [Any patterns that need refinement]
   - [Additional patterns to consider]
   ```

8. Re-run validation if you have ground truth for any newly classified products:
   ```bash
   python scripts/validate_system.py > outputs/validation_87patterns.txt
   ```

9. Commit: "Add 10 new product type patterns (77 → 87 total)"

10. **Mark task complete:**
    ```python
    python -c "
    import sys, json
    sys.path.insert(0, '/home/user/CC/scripts')
    from workflow_engine import WorkflowEngine
    from classify_products import ProductClassifier

    # Count patterns
    classifier = ProductClassifier()
    pattern_count = len(classifier.patterns)

    # Load new classifications
    with open('/home/user/CC/outputs/final_product_types.json', 'r') as f:
        classifications = json.load(f)

    unknown_count = sum(1 for c in classifications if 'Unknown' in c['product_type'])

    w = WorkflowEngine()
    w.mark_task_complete('add_new_patterns', {
        'total_patterns': pattern_count,
        'patterns_added': pattern_count - 77,
        'unknown_remaining': unknown_count,
        'coverage_improved': True
    })
    "
    ```

Expected outputs:
- Updated classify_products.py (87 patterns, was 77)
- new_patterns_report.md (impact analysis)
- Updated final_product_types.json (reclassified products)
- NEXT_PROMPT.txt (auto-generated!)
```

---

## ⚡ How to Use These Prompts

1. **Start anywhere!** Pick the prompt that excites you most
2. **Copy the ENTIRE prompt** (including the workflow engine command at the end)
3. **Paste to a new Claude conversation**
4. **Agent completes the task** and runs the final command
5. **Get your next prompt** automatically from: `/home/user/CC/workflow/NEXT_PROMPT.txt`
6. **Repeat!** 🔁

---

## 🎯 Quick Access Commands

Check what to do next:
```bash
cd /home/user/CC
python scripts/workflow_engine.py next
```

See your progress:
```bash
python scripts/workflow_engine.py status
```

Read the next prompt:
```bash
cat workflow/NEXT_PROMPT.txt
```

---

## 🌟 The Magic

Each prompt ends with a workflow engine command that:
- ✅ Marks the task complete
- 📝 Logs the results (counts, scores, etc.)
- 🎯 **Analyzes what you just did**
- 🔮 **Generates an intelligent next prompt** based on:
  - Your actual results (not generic!)
  - What's left to do
  - Dependencies between tasks
  - Quality of your data

**You never have to think "what's next?" again!** The system tells you. 🚀

---

Ready to start? Pick Prompt 1 and go! 🎉
