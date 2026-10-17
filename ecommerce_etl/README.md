# End-to-End E-commerce Data Engineering Project

Uses the **actual uploaded Online Retail CSV** (2010–2011 invoice-line records). Source currency is GBP. Dataset included in `data/raw/data.csv` so the project runs offline. This is a historical dataset, not live sales.

## Architecture
CSV → pandas extraction & validation → cleaned/rejected CSV + JSON quality report → SQL database → SQL analytics CSV exports → Streamlit dashboard.

## Run on Windows (VS Code PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.pipeline
python -m src.analytics
python -m pytest -q
python -m streamlit run dashboard.py
```
If PowerShell blocks activation, run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and use `.venv\Scripts\python.exe` instead of `python` in commands.

## Optional MySQL
Create a database: `CREATE DATABASE ecommerce;` then set your connection (replace credentials):
```powershell
$env:DATABASE_URL='mysql+pymysql://USER:PASSWORD@localhost:3306/ecommerce'
python -m src.pipeline
python -m src.analytics
python -m streamlit run dashboard.py
```
Use URL encoding for special characters in passwords. By default, SQLite is used, requiring no database server. The pipeline **replaces** the `transactions` table on each run (idempotent full refresh); do not point it at an existing production table.

## Cleaning policy
- Keep valid distinct invoice line items even when InvoiceNo repeats (an invoice has multiple products).
- Drop only **exact** duplicate rows (note: without a source line-item ID, identical legitimate items cannot be distinguished).
- Reject missing critical keys/date/numeric fields, negative unit prices and zero quantities to `data/processed/rejected_rows.csv`.
- Retain unknown customers as `UNKNOWN` rather than inventing an ID; missing descriptions as `UNKNOWN`.
- Retain cancellation/return lines in the clean ledger; `is_sale` excludes cancellations, nonpositive quantities and zero-price items from sales KPIs.
- Keep non-cancellation negative-quantity adjustments in ledger but not gross sales; do not interpret gross sales as net revenue.
- Preserve original InvoiceNo and StockCode as strings (including prefixes/leading zeros).

## Outputs
- `data/processed/transactions_clean.csv`: validated ledger with `is_sale`, `is_cancellation`, `line_amount`, `invoice_month`.
- `data/processed/rejected_rows.csv`: invalid records for inspection.
- `reports/quality_report.json`: pipeline row counts and sales metric.
- `reports/summary.csv`, `monthly_sales.csv`, `top_products.csv`, `country_sales.csv`: SQL analytics.
- `ecommerce.db`: default SQLite database.

## Portfolio talking points
CSV ingestion, schema checks, missing values, line-item deduplication, return handling, SQL loading, SQL aggregations, reproducible execution, data-quality reporting, unit tests, and dashboarding.
