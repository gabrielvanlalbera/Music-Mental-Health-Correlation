"""Loading and cleaning. Every cleaning rule is logged so it can be reported."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C


def load_raw(path) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple[str, int]]]:
    """Apply the documented cleaning rules. Returns (clean_df, log)."""
    df = raw.drop(columns=[c for c in ("Timestamp", "Permissions") if c in raw.columns]).copy()
    log: list[tuple[str, int]] = []

    lo, hi = C.BPM_RANGE
    bad_bpm = (df["BPM"] < lo) | (df["BPM"] > hi)
    log.append((f"BPM outside {lo}-{hi} set to NaN", int(bad_bpm.sum())))
    df.loc[bad_bpm, "BPM"] = np.nan
    df["bpm_missing"] = df["BPM"].isna().astype(int)
    log.append(("BPM missing after cleaning", int(df["BPM"].isna().sum())))

    bad_hours = df["Hours per day"] > C.MAX_HOURS
    log.append((f"Hours per day > {C.MAX_HOURS} set to NaN", int(bad_hours.sum())))
    df.loc[bad_hours, "Hours per day"] = np.nan

    for g in C.GENRES:
        df[f"freq_{g}"] = df[f"Frequency [{g}]"].map(C.FREQ_MAP)
    df = df.drop(columns=[f"Frequency [{g}]" for g in C.GENRES])

    for c in C.BINARY_COLS:
        df[c] = df[c].map({"Yes": 1, "No": 0})

    df["age_group"] = pd.cut(df["Age"], C.AGE_BINS, labels=C.AGE_LABELS)
    df["genre_diversity"] = (df[C.FREQ_COLS] >= 2).sum(axis=1)  # genres heard 'Sometimes' or more
    for t in C.TARGETS:
        df[f"{t}_high"] = (df[t] >= C.HIGH_THRESHOLD).astype(int)

    log.append(("Respondents under 18 (kept, flagged via age_group)", int((df["Age"] < 18).sum())))
    log.append(("Missing Age", int(df["Age"].isna().sum())))
    return df, log
