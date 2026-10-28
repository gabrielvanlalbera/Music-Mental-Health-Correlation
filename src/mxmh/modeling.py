"""Model zoo, cross-validated evaluation and paired comparison utilities."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import (HistGradientBoostingClassifier, HistGradientBoostingRegressor,
                              RandomForestClassifier, RandomForestRegressor)
from sklearn.linear_model import LogisticRegressionCV, RidgeCV
from sklearn.metrics import make_scorer
from sklearn.model_selection import RepeatedKFold, RepeatedStratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline

from . import config as C
from .features import FEATURE_SETS, make_preprocessor

PRIMARY = {"regression": "ridge", "classification": "logistic"}  # pre-specified, see docs/methodology.md


def regressors() -> dict:
    return {
        "mean": DummyRegressor(strategy="mean"),
        "ridge": RidgeCV(alphas=np.logspace(-2, 3, 20)),
        "rf": RandomForestRegressor(n_estimators=150, min_samples_leaf=10, max_features=0.5,
                                    random_state=C.SEED, n_jobs=-1),
        "hgb": HistGradientBoostingRegressor(learning_rate=0.05, max_depth=3, max_iter=120,
                                             l2_regularization=1.0, random_state=C.SEED),
    }


def classifiers() -> dict:
    return {
        "prevalence": DummyClassifier(strategy="prior"),
        "logistic": LogisticRegressionCV(Cs=10, cv=5, scoring="roc_auc", max_iter=3000,
                                         random_state=C.SEED),
        "rf": RandomForestClassifier(n_estimators=150, min_samples_leaf=10, max_features=0.5,
                                     random_state=C.SEED, n_jobs=-1),
        "hgb": HistGradientBoostingClassifier(learning_rate=0.05, max_depth=3, max_iter=120,
                                              l2_regularization=1.0, random_state=C.SEED),
    }


def _spearman(y, p):
    return stats.spearmanr(y, p)[0] if np.std(p) > 0 else 0.0


REG_SCORING = {"r2": "r2", "mae": "neg_mean_absolute_error",
               "spearman": make_scorer(_spearman)}
CLF_SCORING = {"auroc": "roc_auc", "pr_auc": "average_precision", "brier": "neg_brier_score"}


def make_pipeline(columns, model) -> Pipeline:
    return Pipeline([("prep", make_preprocessor(columns)), ("model", model)])


def cv_compare(df: pd.DataFrame, target: str, task: str, n_splits=5, n_repeats=2) -> pd.DataFrame:
    """Per-fold scores for every (feature set, model). Identical folds across feature sets
    (fixed seed) so differences can be tested as paired."""
    if task == "regression":
        y, models, scoring = df[target], regressors(), REG_SCORING
        cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=C.SEED)
    else:
        y, models, scoring = df[f"{target}_high"], classifiers(), CLF_SCORING
        cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=C.SEED)
    rows = []
    for fs_name, cols in FEATURE_SETS.items():
        for m_name, model in models.items():
            res = cross_validate(make_pipeline(cols, model), df[cols], y, cv=cv, scoring=scoring)
            for k in range(len(res["fit_time"])):
                row = {"task": task, "target": target, "feature_set": fs_name, "model": m_name, "fold": k}
                for s in scoring:
                    v = res[f"test_{s}"][k]
                    row[s] = -v if s in ("mae", "brier") else v
                rows.append(row)
    return pd.DataFrame(rows)


def nadeau_bengio(diffs: np.ndarray, n_train: int, n_test: int) -> tuple[float, float, float]:
    """Corrected resampled t-test (Nadeau & Bengio 2003) for repeated-CV score differences.
    Plain paired t-tests over repeated CV are anti-conservative because folds overlap."""
    diffs = np.asarray(diffs, float)
    k = len(diffs)
    var = diffs.var(ddof=1)
    if var == 0:
        return float(diffs.mean()), 0.0, 1.0
    t = diffs.mean() / np.sqrt((1 / k + n_test / n_train) * var)
    p = 2 * stats.t.sf(abs(t), k - 1)
    return float(diffs.mean()), float(t), float(p)


def bootstrap_metric(y, pred, metric, n_boot=1000, seed=C.SEED):
    """Point estimate and 95% bootstrap CI for metric(y, pred) on a held-out set."""
    rng = np.random.default_rng(seed)
    y, pred = np.asarray(y), np.asarray(pred)
    vals = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        try:
            vals.append(metric(y[i], pred[i]))
        except ValueError:      # resample with a single class
            continue
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return metric(y, pred), lo, hi
