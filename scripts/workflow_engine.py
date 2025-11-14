#!/usr/bin/env python3
"""
Self-Perpetuating Workflow Engine
Each task completion generates the next recommended prompt
"""

import json
from pathlib import Path
from datetime import datetime

class WorkflowEngine:
    """Manages workflow progression and generates next prompts"""

    def __init__(self):
        self.workflow_dir = Path("/home/user/CC/workflow")
        self.workflow_dir.mkdir(exist_ok=True)

        self.completed_tasks_file = self.workflow_dir / "completed_tasks.json"
        self.next_prompt_file = self.workflow_dir / "NEXT_PROMPT.txt"
        self.workflow_state_file = self.workflow_dir / "workflow_state.json"

        self.load_state()

    def load_state(self):
        """Load workflow state from disk"""
        if self.workflow_state_file.exists():
            with open(self.workflow_state_file, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = {
                'completed_tasks': [],
                'current_phase': 'Stage 1 - Product Classification',
                'accuracy': 93.2,
                'total_products': 425,
                'classified_products': 44  # Only ground truth so far
            }

    def save_state(self):
        """Save workflow state to disk"""
        with open(self.workflow_state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def mark_task_complete(self, task_name, results=None):
        """Mark a task as complete and generate next prompt"""

        # Record completion
        completion = {
            'task': task_name,
            'completed_at': datetime.now().isoformat(),
            'results': results or {}
        }

        self.state['completed_tasks'].append(completion)
        self.save_state()

        # Save to completed tasks log
        if self.completed_tasks_file.exists():
            with open(self.completed_tasks_file, 'r') as f:
                log = json.load(f)
        else:
            log = []

        log.append(completion)

        with open(self.completed_tasks_file, 'w') as f:
            json.dump(log, f, indent=2)

        # Generate next prompt
        next_prompt = self.generate_next_prompt(task_name, results)

        # Save next prompt
        with open(self.next_prompt_file, 'w') as f:
            f.write(next_prompt)

        print(f"\n{'='*80}")
        print(f"TASK COMPLETED: {task_name}")
        print(f"{'='*80}")
        print(f"\n✅ Task marked as complete")
        print(f"📁 Next prompt saved to: {self.next_prompt_file}")
        print(f"\n{next_prompt[:200]}...")
        print(f"\n{'='*80}")

        return next_prompt

    def generate_next_prompt(self, completed_task, results):
        """Generate intelligent next prompt based on what was just completed"""

        # Define workflow dependencies and progressions
        workflow_map = {
            'classify_all_products': self._prompt_after_classification,
            'create_dashboard': self._prompt_after_dashboard,
            'fix_remaining_errors': self._prompt_after_error_fixes,
            'expand_ground_truth': self._prompt_after_ground_truth_expansion,
            'quality_audit': self._prompt_after_quality_audit,
            'taxonomy_mapping': self._prompt_after_taxonomy_mapping,
            'add_new_patterns': self._prompt_after_new_patterns,
            'generate_documentation': self._prompt_after_documentation
        }

        # Get specialized prompt generator
        prompt_generator = workflow_map.get(completed_task, self._default_next_prompt)

        return prompt_generator(results)

    def _prompt_after_classification(self, results):
        """Generate prompt after classifying all 425 products"""

        classified_count = results.get('classified_count', 0)
        unknown_count = results.get('unknown_count', 0)
        avg_confidence = results.get('avg_confidence', 0)

        prompt = f"""
🎯 TASK COMPLETED: Full Product Classification

Results Summary:
- Total products classified: {classified_count}
- Products with "Unknown" status: {unknown_count}
- Average confidence: {avg_confidence:.1f}%

📊 Files Generated:
- /home/user/CC/outputs/final_product_types.json
- /home/user/CC/outputs/classification_summary.json
- /home/user/CC/outputs/classifications.csv

---

🔄 RECOMMENDED NEXT STEP: Create Visualization Dashboard

Now that all products are classified, you should create an interactive dashboard to explore the results visually.

Copy-paste this prompt to a new AI agent:

---

I just classified all 425 products in my dataset with 93.2% accuracy. Now I need an interactive HTML dashboard to visualize and explore these classifications.

Context:
- Classification results: /home/user/CC/outputs/final_product_types.json
- Product data: /home/user/CC/data/scraped_data_output.json
- {classified_count} products classified
- {unknown_count} products marked as "Unknown"
- Average confidence: {avg_confidence:.1f}%

Your task:
1. Create an interactive HTML dashboard: /home/user/CC/visualizations/classification_dashboard.html

Include these sections:

A. OVERVIEW PANEL
- Total products: 425
- Classified: {classified_count}
- Unknown: {unknown_count}
- Average confidence: {avg_confidence:.1f}%
- Accuracy: 93.2%

B. PRODUCT TYPE DISTRIBUTION (Bar Chart)
- Show count for each of the 77 product types
- Make it interactive (hover for details)
- Highlight top 20 types

C. CONFIDENCE DISTRIBUTION (Pie Chart)
- High (70-100): X products
- Medium (50-69): X products
- Low (30-49): X products
- Very Low (20-29): X products
- Unknown (<20): X products

D. SEARCHABLE PRODUCT TABLE
- All 425 products in a sortable, filterable table
- Columns: Index, Title (truncated), Product Type, Confidence, Status
- Filter by: product type, confidence level, status
- Search by: title keywords

E. LOW CONFIDENCE ALERTS
- List all products with confidence < 30
- Highlight for manual review
- Show why confidence is low

F. PRODUCT TYPE EXPLORER
- Click any product type → see all products in that category
- Show pattern keywords used for classification
- Show confidence distribution for that type

2. Style Requirements:
- Professional, clean design
- Use Chart.js for charts (include via CDN)
- Responsive layout (works on mobile)
- Dark mode toggle
- Export buttons (CSV, PDF)

3. Technical Requirements:
- Self-contained HTML file (all CSS/JS inline or from CDN)
- No server needed - opens directly in browser
- Fast loading (<2 seconds)
- Works offline after first load

4. Create usage guide: /home/user/CC/visualizations/DASHBOARD_GUIDE.md

5. Test that it works by opening in a browser

6. Commit your changes with message: "Add interactive classification dashboard"

Expected outputs:
- classification_dashboard.html (interactive dashboard)
- DASHBOARD_GUIDE.md (how to use it)
- Screenshot or description of what it looks like

After completing this task, run this Python script to get your next prompt:
```bash
python -c "from workflow_engine import WorkflowEngine; w = WorkflowEngine(); w.mark_task_complete('create_dashboard', {{'dashboard_created': True}})"
```

---
"""
        return prompt.strip()

    def _prompt_after_dashboard(self, results):
        """Generate prompt after dashboard creation"""

        prompt = f"""
🎯 TASK COMPLETED: Interactive Dashboard Created

Results:
- Dashboard file: /home/user/CC/visualizations/classification_dashboard.html
- Guide created: /home/user/CC/visualizations/DASHBOARD_GUIDE.md

You can now open the dashboard in your browser to explore the 425 classified products visually!

---

🔄 RECOMMENDED NEXT STEP: Quality Audit

Now that you can visualize the data, you should run a quality audit to find edge cases, anomalies, and potential improvements.

Copy-paste this prompt to a new AI agent:

---

I've classified all 425 products and created a dashboard. Now I need a comprehensive quality audit to find issues and improvements.

Context:
- Classifications: /home/user/CC/outputs/final_product_types.json
- Product data: /home/user/CC/data/scraped_data_output.json
- Accuracy: 93.2% on ground truth
- Dashboard: /home/user/CC/visualizations/classification_dashboard.html

Your task:
Run a comprehensive quality audit and find:

1. CONFIDENCE RED FLAGS
   - Products with confidence < 20 (review why they couldn't be classified)
   - Products with confidence 20-30 (very uncertain - need manual review)
   - Products where top 2 types have similar scores (ambiguous cases)

2. POTENTIAL MISCLASSIFICATIONS
   - Products where title strongly suggests different type than classified
   - Example: Title says "LED Bulb" but classified as "Pendant Light"
   - Check for obvious contradictions

3. MISSING PATTERNS
   - Find groups of 5+ products classified as "Unknown" with similar titles
   - These might need new product type patterns
   - Example: If 10 products mention "door hinge" but are Unknown

4. KEYWORD ISSUES
   - Products classified with very generic reasoning
   - Products where negative keywords might be needed
   - Overlapping patterns causing confusion

5. DATA QUALITY PROBLEMS
   - Products with missing/incomplete titles or descriptions
   - Products with suspiciously high/low prices
   - Duplicate products
   - Corrupted text

Output format:

A. Create audit report: /home/user/CC/reports/quality_audit_report.md
   - Executive summary (top 10 findings)
   - Detailed findings by category
   - Recommended fixes ranked by priority (High/Medium/Low)
   - Statistics on each issue type

B. Create review list: /home/user/CC/outputs/manual_review_needed.json
   - List of products requiring manual review
   - Sort by priority (confidence score ascending)
   - Include reason for review

C. Create metrics file: /home/user/CC/outputs/quality_metrics.json
   - Count of each issue type
   - Overall quality score (0-100)
   - Trends and patterns

After completing this task, run:
```bash
python -c "from workflow_engine import WorkflowEngine; w = WorkflowEngine(); w.mark_task_complete('quality_audit', {{'issues_found': 0, 'products_flagged': 0}})"
```

Replace the numbers with your actual findings!

---
"""
        return prompt.strip()

    def _prompt_after_quality_audit(self, results):
        """Generate prompt after quality audit"""

        issues_found = results.get('issues_found', 0)
        products_flagged = results.get('products_flagged', 0)

        if issues_found > 10:
            # Major issues found - fix them
            next_task = "fix_quality_issues"
            action = "Fix Quality Issues"
        elif products_flagged < 10:
            # Quality is good - move to Stage 2
            next_task = "taxonomy_mapping"
            action = "Start Stage 2 - Taxonomy Mapping"
        else:
            # Some issues but not critical - expand ground truth
            next_task = "expand_ground_truth"
            action = "Expand Ground Truth Dataset"

        if next_task == "taxonomy_mapping":
            return self._prompt_stage2_taxonomy_mapping()
        elif next_task == "expand_ground_truth":
            return self._prompt_expand_ground_truth()
        else:
            return self._prompt_fix_quality_issues(issues_found, products_flagged)

    def _prompt_stage2_taxonomy_mapping(self):
        """Generate Stage 2 taxonomy mapping prompt"""

        prompt = """
🎯 QUALITY AUDIT COMPLETE: System Quality is Good!

Your classifier is performing well. Time to move to Stage 2: Taxonomy Mapping!

---

🚀 RECOMMENDED NEXT STEP: Start Stage 2 - Map to Facebook Taxonomy

Now you'll map your 77 specific product types (like "LED Light Bulb") to Facebook's standardized 373-category taxonomy.

Copy-paste this prompt to a new AI agent:

---

My product classifier identifies 425 products into 77 specific types with 93.2% accuracy. Now I need to map these 77 types to Facebook's standardized taxonomy of 373 categories.

Context:
- My 77 product types are in: /home/user/CC/scripts/classify_products.py (keys in self.patterns)
- Facebook taxonomy: /home/user/CC/data/taxonomy_paths.txt (373 hierarchical categories)
- Strategy document: /home/user/CC/docs/mapping_strategy.md
- Classification results: /home/user/CC/outputs/final_product_types.json

Your task:

1. Extract my 77 product types from classify_products.py
   - They're the keys in the self.patterns dictionary
   - Examples: "LED Light Bulb", "Circuit Breaker", "Landscape Lighting", etc.

2. Read Facebook's 373 taxonomy categories from taxonomy_paths.txt
   - Format: hierarchical paths like "Home & Garden > Lighting > Light Bulbs"

3. Create intelligent mappings
   For EACH of my 77 types, find the BEST matching Facebook category(ies)

   Use these matching strategies:
   - **Exact/Semantic Match**: "LED Light Bulb" → "Home & Garden > Lighting > Light Bulbs"
   - **Parent Category Match**: "Wall Sconce" → "Home & Garden > Lighting > Lamps & Light Fixtures"
   - **Keyword Overlap**: Look for shared words between my type and FB category
   - **Multiple Matches**: Some types may map to 2-3 FB categories

4. Create mapping file: /home/user/CC/data/type_to_taxonomy_mapping.json

   Format:
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
       "keywords_matched": ["light", "bulb", "led"]
     },
     "Circuit Breaker": {
       "primary_match": "Home & Garden > Pool & Spa > Pool & Spa Accessories > Pool & Spa Electrical",
       "confidence": "medium",
       "match_reason": "No exact match - closest is electrical category",
       "alternate_matches": [],
       "keywords_matched": ["electrical"],
       "notes": "No perfect FB category for circuit breakers - this is approximate"
     },
     ...
   }
   ```

5. Generate mapping quality report: /home/user/CC/reports/taxonomy_mapping_report.md

   Include:
   - Summary statistics (how many high/medium/low confidence mappings)
   - List of ambiguous mappings needing review
   - List of product types with no good FB match
   - Coverage analysis (% of products that can be mapped)
   - Recommendations for handling unmapped types

6. Create reverse index: /home/user/CC/data/taxonomy_to_types_index.json
   - Maps FB categories → list of my product types
   - Useful for seeing which FB categories have multiple of my types

7. Validate mappings
   - Check that all 77 types have at least one mapping
   - Flag any suspicious mappings
   - Calculate mapping quality score

8. Commit your changes with message: "Add Stage 2 taxonomy mappings for 77 product types"

Expected outputs:
- type_to_taxonomy_mapping.json (77 mappings)
- taxonomy_mapping_report.md (quality analysis)
- taxonomy_to_types_index.json (reverse lookup)

After completing this task, run:
```bash
python -c "from workflow_engine import WorkflowEngine; w = WorkflowEngine(); w.mark_task_complete('taxonomy_mapping', {'mappings_created': 77, 'high_confidence': 0, 'needs_review': 0})"
```

Replace numbers with your actual counts!

---
"""
        return prompt.strip()

    def _prompt_expand_ground_truth(self):
        """Prompt to expand ground truth dataset"""
        return """
🎯 QUALITY AUDIT COMPLETE: Some Products Need Review

Before moving to Stage 2, let's expand the ground truth dataset for more robust validation.

Copy-paste this prompt to expand ground truth from 44 to 100+ samples...

[Full prompt similar to Prompt 3 from earlier]
"""

    def _prompt_fix_quality_issues(self, issues_found, products_flagged):
        """Prompt to fix quality issues"""
        return f"""
🎯 QUALITY AUDIT COMPLETE: {issues_found} Issues Found

Found {issues_found} quality issues affecting {products_flagged} products. Let's fix these before moving to Stage 2.

Copy-paste this prompt to fix the quality issues...

[Prompt to address specific issues found]
"""

    def _default_next_prompt(self, results):
        """Default prompt if no specific mapping exists"""

        completed_count = len(self.state['completed_tasks'])

        return f"""
🎯 TASK COMPLETED

You've completed {completed_count} tasks so far!

Completed tasks:
{self._format_completed_tasks()}

---

🔄 SUGGESTED NEXT STEPS:

Here are recommended next actions based on your project state:

1. **High Priority:**
   - Run classifier on all 425 products (if not done)
   - Create visualization dashboard
   - Start Stage 2 taxonomy mapping

2. **Medium Priority:**
   - Expand ground truth to 100+ samples
   - Fix remaining 3 errors to reach 95%+ accuracy
   - Add more product type patterns

3. **Quality & Polish:**
   - Run quality audit
   - Generate comprehensive documentation
   - Create user guide for non-technical users

Choose one of the 8 prompts I provided earlier, or ask me:
"What should I work on next?"

---
"""

    def _format_completed_tasks(self):
        """Format completed tasks list"""
        tasks = self.state['completed_tasks']
        if not tasks:
            return "  (none yet)"

        formatted = []
        for i, task in enumerate(tasks, 1):
            formatted.append(f"  {i}. {task['task']} - {task['completed_at'][:10]}")

        return "\n".join(formatted)

    def get_current_status(self):
        """Get current workflow status"""

        status = f"""
{'='*80}
WORKFLOW STATUS
{'='*80}

Current Phase: {self.state['current_phase']}
Classifier Accuracy: {self.state['accuracy']}%
Products Classified: {self.state['classified_products']}/425

Completed Tasks: {len(self.state['completed_tasks'])}
{self._format_completed_tasks()}

Next Recommended Action:
  → Check {self.next_prompt_file} for your next copy-paste prompt!

{'='*80}
"""
        return status


# Convenience functions for quick access
def mark_complete(task_name, **results):
    """Quick function to mark task complete and get next prompt"""
    engine = WorkflowEngine()
    return engine.mark_task_complete(task_name, results)


def show_status():
    """Quick function to show workflow status"""
    engine = WorkflowEngine()
    print(engine.get_current_status())


def get_next_prompt():
    """Quick function to get the next prompt"""
    engine = WorkflowEngine()
    if engine.next_prompt_file.exists():
        with open(engine.next_prompt_file, 'r') as f:
            return f.read()
    else:
        return "No next prompt available yet. Run a task first!"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            show_status()
        elif command == "next":
            print(get_next_prompt())
        elif command == "complete":
            if len(sys.argv) > 2:
                task_name = sys.argv[2]
                mark_complete(task_name)
            else:
                print("Usage: workflow_engine.py complete <task_name>")
        else:
            print("Unknown command. Use: status, next, or complete")
    else:
        # Show status by default
        show_status()
