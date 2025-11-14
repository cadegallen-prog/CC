# Ground Truth Sampling Bias Analysis Report

**Analysis Date:** 2025-11-14
**Ground Truth Size:** 48 samples
**Full Dataset Size:** 425 products
**Sampling Ratio:** 1:8.9

---

## Executive Summary

The ground truth sample exhibits **significant sampling bias** and is **NOT properly stratified**. The statistical analysis reveals:

- **Chi-square statistic:** 61.85 (df=9) - indicates substantial deviation from expected distribution
- **KL Divergence:** 0.3957 - shows meaningful divergence between distributions
- **Stratification:** NOT stratified (chi-square > 20 threshold)
- **Missing Types:** 23 product types completely missing from ground truth
- **Coverage:** Ground truth covers only 41 of 51 unique product types (80.4%)

---

## Domain Distribution Comparison

| Domain | Ground Truth | Full Dataset | Difference | Status |
|--------|-------------|--------------|------------|--------|
| **Other** | 16.67% (8) | 46.59% (198) | **-29.9%** | **SEVERELY UNDER** |
| **Hardware** | 10.42% (5) | 1.41% (6) | **+9.0%** | **OVER** |
| **Safety/PPE** | 10.42% (5) | 2.59% (11) | **+7.8%** | **OVER** |
| **Tools** | 12.50% (6) | 5.18% (22) | **+7.3%** | **OVER** |
| Lighting | 20.83% (10) | 20.47% (87) | +0.4% | Balanced |
| Electrical | 14.58% (7) | 11.53% (49) | +3.1% | Balanced |
| Plumbing | 8.33% (4) | 9.41% (40) | -1.1% | Balanced |
| HVAC | 2.08% (1) | 1.88% (8) | +0.2% | Balanced |
| Home & Decor | 4.17% (2) | 0.71% (3) | +3.5% | Balanced |
| Paint | 0.00% (0) | 0.24% (1) | -0.2% | Balanced |

---

## Critical Issues Identified

### 1. "Other" Category Severely Under-Represented (-29.9%)
- **Ground Truth:** 16.67% (8 samples)
- **Full Dataset:** 46.59% (198 products)
- **Impact:** Nearly HALF of the dataset falls into "Other" but only 17% of ground truth
- **Missing:** 165 "Unknown - Unable to Classify" products (38.8% of full dataset!)

### 2. Tools Domain Over-Represented (+7.3%)
- Ground truth has 2.4x more tool samples than expected
- Examples: Multi-position ladder, SDS rebar cutter, hex driver bits, chainsaw tune-up kit

### 3. Safety/PPE Domain Over-Represented (+7.8%)
- Ground truth has 4x more safety samples than expected
- Examples: Disposable earplugs (2 samples), respirator cartridge, work gloves

### 4. Hardware Domain Over-Represented (+9.0%)
- Ground truth has 7.4x more hardware samples than expected
- Examples: Shelf brackets, stair nosing trim, curtain rod, velcro tape

---

## Top Missing Product Types (>5 occurrences in dataset)

| Rank | Product Type | Full Dataset | Domain | Status |
|------|-------------|--------------|--------|--------|
| 1 | **Unknown - Unable to Classify** | 165 (38.8%) | Other | Missing |
| 2 | **Recessed Light** | 23 (5.4%) | Lighting | Missing |
| 3 | **LED Light Bulb** | 17 (4.0%) | Lighting | Missing |
| 4 | **Circuit Breaker** | 17 (4.0%) | Electrical | Missing |
| 5 | Load Center | 11 (2.6%) | Electrical | Missing |
| 6 | Unknown - Missing Data | 10 (2.4%) | Other | Missing |
| 7 | Light Switch | 9 (2.1%) | Lighting | Missing |
| 8 | Faucet | 9 (2.1%) | Plumbing | Missing |
| 9 | Electrical Outlet | 9 (2.1%) | Electrical | Missing |
| 10 | Work Gloves | 9 (2.1%) | Safety/PPE | Missing |
| 11 | Wire | 8 (1.9%) | Electrical | Missing |
| 12 | Saw | 8 (1.9%) | Tools | Missing |
| 13 | Toilet | 8 (1.9%) | Plumbing | Missing |
| 14 | Plumbing Fitting | 7 (1.7%) | Plumbing | Missing |
| 15 | Exhaust Fan | 7 (1.7%) | HVAC | Missing |
| 16 | Track Lighting | 6 (1.4%) | Lighting | Missing |
| 17 | Under Cabinet Light | 6 (1.4%) | Lighting | Missing |
| 18 | Pendant Light | 6 (1.4%) | Lighting | Missing |
| 19 | Skylight | 6 (1.4%) | Lighting | Missing |
| 20 | Saw Blade | 5 (1.2%) | Tools | Missing |
| 21 | Tape | 5 (1.2%) | Other | Missing |
| 22 | Drain | 5 (1.2%) | Plumbing | Missing |

**Total: 23 completely missing product types representing 92.5% of the full dataset**

---

## Statistical Analysis

### Expected vs. Actual Distribution

Based on the full dataset distribution, the ground truth SHOULD have contained:

| Domain | Expected Count | Actual Count | Deviation |
|--------|---------------|--------------|-----------|
| Other | 22.4 | 8 | -14.4 |
| Lighting | 9.8 | 10 | +0.2 |
| Electrical | 5.5 | 7 | +1.5 |
| Plumbing | 4.5 | 4 | -0.5 |
| Tools | 2.5 | 6 | +3.5 |
| HVAC | 0.9 | 1 | +0.1 |
| Hardware | 0.7 | 5 | +4.3 |
| Safety/PPE | 1.2 | 5 | +3.8 |
| Home & Decor | 0.3 | 2 | +1.7 |
| Paint | 0.1 | 0 | -0.1 |

---

## Recommendations

### HIGH PRIORITY

1. **Drastically Reduce Over-Sampled Domains:**
   - **Tools:** Reduce from 12.5% to ~5% (remove 3-4 samples)
   - **Safety/PPE:** Reduce from 10.4% to ~3% (remove 3-4 samples)
   - **Hardware:** Reduce from 10.4% to ~1% (remove 4 samples)

2. **Massively Increase "Other" Category:**
   - Increase from 16.7% to ~47% (add 14-15 samples)
   - CRITICAL: Add samples of "Unknown - Unable to Classify" products
   - These are the hardest to classify and MUST be in ground truth

### MEDIUM PRIORITY

3. **Add Common Product Types Missing from Ground Truth:**
   - **Lighting:** Recessed Light (23 in dataset), LED Light Bulb (17), Light Switch (9)
   - **Electrical:** Circuit Breaker (17), Load Center (11), Electrical Outlet (9)
   - **Plumbing:** Faucet (9), Toilet (8), Drain (5)
   - **Tools:** Saw (8), Saw Blade (5)

4. **Implement Proportional Stratified Sampling:**
   - Sample each domain in proportion to its frequency in full dataset
   - Formula: `samples_needed = (domain_count / total_products) * target_sample_size`
   - For 48 samples:
     - Other: 22 samples (46.6%)
     - Lighting: 10 samples (20.5%)
     - Electrical: 6 samples (11.5%)
     - Plumbing: 5 samples (9.4%)
     - Tools: 2-3 samples (5.2%)
     - Safety/PPE: 1-2 samples (2.6%)
     - HVAC: 1 sample (1.9%)
     - Hardware: 1 sample (1.4%)

5. **Reduce Edge Cases:**
   - Currently 4 "missing_data" edge cases (8.3% of ground truth)
   - These should be <5% of sample
   - Replace with representative real-world products

### LOW PRIORITY

6. **Balance Specific Product Type Coverage:**
   - Ensure major product types (>2% of dataset) have at least 1-2 samples
   - This ensures classifier can learn from actual examples

---

## Impact Assessment

### Current Ground Truth Problems:

1. **Poor Generalization:** Over-emphasis on specialized products (tools, hardware, safety gear) means classifier may be over-tuned for rare cases
2. **Missing Common Cases:** Most common products (LED bulbs, circuit breakers, outlets, faucets) completely missing
3. **"Other" Category:** Classifier has almost NO training data for ambiguous/hard-to-classify products (47% of dataset!)
4. **Bias Toward Complex Products:** Ground truth favors niche, specific products over common, simple ones

### Expected Improvements After Re-Sampling:

- **Better classifier accuracy** on common product types
- **Reduced false confidence** on ambiguous products
- **More realistic performance metrics** that reflect actual dataset composition
- **Improved handling** of "Unknown" classifications

---

## Action Plan

### Immediate Actions:

1. **Remove 10-12 samples** from over-represented categories (Tools, Safety/PPE, Hardware)
2. **Add 10-12 samples** from "Other" category, especially:
   - Products that classifier marked as "Unknown - Unable to Classify"
   - Ambiguous products that could fall into multiple categories
   - Products with minimal/missing descriptions

### Next Steps:

3. **Add samples for top missing types:**
   - At least 2-3 LED Light Bulb samples
   - At least 2-3 Recessed Light samples
   - At least 2 Circuit Breaker samples
   - At least 1-2 Faucet samples

4. **Validate new ground truth:**
   - Re-run this bias analysis script
   - Target chi-square < 20 for "stratified" classification
   - Ensure no domain has >5% deviation from expected

---

## Files Generated

1. **/home/user/CC/outputs/ground_truth_bias_analysis.json** - Complete analysis with all metrics
2. **/home/user/CC/outputs/bias_analysis_summary.md** - This summary report
3. **/home/user/CC/analyze_sampling_bias.py** - Reusable analysis script

---

## Conclusion

The current ground truth sample has **significant sampling bias** that will negatively impact classifier training and validation. The most critical issue is the severe under-representation of the "Other" category, which constitutes nearly half of the full dataset but only 17% of ground truth.

**The ground truth needs substantial revision** to properly represent the full dataset distribution. Following the recommendations above will create a more balanced, representative sample that will yield more accurate and reliable classifier performance metrics.
