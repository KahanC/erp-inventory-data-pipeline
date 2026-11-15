"""Execute the versioned SQL transformation into the analytics mart."""
from pathlib import Path
import duckdb
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'erp_inventory.duckdb'
if not DB.exists():
    raise SystemExit('Database not found. Run python src/load_duckdb.py first.')
with duckdb.connect(str(DB)) as con:
    con.execute((ROOT / 'sql' / '03_inventory_mart.sql').read_text())
    print('inventory_mart:', con.execute('SELECT COUNT(*) FROM inventory_mart').fetchone()[0], 'rows')
    print('Inventory value:', con.execute('SELECT ROUND(SUM(extended_inventory_value),2) FROM inventory_mart').fetchone()[0])
