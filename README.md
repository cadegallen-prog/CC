# CC Product Type Identifier Workspace

*(Legacy repo motto: "shrug" — preserved from the original README.)*

## Purpose
This repository packages the raw ingredients that Claude Code Browser (or any agent) can use to build a product-type identification workflow capable of labeling about 425 Home Depot listings with >=98% accuracy. The resources here focus on grounding the taxonomy, describing the scraped catalog data, and outlining a staged plan that spans ingestion through deployment.

### Product-Type Discovery Principles
- The scraped JSON is the sole source of truth for discovering fine-grained product types; agents should let item titles, descriptions, and brand cues drive the label space organically.
- `taxonomy_paths.txt` acts only as a downstream mapping target once confident product-type identifiers exist. Do not force-fit items into taxonomy leaves until the classifier produces precise, data-derived labels.
- Any mapping or roll-up back into the taxonomy should be handled in a later phase, ideally with documented rules/audits so accuracy is preserved.

## Included Assets
- `data/taxonomy_paths.txt` - 374 hierarchical taxonomy leaves formatted as `Department//Category//Subcategory`. Treat it as a reference catalog for later mapping once fine-grained product types emerge from the scraped data; do not let it constrain discovery.
- `data/scraped_data_output.json` - 425 structured product records captured from homedepot.com. Each entry includes `title`, `description`, `brand`, `model`, `price`, and a list of media URLs. This is the working dataset for prototyping, feature discovery, and evaluation.
- `requirements_product_identifier.txt` - environment, tooling, and process requirements that ensure Claude (or any assistant) can recreate the analysis stack deterministically.

## Suggested Workflow Roadmap
1. **Data Intake & Audit** - Validate JSON schema, deduplicate listings, and inventory naturally occurring product-type signals (keywords, attributes, brands) without imposing the taxonomy yet.
2. **Feature Engineering** - Derive signals such as brand embeddings, key attribute extraction (dimensions, wattage, material), and n-gram keyword buckets. Store intermediate tables in DuckDB/Parquet for reproducibility.
3. **Label Bootstrapping** - Seed data-native product-type labels via heuristic mapping (title/description regex, brand-to-category priors). Capture uncertain items (<0.7 confidence) for quick human review, then translate mature labels into taxonomy leaves only after confidence is established.
4. **Model Training** - Train lightweight classifiers (e.g., SentenceTransformers + cosine, or gradient-boosted trees on TF-IDF + metadata) with stratified cross-validation. Track experiments in Weights & Biases or MLflow.
5. **Evaluation & QA** - Require >=98% macro accuracy and >=0.95 recall on each high-volume category. Add a hold-out SKU list plus a spot-check script that prints misclassifications with rationale.
6. **Deployment Prep** - Package the predictor behind a CLI/REST shim (FastAPI) with baked-in taxonomy validation, logging, and confidence thresholds. Document retraining triggers.
7. **Automation & Monitoring** - Schedule nightly runs (Prefect or Airflow) and push predictions plus confidence to warehouse/BI for downstream monitoring.

## Data Stack Recommendations
- **Storage & Access**: DuckDB/Parquet for local iteration, Postgres (with JSONB) for shared persistence, optional S3 bucket for artifact versioning.
- **Processing & Modeling**: Python 3.11, Pandas or Polars, scikit-learn, SentenceTransformers (`all-MiniLM-L12-v2` or `text-embedding-3-large` if API access is allowed), RapidFuzz for string matching.
- **Orchestration & Observability**: Prefect (lightweight) or Airflow for scheduled enrichment, Weights & Biases for experiment tracking, and EvidentlyAI for drift detection once the classifier is in production.
- **Quality Safeguards**: Add a small human vetting loop (10 percent sample), maintain a taxonomy change log, and version both datasets plus trained weights.

## How Claude Code Browser Can Use This Package
1. Load the JSON file, normalize fields, and catalog organically derived product-type candidates before any taxonomy mapping.
2. Implement the roadmap phase by phase, using the requirements file to install dependencies.
3. Export updated predictions back to JSON/CSV so they can be re-ingested into this repo or any downstream tool.

Document any new scripts or models in logical subfolders (for example, `notebooks/`, `models/`, `mapping/`) so future contributors can trace lineage without touching unrelated parts of the repository.
