# Context-Aware Negative Keyword Algorithm Design

## Problem Statement

Current negative keyword matching is **naive string matching** that causes false positives:
- "Chandelier LED Light Bulb" blocked by "chandelier" negative keyword
- Product IS a bulb FOR chandeliers, NOT a chandelier fixture
- Need to distinguish USE CASE mentions from PRODUCT TYPE mentions

## Core Insight: Noun Phrase Structure

### False Positive Pattern
```
[FIXTURE_TYPE MODIFIER] + [PRODUCT_TYPE HEAD_NOUN]
"Chandelier" + "LED Light Bulb" = Bulb FOR chandeliers (BULB is the product)
```

### True Block Pattern
```
[PRODUCT_TYPE HEAD_NOUN] + [optional modifiers]
"Chandelier" + "with LED bulbs" = Chandelier fixture (CHANDELIER is the product)
```

## Algorithm Components

### 1. Product Type Strong Keywords
Identify what the product ACTUALLY IS by checking for strong keywords:
- LED Light Bulb: "light bulb", "led bulb", "lamp bulb"
- Ceiling Fan: "ceiling fan"
- Door Lock: "door lock", "deadbolt"

### 2. Modifier Position Analysis
Check WHERE the negative keyword appears relative to product type keywords:

**Pattern A: Modifier + Product Type (FALSE POSITIVE)**
```
"Chandelier LED Light Bulb"
         ↑        ↑
   modifier   product_type

RULE: Don't block - negative keyword is DESCRIBING what product is FOR
```

**Pattern B: Product Type + Accessory Mention (TRUE BLOCK)**
```
"Chandelier with bulbs included"
     ↑              ↑
product_type   accessory_mention

RULE: Block - negative keyword IS the product type
```

### 3. Prepositional Phrase Detection
Identify use case mentions via prepositions:
- "for [fixture]" → use case
- "compatible with [fixture]" → use case
- "replacement for [fixture]" → use case
- "works with [fixture]" → use case

### 4. N-gram Context Windows
Analyze words immediately adjacent to negative keyword:

**False Positive Indicators (words appearing AFTER negative keyword):**
- "chandelier **bulb**" → bulb for chandelier
- "ceiling fan **light**" → light for ceiling fan
- "pendant **led**" → LED for pendant

**True Block Indicators (words appearing AFTER negative keyword):**
- "chandelier **with**" → chandelier fixture
- "chandelier **features**" → chandelier fixture
- "chandelier **includes**" → chandelier fixture

### 5. Semantic Role Classification
Classify negative keyword's role:
- **MODIFIER**: Describes what product is FOR → don't block
- **HEAD_NOUN**: Describes what product IS → block
- **ACCESSORY**: Mentioned as included component → depends on context

## Implementation Strategy

### Phase 1: Pattern-Based Rules (Immediate Fix)
Implement heuristic rules based on observed patterns:

```python
def is_false_positive_block(text, negative_kw, pattern):
    """
    Determine if negative keyword match is a false positive
    Returns True if we should NOT block (false positive detected)
    """

    # Rule 1: Product Type After Negative Keyword
    # "chandelier led bulb" - bulb is after chandelier
    for strong_kw in pattern['strong_keywords']:
        # Check if strong keyword appears AFTER negative keyword
        if f"{negative_kw} {strong_kw}" in text:
            return True  # False positive - don't block

        # Check with intervening words (window of 3 words)
        words = text.split()
        for i, word in enumerate(words):
            if negative_kw in word:
                # Check next 3 words for strong keyword
                window = ' '.join(words[i:i+4])
                if any(strong_kw in window for strong_kw in pattern['strong_keywords']):
                    return True  # False positive

    # Rule 2: Prepositional Phrases
    prep_phrases = [
        f"for {negative_kw}",
        f"for use with {negative_kw}",
        f"compatible with {negative_kw}",
        f"replacement for {negative_kw}",
    ]
    if any(phrase in text for phrase in prep_phrases):
        return True  # Use case mention - don't block

    # Rule 3: Compound Product Type Names
    # "chandelier bulb", "pendant bulb", "sconce bulb"
    compound_patterns = [
        f"{negative_kw} bulb",
        f"{negative_kw} led",
        f"{negative_kw} light bulb",
        f"{negative_kw} lamp",
    ]
    if any(compound in text for compound in compound_patterns):
        return True  # Product type compound - don't block

    # Rule 4: Integrated Products (e.g., "faucet with drain")
    # If product has strong keyword AND negative keyword, check if integrated
    has_strong_keyword = any(
        classifier.contains_keyword(text, kw)
        for kw in pattern['strong_keywords']
    )

    if has_strong_keyword:
        # Check if negative keyword is describing included component
        inclusion_patterns = [
            f"includes {negative_kw}",
            f"with {negative_kw}",
            f"features {negative_kw}",
        ]
        if any(pattern in text for pattern in inclusion_patterns):
            # Integrated product - depends on whether neg_kw is main product
            # If strong keyword is in TITLE, product is the strong keyword type
            return True  # Don't block

    return False  # Not a false positive - proceed with block
```

### Phase 2: Expanded Context Rules (Enhancement)
Add more sophisticated pattern matching:

1. **Bidirectional Context Windows**: Check words both before AND after
2. **Position Weighting**: Keywords in title carry more weight
3. **Phrase Templates**: Pre-defined templates for common patterns
4. **Exception Lists**: Known edge cases

### Phase 3: ML-Based (Future Consideration)
For scaling to 1000s of products:
- Named Entity Recognition (NER) for product types
- Dependency parsing for grammatical relationships
- Trained classifier for modifier vs head noun detection

## Pattern-Specific Rules

### Lighting Fixtures vs Bulbs
**Problem**: "Chandelier LED Light Bulb" blocked by chandelier pattern

**Solution**:
```python
# For fixture-type negative keywords in bulb patterns
FIXTURE_KEYWORDS = ['chandelier', 'sconce', 'pendant', 'ceiling fan']

if negative_kw in FIXTURE_KEYWORDS:
    # Check if it's a bulb FOR that fixture
    bulb_indicators = ['bulb', 'led bulb', 'light bulb', 'lamp']

    # Pattern: [fixture] [bulb_indicator]
    for bulb_word in bulb_indicators:
        if f"{negative_kw} {bulb_word}" in text:
            return True  # False positive - it's a bulb FOR fixture

        # With intervening words: "chandelier led light bulb"
        pattern = rf"{negative_kw}\s+\w*\s*{bulb_word}"
        if re.search(pattern, text):
            return True  # False positive
```

### Integrated Components vs Standalone
**Problem**: "Faucet with drain" blocked by faucet pattern's "drain" negative keyword

**Solution**:
```python
# If product clearly has the strong keyword, negative keyword is likely a component
if has_strong_keyword_in_title:
    # Check if negative keyword is mentioned as included component
    if f"with {negative_kw}" in text or f"includes {negative_kw}" in text:
        return True  # Integrated component - don't block
```

### Accessories vs Products
**Problem**: "Door handle set with knob" blocked by door handle pattern's "knob" negative keyword

**Solution**:
```python
# If strong keyword appears first in title, it's the primary product
title_words = title.split()
strong_kw_position = None
neg_kw_position = None

for i, word in enumerate(title_words):
    if strong_keyword in ' '.join(title_words[i:i+3]):
        strong_kw_position = i
    if negative_kw in word:
        neg_kw_position = i

if strong_kw_position is not None and neg_kw_position is not None:
    if strong_kw_position < neg_kw_position:
        # Strong keyword comes first - it's the main product
        return True  # Don't block
```

## Test Cases

### Should NOT Block (False Positives to Fix)
1. ✓ "Chandelier LED Light Bulb" - bulb FOR chandelier
2. ✓ "Ceiling Fan Light Bulb" - bulb FOR ceiling fan
3. ✓ "Pendant Light Bulb" - bulb FOR pendant
4. ✓ "Faucet with Push & Seal Drain" - faucet WITH drain included
5. ✓ "Door Handle Set with Georgian Knob" - handle set WITH knob option
6. ✓ "Dimmer Switch for LED and Incandescent Bulbs" - switch FOR bulbs
7. ✓ "Vanity Top for 37-inch Vanity Cabinet" - vanity top FOR cabinet
8. ✓ "Paint Sprayer" tested against Paint pattern - sprayer IS the product

### Should Block (True Blocks to Preserve)
1. ✓ "Crystal Chandelier with LED Bulbs" - blocked by LED Light Bulb pattern
2. ✓ "Pendant Light Fixture" - blocked by LED Light Bulb pattern
3. ✓ "Wall Sconce Light Fixture" - blocked by LED Light Bulb pattern
4. ✓ "LED Light Switch" - blocked by LED Light Bulb pattern
5. ✓ "Ceiling Fan with Light Kit" - blocked by LED Light Bulb pattern

## Edge Cases

### 1. Multi-Function Products
"Ceiling Fan with Light and Remote Control"
- Is it a ceiling fan? Yes (strong keyword in title)
- Does it have a light? Yes (integrated component)
- Should "light" negative keyword block it from "light bulb" pattern? Yes
- Should it match "ceiling fan" pattern? Yes

### 2. Replacement Parts
"Chandelier Replacement Glass Shade"
- Is it a chandelier? No
- Is it FOR a chandelier? Yes
- What is it actually? Glass shade (replacement part)
- Should "chandelier" block it? No (it's a use case mention)

### 3. Compatible Accessories
"LED Bulbs Compatible with Chandeliers and Sconces"
- Is it a bulb? Yes
- Is it for chandeliers? Yes (compatible with)
- Should "chandelier" block it from bulb pattern? No

## Success Metrics

After implementation, expect:
- **False positive blocks**: 73 → 0
- **Classification accuracy**: 81.4% → 90%+ (fixing just the negative keyword logic)
- **Unknown products**: Reduced as previously blocked products now match correctly
- **True block preservation**: 1205 correct blocks maintained

## Implementation Priority

1. **Immediate**: Fix fixture-type keywords in lighting products (chandelier, sconce, pendant)
2. **High**: Fix integrated components (drain, switch, etc.)
3. **Medium**: Fix accessory mentions (tool, sprayer, etc.)
4. **Low**: Edge cases and multi-function products
