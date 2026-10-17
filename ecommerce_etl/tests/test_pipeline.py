import pandas as pd
from src.pipeline import transform

def test_duplicates_and_returns_and_missing_customer():
    df=pd.DataFrame([
        ['1','A','Item',2,'12/1/2010 8:26',3,None,'United Kingdom'],
        ['1','A','Item',2,'12/1/2010 8:26',3,None,'United Kingdom'],
        ['1','B','Other',1,'12/1/2010 8:26',5,'123','United Kingdom'],
        ['C2','A','Item',-1,'12/1/2010 8:26',3,'123','United Kingdom'],
        ['3','A','Item',1,'12/1/2010 8:26',-3,'123','United Kingdom'],
    ],columns=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country'])
    clean,rejected,stats=transform(df)
    assert stats['exact_duplicates_removed']==1
    assert len(clean)==3 and len(rejected)==1
    assert stats['sale_rows']==2 and stats['cancellation_rows']==1
    assert stats['sales_revenue']==11
    assert clean.loc[clean['InvoiceNo']=='1','StockCode'].nunique()==2
    assert 'UNKNOWN' in clean['CustomerID'].values
