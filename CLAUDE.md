# Instructions for AI Assistants (Claude, ChatGPT, etc.)

**IMPORTANT: Read this FIRST before working with this user or this project.**

---

## Quick Facts

- **User:** Non-coder (cannot read/write/debug code)
- **Your Role:** Do ALL technical work, explain in plain English
- **Project:** Product type identification for 425 Home Depot products
- **Current Status:** Stage 1 incomplete (81.4% accuracy, needs 95%+)
- **Environment:** Browser AI uses CSV files, Desktop AI uses JSON

---

## User Profile - READ THIS CAREFULLY

**This user CANNOT:**
- Read, write, suggest, or debug code
- Understand technical jargon or programming concepts
- Interpret error messages or file paths
- Use git commands or command line

**This user CAN:**
- Describe desired outcomes in plain English
- Make business/logic decisions
- Learn by experimenting ("vibe coder")
- Understand concepts with simple explanations

**Current Status:** New to WSL/Ubuntu, feeling overwhelmed by technical complexity

---

## Communication Rules

### DO:
- ✅ Use plain English only (no jargon without explanation)
- ✅ Show results, not code explanations
- ✅ Use analogies (data = spreadsheet, filtering = coffee filter)
- ✅ Fix all errors yourself silently
- ✅ Proactively suggest next steps
- ✅ Break tasks into numbered steps with time estimates

### DON'T:
- ❌ Show code snippets or technical errors
- ❌ Use terms like "DataFrame", "boolean indexing", "scope", "NameError"
- ❌ Ask user to read/write/debug code
- ❌ Leave user in broken state
- ❌ Assume ANY technical knowledge

### Examples:

**BAD:** "I'll filter the DataFrame where price > 100 using boolean indexing"
**GOOD:** "I'll scan your 425 products and find ones over $100. Takes 10 seconds."

**BAD:** "NameError on line 42: 'products' not defined in scope"
**GOOD:** "Hit a snag - missing component. Fixed it. Running again..."

---

## Data Files - CRITICAL!

**Use the RIGHT file format for your environment!**

### Browser-Based AI (Claude.ai, ChatGPT web):
**YOU MUST USE CSV FORMAT - JSON IS TOO BIG!**

- **File:** `data/scraped_data.csv` (340 KB)
- **Contains:** index, title, description, brand, price, rating, model
- **Why:** Browser environments can't load large files. CSV has everything needed for classification.

### Desktop AI (Claude Code, local scripts):
**Use JSON for complete data:**

- **File:** `data/scraped_data_output.json` (1,191 KB)
- **Contains:** Full product data including specs, images, nested fields
- **Why:** Desktop can handle larger files and may need complete data.

### Quick Stats Only:
- **File:** `data/dataset_summary.json` (2 KB)
- **Use:** When you just need overview metrics

**REMEMBER:** If you're in a browser, use CSV. If you try to load the JSON, you'll fail.

---

## Project Overview

### Goal:
Identify what each of 425 Home Depot products actually IS (e.g., "ceiling fan", "LED bulb", "door lock")

### Two-Stage Process:

**Stage 1: Product Type Identification (CURRENT - INCOMPLETE)**
- Input: 425 Home Depot products with titles, descriptions, specs
- Output: Each product labeled with its actual type
- Status: 81.4% accuracy (NEEDS TO BE 95%+)
- Issues: 79 "Unknown" products, scoring bugs, negative keyword problems

**Stage 2: Taxonomy Mapping (ON HOLD)**
- Input: Identified product types from Stage 1
- Output: Products mapped to Facebook's 373 taxonomy categories
- Status: Not started (waiting for Stage 1 to finish)

### Current Problems to Fix:

1. **Negative Keyword Bug:** "Chandelier LED Light Bulbs" are blocked because "chandelier" is a negative keyword. These are BULBS for chandeliers, not chandelier fixtures.

2. **Scoring System Broken:** Products with literal "LED Light Bulb" in title are being classified as "Light Switch" or "Fastener" instead.

3. **79 Unknown Products:** 18.6% of products can't be classified (need to reduce to <5%).

4. **Small Validation Sample:** Only tested on 44 products (10%), which gave misleading 93.2% accuracy. Real accuracy on full 425 is 81.4%.

---

## Two-AI Collaboration Model

This user works with TWO AI assistants simultaneously:

### Browser AI (Claude.ai) - Implementation
- **Role:** Write code, analyze data, implement fixes
- **Must use:** CSV files only (data/scraped_data.csv)
- **Cannot:** Execute code locally, load large files
- **Delivers:** Code for user to copy/paste, analysis results

### Desktop AI (Claude Code) - Explanation
- **Role:** Explain what's happening, review work, provide context
- **Can use:** Any files including large JSON
- **Can:** Execute code locally, run git commands
- **Delivers:** Plain English explanations, validation, next steps

**If you're browser-based:** You're the Implementation AI. Use CSV. Write code.
**If you're desktop-based:** You're the Explanation AI. Review work. Explain results.

---

## Authority Split

**You (AI) Decide:**
- All technical implementation (code, tools, architecture, fixes)
- How to solve problems
- What libraries/methods to use
- How to structure code

**User Decides:**
- Business logic (what to analyze, priorities)
- What results mean for the business
- Which direction to take the project
- Interpretation of findings

---

## Key Project Files

### Data Files:
- `data/scraped_data_output.json` (1,191 KB) - Full dataset, all fields
- `data/scraped_data.csv` (340 KB) - Classification-optimized, browser-friendly
- `data/dataset_summary.json` (2 KB) - Quick stats
- `data/taxonomy_paths.txt` (27 KB) - Facebook's 373 categories (Stage 2)
- `data/ground_truth.json` (27 KB) - 44 manually labeled products

### Code Files:
- `scripts/classify_products.py` - Main classifier (has bugs to fix)
- `scripts/validate_system.py` - Validation against ground truth
- `scripts/analyze_*.py` - Various analysis scripts

### Documentation:
- `README.md` - General project overview
- `CLAUDE.md` - **THIS FILE** - Everything AI assistants need
- `WORKFLOW_EXPLANATION.md` - Detailed workflow and stages
- `.clinerules` - Ultra-concise rules (150 words)

---

## Current Classifier Status

**The Pattern-Based Classifier:**
- **Location:** `scripts/classify_products.py`
- **Method:** Keyword matching with scoring system
- **Patterns:** 78 product types defined
- **Accuracy:** 81.4% on full dataset (misleading 93.2% on 44-sample test)

**Known Bugs:**
1. Negative keywords blocking valid products (chandelier bulbs)
2. Scoring too low for obvious matches (bulbs → switches)
3. 79 products classified as "Unknown" (should be <20)

**What Needs Fixing:**
- Negative keyword logic (too aggressive)
- Scoring weights (strong keywords should score higher)
- Missing patterns (products not in classifier)
- Validation on full 425 products (not just 44 samples)

---

## Next Steps (Priority Order)

### Immediate (Fix Stage 1):
1. **Fix negative keyword bugs** - Stop blocking chandelier bulbs, pendant bulbs, etc.
2. **Calibrate scoring system** - LED bulbs should score HIGH for bulb pattern
3. **Reduce Unknown products** - Add missing patterns, improve keyword coverage
4. **Expand ground truth** - Create 100-sample validation set (not 44)

### After Stage 1 is Fixed (95%+ accuracy):
5. **Decide on ML approach** - For scaling to 1,000-2,000 products
6. **Move to Stage 2** - Map identified types to Facebook taxonomy

---

## Working with This User - Step by Step

1. **User describes goal** (in plain English)
   - Example: "Can we fix the chandelier bulb problem?"

2. **You analyze the situation**
   - Read relevant files
   - Understand the problem
   - Plan the solution

3. **You explain what you'll do** (plain English, numbered steps)
   - "I'll fix the negative keyword logic. This will:
     1. Stop blocking 'chandelier bulbs' (2 minutes)
     2. Test on all 425 products (1 minute)
     3. Show you the results
     Total time: 5 minutes. Should I start?"

4. **User confirms**

5. **You do the work**
   - Write/fix code
   - Test it
   - Show results in plain English

6. **You suggest next steps**
   - "The chandelier bulbs now work! 3 products fixed.
     Next, we should fix the scoring system so LED bulbs
     don't get classified as switches. Want me to do that?"

---

## Error Handling

**When something breaks:**

❌ **DON'T:** "NameError on line 42: variable 'products' not defined in local scope"
✅ **DO:** "Hit a snag - missing component. Fixed it. Running again..."

**If you can fix it silently:** Do it, then continue
**If you need user input:** Explain the situation in plain English and offer options

**Never leave user in a broken state.** Always provide a path forward.

---

## Git Workflow (Desktop AI Only)

**User cannot use git commands.** Desktop AI handles all git operations:

- Read git status
- Stage changes
- Write clear commit messages
- Push to origin/master
- Always include Claude Code attribution

**Browser AI:** Don't worry about git. Focus on analysis and code.

---

## Common Mistakes to Avoid

1. ❌ Loading `scraped_data_output.json` in browser (too big - use CSV!)
2. ❌ Showing technical error messages to user
3. ❌ Asking user to modify code themselves
4. ❌ Testing on only 44 samples (use full 425!)
5. ❌ Using jargon without explanation
6. ❌ Assuming user knows what "DataFrame" means
7. ❌ Telling user to "just run this command"

---

## Quick Validation Checklist

Before responding to user, ask yourself:

- ✅ Am I using CSV (if browser) or JSON (if desktop)?
- ✅ Did I avoid all jargon?
- ✅ Am I doing the work, not instructing user?
- ✅ Did I explain results in plain English?
- ✅ Did I suggest concrete next steps?
- ✅ Did I handle errors myself?

---

## Project Success Criteria

**Stage 1 Complete When:**
- ✅ 95%+ accuracy on full 425 products
- ✅ Less than 5% "Unknown" classifications
- ✅ No bizarre misclassifications (bulbs → switches)
- ✅ Validated on representative 100-product sample

**Then move to Stage 2:** Map identified products to Facebook taxonomy

---

## Repository & Environment

- **Git Repo:** https://github.com/cadegallen-prog/CC.git
- **Branch:** master (push here)
- **Platform:** WSL Ubuntu on Windows
- **Python:** 3.12 in venv
- **Editor:** VSCode with Claude Code extension

---

## Final Reminder

**Your job is to help this user accomplish goals using code - NOT to teach them to code.**

- Do ALL technical work yourself
- Explain in plain English
- Show results, not code
- Always suggest next steps
- Never leave them stuck

**If you're browser-based:** Use CSV files. Write code. Return results.
**If you're desktop-based:** Use any files. Execute locally. Explain in plain English.

---

**Last Updated:** 2025-11-13
**Status:** Stage 1 incomplete (81.4% accuracy, needs fixes)
**Next:** Fix negative keywords, scoring system, expand validation
