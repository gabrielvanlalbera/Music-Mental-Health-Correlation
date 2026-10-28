import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mxmh import config as C                      # noqa: E402
from mxmh.data import clean_data, load_raw        # noqa: E402
from mxmh.modeling import nadeau_bengio           # noqa: E402


def _toy(n=4):
    d = {"Timestamp": ["t"] * n, "Permissions": ["ok"] * n, "Age": [20, 15, 40, 30][:n],
         "Hours per day": [2, 24, 3, 1][:n], "BPM": [120, 999999999, 0, 90][:n],
         "While working": ["Yes", "No", "Yes", "No"][:n], "Instrumentalist": ["Yes", "No", None, "No"][:n],
         "Composer": ["No"] * n, "Exploratory": ["Yes"] * n, "Foreign languages": ["No"] * n,
         "Fav genre": ["Rock"] * n, "Primary streaming service": ["Spotify"] * n,
         "Anxiety": [3, 8, 7, 0][:n], "Depression": [1, 9, 2, 0][:n],
         "Insomnia": [0, 5, 7, 2][:n], "OCD": [0, 1, 2, 3][:n], "Music effects": ["Improve"] * n}
    for g in C.GENRES:
        d[f"Frequency [{g}]"] = ["Never", "Very frequently", "Sometimes", "Rarely"][:n]
    return pd.DataFrame(d)


def test_cleaning_rules():
    df, log = clean_data(_toy())
    assert df["BPM"].isna().sum() == 2 and df["bpm_missing"].sum() == 2
    assert pd.isna(df.loc[1, "Hours per day"])              # 24 h/day is implausible
    assert df.loc[1, "freq_Rock"] == 3 and df.loc[0, "freq_Rock"] == 0
    assert df["Instrumentalist"].isna().sum() == 1          # missing kept as NaN, not imputed
    assert df.loc[1, "Anxiety_high"] == 1 and df.loc[0, "Anxiety_high"] == 0
    assert str(df.loc[1, "age_group"]) == "<18"
    assert "Timestamp" not in df and "Permissions" not in df
    assert dict(log)["Respondents under 18 (kept, flagged via age_group)"] == 1


def test_nadeau_bengio_zero_variance():
    m, t, p = nadeau_bengio(np.zeros(10), 100, 25)
    assert (m, p) == (0.0, 1.0)


def test_nadeau_bengio_detects_shift():
    rng = np.random.default_rng(0)
    m, t, p = nadeau_bengio(0.5 + 0.01 * rng.standard_normal(10), 100, 25)
    assert m > 0.4 and p < 0.01


RAW = ROOT / "data" / "raw" / "mxmh_survey_results.csv"


@pytest.mark.skipif(not RAW.exists(), reason="raw data not present")
def test_real_data_shape():
    df, _ = clean_data(load_raw(RAW))
    assert len(df) == 736
    assert df[C.FREQ_COLS].isin([0, 1, 2, 3]).all().all()
    assert df["BPM"].dropna().between(*C.BPM_RANGE).all()
