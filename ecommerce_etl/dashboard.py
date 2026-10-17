"""Run with: streamlit run dashboard.py"""
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
st.set_page_config(page_title='E-commerce Data Engineering',layout='wide')
st.title('E-commerce Sales Analytics')
st.caption('Sales exclude cancellation invoices, returns, zero-price items and invalid records. Currency: GBP (source dataset).')
ROOT=Path(__file__).resolve().parent
engine=create_engine(os.environ.get('DATABASE_URL') or f'sqlite:///{ROOT / "ecommerce.db"}')
try:
    with engine.connect() as conn:
        df=pd.read_sql_query(text('SELECT * FROM transactions'),conn)
except Exception as exc:
    st.error(f'Run python -m src.pipeline first. Database error: {exc}');st.stop()
df['is_sale']=df['is_sale'].astype(bool)
sales=df[df['is_sale']].copy()
a,b,c=st.columns(3)
a.metric('Sales revenue',f"£{sales['line_amount'].sum():,.2f}")
b.metric('Sale invoices',f"{sales['InvoiceNo'].nunique():,}")
c.metric('Units sold',f"{sales['Quantity'].sum():,.0f}")
months=sales.groupby('invoice_month',as_index=False)['line_amount'].sum().set_index('invoice_month')
st.subheader('Monthly sales');st.line_chart(months)
left,right=st.columns(2)
with left:
    st.subheader('Top products by revenue')
    products=sales.groupby('Description')['line_amount'].sum().nlargest(10)
    st.bar_chart(products)
with right:
    st.subheader('Top countries by revenue')
    countries=sales.groupby('Country')['line_amount'].sum().nlargest(10)
    st.bar_chart(countries)
st.subheader('Clean transaction preview');st.dataframe(df.head(100),use_container_width=True)
