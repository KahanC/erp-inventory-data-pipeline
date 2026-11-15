"""Fail fast if inventory mart loses rows, duplicates keys, or misstates valuation."""
from pathlib import Path
import duckdb
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'erp_inventory.duckdb'
if not DB.exists():
    raise SystemExit('Database not found. Run load_duckdb.py and build_mart.py first.')
checks = {
 'source_has_600_rows': 'SELECT COUNT(*) = 600 FROM inventory',
 'mart_matches_source_count': 'SELECT (SELECT COUNT(*) FROM inventory_mart) = (SELECT COUNT(*) FROM inventory)',
 'no_duplicate_warehouse_sku': 'SELECT COUNT(*) = COUNT(DISTINCT (whse, part_no)) FROM inventory_mart',
 'all_warehouses_joined': 'SELECT COUNT(*) = 0 FROM inventory_mart WHERE warehouse_name IS NULL',
 'all_product_codes_joined': 'SELECT COUNT(*) = 0 FROM inventory_mart WHERE product_group IS NULL',
 'no_null_costs_or_quantities': 'SELECT COUNT(*) = 0 FROM inventory_mart WHERE onhand_qty IS NULL OR average_cost IS NULL',
 'valuation_reconciles': "SELECT COALESCE(SUM(ABS(extended_inventory_value - ROUND(onhand_qty * average_cost,2))),0) = 0 FROM inventory_mart",
 'no_negative_onhand': 'SELECT COUNT(*) = 0 FROM inventory_mart WHERE onhand_qty < 0',
 'valid_price_parsing': 'SELECT COUNT(*) = 0 FROM inventory_mart WHERE retail_price IS NULL OR wholesale_price IS NULL OR us_price IS NULL'
}
failures=[]
with duckdb.connect(str(DB), read_only=True) as con:
    for name, sql in checks.items():
        ok=bool(con.execute(sql).fetchone()[0])
        print(('PASS' if ok else 'FAIL') + '  ' + name)
        if not ok: failures.append(name)
if failures: raise SystemExit(f'{len(failures)} validation(s) failed')
print('All data quality checks passed.')
