# README for AI Assistants

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

## Data Files (Use Right Format!)
- **Browser AI?** → Use `data/scraped_data.csv` (340 KB, 71% smaller)
- **Desktop AI?** → Use `data/scraped_data_output.json` (1,191 KB, complete)
- **Just stats?** → Use `data/dataset_summary.json` (2 KB, overview)

**Why CSV for browsers:** Large JSON files choke browser-based AI. CSV has everything needed for classification (title, description, brand, price) in a fraction of the size.

---

**Details:** [AI_ASSISTANT_INSTRUCTIONS.md](AI_ASSISTANT_INSTRUCTIONS.md) (650 words)
**Ultra-concise:** [.clinerules](.clinerules) (150 words)
