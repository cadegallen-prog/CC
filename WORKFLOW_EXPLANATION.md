# Project Workflow Explanation

## The Real Goal

This project is about identifying **what each product actually is** so they can later be categorized properly.

---

## Two-Stage Process

### Stage 1: Product Type Identification (CURRENT FOCUS)

**Goal:** Look at each of the 425 products and figure out what it IS.

**Input:** [data/scraped_data_output.json](data/scraped_data_output.json) - 425 Home Depot products with:
- Product titles
- Descriptions
- Prices
- Ratings
- Images
- Specifications
- And more

**Output:** Each product gets identified as its actual product type.

**Examples:**
- Product with title "Hampton Bay 52-inch Ceiling Fan" → Identified as: **"ceiling fan"**
- Product with title "EcoSmart 60W LED Bulb" → Identified as: **"LED light bulb"**
- Product with title "Orbit 50ft Garden Hose" → Identified as: **"garden hose"**

**Why this matters:**
You need to know what something IS before you can properly categorize it. A vague product title like "Hampton Bay Altura" doesn't tell you it's a ceiling fan - the system needs to figure that out from the description, specs, and other data.

---

### Stage 2: Taxonomy Mapping (ON BACKBURNER - FOR LATER)

**Goal:** Take the identified product types and assign them to Facebook's category system.

**Input:**
- The identified product types from Stage 1
- [data/taxonomy_paths.txt](data/taxonomy_paths.txt) - Facebook's 373 category paths

**Output:** Each identified product gets mapped to the most appropriate Facebook taxonomy path.

**Example:**
- Identified product type: "ceiling fan" → Maps to: `Home & Garden > Lighting > Ceiling Fans`
- Identified product type: "LED bulb" → Maps to: `Home & Garden > Lighting > Light Bulbs`

**Why it's on the backburner:**
This is the second step. You can't map products to categories until you first know what they are.

---

## Visual Workflow

```
┌─────────────────────────────────────┐
│  data/scraped_data_output.json      │
│  (425 Home Depot products)          │
│                                     │
│  - Titles (sometimes vague)         │
│  - Descriptions                     │
│  - Specs                            │
│  - Prices, ratings, images, etc.   │
└──────────────┬──────────────────────┘
               │
               │ STAGE 1 (NOW)
               │ Product Type Identification
               ▼
┌─────────────────────────────────────┐
│  Identified Product Types           │
│                                     │
│  Product #1: "ceiling fan"          │
│  Product #2: "LED bulb"             │
│  Product #3: "garden hose"          │
│  ... (all 425 products identified)  │
└──────────────┬──────────────────────┘
               │
               │ STAGE 2 (LATER)
               │ Taxonomy Mapping
               ▼
┌─────────────────────────────────────┐
│  Mapped to Facebook Taxonomy        │
│                                     │
│  Product #1 → Home & Garden >       │
│               Lighting >            │
│               Ceiling Fans          │
│                                     │
│  Product #2 → Home & Garden >       │
│               Lighting >            │
│               Light Bulbs           │
│                                     │
│  (Uses taxonomy_paths.txt)          │
└─────────────────────────────────────┘
```

---

## Why Two Stages?

**Problem:** Product titles are often unclear or incomplete.
- "Hampton Bay Altura 68" - Is that a ceiling fan? A light fixture? Something else?
- "EcoSmart A19" - What even is that?

**Solution:**
1. First, use ALL available data (title + description + specs + everything) to identify the actual product type
2. Then, once you know what it is, map it to the appropriate category

**Bad approach (skip Stage 1):**
Try to map "Hampton Bay Altura 68" directly to a category → Fail, because we don't know what it is

**Good approach (two stages):**
1. Analyze "Hampton Bay Altura 68" + its description + specs → Identify as "ceiling fan"
2. Map "ceiling fan" → `Home & Garden > Lighting > Ceiling Fans` → Success!

---

## Data Files Explained

### data/scraped_data_output.json (THE MAIN DATA)
**What it is:** 425 Home Depot products with complete details

**Used for:** Stage 1 - Figuring out what each product is

**Contains:**
- `item_id` - Unique product ID
- `title` - Product name (sometimes unclear)
- `description` - Full product description (helpful!)
- `price` - Current price
- `rating` - Customer rating
- `rating_count` - Number of reviews
- `image_url` - Product photo
- `specs` - Technical specifications (very helpful!)
- `additional_details` - Extra info
- And more...

### data/taxonomy_paths.txt (FOR LATER)
**What it is:** Facebook's 373 category paths

**Used for:** Stage 2 - Mapping identified products to categories

**Contains:** Hierarchical category paths like:
- `Animals & Pet Supplies > Pet Supplies > Dog Supplies`
- `Home & Garden > Kitchen & Dining > Cookware & Bakeware`
- `Electronics > Computers > Computer Components`

**Current status:** On the backburner. Not needed until Stage 1 is complete.

---

## Current Priority

**Focus on Stage 1:** Build a system that can look at each product's data and identify what type of product it is.

**Don't worry about Stage 2 yet:** The Facebook taxonomy mapping is for later.

---

## Key Takeaway

**What the project is NOT:**
❌ "Classify 425 products into 373 categories"

**What the project IS:**
✅ "Identify what each of 425 products actually is (their product type)"
✅ "Then later, map those identified types to Facebook's 373 taxonomy"

---

## For AI Assistants

When this user talks about:
- **"Product type identification"** → They mean Stage 1 (current focus)
- **"The taxonomy"** or **"373 categories"** → They mean Stage 2 (backburner)
- **"What this product is"** → They want to know the actual product type
- **"Mapping to categories"** → That's Stage 2, for later

**Current work should focus on:** Analyzing product data to determine product types
**Current work should NOT focus on:** Matching to Facebook taxonomy (that's later)
