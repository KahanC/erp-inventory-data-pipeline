-- Warehouse-SKU grain. Source price list is a PostgreSQL-style array literal in CSV.
CREATE OR REPLACE TABLE inventory_mart AS
WITH normalized AS (
 SELECT i.whse, i.part_no, i.description, i.product_code, i.hold,
   TRY_CAST(i.onhand_qty AS DECIMAL(18,2)) AS onhand_qty,
   TRY_CAST(i.committed_qty AS DECIMAL(18,2)) AS committed_qty,
   TRY_CAST(i.backorder_qty AS DECIMAL(18,2)) AS backorder_qty,
   TRY_CAST(i.purchase_qty AS DECIMAL(18,2)) AS on_po_qty,
   TRY_CAST(i.reorder_qty AS DECIMAL(18,2)) AS reorder_point,
   TRY_CAST(i.average_cost AS DECIMAL(18,2)) AS average_cost,
   TRY_CAST(i.current_cost AS DECIMAL(18,2)) AS current_cost,
   TRY_CAST(i.min_buy_qty AS DECIMAL(18,2)) AS min_buy_qty,
   TRY_CAST(json_extract_string(i.udf_data, '$.lead_time') AS INTEGER) AS lead_time_days,
   TRY_CAST(json_extract_string(i.udf_data, '$.maxstock') AS DECIMAL(18,2)) AS max_stock,
   TRY_CAST(json_extract_string(i.udf_data, '$.shelf_life') AS INTEGER) AS shelf_life_days,
   json_extract_string(i.udf_data, '$.sub_type') AS inventory_sub_type,
   json_extract_string(i.udf_data, '$.flavour_type') AS flavour_type,
   i.sales_acct, i.preferred_vendor, i.uom_inventory,
   TRY_CAST(i.this_year_revenue AS DECIMAL(18,2)) AS this_year_revenue
 FROM inventory i
), enriched AS (
 SELECT n.*, w.description AS warehouse_name, pc.description AS product_group,
   sd.description AS sales_department, u.whse_location AS location, upc.upc_code,
   TRY_CAST(list_extract(string_split(trim(u.sell_prices, '{}'), ','), 1) AS DECIMAL(18,2)) AS retail_price,
   TRY_CAST(list_extract(string_split(trim(u.sell_prices, '{}'), ','), 2) AS DECIMAL(18,2)) AS wholesale_price,
   TRY_CAST(list_extract(string_split(trim(u.sell_prices, '{}'), ','), 10) AS DECIMAL(18,2)) AS us_price
 FROM normalized n
 LEFT JOIN inventory_warehouses w ON n.whse = w.whse
 LEFT JOIN inventory_product_codes pc ON n.product_code = pc.product_code
 LEFT JOIN sales_departments sd ON n.sales_acct = sd.id
 LEFT JOIN inventory_uoms u ON n.whse = u.whse AND n.part_no = u.part_no AND n.uom_inventory = u.uom
 LEFT JOIN inventory_upc_codes upc ON n.whse = upc.whse AND n.part_no = upc.part_no AND n.uom_inventory = upc.uom
)
SELECT *,
 CASE hold WHEN 0 THEN 'Active' WHEN 1 THEN 'On hold' WHEN 2 THEN 'Inactive' ELSE 'Unknown' END AS inventory_status,
 onhand_qty - committed_qty AS available_qty,
 onhand_qty - committed_qty + on_po_qty - backorder_qty AS projected_available_qty,
 ROUND(onhand_qty * average_cost, 2) AS extended_inventory_value,
 CASE WHEN onhand_qty - committed_qty <= reorder_point THEN TRUE ELSE FALSE END AS below_reorder_point
FROM enriched;
