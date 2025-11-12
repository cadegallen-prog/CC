# Product Type Identifier → Taxonomy Mapping Strategy

## Overview
This document specifies the bridge between organically discovered product-type identifiers (derived from scraped data) and the canonical taxonomy defined in `data/taxonomy_paths.txt`. The design ensures version control, auditability, and deterministic mapping while maintaining the >=98% accuracy requirement.

---

## 1. ARCHITECTURE

### 1.1 Versioning System for Organic Identifiers

#### Identifier Format
Each organic identifier is a data-derived label extracted from product titles, descriptions, and attributes.

**Structure:**
```
{
  "identifier_id": "uuid-v4",
  "identifier_name": "LED Chandelier Light Bulb",
  "version": "1.0.0",
  "created_at": "2025-11-12T10:30:00Z",
  "source_signals": {
    "title_keywords": ["LED", "Chandelier", "Light Bulb"],
    "description_keywords": ["bulb", "chandelier", "sconce", "E26"],
    "brand": "Feit Electric",
    "attributes": {
      "base_type": "B10",
      "wattage": 5.5,
      "lumens": 500
    }
  },
  "sample_skus": ["1010398944", "..."],
  "occurrence_count": 42
}
```

**Versioning Scheme (Semantic Versioning):**
- **MAJOR** (X.0.0): Breaking changes to identifier definition or taxonomy structure changes
- **MINOR** (0.X.0): New identifiers added or refinement of existing identifier scope
- **PATCH** (0.0.X): Bug fixes, typo corrections, metadata updates

**Version Tracking:**
- Store in `mapping/identifiers/versions.json` with changelog
- Each version change requires git commit with descriptive message
- Link each version to taxonomy version (taxonomy also versioned)

#### Storage Location
```
mapping/
├── identifiers/
│   ├── organic_identifiers_v1.0.0.json    # Current version
│   ├── organic_identifiers_v0.9.0.json    # Previous versions
│   ├── versions.json                       # Version changelog
│   └── discovery_metadata.json             # Discovery process metadata
├── rules/
│   ├── mapping_rules_v1.0.0.json          # Current mapping rules
│   ├── mapping_rules_v0.9.0.json          # Previous versions
│   └── rule_changelog.json                 # Rule modification history
├── confidence/
│   ├── confidence_scores.parquet          # Per-SKU confidence scores
│   └── confidence_distribution.json        # Aggregate statistics
└── audit/
    ├── mapping_audit_trail.jsonl          # Append-only audit log
    └── human_reviews.parquet              # Human review decisions
```

### 1.2 Storage Format

#### Primary Storage: JSON + Parquet Hybrid
- **Schemas and Rules**: JSON (human-readable, git-friendly)
- **Large Datasets**: Parquet (efficient, typed, DuckDB-compatible)
- **Audit Logs**: JSONL (append-only, streaming-friendly)

#### Organic Identifier Store Schema
**File:** `mapping/identifiers/organic_identifiers_v{VERSION}.json`

```json
{
  "version": "1.0.0",
  "created_at": "2025-11-12T10:30:00Z",
  "taxonomy_version": "1.0.0",
  "git_commit": "bb4e77f",
  "identifiers": [
    {
      "identifier_id": "550e8400-e29b-41d4-a716-446655440000",
      "identifier_name": "LED Chandelier Light Bulb",
      "category_type": "lighting_product",
      "discovery_method": "title_ngrams + attribute_clustering",
      "confidence_stats": {
        "mean_confidence": 0.94,
        "min_confidence": 0.82,
        "sample_size": 42
      },
      "sample_products": [
        {
          "sku": "1010398944",
          "title": "Feit Electric 60-Watt Equivalent B10 E26...",
          "match_score": 0.96
        }
      ],
      "attributes": {
        "required": ["base_type", "wattage", "lumens"],
        "optional": ["color_temp", "dimmable"]
      }
    }
  ]
}
```

#### Mapping Rules Store Schema
**File:** `mapping/rules/mapping_rules_v{VERSION}.json`

```json
{
  "version": "1.0.0",
  "created_at": "2025-11-12T10:30:00Z",
  "taxonomy_version": "1.0.0",
  "git_commit": "bb4e77f",
  "rules": [
    {
      "rule_id": "rule_001",
      "identifier_id": "550e8400-e29b-41d4-a716-446655440000",
      "identifier_name": "LED Chandelier Light Bulb",
      "taxonomy_path": "Home & Kitchen//Lamps & Lighting//Light Bulbs",
      "mapping_logic": {
        "primary_match": {
          "method": "keyword_embedding_cosine",
          "threshold": 0.85,
          "signals": ["title", "description"]
        },
        "validation_checks": [
          {
            "field": "structured_specifications.base_type",
            "condition": "exists"
          },
          {
            "field": "structured_specifications.wattage",
            "condition": "exists"
          }
        ]
      },
      "confidence_floor": 0.70,
      "human_review_threshold": 0.75,
      "validation_status": "approved",
      "approved_by": "system",
      "approved_at": "2025-11-12T10:30:00Z"
    }
  ]
}
```

---

## 2. MAPPING RULES

### 2.1 Linking Logic to taxonomy_paths.txt

#### Step 1: Candidate Generation
For each organic identifier, generate candidate taxonomy paths using:

1. **Semantic Similarity (Primary)**
   - Embed identifier name using SentenceTransformers (`all-MiniLM-L12-v2`)
   - Embed all 374 taxonomy paths
   - Compute cosine similarity
   - Select top-5 candidates with similarity >= 0.70

2. **Keyword Overlap (Secondary)**
   - Extract tokens from identifier name
   - Use RapidFuzz to fuzzy-match against taxonomy path components
   - Compute token overlap ratio
   - Boost score if brand name appears in taxonomy path

3. **Attribute-Based Filtering (Tertiary)**
   - If product has structured attributes (wattage, dimensions, material), filter candidates
   - Example: Products with "wattage" → likely "Lamps & Lighting" or "Major Appliances"

#### Step 2: Candidate Scoring
Combine scores with weighted formula:

```python
final_score = (
    0.60 * semantic_similarity +
    0.25 * keyword_overlap +
    0.15 * attribute_match
)
```

#### Step 3: Validation Rules
Before accepting a mapping, validate:

1. **Consistency Check**: Do all products with this identifier map to the same taxonomy path?
2. **Confidence Aggregation**: Is the mean confidence across all products >= 0.80?
3. **Sample Size**: Are there at least 3 products with this identifier?
4. **Taxonomy Depth**: Does the path have at least 3 levels (Department//Category//Subcategory)?

#### Step 4: Ambiguity Resolution
If multiple taxonomy paths score >= 0.80:
- Flag as **ambiguous**
- Route to human review queue
- Log all candidate paths with scores
- Require human to select canonical path

### 2.2 Confidence Thresholds

#### Per-Product Confidence Tiers

| Confidence Range | Status | Action |
|-----------------|--------|--------|
| **0.95 - 1.00** | High Confidence | Auto-approve, log for audit |
| **0.80 - 0.94** | Medium-High | Auto-approve, sample 10% for spot-check |
| **0.70 - 0.79** | Medium | Route to human review queue |
| **0.50 - 0.69** | Low | Reject mapping, flag for re-discovery |
| **< 0.50** | Very Low | Exclude from mapping, log as unmapped |

#### Aggregate Confidence Requirements (per Identifier)
For an identifier to be promoted to production:
- **Mean confidence** across all products >= 0.85
- **Minimum confidence** of any single product >= 0.70
- **Sample size** >= 5 products (or 2% of dataset, whichever is larger)
- **Taxonomy path consistency** >= 95% (same path for 95% of products)

#### Confidence Score Calculation
```python
def calculate_confidence(product, identifier, taxonomy_path):
    """
    Calculate mapping confidence for a product.

    Returns: float [0.0, 1.0]
    """
    scores = []

    # Semantic similarity between product title and taxonomy path
    title_taxonomy_sim = cosine_similarity(
        embed(product['title']),
        embed(taxonomy_path)
    )
    scores.append(('semantic', title_taxonomy_sim, 0.40))

    # Identifier match score
    identifier_match = cosine_similarity(
        embed(product['title']),
        embed(identifier['identifier_name'])
    )
    scores.append(('identifier', identifier_match, 0.30))

    # Attribute validation score
    attribute_score = validate_attributes(
        product['structured_specifications'],
        identifier['attributes']['required']
    )
    scores.append(('attributes', attribute_score, 0.20))

    # Keyword overlap with taxonomy
    keyword_score = keyword_overlap_ratio(
        product['title'] + ' ' + product['description'],
        taxonomy_path
    )
    scores.append(('keywords', keyword_score, 0.10))

    # Weighted sum
    confidence = sum(score * weight for _, score, weight in scores)

    return confidence
```

### 2.3 Human Review Triggers

#### Automatic Review Queue Triggers
Products are routed to human review when:

1. **Low Confidence**: Final confidence score in [0.70, 0.79]
2. **Ambiguous Mapping**: Multiple taxonomy paths score >= 0.80
3. **Identifier Conflict**: Product matches multiple identifiers with similar confidence
4. **New Identifier**: First 5 products for any newly discovered identifier
5. **Taxonomy Mismatch**: Identifier maps to taxonomy path with different department than expected
6. **Statistical Outlier**: Product confidence is >2 standard deviations below identifier mean

#### Review Interface Requirements
The human review tool should display:
- Product title, description, brand, model
- Structured attributes (wattage, dimensions, material, etc.)
- Proposed identifier name
- Proposed taxonomy path with confidence score
- Alternative taxonomy paths (if any)
- 3-5 similar products for context

#### Review Decisions
Reviewers can:
- **Approve** mapping (record decision + timestamp)
- **Reject** mapping (select alternate taxonomy path or flag for re-discovery)
- **Flag** for taxonomy update (if no appropriate path exists)
- **Defer** decision (request more product samples)

#### Review Tracking
Store all reviews in `mapping/audit/human_reviews.parquet`:

```python
{
    "review_id": "uuid",
    "sku": "1010398944",
    "identifier_id": "uuid",
    "proposed_taxonomy_path": "Home & Kitchen//Lamps & Lighting//Light Bulbs",
    "reviewer": "analyst_01",
    "decision": "approve",  # approve | reject | flag | defer
    "alternate_path": null,  # if reject, record chosen path
    "confidence_override": null,  # optional manual confidence
    "comments": "Clear match, all attributes present",
    "reviewed_at": "2025-11-12T11:00:00Z"
}
```

#### Quality Control
- **Inter-Rater Reliability**: 10% of reviews assigned to multiple reviewers
- **Expert Review**: Randomly sample 5% of auto-approved mappings for expert validation
- **Feedback Loop**: Track reviewer agreement rates and retrain models if agreement < 85%

---

## 3. FILE STRUCTURE

### 3.1 Proposed Directory Layout

```
product_type_identifier/
├── data/                              # [EXISTING] Source data
│   ├── taxonomy_paths.txt
│   └── scraped_data_output.json
├── mapping/                           # [NEW] Mapping artifacts
│   ├── identifiers/
│   │   ├── organic_identifiers_v1.0.0.json
│   │   ├── organic_identifiers_v0.9.0.json
│   │   ├── versions.json
│   │   └── discovery_metadata.json
│   ├── rules/
│   │   ├── mapping_rules_v1.0.0.json
│   │   ├── mapping_rules_v0.9.0.json
│   │   └── rule_changelog.json
│   ├── confidence/
│   │   ├── confidence_scores.parquet
│   │   └── confidence_distribution.json
│   └── audit/
│       ├── mapping_audit_trail.jsonl
│       └── human_reviews.parquet
├── evaluation/                        # [NEW] Evaluation artifacts
│   ├── holdout.csv                    # 15% blind holdout SKUs
│   ├── holdout_predictions.parquet   # Model predictions on holdout
│   ├── confusion_matrix.json         # Per-taxonomy-path confusion
│   ├── misclassifications.parquet    # Detailed error analysis
│   └── metrics_history.json          # Historical accuracy/recall
├── logs/                             # [NEW] Runtime logs
│   ├── mapping_runs/
│   │   ├── 2025-11-12_run_001.log
│   │   └── 2025-11-13_run_002.log
│   ├── human_review_sessions/
│   │   └── session_20251112.jsonl
│   └── errors/
│       └── mapping_errors_20251112.jsonl
└── models/                           # [NEW] Trained artifacts
    ├── embeddings/
    │   └── sentence_transformer_v1.pkl
    ├── vectorizers/
    │   └── tfidf_vectorizer_v1.pkl
    └── classifiers/
        └── product_classifier_v1.pkl
```

### 3.2 Data Lineage Tracking

#### Lineage Metadata Structure
Each generated artifact must include lineage metadata:

```json
{
  "artifact_type": "mapping_rules",
  "version": "1.0.0",
  "created_at": "2025-11-12T10:30:00Z",
  "lineage": {
    "inputs": [
      {
        "source": "data/scraped_data_output.json",
        "git_commit": "bb4e77f",
        "file_hash": "sha256:abcd1234..."
      },
      {
        "source": "data/taxonomy_paths.txt",
        "git_commit": "bb4e77f",
        "file_hash": "sha256:efgh5678..."
      },
      {
        "source": "mapping/identifiers/organic_identifiers_v1.0.0.json",
        "git_commit": "bb4e77f",
        "file_hash": "sha256:ijkl9012..."
      }
    ],
    "process": {
      "script": "scripts/generate_mapping_rules.py",
      "git_commit": "bb4e77f",
      "python_version": "3.11.5",
      "dependencies": {
        "pandas": "2.2.0",
        "sentence-transformers": "3.0.0",
        "rapidfuzz": "3.5.2"
      }
    },
    "parameters": {
      "semantic_threshold": 0.85,
      "confidence_floor": 0.70,
      "min_sample_size": 5
    }
  }
}
```

#### Lineage Graph (Conceptual)
```
scraped_data_output.json ──┐
                            ├──> organic_identifiers_v1.0.0.json ──┐
taxonomy_paths.txt ─────────┘                                       │
                                                                    ├──> mapping_rules_v1.0.0.json
                                                                    │
                            ┌───────────────────────────────────────┘
                            │
                            ├──> confidence_scores.parquet
                            │
                            └──> human_reviews.parquet ──> mapping_audit_trail.jsonl
```

#### Audit Trail Format
**File:** `mapping/audit/mapping_audit_trail.jsonl`

Append-only log of all mapping operations:

```jsonl
{"event_type":"identifier_created","identifier_id":"550e8400-e29b-41d4-a716-446655440000","identifier_name":"LED Chandelier Light Bulb","timestamp":"2025-11-12T10:30:00Z","user":"system","git_commit":"bb4e77f"}
{"event_type":"mapping_rule_created","rule_id":"rule_001","identifier_id":"550e8400-e29b-41d4-a716-446655440000","taxonomy_path":"Home & Kitchen//Lamps & Lighting//Light Bulbs","confidence":0.94,"timestamp":"2025-11-12T10:31:00Z","user":"system","git_commit":"bb4e77f"}
{"event_type":"human_review_completed","review_id":"review_001","sku":"1010398944","decision":"approve","reviewer":"analyst_01","timestamp":"2025-11-12T11:00:00Z"}
{"event_type":"mapping_rule_updated","rule_id":"rule_001","change":"confidence_threshold_lowered","old_value":0.75,"new_value":0.70,"reason":"improve_recall","timestamp":"2025-11-12T14:00:00Z","user":"data_scientist_01","git_commit":"c8f12ab"}
```

#### Lineage Queries
Support common lineage queries via DuckDB:

```sql
-- Find all products mapped using a specific rule version
SELECT sku, identifier_name, taxonomy_path, confidence
FROM confidence_scores
WHERE rule_version = '1.0.0';

-- Trace lineage of a specific product mapping
SELECT *
FROM mapping_audit_trail
WHERE sku = '1010398944'
ORDER BY timestamp;

-- Identify mappings requiring re-evaluation after taxonomy update
SELECT DISTINCT identifier_id, identifier_name
FROM mapping_rules
WHERE taxonomy_version = '0.9.0';
```

---

## 4. IMPLEMENTATION CHECKLIST

### Phase 1: Discovery & Identifier Creation
- [ ] Run identifier discovery on `data/scraped_data_output.json`
- [ ] Generate `mapping/identifiers/organic_identifiers_v1.0.0.json`
- [ ] Create `mapping/identifiers/discovery_metadata.json` with lineage
- [ ] Commit to git with message: "Initial identifier discovery v1.0.0"

### Phase 2: Mapping Rule Generation
- [ ] Load taxonomy from `data/taxonomy_paths.txt`
- [ ] Generate candidate mappings using semantic similarity + keyword matching
- [ ] Calculate confidence scores for each product-identifier-taxonomy triplet
- [ ] Generate `mapping/rules/mapping_rules_v1.0.0.json`
- [ ] Export confidence scores to `mapping/confidence/confidence_scores.parquet`
- [ ] Commit with message: "Initial mapping rules v1.0.0"

### Phase 3: Human Review Queue
- [ ] Identify products with confidence in [0.70, 0.79]
- [ ] Identify ambiguous mappings (multiple high-confidence paths)
- [ ] Export review queue to `mapping/audit/human_reviews.parquet`
- [ ] Build simple review interface (CLI or Jupyter notebook)
- [ ] Conduct reviews and update mapping rules
- [ ] Log all decisions to `mapping/audit/mapping_audit_trail.jsonl`

### Phase 4: Validation & QA
- [ ] Load holdout set from `evaluation/holdout.csv`
- [ ] Run predictions on holdout using final mapping rules
- [ ] Calculate accuracy, precision, recall per taxonomy branch
- [ ] Verify >=98% macro accuracy and >=0.95 recall requirements
- [ ] Generate confusion matrix and misclassification report
- [ ] Document results in `evaluation/metrics_history.json`

### Phase 5: Deployment Prep
- [ ] Package mapping rules as Python module
- [ ] Create CLI tool: `map_product_to_taxonomy(sku, product_data) -> (taxonomy_path, confidence)`
- [ ] Add validation: reject if confidence < 0.70, log warning if < 0.80
- [ ] Create FastAPI endpoint for real-time inference
- [ ] Add health check endpoint with taxonomy version info
- [ ] Document API in README

---

## 5. MAINTENANCE & EVOLUTION

### Retraining Triggers
Retrain mapping rules when:
1. New products added to dataset (monthly batch)
2. Taxonomy updated (taxonomy_paths.txt changes)
3. Accuracy drops below 95% on spot-checks
4. >10% of products fall below confidence threshold

### Version Migration Process
When bumping identifier or rule versions:
1. Create new version file (e.g., `organic_identifiers_v1.1.0.json`)
2. Update `versions.json` changelog
3. Regenerate dependent artifacts with new version references
4. Run validation suite on new version
5. Git commit with semantic version tag
6. Update production deployment

### Monitoring
Track these metrics in production:
- Mean confidence score (daily)
- Distribution of confidence tiers (weekly)
- Human review queue length (daily)
- Mapping latency (real-time)
- Taxonomy coverage (% of products mapped)
- Unmapped product count and patterns

---

## 6. EXAMPLE WORKFLOW

### End-to-End Example: Mapping a New Product

**Input Product:**
```json
{
  "sku": "1010398944",
  "title": "Feit Electric 60-Watt Equivalent B10 E26 Base Chandelier LED Light Bulb",
  "description": "Upgrade your lighting to Feit Electric's elegant Exposed White Filament...",
  "brand": "Feit Electric",
  "structured_specifications": {
    "wattage": {"value": 5.5, "unit": "W"},
    "base_type": "B10"
  }
}
```

**Step 1:** Match to identifier
- Semantic embedding similarity → "LED Chandelier Light Bulb" (score: 0.94)

**Step 2:** Lookup mapping rule
- Identifier "LED Chandelier Light Bulb" → Taxonomy: "Home & Kitchen//Lamps & Lighting//Light Bulbs"

**Step 3:** Calculate confidence
- Semantic similarity: 0.92
- Attribute validation: 1.0 (wattage + base_type present)
- Keyword overlap: 0.88
- **Final confidence: 0.91**

**Step 4:** Validate & route
- Confidence 0.91 >= 0.80 → Auto-approve
- Log to audit trail
- Return: `("Home & Kitchen//Lamps & Lighting//Light Bulbs", 0.91)`

**Audit Log Entry:**
```jsonl
{"event_type":"product_mapped","sku":"1010398944","identifier_id":"550e8400-e29b-41d4-a716-446655440000","taxonomy_path":"Home & Kitchen//Lamps & Lighting//Light Bulbs","confidence":0.91,"method":"auto_approved","timestamp":"2025-11-12T15:30:00Z"}
```

---

## 7. SUCCESS METRICS

Track these KPIs to measure mapping quality:

| Metric | Target | Measured By |
|--------|--------|-------------|
| Macro Accuracy | >= 98% | Holdout set evaluation |
| Recall (per taxonomy branch) | >= 0.95 | Confusion matrix analysis |
| Mean Confidence | >= 0.85 | Aggregate confidence scores |
| Auto-Approval Rate | >= 80% | % products with confidence >= 0.80 |
| Human Review Turnaround | < 24 hours | Median time from queue to decision |
| Taxonomy Coverage | >= 95% | % products successfully mapped |
| Mapping Latency | < 100ms | P95 inference time |

---

## 8. REFERENCES

- **Taxonomy Source:** `data/taxonomy_paths.txt` (374 paths)
- **Product Data:** `data/scraped_data_output.json` (425 products)
- **Requirements:** `requirements_product_identifier.txt`
- **Workflow Roadmap:** `README.md` (Section: Suggested Workflow Roadmap)
- **Git Commit:** Current branch `claude/design-identifier-taxonomy-bridge-011CV48Jxkpepj1snDpUDo3f`

---

**Document Version:** 1.0.0
**Created:** 2025-11-12
**Last Updated:** 2025-11-12
**Status:** Implementation-Ready
