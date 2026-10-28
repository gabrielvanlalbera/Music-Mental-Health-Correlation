"""Execute both notebooks in order and write results to reports/ and data/processed/.

    python scripts/run_pipeline.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ["01_cleaning_eda.ipynb", "02_personas_and_modeling.ipynb"]

for nb in NOTEBOOKS:
    print(f"==> executing {nb}", flush=True)
    cmd = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace",
           str(ROOT / "notebooks" / nb), "--ExecutePreprocessor.timeout=3600"]
    subprocess.run(cmd, check=True, cwd=ROOT / "notebooks")
print("done. See reports/tables and reports/figures.")
