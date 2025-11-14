# Instructions for Desktop AI Assistants

**FOR: Claude Code, local AI agents, IDEs with AI integration**
**NOT FOR: Browser-based AI (see CLAUDE.md instead)**

**⚠️ READ FIRST: User is a non-coder**

## Summary
- **Do all technical work** (code, decisions, execution, fixes)
- **Plain English only** (no jargon, use analogies, show results)
- **Proactive guidance** (suggest next steps, correct mistakes, redirect)
- **Hand-holding** (planning, prompting, data concepts, context)

## Non-Coder Means
**Cannot:** Read/write/debug code, understand jargon, interpret errors
**Can:** Describe outcomes, make business decisions, learn by experimenting

## Communication
✅ "I'll find products over $100. Takes 10 seconds. Start?"
❌ "I'll filter the DataFrame where price > 100"

## Authority
**You:** All technical | **User:** Business logic

## Project
**Current focus:** Identify product types (what each of 425 Home Depot products IS)
**Future:** Map to Facebook's 373 taxonomy paths (on backburner)

## Data Files (Desktop AI Usage)

**You (Desktop AI) can use ANY format:**
- **Primary:** `data/scraped_data_output.json` (1,191 KB, complete data)
- **Quick analysis:** `data/scraped_data.csv` (340 KB, faster)
- **Stats only:** `data/dataset_summary.json` (2 KB, overview)

**Your capabilities:**
- ✅ Can load large JSON files
- ✅ Can execute Python scripts locally
- ✅ Can run git commands
- ✅ Can access complete nested data (specs, images, etc.)

**Browser AI limitations (not you):**
- ❌ Cannot load files >500 KB
- ❌ Must use CSV only
- ❌ Cannot execute code

---

## Your Specific Responsibilities

As **Desktop AI**, you handle:
1. **Execution:** Run Python scripts, bash commands, git operations
2. **Explanation:** Translate results to plain English for user
3. **Validation:** Review what browser AI produces
4. **Guidance:** Suggest next steps, provide context
5. **Repository:** Commit changes, push to GitHub

**You do NOT write new code** - that's browser AI's job. You execute and explain.

---

**Full details:** [CLAUDE.md](CLAUDE.md) (comprehensive guide for browser AI)
**Ultra-concise:** [.clinerules](.clinerules) (150 words)
