"""Export validated inventory mart to CSV and a formatted Excel workbook."""
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal
import csv
import duckdb
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "erp_inventory.duckdb"
OUT = ROOT / "outputs"

def export_reports():
    if not DB.exists():
        raise FileNotFoundError("Database missing: run python src/pipeline.py first")
    OUT.mkdir(exist_ok=True)
    with duckdb.connect(str(DB), read_only=True) as con:
        rows = con.execute("SELECT * FROM inventory_mart ORDER BY whse, product_code, part_no").fetchall()
        columns = [d[0] for d in con.description]
        summary = con.execute("""SELECT whse, warehouse_name, COUNT(*) AS sku_count,
            ROUND(SUM(extended_inventory_value),2) AS inventory_value,
            SUM(CASE WHEN below_reorder_point THEN 1 ELSE 0 END) AS below_rop_skus
            FROM inventory_mart GROUP BY whse, warehouse_name ORDER BY whse""").fetchall()
    with (OUT / "inventory_mart.csv").open("w", newline="", encoding="utf-8") as f:
        writer=csv.writer(f); writer.writerow(columns); writer.writerows(rows)
    wb=Workbook(); ws=wb.active; ws.title="Inventory Mart"
    ws.append(columns)
    for row in rows:
        ws.append([float(v) if isinstance(v,Decimal) else v for v in row])
    sm=wb.create_sheet("Warehouse Summary")
    sm.append(["Warehouse", "Warehouse Name", "SKUs", "Inventory Value", "Below ROP SKUs"])
    for row in summary:
        sm.append([float(v) if isinstance(v,Decimal) else v for v in row])
    for sheet in wb:
        sheet.freeze_panes="A2"
        sheet.auto_filter.ref=sheet.dimensions
        for cell in sheet[1]:
            cell.fill=PatternFill("solid",fgColor="16324F")
            cell.font=Font(color="FFFFFF",bold=True)
            cell.alignment=Alignment(wrap_text=True)
        for col in sheet.columns:
            letter=get_column_letter(col[0].column)
            max_len=max(len(str(c.value or "")) for c in list(col)[:150])
            sheet.column_dimensions[letter].width=min(max(12,max_len+2),36)
    sm.column_dimensions["B"].width=25
    sm.column_dimensions["D"].width=20
    for cell in sm["D"][1:]: cell.number_format='#,##0.00'
    path=OUT / "inventory_report.xlsx"; wb.save(path)
    print(f"Exported {len(rows)} rows to {OUT / 'inventory_mart.csv'}")
    print(f"Exported workbook to {path}")
    return path

if __name__ == "__main__": export_reports()
