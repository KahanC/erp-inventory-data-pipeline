-- All dashboard metrics are computed from the validated warehouse-SKU mart.
-- Keep one row per warehouse/SKU in the mart; aggregate only downstream.
SELECT whse, warehouse_name, COUNT(*) AS sku_count,
       ROUND(SUM(extended_inventory_value), 2) AS inventory_value,
       SUM(CASE WHEN below_reorder_point THEN 1 ELSE 0 END) AS below_rop,
       SUM(CASE WHEN available_qty < 0 THEN 1 ELSE 0 END) AS shortages,
       ROUND(SUM(available_qty), 0) AS available_units
FROM inventory_mart
GROUP BY whse, warehouse_name ORDER BY whse;
