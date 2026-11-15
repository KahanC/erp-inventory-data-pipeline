# ERP Inventory Data Engineering Pipeline

**DuckDB · Advanced SQL · Python ETL · Data Quality · Excel · Plotly**

A reproducible inventory ETL pipeline built with **synthetic ERP-style data**. Inspired by a real-world inventory reporting workflow, but not connected to Spire or any company system. No proprietary data or credentials.

## Architecture

```text
Six synthetic ERP CSVs
        │
        ▼
DuckDB source tables ── SQL CTEs + joins + JSON extraction + price parsing
        │
        ▼
inventory_mart (warehouse × SKU grain)
        │
        ▼
Nine data-quality assertions (fail-fast)
        │
        ├── outputs/inventory_mart.csv
        ├── outputs/inventory_report.xlsx (mart + warehouse summary)
        ├── outputs/pipeline.log
        └── docs/index.html (interactive GitHub Pages dashboard)
```

## Quick start (Mac / Linux, no Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/pipeline.py
python -m unittest discover -s tests -v
```

**Expected:** 600 inventory source rows, 600 mart rows, nine validation checks passing, four integration tests passing, two report files in `outputs/`, and `docs/index.html`.

Run again with `python src/pipeline.py --skip-generate` to reuse the existing CSVs.

## SQL engineering

- `sql/03_inventory_mart.sql`: warehouse–SKU-grain SQL transformation using CTEs, six source tables, `LEFT JOIN`s, JSON field extraction, and price parsing.
- Calculates available stock, projected stock, inventory valuation, and below-reorder-point flags.
- `src/validate.py`: checks source-to-mart reconciliation, duplicate keys, lookup joins, missing costs, valuation, and prices.
- `tests/test_pipeline.py`: integration tests against the generated database and Excel output.

## Project structure

```text
sql/                 SQL mart and PostgreSQL reference scripts
src/generate_data.py synthetic source generator
src/load_duckdb.py   CSV → DuckDB source tables
src/build_mart.py    SQL → inventory_mart
src/validate.py      data-quality gate
src/export.py        CSV + formatted Excel workbook
src/pipeline.py      orchestrated ETL runner
 tests/              integration tests
outputs/             generated reports (ignored by Git)
```

## Limitations and roadmap

This is a **local batch ETL demo**, not real-time ingestion. DuckDB replaces the original PostgreSQL/Spire backend. Next: build a Plotly HTML dashboard and publish it with GitHub Pages. The PostgreSQL reference scripts are **not** used in the DuckDB pipeline.

## Stage 4 — Interactive dashboard

The dashboard is built **from the validated DuckDB inventory mart**, using SQL aggregations in `sql/04_dashboard_aggregates.sql` and Plotly in `src/dashboard.py`.

```bash
python src/pipeline.py
open docs/index.html  # macOS
```

To regenerate only the dashboard after an existing successful pipeline run:

```bash
python src/dashboard.py
```

To publish: commit `docs/index.html`, then in GitHub repository Settings → Pages choose **Deploy from a branch**, branch **main**, folder **/docs**. GitHub Pages serves the pre-generated HTML; it does not execute DuckDB or Python. Re-run the pipeline and push the updated HTML to refresh the site.

**Important:** Generated data is entirely synthetic. This is a local batch pipeline, not a live ERP API connection. The HTML embeds Plotly JavaScript and is standalone.
