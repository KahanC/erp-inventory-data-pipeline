"""Load six synthetic ERP CSV tables into a local DuckDB database."""
from pathlib import Path
import duckdb
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'erp_inventory.duckdb'
TABLES = ('inventory_warehouses','inventory_product_codes','sales_departments','inventory','inventory_uoms','inventory_upc_codes')
with duckdb.connect(str(DB)) as con:
    for table in TABLES:
        path = ROOT / 'data' / f'{table}.csv'
        if not path.is_file():
            raise SystemExit(f'Missing {path}. Run python src/generate_data.py first.')
        # Explicit VARCHAR ingestion prevents auto-inference from changing SKU/warehouse identifiers.
        con.execute(f'CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, all_varchar=true)', [str(path)])
        print(f'{table}: {con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]} rows')
print(f'Loaded database: {DB}')
