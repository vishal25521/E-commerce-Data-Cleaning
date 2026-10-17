"""Reproducible retail line-item ETL. Defaults to local SQLite; supports MySQL via DATABASE_URL."""
import argparse
import json
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
COLS = ['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']

def transform(df):
    df = df.copy()
    input_rows = len(df)
    df.columns = df.columns.str.strip()
    missing = set(COLS) - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    df = df[COLS]
    for col in ['InvoiceNo','StockCode','Description','CustomerID','Country']:
        df[col] = df[col].astype('string').str.strip()
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M', errors='coerce')
    df['CustomerID'] = df['CustomerID'].replace('', pd.NA)
    df['Description'] = df['Description'].replace('', pd.NA)
    df['Country'] = df['Country'].replace('', pd.NA)
    duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy() # exact duplicates only; repeated invoice numbers are legitimate
    df['is_cancellation'] = df['InvoiceNo'].str.upper().str.startswith('C', na=False)
    required = ['InvoiceNo','StockCode','InvoiceDate','Quantity','UnitPrice','Country']
    bad = df[required].isna().any(axis=1) | (df['UnitPrice'] < 0) | (df['Quantity'] == 0)
    rejected = df.loc[bad].copy()
    df = df.loc[~bad].copy()
    # Negative quantities and cancellation invoices retained in transaction ledger, excluded from sales.
    df['is_sale'] = (~df['is_cancellation']) & (df['Quantity'] > 0) & (df['UnitPrice'] > 0)
    df['line_amount'] = (df['Quantity'] * df['UnitPrice']).round(2)
    df['invoice_month'] = df['InvoiceDate'].dt.strftime('%Y-%m')
    df['CustomerID'] = df['CustomerID'].fillna('UNKNOWN')
    df['Description'] = df['Description'].fillna('UNKNOWN')
    stats = dict(input_rows=input_rows, exact_duplicates_removed=duplicates, rejected_invalid_rows=len(rejected), retained_rows=len(df), sale_rows=int(df['is_sale'].sum()), cancellation_rows=int(df['is_cancellation'].sum()), unknown_customer_rows=int((df['CustomerID']=='UNKNOWN').sum()), sales_revenue=round(float(df.loc[df['is_sale'],'line_amount'].sum()),2))
    return df, rejected, stats

def run(input_path=None, database_url=None):
    source = Path(input_path) if input_path else ROOT/'data/raw/data.csv'
    if not source.exists():
        raise FileNotFoundError(f'Input not found: {source}')
    df = pd.read_csv(source, dtype={'InvoiceNo':'string','StockCode':'string','CustomerID':'string'}, low_memory=False, encoding='cp1252')
    clean, rejected, stats = transform(df)
    processed = ROOT/'data/processed'; processed.mkdir(parents=True,exist_ok=True)
    reports = ROOT/'reports'; reports.mkdir(parents=True,exist_ok=True)
    clean.to_csv(processed/'transactions_clean.csv', index=False)
    rejected.to_csv(processed/'rejected_rows.csv', index=False)
    url = database_url or os.environ.get('DATABASE_URL') or f'sqlite:///{ROOT / "ecommerce.db"}'
    engine = create_engine(url)
    with engine.begin() as conn:
        clean.to_sql('transactions', conn, if_exists='replace', index=False, chunksize=5000, method=None)
        conn.execute(text('CREATE INDEX ix_transactions_invoice ON transactions ("InvoiceNo")' if engine.dialect.name=='sqlite' else 'CREATE INDEX ix_transactions_invoice ON transactions (InvoiceNo)'))
    stats['database'] = engine.dialect.name
    (reports/'quality_report.json').write_text(json.dumps(stats,indent=2), encoding='utf-8')
    print(json.dumps(stats,indent=2))
    return stats

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',default=None,help='Input CSV path')
    parser.add_argument('--database-url',default=None,help='SQLAlchemy database URL; default SQLite')
    args=parser.parse_args()
    run(args.input,args.database_url)
