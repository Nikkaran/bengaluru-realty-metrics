#!/usr/bin/env python3
"""
data_prep.py
============
Memory-conscious data preparation and baseline modelling for the
Kaggle "Bengaluru House Price Data" (train.csv).

What this script does
---------------------
1. Reads only the six columns required for modelling (projection pushdown).
2. Parses "size" (2 BHK / 3 Bedroom) into a numeric bhk feature.
3. Parses "total_sqft", including ranges such as "1000-1200" -> 1100.
4. Normalises location names and groups locations with fewer than 10
   retained listings into "Other".
5. Removes price-per-sq.ft. outliers using Tukey fences on the log scale
   (price per sq.ft. is strongly right-skewed).
6. Trains a deliberately small Random Forest with 5-fold out-of-fold (OOF)
   predictions. Every row receives a prediction from a model that did not
   see that row during training.
7. Writes cleaned_bengaluru_housing.csv and feature_importances.csv.

The script is designed to run comfortably on an 8 GB laptop. It avoids
loading area_type, availability and society, uses sparse one-hot encoding,
float32 where practical, and trains folds sequentially.

Usage
-----
    python data_prep.py
    python data_prep.py --input train.csv --output-dir .
    python data_prep.py --cv-folds 3 --n-estimators 80

Requirements: pandas, numpy, scikit-learn (see README.md).
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INPUT_COLUMNS = ("location", "size", "total_sqft", "bath", "balcony", "price")
UNUSED_COLUMNS = ("area_type", "availability", "society")
NUMERIC_FEATURES = ("bhk", "total_sqft", "bath", "balcony")
CATEGORICAL_FEATURES = ("location",)
TARGET = "price_lakh"

MAX_BHK = 10                 # residential sanity rule; filters hostel/commercial entries
MIN_LOCATION_COUNT = 10      # locations below this count become "Other"
OUTLIER_IQR_MULTIPLIER = 1.5 # Tukey fence on log(price per sq.ft.)
OOF_FOLDS = 5
N_ESTIMATORS = 120
MAX_DEPTH = 10
RANDOM_STATE = 42
CLEANED_FILENAME = "cleaned_bengaluru_housing.csv"
IMPORTANCE_FILENAME = "feature_importances.csv"
KAGGLE_URL = "https://www.kaggle.com/datasets/amitabhajoy/bengaluru-house-price-data"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def frame_memory_mb(frame: pd.DataFrame) -> float:
    """Return approximate in-memory size, including object/category contents."""
    return float(frame.memory_usage(deep=True).sum() / (1024**2))


def report_memory(label: str, frame: pd.DataFrame) -> None:
    print(f"[memory] {label:<28} {frame_memory_mb(frame):6.2f} MB  "
          f"({len(frame):,} rows)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean Bengaluru house-price data and create OOF price estimates."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("train.csv"),
        help="Path to Kaggle train.csv (default: ./train.csv).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory for the two CSV outputs (default: current directory).",
    )
    parser.add_argument(
        "--cv-folds",
        type=int,
        default=OOF_FOLDS,
        help=f"Number of out-of-fold splits (default: {OOF_FOLDS}).",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=N_ESTIMATORS,
        help=f"Number of trees per forest (default: {N_ESTIMATORS}).",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help=(
            "Parallel jobs for the forest (default: 1, lowest peak memory). "
            "Use -1 for all cores on a machine with headroom."
        ),
    )
    return parser.parse_args()


def load_required_columns(path: Path) -> pd.DataFrame:
    """Read only the modelling columns so the three unused fields never enter RAM."""
    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {path}\n"
            f"Download train.csv from {KAGGLE_URL} and place it beside this script."
        )

    header = pd.read_csv(path, nrows=0)
    available = set(header.columns)
    missing = set(INPUT_COLUMNS) - available
    if missing:
        raise ValueError(
            "train.csv is missing required column(s): "
            + ", ".join(sorted(missing))
            + f"\nExpected columns: {', '.join(INPUT_COLUMNS)}"
        )

    loaded_dtypes = {
        "location": "category",
        "size": "category",
        "bath": "float32",
        "balcony": "float32",
        "price": "float32",
    }
    frame = pd.read_csv(
        path,
        usecols=list(INPUT_COLUMNS),  # column projection happens at read time
        dtype=loaded_dtypes,
    )

    unused_present = sorted(available.intersection(UNUSED_COLUMNS))
    skipped = ", ".join(unused_present) if unused_present else "none"
    print(f"[load]   {len(frame):,} rows x {len(frame.columns)} required columns")
    print(f"[load]   Not loaded (unnecessary): {skipped}")
    return frame


def parse_total_sqft(series: pd.Series) -> pd.Series:
    """
    Convert total_sqft to float32.

    Supported:
      * plain numbers: "1056" -> 1056
      * ranges: "1000-1200" -> 1100
      * thousands separators and y-en/em dashes

    Values expressed in other units (Acres, Sq. Meter, Perch, etc.) are
    intentionally coerced to NaN rather than silently mixed with square feet.
    """
    text = (
        series.astype("string")
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace(r"[\u2013\u2014]", "-", regex=True)
    )

    plain = pd.to_numeric(text, errors="coerce")
    bounds = text.str.extract(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$")
    low = pd.to_numeric(bounds[0], errors="coerce")
    high = pd.to_numeric(bounds[1], errors="coerce")
    midpoint = (low + high) / 2

    parsed = plain.where(plain.notna(), midpoint)
    return parsed.astype("float32")


def pretty_feature_name(raw_name: str) -> str:
    """Turn sklearn's transformer-prefixed names into chart-friendly labels."""
    if raw_name.startswith("num__"):
        return raw_name.removeprefix("num__")
    if raw_name.startswith("loc__"):
        label = raw_name.removeprefix("loc__")
        # ColumnTransformer also includes the input column name.
        if label.startswith("location_"):
            label = label.removeprefix("location_")
        return f"location = {label}"
    return raw_name


def build_pipeline(n_estimators: int, jobs: int) -> Pipeline:
    """Small sparse-input forest; feature scaling is not needed for trees."""
    numeric_transformer = SimpleImputer(strategy="median")

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=True,
        dtype=np.float32,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, list(NUMERIC_FEATURES)),
            ("loc", categorical_transformer, list(CATEGORICAL_FEATURES)),
        ],
        remainder="drop",
        sparse_threshold=0.3,
        verbose_feature_names_out=True,
    )

    forest = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=MAX_DEPTH,          # primary RAM / variance control
        min_samples_leaf=2,
        min_samples_split=2,
        max_features=0.6,
        bootstrap=True,
        n_jobs=jobs,
        random_state=RANDOM_STATE,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", forest),
        ]
    )


def format_metrics_block(name: str, r2: float, mae: float, rmse: float) -> str:
    return f"{name:<12} R2={r2:7.4f}  MAE={mae:8.2f} lakh  RMSE={rmse:8.2f} lakh"


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()
    if args.cv_folds < 2:
        raise ValueError("--cv-folds must be at least 2.")
    if args.n_estimators < 10:
        raise ValueError("--n-estimators must be at least 10.")

    started = time.perf_counter()
    raw = load_required_columns(args.input)
    report_memory("after selective load", raw)

    # Stable identifier so the Power BI detail table can show individual homes.
    raw = raw.reset_index(drop=True)
    raw.insert(0, "property_id", np.arange(1, len(raw) + 1, dtype=np.int32))

    # --- Size -> BHK ------------------------------------------------------
    size_numeric = pd.to_numeric(
        raw["size"].astype("string").str.extract(r"(\d+)", expand=False),
        errors="coerce",
    )
    raw["bhk"] = size_numeric.astype("float32")
    unparsed_size = int(raw["size"].notna().sum() - raw["bhk"].notna().sum())

    # --- Square feet ------------------------------------------------------
    raw_sqft_missing = int(raw["total_sqft"].isna().sum())
    parsed_sqft = parse_total_sqft(raw["total_sqft"])
    sqft_unparsed = int(parsed_sqft.isna().sum() - raw_sqft_missing)
    raw["total_sqft"] = parsed_sqft

    # --- Target and numeric hygiene --------------------------------------
    raw = raw.rename(columns={"price": TARGET})
    raw[TARGET] = pd.to_numeric(raw[TARGET], errors="coerce").astype("float32")

    # --- Location text normalisation (rare grouping happens later) --------
    location_text = (
        raw["location"]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    raw["location"] = (
        location_text.mask(location_text.eq(""), pd.NA)
        .fillna("Unknown")
        .astype("category")
    )

    report_memory("after field cleaning", raw)

    # --- Validity filters -------------------------------------------------
    row_count_loaded = len(raw)
    valid_mask = (
        raw[TARGET].gt(0)
        & raw["total_sqft"].gt(0)
        & raw["bhk"].between(1, MAX_BHK)
    )
    df = raw.loc[valid_mask].copy()
    del raw
    gc.collect()

    rejected_invalid = row_count_loaded - len(df)
    print(
        f"[clean]  Dropped {rejected_invalid:,} invalid/incomplete rows "
        f"(missing target, non-positive area, or BHK outside 1-{MAX_BHK})"
    )
    print(
        f"[clean]  Unparsed sizes: {unparsed_size:,}; "
        f"unparsed/non-sq.ft. area values: {max(sqft_unparsed, 0):,}"
    )

    # Bath and balcony stay missing in the output for data lineage; the model
    # pipeline imputes them with the training-fold median.
    for col in ("bath", "balcony"):
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")

    # --- Price-per-sq.ft. outlier treatment -------------------------------
    df["price_per_sqft"] = (
        df[TARGET].astype("float64") * 100_000 / df["total_sqft"].astype("float64")
    ).astype("float32")

    positive_psf = df.loc[df["price_per_sqft"] > 0, "price_per_sqft"].astype("float64")
    log_psf = np.log(positive_psf)
    q1, q3 = np.quantile(log_psf, [0.25, 0.75])
    iqr = q3 - q1
    lower_log = q1 - OUTLIER_IQR_MULTIPLIER * iqr
    upper_log = q3 + OUTLIER_IQR_MULTIPLIER * iqr
    lower_fence, upper_fence = np.exp(lower_log), np.exp(upper_log)

    before_outliers = len(df)
    df = df.loc[df["price_per_sqft"].between(lower_fence, upper_fence)].copy()
    removed_outliers = before_outliers - len(df)
    print(
        f"[clean]  Price/sq.ft. log-IQR fences: "
        f"INR {lower_fence:,.0f} - {upper_fence:,.0f}; "
        f"removed {removed_outliers:,} rows ({removed_outliers / before_outliers:.2%})"
    )

    # --- Rare locations (<10 retained listings) -> Other -----------------
    location_counts = df["location"].value_counts()
    rare_locations = location_counts[location_counts < MIN_LOCATION_COUNT].index
    rare_rows = int(df["location"].isin(rare_locations).sum())

    location_as_text = df["location"].astype("string")
    df["location"] = (
        location_as_text.mask(location_as_text.isin(rare_locations), "Other")
        .astype("category")
    )
    df["location"] = df["location"].cat.remove_unused_categories()

    print(
        f"[clean]  Rare locations grouped: {len(rare_locations):,} labels / "
        f"{rare_rows:,} rows -> 'Other'"
    )
    print(f"[clean]  Final locations: {df['location'].nunique():,} (including Other)")
    print(f"[clean]  Final modelling rows: {len(df):,}")
    report_memory("final cleaned frame", df)

    # --- Features / target -------------------------------------------------
    feature_columns = list(NUMERIC_FEATURES) + list(CATEGORICAL_FEATURES)
    X = df[feature_columns].copy()
    y = df[TARGET].to_numpy(dtype=np.float32)

    base_pipeline = build_pipeline(args.n_estimators, args.jobs)
    folds = KFold(n_splits=args.cv_folds, shuffle=True, random_state=RANDOM_STATE)

    oof_pred = np.empty(len(df), dtype=np.float32)
    fold_metrics: list[tuple[int, float, float, float]] = []
    importance_sum: pd.Series | None = None

    print(
        f"[model]  RandomForestRegressor: {args.n_estimators} trees, "
        f"max_depth={MAX_DEPTH}, sparse one-hot, {args.cv_folds}-fold OOF"
    )

    for fold_no, (train_idx, test_idx) in enumerate(folds.split(X), start=1):
        fold_model = clone(base_pipeline)
        fold_model.fit(X.iloc[train_idx], y[train_idx])

        predictions = fold_model.predict(X.iloc[test_idx]).astype(np.float32)
        oof_pred[test_idx] = predictions

        fold_r2 = r2_score(y[test_idx], predictions)
        fold_mae = mean_absolute_error(y[test_idx], predictions)
        fold_rmse = float(np.sqrt(mean_squared_error(y[test_idx], predictions)))
        fold_metrics.append((fold_no, fold_r2, fold_mae, fold_rmse))

        fitted_preprocessor = fold_model.named_steps["preprocessor"]
        fitted_forest = fold_model.named_steps["model"]
        names = fitted_preprocessor.get_feature_names_out()
        importances = fitted_forest.feature_importances_
        fold_series = pd.Series(importances, index=names, dtype="float64")
        importance_sum = (
            fold_series if importance_sum is None
            else importance_sum.add(fold_series, fill_value=0.0)
        )

        print(
            f"[model]  Fold {fold_no}/{args.cv_folds}  "
            f"train={len(train_idx):,} test={len(test_idx):,}  "
            + format_metrics_block("", fold_r2, fold_mae, fold_rmse).strip()
        )

        del fold_model, fitted_preprocessor, fitted_forest, predictions
        gc.collect()

    if np.isnan(oof_pred).any():
        raise RuntimeError("Some rows did not receive an out-of-fold prediction.")

    overall_r2 = r2_score(y, oof_pred)
    overall_mae = mean_absolute_error(y, oof_pred)
    overall_rmse = float(np.sqrt(mean_squared_error(y, oof_pred)))

    print("[model]  Out-of-fold performance (all rows):")
    print("         " + format_metrics_block("Overall", overall_r2, overall_mae, overall_rmse))

    mean_r2 = float(np.mean([m[1] for m in fold_metrics]))
    std_r2 = float(np.std([m[1] for m in fold_metrics]))
    print(f"         Fold R2 mean +/- sd: {mean_r2:.4f} +/- {std_r2:.4f}")

    # --- Outputs -----------------------------------------------------------
    df["predicted_price_lakh"] = np.round(oof_pred, 2).astype("float32")

    output_columns = [
        "property_id",
        "location",
        "bhk",
        "total_sqft",
        "bath",
        "balcony",
        TARGET,
        "price_per_sqft",
        "predicted_price_lakh",
    ]
    cleaned = df.loc[:, output_columns].copy()
    cleaned["bhk"] = cleaned["bhk"].astype("int8")
    for col in ("total_sqft", "bath", "balcony", TARGET, "price_per_sqft",
                "predicted_price_lakh"):
        cleaned[col] = cleaned[col].round(2)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = output_dir / CLEANED_FILENAME
    importances_path = output_dir / IMPORTANCE_FILENAME

    cleaned.to_csv(cleaned_path, index=False, encoding="utf-8", float_format="%.2f")

    if importance_sum is None:
        raise RuntimeError("No feature importances were collected.")

    mean_importance = (importance_sum / args.cv_folds).sort_values(ascending=False)
    importance_share = mean_importance / mean_importance.sum() * 100.0

    top_importances = (
        pd.DataFrame(
            {
                "feature": [pretty_feature_name(name) for name in mean_importance.index],
                "importance": mean_importance.values,
                "importance_pct": importance_share.values,
            }
        )
        .head(10)
        .reset_index(drop=True)
    )
    top_importances.insert(0, "rank", np.arange(1, len(top_importances) + 1))
    top_importances["importance"] = top_importances["importance"].round(6)
    top_importances["importance_pct"] = top_importances["importance_pct"].round(3)
    top_importances.to_csv(importances_path, index=False, encoding="utf-8")

    elapsed = time.perf_counter() - started
    print("\n[done]   Files written:")
    print(f"         - {cleaned_path.resolve()} ({len(cleaned):,} rows)")
    print(f"         - {importances_path.resolve()} ({len(top_importances)} features)")
    print(f"[done]   Runtime: {elapsed:,.1f} seconds")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"[error]  {exc}", file=sys.stderr)
        sys.exit(1)
