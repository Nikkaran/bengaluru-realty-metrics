# Bengaluru Residential Market Intelligence

**An end-to-end, memory-conscious data analytics portfolio project for the Indian real-estate market.**
Python for cleaning and predictive modelling, Power BI for executive reporting, and DAX for an interactive pricing simulator.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="scikit-learn" src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square&logo=scikitlearn&logoColor=white">
  <img alt="Power BI" src="https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=flat-square&logo=powerbi&logoColor=black">
  <img alt="DAX" src="https://img.shields.io/badge/DAX-What--If-0B1F3A?style=flat-square">
</p>

> **Portfolio note:** this scaffold contains the production-style Python pipeline,
> the three-page Power BI build guide, the exact DAX measures and this README.
> Add your built `.pbix` file and the three dashboard screenshots before publishing.
> Screenshot placeholders are provided below.

---

## The Business Problem

Residential property pricing in Bengaluru is opaque. Listing portals show individual
homes but rarely give a clean, comparable view of how price behaves across size,
configuration and micro-market. Buyers overpay, sellers underprice, and analysts spend
too much time cleaning inconsistent square-foot fields and rare location labels.

This project turns a messy, well-known Indian housing dataset into a decision-support
asset:

- **What does a typical home cost, and where is supply concentrated?**
- **Which locations carry a price-per-sq.ft. premium after removing extreme tails?**
- **What drives asking price, and what does the model rely on?**
- **What might a hypothetical 1,200 sq.ft., 3 BHK home cost in a selected area?**

The result is a compact market-intelligence report and a transparent what-if
simulator — built to run on an **8 GB laptop**, not a GPU workstation.

### Business value

| Stakeholder | Decision this enables |
|---|---|
| **Home buyer / investor** | Sanity-check an asking price against a comparable-segment benchmark and spot area-level premiums before shortlisting |
| **Seller / broker** | Understand how size, BHK and location position a listing against the cleaned market distribution |
| **Developer / market analyst** | See which configurations and micro-markets carry pricing power, and where supply is concentrated |
| **Data team** | Reuse a reproducible cleaning pipeline and a semantic model that separates descriptive KPIs from a clearly-labelled model estimate |

The project is intentionally framed around **decision support**, not price
prediction theatre. It shows what the data can support, what it cannot, and where a
human valuation or physical inspection is still required.

### Why this matters for the Indian job market

The project mirrors the work of a data analyst / BI consultant in an Indian real-estate,
consulting or consumer business:

| Capability | Demonstrated by |
|---|---|
| Messy real-world data cleaning | BHK parsing, square-foot ranges, units, rare location grouping, outlier treatment |
| Memory-aware engineering | Column projection, `float32`, sparse one-hot encoding, shallow trees, fold-by-fold training |
| Model validation discipline | 5-fold out-of-fold predictions, R²/MAE/RMSE reporting, no in-sample predictions in the dashboard |
| Semantic modelling | Clean one-fact Power BI model, disconnected parameter table, model-metadata table |
| DAX and scenario design | Weighted KPI, fallback logic, dynamic estimate, reset state |
| Executive communication | Dark-blue/white 3-page layout, KPI hierarchy, drill-through and insight copy |
| Business judgement | Clear limitations, no claim that listing prices are registered sale prices |

---

## Dashboard Gallery

> **Screenshots pending.** Build the report from
> [`dashboard_blueprint.md`](./dashboard_blueprint.md), export the three pages to PNG,
> and add them under `assets/screenshots/` using the exact names below.

| Page | Preview file |
|---|---|
| 01 · Executive Summary | `assets/screenshots/01-executive-summary.png` |
| 02 · Price Drivers | `assets/screenshots/02-price-drivers.png` |
| 03 · What-If Simulator | `assets/screenshots/03-what-if-simulator.png` |

### 01 · Executive Summary

*Market size, average price, area-weighted price per sq.ft., top locations, BHK mix
and premium micro-markets.*

> **Screenshot placeholder** — save the exported page as
> `assets/screenshots/01-executive-summary.png` (recommended 1920 × 1080 PNG).

<!-- After adding the file, replace this comment with:
![Executive Summary](assets/screenshots/01-executive-summary.png)
-->

**Suggested caption:** “Cleaned market view: listing volume, price level and BHK mix
across Bengaluru, with the `Other` location bucket excluded from rankings.”

### 02 · Price Drivers

*Price versus size, a location → BHK → bath decomposition tree, and the top 10 model
feature importances.*

> **Screenshot placeholder** — save the exported page as
> `assets/screenshots/02-price-drivers.png` (recommended 1920 × 1080 PNG).

<!-- After adding the file, replace this comment with:
![Price Drivers](assets/screenshots/02-price-drivers.png)
-->

**Suggested caption:** “Size dominates the model’s split activity; location and
configuration reveal premium pockets that a citywide average hides.”

### 03 · What-If Simulator

*A disconnected sq.ft. slider, BHK/location segment controls, a dynamic estimate
card and a row-level comparable-listings table.*

> **Screenshot placeholder** — save the exported page as
> `assets/screenshots/03-what-if-simulator.png` (recommended 1920 × 1080 PNG).

<!-- After adding the file, replace this comment with:
![What-If Simulator](assets/screenshots/03-what-if-simulator.png)
-->

**Suggested caption:** “A hypothesis-testing surface: set a target size, choose a
segment, and compare the indicative model benchmark with actual listings.”

---

## Project Architecture

```text
Kaggle train.csv
      │
      ▼
data_prep.py
  ├─ read only 6 required columns (projection at load time)
  ├─ parse BHK and total_sqft ranges / units
  ├─ normalise location; <10 retained labels → Other
  ├─ trim price-per-sq.ft. tails on log scale
  ├─ 5-fold Random Forest, out-of-fold predictions
  └─ write two analysis-ready CSVs
      │
      ├──────────────────────────────┐
      ▼                              ▼
cleaned_bengaluru_housing.csv   feature_importances.csv
      │                              │
      └──────────────┬───────────────┘
                     ▼
Power BI semantic model
  ├─ Fact table: Bengaluru Housing
  ├─ Metadata: Feature Importances (no relationship)
  ├─ Parameter: SqFt Parameter (disconnected)
  ├─ Page 1: Executive Summary
  ├─ Page 2: Price Drivers
  └─ Page 3: What-If Simulator
```

No database or cloud service is required. The pipeline is deliberately portable so
that it can run on a standard 8 GB Windows laptop.

### Tech stack

| Layer | Tools | Role |
|---|---|---|
| Data preparation | **Python**, pandas, NumPy | Selective loading, type coercion, outlier treatment, memory logging |
| Machine learning | **scikit-learn** | Sparse one-hot pipeline, median imputation, 5-fold Random Forest, OOF predictions |
| BI and semantic model | **Power BI Desktop** | Table import, relationships, star-style model, report authoring |
| Business logic | **DAX** | Weighted KPIs, disconnected What-If parameter, fallback benchmark, dynamic estimate |
| Delivery and documentation | Git, GitHub, Markdown | Version control, portfolio narrative, screenshots |

```text
Python 3.9+  ·  pandas  ·  NumPy  ·  scikit-learn  ·  Power BI Desktop  ·  DAX
```

---

## Dataset

| Item | Detail |
|---|---|
| Dataset | **Bengaluru House Price Data** (`train.csv`) |
| Source | [Kaggle dataset](https://www.kaggle.com/datasets/amitabhajoy/bengaluru-house-price-data) |
| Raw shape | 13,320 rows × 9 columns |
| Original fields | `area_type`, `availability`, `location`, `size`, `society`, `total_sqft`, `bath`, `balcony`, `price` |
| Target | `price` — asking price in **INR lakh** |
| Geography | Bengaluru, Karnataka, India |
| Time dimension | **None** (the dataset has no transaction date) |
| Data status | Historical listing snapshot; not verified registered transactions |

The dataset is **not committed** to this repository. Download it from Kaggle and
place `train.csv` in the project root. Refer to the Kaggle page for the current
licence and attribution requirements.

### Data dictionary — generated output

| Column | Type | Description |
|---|---|---|
| `property_id` | integer | Stable source row identifier, generated at load time |
| `location` | text | Whitespace-normalised location; labels with <10 retained rows → `Other` |
| `bhk` | integer | Bedrooms parsed from `size`; retained only for 1–10 BHK |
| `total_sqft` | float | Square feet; numeric ranges converted to their midpoint; unsupported units → blank/dropped |
| `bath` | float | Bathrooms; blanks retained for lineage, median-imputed inside each model fold |
| `balcony` | float | Balconies; blanks retained for lineage, median-imputed inside each model fold |
| `price_lakh` | float | Original asking price in INR lakh |
| `price_per_sqft` | float | `price_lakh × 100,000 ÷ total_sqft` |
| `predicted_price_lakh` | float | Out-of-fold Random Forest prediction (a model trained without that row) |

---

## Data Cleaning and Feature Engineering

Every decision below is implemented in [`data_prep.py`](./data_prep.py) and logged to
the console.

### 1. Projection before loading

The raw file has nine columns but the model needs six. The script reads with
`usecols`, so `area_type`, `availability` and `society` **never enter memory**. At load
time the six-column frame is approximately 1 MB in this dataset. This is better than
reading all columns and dropping them afterwards.

### 2. Size → BHK

`size` values such as `2 BHK`, `3 Bedroom` and `1 RK` are reduced to an integer with a
leading-number extraction. Unparseable sizes become missing and are dropped. Values
above 10 BHK are treated as non-residential/entry errors and removed; this excludes
only a handful of rows.

### 3. Square feet

`total_sqft` is a mixed-type field:

```text
"1056"          → 1056
"1000-1200"     → 1100
"1000 - 1200"   → 1100
"34.46Sq. Meter" → NaN (unsupported unit)
"4125Perch"     → NaN
```

Ranges are averaged; commas and dash variants are normalised. Unit-bearing values are
intentionally **not** converted, because silently mixing acres, perches and square
metres would corrupt the target relationship. The output records only square feet.
About 46 such entries are excluded in the reference run.

### 4. Location hygiene

Location strings are stripped and internal runs of whitespace are collapsed. After
the main validation and outlier filters, any location with fewer than 10 retained
listings is grouped into `Other`. This protects the one-hot encoder from creating
hundreds of tiny, unstable dummies. The reference run reduces 1,305 raw labels to
242 categories (including `Other`).

### 5. Price-per-sq.ft. outlier treatment

Price per sq.ft. is strongly right-skewed. The script computes **Tukey fences on the
log scale** (1.5 × IQR) and removes rows outside them. This is more defensible than an
arbitrary “delete anything above ₹10,000/sq.ft.” rule and avoids letting extreme tails
dominate the forest and the executive averages. The reference fences are approximately
**₹1,907–₹16,374 per sq.ft.**, removing 561 of 13,246 valid rows (4.2%).

### 6. Missing numeric fields

`bath` and `balcony` are left blank in the output so the lineage is visible. Inside
each cross-validation fold, the model pipeline median-imputes them using **training
fold only**, preventing validation leakage.

---

## Model

A deliberately small Random Forest is used as an interpretable baseline, not as a
production valuation engine.

| Setting | Value | Why |
|---|---|---|
| Algorithm | `RandomForestRegressor` | Handles non-linearity and mixed feature effects; no scaling required |
| Trees | 120 | Stable enough for a portfolio baseline, still light |
| `max_depth` | **10** | Primary variance and memory control |
| `min_samples_leaf` | 2 | Prevents one-row leaves |
| `max_features` | 0.6 | Faster, more decorrelated trees |
| Categorical treatment | Sparse one-hot for `location` | Avoids dense ~13k × 242 matrices |
| Numeric imputation | Median, inside each fold | No validation leakage |
| Features | `bhk`, `total_sqft`, `bath`, `balcony`, `location` | Physical + micro-market signals |
| Validation | 5-fold `KFold`, shuffled, seed 42 | Out-of-fold predictions for every row |

### Why out-of-fold predictions?

A standard tutorial trains on 100% of the data and writes predictions back to the same
rows. The dashboard would then display optimistic, in-sample predictions. This project
instead trains five models, predicts each holdout fold, and writes the combined
**out-of-fold** predictions. Each candidate in the cleaned dataset has a prediction
from a model that did not see it during training.

That makes the simulator and the model diagnostics more credible — and is an easy
point to defend in an interview.

### Reference results

Run on the Kaggle snapshot with Python 3.12, pandas 2.3.0 and scikit-learn 1.9.1:

| Metric | Out-of-fold value |
|---|---:|
| R² | **0.749** |
| MAE | **24.48 lakh** |
| RMSE | **45.77 lakh** |
| Clean rows | 12,685 |
| Runtime | Well under a minute, single-threaded, reference machine |

These are descriptive baseline results. Exact values can move with library versions
and random seeds. The relatively high MAE against a median asking price of ₹70 lakh is
a useful honesty signal: this model is suitable for **segment benchmarking**, not for
pricing an individual home.

Top model signals from the reference run:

| Rank | Feature | Importance share |
|---:|---|---:|
| 1 | `total_sqft` | 71.7% |
| 2 | `bath` | 14.7% |
| 3 | `bhk` | 6.8% |
| 4–10 | Individual location dummies | small, fragmented shares |

**Caveat:** Random Forest impurity importance splits location across many one-hot
columns. The small location bars do **not** mean location is unimportant; they mean
no single location dummy captures the combined geography effect. Importance also does
not imply causality.

---

## Power BI Report

The report follows a **Dark Blue + White** corporate theme: navy canvas, raised cards,
white type and a restrained cyan accent.

| Page | Purpose | Key visuals |
|---|---|---|
| **01 Executive Summary** | 20-second market read | 3 KPI cards, top 10 locations, BHK distribution, premium-location table, insight panel |
| **02 Price Drivers** | Explain the pattern | Price vs sq.ft. scatter, decomposition tree, top 10 feature importances |
| **03 What-If Simulator** | Test a scenario | Disconnected sq.ft. slider, BHK/location slicers, dynamic estimate card, comparable table |

Full coordinates, field wells, formatting, interactions and QA steps are in
[`dashboard_blueprint.md`](./dashboard_blueprint.md).
Copy-paste-ready measures and the disconnected table setup are in
[`dax_measures.txt`](./dax_measures.txt).

### KPI definitions

| Measure | Definition |
|---|---|
| Total Properties | `COUNTROWS('Bengaluru Housing')` |
| Average Price | `AVERAGE('Bengaluru Housing'[price_lakh])` |
| Average Price per Sq.Ft. | `SUM(price_lakh × 100,000) ÷ SUM(total_sqft)` — area-weighted, not an average of row ratios |
| Estimated Price | Target sq.ft. from the disconnected What-If table × the selected segment’s area-weighted model benchmark ÷ 100,000 |

The simulator uses a **minimum-five-comparable guardrail**. If the selected BHK/location
segment has fewer than five listings, the measure falls back to the citywide model
benchmark and labels the basis accordingly.

---

## Quick Start

### 1. Prerequisites

- Python 3.9+ (tested on 3.12)
- 8 GB RAM is sufficient
- Power BI Desktop (Windows) for the report layer

### 2. Get the data

Download `train.csv` from the
[Kaggle dataset page](https://www.kaggle.com/datasets/amitabhajoy/bengaluru-house-price-data)
and place it beside `data_prep.py`.

### 3. Install Python packages

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install pandas numpy scikit-learn
```

The code uses the `sparse_output` argument on `OneHotEncoder`, so install
**scikit-learn 1.2 or newer**. The reference run used scikit-learn 1.9.1.

### 4. Run the pipeline

```bash
python data_prep.py
```

Expected console output includes selective-load memory, cleaning counts, out-of-fold
metrics, and the paths of the two outputs:

```text
cleaned_bengaluru_housing.csv
feature_importances.csv
```

Useful options:

```bash
# Custom paths
python data_prep.py --input /path/to/train.csv --output-dir outputs

# Lower memory / faster experiment on a very tight machine
python data_prep.py --n-estimators 80

# Use all CPU cores if you have RAM and thermal headroom
python data_prep.py --jobs -1

# Fewer folds (less robust; useful only for smoke tests)
python data_prep.py --cv-folds 3
```

The default is `--jobs 1`: the dataset is small, the run completes in well under a
minute, and a single-worker forest has the lowest peak RAM. Use `--jobs -1` when you
want speed and have memory headroom.

### 5. Build the Power BI report

1. Open Power BI Desktop → **Get data** → **Text/CSV**.
2. Import `cleaned_bengaluru_housing.csv`; rename the table to `Bengaluru Housing`.
3. Import `feature_importances.csv`; rename it to `Feature Importances`.
4. Confirm there are **no relationships** between the two tables.
5. Create the disconnected `SqFt Parameter` What-If table from
   [`dax_measures.txt`](./dax_measures.txt).
6. Add the measures exactly as written, using a `_Measures` table.
7. Follow [`dashboard_blueprint.md`](./dashboard_blueprint.md) page by page.
8. Export three PNG screenshots into `assets/screenshots/` and uncomment the image
   tags in the gallery above.

Add the finished `.pbix` to the repository root as
`bengaluru_market_intelligence.pbix`.

---

## Repository Structure

```text
bengaluru-market-intelligence/
├── data_prep.py                     # cleaning + OOF model + CSV outputs
├── dashboard_blueprint.md           # 3-page Power BI layout and UX spec
├── dax_measures.txt                 # exact DAX, What-If setup, formatting
├── README.md                        # this file
├── train.csv                        # add from Kaggle (not committed)
├── cleaned_bengaluru_housing.csv    # generated
├── feature_importances.csv          # generated
├── bengaluru_market_intelligence.pbix  # add after building the report
└── assets/
    └── screenshots/
        ├── 01-executive-summary.png  # placeholder
        ├── 02-price-drivers.png      # placeholder
        └── 03-what-if-simulator.png  # placeholder
```

Suggested `.gitignore` entries:

```gitignore
.venv/
__pycache__/
train.csv
```

Commit the generated CSVs if you want the dashboard to be reproducible from a fresh
clone without downloading Kaggle data. They are small (under 1 MB).

---

## What Makes This Different From a Standard Tutorial

- **It keeps validation honest.** Out-of-fold predictions, fold-local imputation
  and metrics reported on unseen rows. The only full-snapshot pre-processing is
  descriptive cleaning (outlier fences and location grouping) applied to create a
  stable reporting population before cross-validation.
- **It respects the 8 GB constraint.** Column projection at read, sparse encoding,
  shallow trees, sequential folds, and explicit memory logs.
- **It distinguishes a listing price from a transaction price.** The README and
  dashboard both carry that caveat.
- **It uses weighted market rates.** A ₹5 crore home should not have the same influence
  as a ₹30 lakh home when computing the city’s price per sq.ft.
- **It gives the what-if page a real sample-size guardrail** instead of producing a
  confident answer from two comparable listings.
- **It treats dashboard design as part of analytics.** The blueprint specifies
  coordinates, field wells, interaction rules and accessibility, not just chart names.

---

## Limitations

- **Asking prices, not registered sales.** Listing prices can differ materially from
  actual transaction prices. The dataset does not include negotiation outcomes.
- **No time dimension.** The snapshot has no transaction date, so the dashboard cannot
  make seasonality or market-cycle claims.
- **Limited property attributes.** Floor, age, facing, amenities, parking and condition
  are absent. `area_type`, `availability` and `society` were deliberately excluded to
  keep the pipeline lean, so plots and built-up apartments are pooled; the
  price-per-sq.ft. filter reduces, but does not eliminate, that heterogeneity.
- **Geographic granularity varies.** After rare grouping, 242 categories remain, but
  some labels are broad corridors while others are micro-layouts.
- **Outlier trimming is a defensible choice, not ground truth.** The log-IQR rule
  removes some legitimate luxury inventory from the modelling and KPI population.
- **The simulator is a benchmark, not an automated valuation model.** It applies a
  selected-segment model rate to a hypothetical area; the trained forest itself is not
  deployed into Power BI.
- **Feature importance is not causality.** Location effects are fragmented across
  one-hot columns.

---

## Roadmap

- [ ] Add a time dimension if a dated Bengaluru transaction dataset becomes available.
- [ ] Compare Random Forest with HistGradientBoosting and regularised linear baselines.
- [ ] Add SHAP-based local explanations for property-level estimates.
- [ ] Introduce geospatial features (distance to tech parks, metro, ring road).
- [ ] Package the final estimator behind a FastAPI endpoint and connect it to Power BI.
- [ ] Publish the report to Power BI Service with row-level security by region.
- [ ] Add the three dashboard screenshots and a 60-second Loom walkthrough.

---

## Skills Demonstrated

`Python` · `pandas` · `scikit-learn` · `Random Forest` · `cross-validation` ·
`feature engineering` · `outlier treatment` · `memory optimisation` ·
`Power BI` · `DAX` · `What-If parameters` · `data modelling` · `dashboard UX` ·
`data storytelling` · `business communication`

---

## Author

**[Your Name]**
Data Analyst / BI Consultant · Bengaluru, India
[LinkedIn](https://www.linkedin.com/in/your-handle) · [Email](mailto:you@example.com) · [Portfolio](https://your-portfolio.example)

> Replace the placeholders above before publishing. Add a short 2–3 line bio that
> connects this project to the roles you are targeting.

## Licence and Credits

- Code in this repository: add your preferred licence (for example, MIT) and include a
  `LICENSE` file before distributing.
- Dataset: **Bengaluru House Price Data**, available on
  [Kaggle](https://www.kaggle.com/datasets/amitabhajoy/bengaluru-house-price-data).
  The dataset is not redistributed here. Follow the Kaggle page for licence and
  attribution terms.
- Built with Python, pandas, scikit-learn and Microsoft Power BI.
