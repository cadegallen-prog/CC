# Prioritized Classifier Fixes
## Based on Comprehensive Accuracy Audit

**Current Performance:** 61.7% accuracy on ground truth
**Target:** 95%+ accuracy
**Gap:** 33.3 percentage points

---

## CRITICAL FIXES (Implement First - High Impact)

### 1. **Fix Text Normalization** (Impact: ~15-20% accuracy gain)
**Problem:** Hyphens and special characters prevent keyword matching
- "mini-pendant" in pattern doesn't match "Mini Pendant" in title
- "1-Light" creates word boundary issues

**Fix:** Normalize hyphens to spaces and handle special characters
```python
def normalize_text(self, text: str) -> str:
    if not text:
        return ""
    # Replace hyphens with spaces
    text = text.replace('-', ' ')
    # Replace slashes with spaces
    text = text.replace('/', ' ')
    # Convert to lowercase and remove extra spaces
    return " ".join(text.lower().split())
```

**Products Fixed:** Mini pendants, multi-position ladders, double-hung windows, etc.

---

### 2. **Fix Negative Keyword Logic** (Impact: ~10-15% accuracy gain)
**Problem:** Negative keywords blocking valid products
- "Wall Sconce with Switch" blocked by 'switch' keyword
- Context-insensitive blocking

**Fix:** Implement context-aware negative keyword matching
- Only block if negative keyword is the PRIMARY subject, not an accessory
- "sconce with switch" = sconce (valid)
- "switch plate" = not a sconce (block)

**Products Fixed:** 10+ wall sconces, other fixtures with accessories

---

### 3. **Add Missing Product Type Patterns** (Impact: ~10% accuracy gain)
**Problem:** 32 product types in ground truth but missing from classifier

**Patterns to Add (Priority Order):**
1. **Recessed Light Fixture** - Currently exists as "Recessed Light" but ground truth uses different name
2. **Mini Pendant Light** - Exists as "Pendant Light" but needs separate pattern
3. **LED Troffer Light** - Exists as "Troffer Light" but needs LED variant
4. **USB Outlet** / **GFCI USB Outlet** - Currently just "Electrical Outlet"
5. **Smart Deadbolt Lock** - Currently just "Door Lock"
6. **Surge Protector with USB** - Currently just "Surge Protector"
7. **Under Cabinet LED Light** - Exists but needs better keywords
8. **Landscape Flood Light** - Exists as "Landscape Lighting" but needs specific pattern
9. **Bathroom Exhaust Fan** - Exists as "Exhaust Fan" but needs specific pattern
10. **Double Hung Window** - Exists as "Window" but needs specific pattern

**Fix:** Add pattern aliases or rename existing patterns to match ground truth terminology

---

## HIGH-PRIORITY FIXES (Significant Impact)

### 4. **Improve Scoring Calibration** (Impact: ~5-10% accuracy gain)
**Problem:** Some obvious matches get low scores
- Products with exact keyword matches scoring under 80%
- Weak keyword scoring too high relative to strong keywords

**Fix:**
- Increase title strong keyword match from 80 to 90 points
- Add bonus for exact pattern name match (e.g., "LED Light Bulb" = pattern name)
- Reduce weak keyword max from 30 to 20 points
- Add multi-keyword bonus (if 3+ strong keywords match, +10 bonus)

---

### 5. **Fix Word Boundary Matching** (Impact: ~3-5% accuracy gain)
**Problem:** Some single-word keywords have false matches

**Current Issue:**
- "brush" matches "brushed nickel" (false positive)

**Fix:** Improve `contains_keyword()` to handle edge cases better

---

## MEDIUM-PRIORITY FIXES (Moderate Impact)

### 6. **Add Product Type Variants** (Impact: ~2-5% accuracy gain)
**Problem:** Many ground truth types are just variants of existing patterns

**Solution:** Add equivalence mapping
- "recessed_light_fixture" = "Recessed Light"
- "led_troffer_light" = "Troffer Light"
- "double_hung_window" = "Window"

This way we can match ground truth terminology without creating duplicate patterns.

---

### 7. **Improve Unknown Classification Threshold** (Impact: ~3-5% accuracy gain)
**Problem:** 70 products classified as Unknown (16.5%)
- Many have weak matches (10-15 points) that could be improved
- Threshold of 15 points may be too high

**Fix:**
- Lower unknown threshold from 15 to 12 points
- Improve patterns for commonly unknown categories:
  - Area rugs
  - Wall mirrors
  - Flexible conduit
  - Specialty tools (sanding sheets, specialty pliers)
  - Furniture (folding tables)

---

## LOW-PRIORITY FIXES (Polish)

### 8. **Add Disambiguation Logic** (Impact: ~1-2% accuracy gain)
**Problem:** Some products could match multiple types

**Example:** "Replacement Blade"
- Could be saw blade, lawn mower blade, roofing shovel blade, etc.

**Fix:** Add disambiguation based on additional context keywords
- Check description for usage context
- Check brand (DIABLO = saw blades, Anvil = roofing)

---

### 9. **Improve Confidence Score Distribution** (Impact: Quality of life)
**Problem:** Too many products at extremes (277 high, 79 very low)
- Better calibration would spread scores more evenly

**Fix:** Recalibrate scoring formula after implementing fixes #1-7

---

## IMPLEMENTATION PRIORITY

**Phase 1** (Implement now - 40-45% accuracy gain):
1. Fix text normalization (#1)
2. Fix negative keyword logic (#2)
3. Add missing patterns (#3)
4. Improve scoring calibration (#4)

**Phase 2** (After Phase 1 validation - 8-15% additional gain):
5. Fix word boundary matching (#5)
6. Add product type variants (#6)
7. Improve unknown threshold (#7)

**Phase 3** (Polish - 1-3% additional gain):
8. Add disambiguation logic (#8)
9. Improve confidence distribution (#9)

---

## PROJECTED ACCURACY AFTER FIXES

| Phase | Fixes Applied | Projected Accuracy | Confidence |
|-------|--------------|-------------------|------------|
| Current | None | 61.7% | Actual |
| Phase 1 | #1-4 | 88-92% | High |
| Phase 2 | #1-7 | 93-96% | High |
| Phase 3 | #1-9 | 95-97% | Medium |

**Target:** 95%+ accuracy achievable with Phase 1 + Phase 2 implementation

---

## SPECIFIC PATTERNS TO ADD/FIX

### Patterns Needing Renaming (to match ground truth):
- "Recessed Light" → "Recessed Light Fixture"
- "Troffer Light" → "LED Troffer Light"
- "Window" → Add "Double Hung Window" variant
- "Door Lock" → Add "Smart Deadbolt Lock" variant

### New Patterns Needed:
- **Roofing Shovel Blade** - Different from saw blade
- **Stair Nosing Trim** - Floor transition trim
- **Speaker Wall Mount** - Different from light brackets
- **Sanding Sheet/Pad** - Sandpaper accessories
- **Flexible Conduit** - Electrical conduit
- **Wall Mirror** - Bathroom/vanity mirrors
- **Area Rug** - Home decor rugs
- **Folding Table** - Utility furniture

---

## SUCCESS CRITERIA

After implementing all fixes:
- ✅ Ground truth accuracy ≥ 95%
- ✅ Unknown products < 5% (currently 16.5%)
- ✅ No high-confidence wrong predictions (currently 15)
- ✅ Confidence score calibration improved (better distribution)
- ✅ All ground truth product types have patterns

---

**Status:** Ready for implementation
**Estimated Effort:** 2-3 hours for Phase 1 + Phase 2
**Expected Outcome:** 93-96% accuracy
