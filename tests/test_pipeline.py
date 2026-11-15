"""Run with python -m unittest discover -s tests -v after pipeline execution."""
import unittest
from pathlib import Path
import duckdb
from openpyxl import load_workbook
ROOT=Path(__file__).resolve().parents[1]

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (ROOT / "erp_inventory.duckdb").exists():
            raise unittest.SkipTest("Run python src/pipeline.py before integration tests")
        cls.con=duckdb.connect(str(ROOT / "erp_inventory.duckdb"),read_only=True)
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,"con"): cls.con.close()
    def test_source_and_mart_counts_match(self):
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
                         self.con.execute("SELECT COUNT(*) FROM inventory_mart").fetchone()[0])
    def test_mart_key_unique(self):
        self.assertEqual(self.con.execute("SELECT COUNT(*)-COUNT(DISTINCT (whse,part_no)) FROM inventory_mart").fetchone()[0],0)
    def test_valuation_reconciles(self):
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM inventory_mart WHERE ABS(extended_inventory_value-ROUND(onhand_qty*average_cost,2))>0.001").fetchone()[0],0)
    def test_export_exists(self):
        path=ROOT / "outputs" / "inventory_report.xlsx"
        self.assertTrue(path.is_file())
        wb=load_workbook(path,read_only=True)
        self.assertEqual(wb["Inventory Mart"].max_row-1,self.con.execute("SELECT COUNT(*) FROM inventory_mart").fetchone()[0])
        wb.close()

if __name__ == "__main__": unittest.main()
