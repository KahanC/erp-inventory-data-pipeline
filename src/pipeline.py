"""One-command ETL runner: generate → load → SQL transform → validate → export."""
from pathlib import Path
import argparse
import logging
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
STEPS=["generate_data.py", "load_duckdb.py", "build_mart.py", "validate.py", "export.py", "dashboard.py"]

def main():
    parser=argparse.ArgumentParser(description="Synthetic ERP inventory ETL")
    parser.add_argument("--skip-generate", action="store_true", help="Reuse existing synthetic CSV files")
    args=parser.parse_args()
    (ROOT / "outputs").mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(ROOT / "outputs" / "pipeline.log")])
    for step in STEPS:
        if args.skip_generate and step == "generate_data.py": continue
        logging.info("Starting %s",step)
        result=subprocess.run([sys.executable,str(ROOT / "src" / step)],cwd=ROOT,check=False)
        if result.returncode:
            logging.error("FAILED %s (exit %s). Stopping before downstream steps.",step,result.returncode)
            return result.returncode
        logging.info("Completed %s",step)
    logging.info("Pipeline complete. See outputs/ for reports.")
    return 0

if __name__ == "__main__": sys.exit(main())
