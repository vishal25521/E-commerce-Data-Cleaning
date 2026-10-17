"""Create SQL-based KPI exports from the loaded transactions table."""
import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
ROOT=Path(__file__).resolve().parents[1]
QUERIES={
 'monthly_sales': '''SELECT invoice_month, COUNT(DISTINCT "InvoiceNo") AS invoices, ROUND(SUM(line_amount),2) AS revenue FROM transactions WHERE is_sale = 1 GROUP BY invoice_month ORDER BY invoice_month''',
 'top_products': '''SELECT "StockCode" AS stock_code, MAX("Description") AS description, SUM("Quantity") AS units_sold, ROUND(SUM(line_amount),2) AS revenue FROM transactions WHERE is_sale = 1 GROUP BY "StockCode" ORDER BY revenue DESC LIMIT 20''',
 'country_sales': '''SELECT "Country" AS country, COUNT(DISTINCT "InvoiceNo") AS invoices, ROUND(SUM(line_amount),2) AS revenue FROM transactions WHERE is_sale = 1 GROUP BY "Country" ORDER BY revenue DESC''',
 'summary': '''SELECT COUNT(*) AS transaction_lines, COUNT(DISTINCT "InvoiceNo") AS distinct_invoices, SUM(CASE WHEN is_sale = 1 THEN 1 ELSE 0 END) AS sale_lines, ROUND(SUM(CASE WHEN is_sale = 1 THEN line_amount ELSE 0 END),2) AS gross_sales, SUM(CASE WHEN is_cancellation = 1 THEN 1 ELSE 0 END) AS cancellation_lines FROM transactions'''
}
def run():
    engine=create_engine(os.environ.get('DATABASE_URL') or f'sqlite:///{ROOT / "ecommerce.db"}')
    out=ROOT/'reports';out.mkdir(exist_ok=True)
    for name,query in QUERIES.items():
        with engine.connect() as con: df=pd.read_sql_query(text(query),con)
        df.to_csv(out/f'{name}.csv',index=False)
        print(name, len(df),'rows')
if __name__=='__main__':run()
