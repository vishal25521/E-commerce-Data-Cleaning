-- Run against ecommerce.db (SQLite) or adapt quoting for MySQL.
-- Sales definition: positive quantity and price, non-cancellation invoices.
SELECT invoice_month, ROUND(SUM(line_amount), 2) AS revenue
FROM transactions WHERE is_sale = 1 GROUP BY invoice_month ORDER BY invoice_month;
SELECT "StockCode", MAX("Description") AS product, SUM("Quantity") AS units_sold,
ROUND(SUM(line_amount),2) AS revenue FROM transactions WHERE is_sale = 1
GROUP BY "StockCode" ORDER BY revenue DESC LIMIT 10;
SELECT "Country", ROUND(SUM(line_amount),2) AS revenue FROM transactions
WHERE is_sale = 1 GROUP BY "Country" ORDER BY revenue DESC;
SELECT COUNT(*) AS total_lines, COUNT(DISTINCT "InvoiceNo") AS invoices FROM transactions;
