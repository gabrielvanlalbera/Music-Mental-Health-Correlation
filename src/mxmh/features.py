"""Feature sets and preprocessing. All imputation/scaling lives inside the sklearn
pipeline so it is fitted on training folds only (no leakage)."""
from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from . import config as C

BASELINE = ["Age", "Hours per day"]
HABITS = BASELINE + C.BINARY_COLS + ["BPM", "bpm_missing"]
GENRE_SET = list(C.FREQ_COLS) + ["genre_diversity"]
CATEGORICAL = ["Fav genre", "Primary streaming service"]

FEATURE_SETS = {
    "baseline (age, hours)": BASELINE,
    "habits": HABITS,
    "genres only": GENRE_SET,
    "habits + genres": HABITS + GENRE_SET,
    "habits + genres + categorical": HABITS + GENRE_SET + CATEGORICAL,
}
# 'Music effects' is deliberately absent: it is a self-reported *outcome* of listening.


def make_preprocessor(columns: list[str]) -> ColumnTransformer:
    cat = [c for c in columns if c in CATEGORICAL]
    num = [c for c in columns if c not in CATEGORICAL]
    transformers = [("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                                      ("scale", StandardScaler())]), num)]
    if cat:
        transformers.append(("cat", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(min_frequency=C.MIN_GENRE_GROUP,
                                     handle_unknown="infrequent_if_exist",
                                     sparse_output=False))]), cat))
    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)
