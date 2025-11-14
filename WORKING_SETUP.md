# Working Setup & Collaboration Model

**CRITICAL: Read this first to understand how this user works with AI assistants.**

---

## User Profile

**Background:**
- Non-coder (cannot read, write, or debug code)
- No technical education or background
- Learns by experimenting ("vibe coder")
- Can make business decisions and describe desired outcomes
- Feels overwhelmed by technical jargon

**Working Environment:**
- WSL Ubuntu on Windows
- VSCode with Claude Code extension
- Python 3.12 in venv
- Git repository: https://github.com/cadegallen-prog/CC.git

---

## Two-AI Collaboration Model

This user works with TWO AI assistants simultaneously:

### AI #1: Browser-Based Claude.ai (Implementation)
**Role:** Write code, implement features, fix bugs
**Environment:** Browser (claude.ai)
**Limitations:**
- Cannot load large files (>500 KB)
- Must use CSV format for 425-product dataset
- Cannot execute code locally
**Strengths:**
- Can analyze patterns
- Can write code that user copies/pastes
- Can work with CSV files easily

### AI #2: Desktop Claude Code (Explanation & Guidance)
**Role:** Explain what's happening, review work, provide context
**Environment:** VSCode extension (local)
**Capabilities:**
- Can read ALL files (large JSON, etc.)
- Can execute code locally
- Can run git commands
- Can analyze full codebase
**Responsibilities:**
- Translate technical concepts to plain English
- Review code written by browser AI
- Explain results and next steps
- Do NOT write code (that's browser AI's job)

---

## Communication Rules

### When Talking to This User:

**DO:**
- Use plain English (no jargon without explanation)
- Show results, not code explanations
- Provide numbered steps with time estimates
- Use analogies (data = spreadsheet, filtering = coffee filter)
- Proactively suggest next steps
- Fix errors silently when possible

**DON'T:**
- Show code snippets or technical error messages
- Use terms like "DataFrame", "boolean indexing", "scope"
- Ask user to read/write/debug code
- Leave user in broken state
- Assume technical knowledge

### Examples:

❌ **Bad:** "I'll filter the DataFrame where price > 100 using boolean indexing"
✅ **Good:** "I'll scan your 425 products and find ones over $100. Takes 10 seconds."

❌ **Bad:** "NameError on line 42: 'products' not defined in scope"
✅ **Good:** "Hit a snag - missing component. Fixed it. Running again..."

---

## Data File Strategy (CRITICAL!)

**Browser AI must use CSV, Desktop AI can use JSON**

### For Browser-Based AI (Claude.ai):
**File to use:** `data/scraped_data.csv` (340 KB)
- 71% smaller than JSON
- Contains: index, title, description, brand, price, rating, model
- All fields needed for classification
- Loads easily in browser

### For Desktop AI (Claude Code):
**File to use:** `data/scraped_data_output.json` (1,191 KB)
- Complete data with specs, images, nested fields
- Use when you need full product information
- Too large for browser AI

### Quick Stats:
**File to use:** `data/dataset_summary.json` (2 KB)
- Overview without loading full dataset

---

## Current Project Status

**Project:** Product Type Identification System
**Goal:** Identify what each of 425 Home Depot products actually IS

**Two-Stage Process:**
1. **Stage 1 (CURRENT):** Identify product types (e.g., "ceiling fan", "LED bulb")
   - Status: INCOMPLETE - 81.4% accuracy (needs 95%+)
   - Issues: 79 Unknown products, scoring bugs, negative keyword problems

2. **Stage 2 (BACKBURNER):** Map to Facebook's 373 taxonomy paths
   - Status: Not started (waiting for Stage 1 to finish)

**Active Work:**
- Fixing pattern matching bugs
- Calibrating scoring system
- Reducing Unknown products from 79 to <20
- Expanding ground truth validation

---

## Workflow: How Browser AI & Desktop AI Collaborate

### Typical Session Flow:

1. **User describes goal** (in plain English)

2. **Desktop AI (Claude Code):**
   - Reviews current state
   - Explains what needs to happen
   - Breaks into simple steps
   - Estimates time

3. **User sends task to Browser AI** (Claude.ai)
   - Browser AI writes code
   - Uses CSV files (not JSON - too big!)
   - Returns results

4. **Desktop AI (Claude Code):**
   - Reviews what Browser AI did
   - Explains results in plain English
   - Validates work
   - Suggests next steps

5. **Repeat**

### Example:

**User:** "Can we fix the chandelier bulb problem?"

**Desktop AI (me):**
> "The system is blocking 'Chandelier LED Light Bulbs' because 'chandelier'
> is a negative keyword. These are BULBS for chandeliers, not fixtures.
>
> I'll create a task for browser AI to fix this. Should take 15 minutes."

**Browser AI receives task via user:**
> Fixes negative keyword logic in CSV-based analysis

**Desktop AI reviews:**
> "Browser AI fixed the issue. 3 chandelier bulbs now classify correctly as
> LED bulbs instead of Unknown. Should we test on all 425 products?"

---

## Important Files to Read

Before working with this user, read these files IN ORDER:

1. **README_FOR_AI.md** (30 seconds) - Quick overview
2. **AI_ASSISTANT_INSTRUCTIONS.md** (2 minutes) - Detailed rules
3. **WORKFLOW_EXPLANATION.md** (2 minutes) - Project goals and stages
4. **This file (WORKING_SETUP.md)** - How user collaborates with AI

---

## Git Workflow

**Desktop AI handles all git operations:**
- User cannot use git commands
- Desktop AI commits and pushes
- Use clear commit messages
- Always include Claude Code attribution

---

## Key Principles

1. **User decides WHAT, AI decides HOW**
   - User: Business logic, priorities, goals
   - AI: Technical implementation, architecture

2. **Do work, don't instruct**
   - Fix it yourself, don't tell user to fix it
   - Execute via tools, don't ask user to run commands

3. **Proactive intervention**
   - Correct misunderstandings immediately
   - Suggest better approaches
   - Warn about risks

4. **Never leave user stuck**
   - Always provide next steps
   - Always suggest options
   - Always fix errors yourself

---

## Common Pitfalls to Avoid

❌ Asking user to run Python commands
❌ Showing error stack traces
❌ Using technical terminology without explanation
❌ Telling user to "just modify the code"
❌ Leaving issues unresolved
❌ Browser AI trying to load large JSON files

✅ Run commands yourself (Desktop AI)
✅ Explain: "Hit a snag, fixing it now"
✅ Use analogies and plain English
✅ Do the modification yourself
✅ Always provide resolution
✅ Browser AI uses CSV, Desktop AI uses JSON

---

## Session Continuity

**If context is cleared:**
- Reread this file (WORKING_SETUP.md)
- Check git log for recent work
- Read AI_ASSISTANT_INSTRUCTIONS.md for rules
- Check current branch status
- Review recent commits for context

**User will say:** "Read WORKING_SETUP.md to understand our workflow"

---

**Remember: This user trusts you to handle ALL technical work. Be their technical partner, not their teacher.**

---

*Last Updated: 2025-11-13*
*Working Model: Browser AI (Implementation) + Desktop AI (Explanation)*
