# Power BI Dashboard Blueprint
## Bengaluru Residential Market Intelligence

A three-page corporate report built on `cleaned_bengaluru_housing.csv`.
The design language is **Dark Blue + White**: a deep navy canvas, raised navy
cards, white type, and a restrained cyan accent. The goal is a boardroom-ready
look that still reads clearly on a laptop screen.

---

## 1. Report Specification

| Item | Specification |
|---|---|
| Report name | Bengaluru Residential Market Intelligence |
| Canvas | 1280 × 720 px (16:9), custom fit |
| Pages | 01 Executive Summary · 02 Price Drivers · 03 What-If Simulator |
| Page background | `#081A2F` |
| Header background | `#061529` |
| Card background | `#0F2A48` |
| Card border | `#27496D`, 0.5 px, 8 px radius |
| Primary text | `#FFFFFF` |
| Secondary text | `#AFC6DD` |
| Accent | `#38BDF8` (cyan-blue) |
| Secondary accent | `#60A5FA` |
| Positive | `#34D399` |
| Warning | `#FBBF24` |
| Negative | `#F87171` |
| Font | Segoe UI (Semibold for headings, Regular for body) |
| Grid | 12 columns; 24 px outer margin; 16 px gutters |
| Shadows | Off |
| Chart borders | Off; use card containers for grouping |
| Page transition | None |

### Type scale

| Role | Size / weight | Colour |
|---|---|---|
| Page title | 20 pt Semibold | `#FFFFFF` |
| Page subtitle | 9.5 pt Regular | `#AFC6DD` |
| KPI value | 30–44 pt Semibold | `#FFFFFF` |
| KPI label | 9 pt Semibold, uppercase, 0.5 pt letter spacing | `#AFC6DD` |
| Visual title | 12 pt Semibold | `#FFFFFF` |
| Axis / legend | 8.5 pt Regular | `#C7D7E8` |
| Body / annotation | 9.5 pt Regular | `#C7D7E8` |
| Source note | 7.5 pt Regular | `#7F9AB6` |

### Global chrome (all pages)

1. **Header block** — rectangle `x=0, y=0, w=1280, h=72`, fill `#061529`.
   Bottom accent rule `x=24, y=72, w=1232, h=2`, fill `#38BDF8`, 35% transparency.
2. **Page title** — text box `x=24, y=14, w=720, h=32`.
3. **Page subtitle** — text box `x=24, y=44, w=760, h=20`.
4. **Navigation** — three buttons at `y=20, h=32, w=96`, 8 px gaps:
   `x=952` "Executive" · `x=1056` "Drivers" · `x=1160` "Simulator".
   Active tab fill `#1D4ED8`, white text; inactive tab fill `#0F2A48`,
   1 px border `#315273`. Action = Page navigation.
5. **Footer** — rule at `y=694`, full width inside margins, `#27496D`, 0.5 px.
   Left text box `x=24, y=698, w=760, h=16`: source and cleaning note.
   Right text box `x=960, y=698, w=296, h=16`, right-aligned:
   `Portfolio project · [Your Name]`.
6. Add alt text to every visual. Do not communicate meaning by colour alone.

### Data model

| Table | Source | Relationship |
|---|---|---|
| `Bengaluru Housing` | `cleaned_bengaluru_housing.csv` | Fact table |
| `Feature Importances` | `feature_importances.csv` | **No relationship** |
| `SqFt Parameter` | What-If numeric-range table | **Disconnected** |
| `_Measures` | Empty table for measure organisation | No relationship |

- Rename the CSV query to exactly `Bengaluru Housing`.
- Rename the importance table to `Feature Importances`.
- Confirm there are no auto-detected relationships.
- Hide technical fields if desired: `property_id` can stay visible for the detail table;
  it makes that table row-addressable.
- Format model columns:
  `price_lakh`, `predicted_price_lakh`, `price_per_sqft` → Fixed decimal, 2 places;
  `total_sqft` → Whole number; `bhk` → Whole number.
- Apply measures exactly as listed in `dax_measures.txt`.

---

## 2. Page 01 — Executive Summary

**Purpose:** give a non-technical stakeholder the size, price level, geographic
concentration and product mix of the cleaned Bengaluru market in under
20 seconds. No filter controls are required; cross-filtering is the interaction.

### Wireframe

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ HEADER · Bengaluru Residential Market · Executive Summary      [nav]     │
├───────────────┬───────────────┬───────────────┬──────────────────────────┤
│ TOTAL         │ AVERAGE       │ AVERAGE       │                          │
│ PROPERTIES    │ PRICE         │ PRICE / SQ.FT │                          │
├───────────────┴───────────────┴───────────────┴──────────────────────────┤
│ TOP 10 LOCATIONS BY LISTINGS (bar)        │ BHK DISTRIBUTION (column)    │
│                                           │                              │
├───────────────────────────────────────────┴──────────────────────────────┤
│ PREMIUM LOCATION TABLE                    │ INSIGHT / TAKEAWAYS           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Visual specification

| # | Visual type | Title | Position (x, y, w, h) | Exact fields and setup |
|---|---|---|---|---|
| 1.1 | Card (new), KPI | TOTAL PROPERTIES | `24, 88, 400, 112` | Value: `[Total Properties]`. Reference label: "Cleaned listings". Add 3 px cyan bar at bottom-left inside card. |
| 1.2 | Card (new), KPI | AVERAGE PRICE | `440, 88, 400, 112` | Value: `[Average Price]`. Reference label: "INR lakh · unweighted mean". Same accent bar. |
| 1.3 | Card (new), KPI | AVERAGE PRICE / SQ.FT. | `856, 88, 400, 112` | Value: `[Average Price per Sq.Ft]`. Reference label: "Area-weighted market rate". Same accent bar. |
| 1.4 | Horizontal bar chart | Top 10 locations by listings | `24, 216, 752, 252` | **Y-axis:** `'Bengaluru Housing'[location]`. **X-axis:** `[Total Properties]`. **Tooltips:** `[Average Price]`, `[Average Price per Sq.Ft]`, `[Total Properties]`. Visual filter: `location` is not `Other`; Top N = 10 by `[Total Properties]`. Sort descending. Data labels on, axis labels 8.5 pt, gridlines off, bars `#38BDF8`, corner radius 2. |
| 1.5 | Clustered column chart | BHK distribution | `792, 216, 464, 252` | **X-axis:** `'Bengaluru Housing'[bhk]`. **Y-axis:** `[Total Properties]`. **Tooltips:** `[Average Price]`, `[Average Price per Sq.Ft]`. Sort by `bhk` ascending. Data labels on, bars `#60A5FA`, gridlines off. Turn off the Y-axis title to save space. |
| 1.6 | Table | Premium pockets | `24, 484, 752, 192` | Columns: `location`, `[Total Properties]`, `[Average Price]`, `[Average Price per Sq.Ft]`. Filters: `location` is not `Other`; first restrict to locations with `[Total Properties] >= 25`, then Top N = 5 by `[Average Price]`. Sort `[Average Price per Sq.Ft]` descending. Headers fill `#0B223D`, body white, row banding `#0D2744` / `#102A4C`. Add a subtle data bar on `[Average Price per Sq.Ft]`. |
| 1.7 | Text box / Smart narrative | What the numbers say | `792, 484, 464, 192` | Preferred: Smart narrative with this prompt: “In the current view, there are [Total Properties] listings at an average price of [Average Price] lakh and an area-weighted rate of [Average Price per Sq.Ft] per sq.ft.” Add two static insight bullets after refreshing. Fallback: text box with heading and 3 bullets. |

### Build notes for Page 01

- The three KPI cards must be equal width; align their top and bottom edges.
- Add card titles only; no external labels floating outside the cards.
- Use `location` as a drill-through field to Page 02. On the bar chart a user can
  right-click a location and choose **Drill through → Price Drivers**.
- Recommended insight copy after the reference data refresh (replace if the cleaned
  snapshot changes):
  - “2 BHK and 3 BHK together account for roughly four-fifths of cleaned listings.”
  - “Whitefield, Sarjapur Road and Electronic City lead named-location supply.”
  - “Rajaji Nagar and Malleshwaram carry a visible price-per-sq.ft. premium among
    locations with at least 25 listings.”
- The `Other` group is deliberately excluded from location rankings, but it remains
  in the KPI totals. Add a footnote in the footer: “Other = locations with fewer than
  10 retained listings.”
- Tooltip pages are optional. If time permits, build a single “Location tooltip” page
  with a tiny sparkline-like price/sq.ft. comparison; this is not required for v1.

### Interaction

- Default cross-filtering on. Selecting a bar filters the BHK chart, table and KPIs.
- Selecting a BHK column filters the location chart and table.
- Keep the insight panel filtered by both charts.
- Bookmark **P1 Reset** (Data on, Display off) and add a small reset icon in the header
  if the report will be published with filters.

---

## 3. Page 02 — Price Drivers

**Purpose:** move from description to explanation: what correlates with price,
which combinations create premium pockets, and which variables the model relies on.
Supports drill-through from a selected location on Page 01.

### Wireframe

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ HEADER · Price Drivers                                    [nav]          │
├──────────────────────────────────────────────┬───────────────────────────┤
│ PRICE VS SIZE (scatter)                      │ DECOMPOSITION TREE        │
│                                              │ Location → BHK → Bath     │
├──────────────────────────────────────────────┴───────────────────────────┤
│ FEATURE IMPORTANCE (top 10, horizontal bars) │ MODEL NOTES / READ-OUT     │
└──────────────────────────────────────────────────────────────────────────┘
```

### Visual specification

| # | Visual type | Title | Position (x, y, w, h) | Exact fields and setup |
|---|---|---|---|---|
| 2.1 | Scatter chart | Price vs size | `24, 88, 752, 320` | **X-axis:** `'Bengaluru Housing'[total_sqft]`. **Y-axis:** `'Bengaluru Housing'[price_lakh]`. **Details:** `'Bengaluru Housing'[property_id]` (one point per home; set summarisation to **Don't summarize**). **Legend:** none. **Tooltips:** `location`, `bhk`, `bath`, `price_per_sqft`, `predicted_price_lakh`. Marker: 3 px, fill `#38BDF8`, transparency 65%, no border. Turn on high-density sampling. Axis titles: “Total area (sq.ft.)” and “Asking price (INR lakh)”. Gridlines 15% opacity. Axis ranges: automatic for v1; if the presentation view is too dense, clip at 4,000 sq.ft. / 600 lakh and state that the axes are clipped. |
| 2.2 | Decomposition tree | What creates a premium? | `792, 88, 464, 320` | **Analyze:** `[Average Price]`. **Explain by:** `location`, `bhk`, `bath`. Expand root → `location` (High value) → `bhk` (High value). Add a visual filter `location` is not `Other`. Conditional formatting on the measure bars in cyan. Title plus italic subtitle “Average asking price, INR lakh”. |
| 2.3 | Horizontal bar chart | Model feature importance (top 10) | `24, 424, 752, 252` | **Y-axis:** `Feature Importances[feature]`. **X-axis:** `Feature Importances[importance_pct]`. **Tooltips:** `importance`, `importance_pct`. Sort by `importance_pct` descending; if bars appear small-to-large, reverse the axis. Data labels on, 1 decimal, white; bars `#38BDF8`; gridlines off. Top 10 only (the CSV is already truncated). |
| 2.4 | Text / Smart narrative panel | Reading the drivers | `792, 424, 464, 252` | Heading + four short blocks: (i) `Total sq.ft.` is the dominant split variable; (ii) `Bath` and `BHK` add property-type information; (iii) location enters as separate one-hot levels, so read the location rows individually; (iv) model snapshot from the reference run: R² 0.749, MAE 24.48 lakh, RMSE 45.77 lakh, 5-fold OOF. End with: “Importance ≠ causality.” |

### Build notes for Page 02

- **Drill-through setup:** Page information → Drill through → add
  `'Bengaluru Housing'[location]`. Add a back button top-left inside the content
  area or rely on the page navigation. Keep “Keep all filters” off.
- The scatter shows actual asking prices, not predicted prices. Add a small text
  annotation: “Ask price from the cleaned listing snapshot; each dot is one listing.”
- The decomposition tree can become visually noisy with many locations. Keep only
  the top 15 locations by `[Total Properties]` at the visual level if the reviewer
  audience is non-technical; document that filter in a tooltip or subtitle.
- The feature-importance table has **no relationship** to the fact table. This is
  intentional: it is model metadata, not a slicer.
- Use a consistent axis title style and leave 8 px of padding inside chart cards.
- Recommended insight bullets:
  - “Size explains most of the model’s split activity, with bathrooms and BHK
    adding property-type information.”
  - “Location effects are split across one-hot columns and do not appear as one
    aggregate bar; this understates the combined role of location.”
  - “Outlier trimming removed the extreme price-per-sq.ft. tails before training.”

### Interaction and accessibility

- Default cross-highlighting from scatter to decomposition tree is allowed; the
  feature-importance chart is unaffected because it has no relationship.
- Add alt text: “Scatter of asking price against total square feet for 12,685
  cleaned Bengaluru listings.”
- Use no more than two line weights in the scatter. Do not add a trend line unless
  you also label that it is descriptive, not causal.

---

## 4. Page 03 — What-If Simulator

**Purpose:** let a user test a hypothetical home size against a data-backed
segment benchmark. The target size is a disconnected What-If parameter; BHK and
Location are connected slicers. The estimate is indicative and explicitly labelled
as a model benchmark, never a formal valuation.

### Wireframe

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ HEADER · What-If Pricing Simulator                        [nav]          │
├──────────────┬────────────────────────────────────┬──────────────────────┤
│ SCENARIO     │ ESTIMATED PRICE (hero card)        │ HOW IT IS CALCULATED │
│ CONTROLS     │ ₹ XX.XX L                          │ 1... 2... 3... 4...  │
│              │ [Scenario Summary]                 │                      │
│ Target sq.ft.├──────────────┬──────────────┬──────┴──────────────────────┤
│ BHK          │ RATE USED    │ COMPARABLES  │ ESTIMATE BASIS              │
│ Location     ├──────────────┴──────────────┴─────────────────────────────┤
│ [Reset]      │ COMPARABLE LISTINGS (detailed table)                       │
└──────────────┴────────────────────────────────────────────────────────────┘
```

### Visual specification

| # | Visual type | Title | Position (x, y, w, h) | Exact fields and setup |
|---|---|---|---|---|
| 3.1 | Control panel / rectangle | SCENARIO CONTROLS | `24, 88, 280, 588` | Fill `#0F2A48`, border `#27496D`, 8 px radius. Text labels 9 pt uppercase, `#AFC6DD`. |
| 3.2 | Slicer (single-value numeric slider) | TARGET SIZE (SQ.FT.) | `40, 158, 248, 118` | Field: `SqFt Parameter[Target SqFt]` (disconnected). Slicer settings: single value, slider style, range 300–5,000, increment 50. Show value. Hide header; add label at `40, 136, 248, 18`. |
| 3.3 | Slicer (vertical list / tiles) | BHK SEGMENT | `40, 314, 248, 120` | Field: `'Bengaluru Housing'[bhk]`. Single select on. Values 1–10. Style as compact tiles, 2 columns, selected fill `#1D4ED8`, unselected fill `#0B223D`. Label at `40, 292, 248, 18`. |
| 3.4 | Slicer (dropdown, search on) | LOCATION | `40, 472, 248, 100` | Field: `'Bengaluru Housing'[location]`. Single select recommended; search enabled. Include `Other` only if the user wants the broad fallback segment. Label at `40, 450, 248, 18`. |
| 3.5 | Button | RESET SCENARIO | `40, 588, 248, 36` | Action: bookmark **P3 Reset Scenario**. Style: fill `#1D4ED8`, white 9.5 pt Semibold, icon reset optional. Small note under it: “Clears BHK/location and restores 1,000 sq.ft.” |
| 3.6 | Card (new), hero | ESTIMATED PRICE | `320, 88, 612, 200` | Value: `[Estimated Price (Lakh)]`, 44 pt. Title: “ESTIMATED PRICE · MODEL BENCHMARK”. Reference label: `[Scenario Summary]` (9.5 pt, secondary text). Bottom note: “Indicative estimate — not a valuation.” Fill `#102A4C`; 3 px cyan left border; soft cyan glow is optional. |
| 3.7 | Text panel | HOW IT IS CALCULATED | `948, 88, 308, 200` | Heading plus four numbered lines: (1) target area is a disconnected What-If slider; (2) benchmark is area-weighted model price/sq.ft. for the selected BHK/location; (3) under 5 listings, the citywide benchmark is used; (4) estimate = target area × benchmark ÷ 100,000, displayed in INR lakh. Add a small “Citywide fallback is labelled in the card below” note. |
| 3.8 | Card (new) | RATE USED | `320, 304, 304, 100` | Value: `[Benchmark Price per Sq.Ft Used]`; format `₹#,0 " / sq.ft."`. Reference label: “Area-weighted model rate”. |
| 3.9 | Card (new) | COMPARABLES | `636, 304, 304, 100` | Value: `[Comparable Listings]`. Reference label: “Listings behind the benchmark”. Apply amber font when the value is below 5; the `[Estimate Basis]` card explains the fallback. |
| 3.10 | Card (new), text | ESTIMATE BASIS | `952, 304, 304, 100` | Value: `[Estimate Basis]`, 11 pt Semibold. Apply an amber accent or font colour when the text contains “fallback”. This is the trust label for the hero card. |
| 3.11 | Table | Comparable listings | `320, 420, 936, 256` | Columns: `property_id`, `location`, `bhk`, `total_sqft`, `bath`, `price_lakh`, `predicted_price_lakh`, `price_per_sqft`. Optional column: `[Predicted vs Asking Gap %]` (only because `property_id` makes each row unique). Sort by `predicted_price_lakh` descending. Show 8 rows, scroll for more. Header fill `#0B223D`; body `#0F2A48`; alternate row `#102A4C`; numeric right aligned; price columns 2 decimals. Add title and a small note: “Filtered by BHK and location. The target-size slider does not filter comparables.” Remove totals. |

### Build notes for Page 03

- **Disconnected parameter is mandatory.** The `SqFt Parameter` table must not be
  related to `Bengaluru Housing`. This is what makes the slider hypothetical rather
  than a filter on existing listing sizes.
- The BHK and Location slicers must filter the fact table. They drive the segment
  benchmark and the comparable table; the target-size slider drives only the
  estimate.
- Single-select BHK/location keeps the benchmark explainable. If multi-select is
  enabled, the measure averages across the selected segment and the label should say
  “selected segments”.
- Add a visible sample-size guardrail. At fewer than five listings the measure falls
  back to the citywide model rate, and the `[Estimate Basis]` card turns amber.
- Add a warning text box near the hero card:
  “This simulator uses a benchmark derived from historical listing prices and
  out-of-fold model predictions. It is not a registered valuation and excludes
  floor, age, amenities, facing and negotiation.”
- Create bookmark **P3 Reset Scenario** with Data checked so it restores:
  no BHK selection, no location selection, target size 1,000 sq.ft. If a parameter
  slicer is not captured by the bookmark in your Power BI version, add a second
  bookmark after manually resetting the slider and set the page to open in that state.
- The detailed table is a scrollable evidence panel, not the primary decision
  surface. Keep the hero card visible above the fold on a 1366 × 768 screen.

### Interaction

- BHK/location changes recalculate the hero, support cards and table.
- Target-size changes recalculate only the hero (and any label bound to
  `[Scenario Summary]`).
- No cross-filtering from the detailed table to the hero is required; the slicers are
  the control surface.
- Add a “View methodology” tooltip or bookmark that opens a simple text page. Do not
  add a fourth page in v1; a tooltip is enough.

---

## 5. Build Sequence

1. Load the two generated CSVs; rename tables exactly as above.
2. Create `_Measures` and add measures from `dax_measures.txt` in order:
   core KPIs → parameter → benchmark → estimate → labels → optional gap.
3. Create the `SqFt Parameter` What-If table; confirm it is disconnected.
4. Apply the report theme/background, header and navigation.
5. Build Page 01; validate KPI totals against the CSV.
6. Build Page 02; confirm the feature-importance table has no relationship.
7. Build Page 03; test the slider, fallback state and reset bookmark.
8. Set the report landing page to Page 01.
9. Publish screenshots to `assets/screenshots/` and update `README.md`.

## 6. QA Checklist

- [ ] Total Properties equals the row count in the cleaned CSV (12,685 in the
      reference run).
- [ ] Average Price per Sq.Ft. matches `SUM(price × 100000) / SUM(total_sqft)`.
- [ ] All visible prices are labelled INR lakh or INR/sq.ft.; no ambiguous “price”
      axis.
- [ ] The What-If table has no relationship in Model view.
- [ ] Under-five-comparable fallback is visibly labelled.
- [ ] Page 03 Reset bookmark restores all controls.
- [ ] Charts remain readable with 200% display scaling.
- [ ] Alt text exists on every visual.
- [ ] Page 01 contains no false precision: no claims that listed prices are
      registered transaction prices.
- [ ] Screenshot files in README use the same page names as this blueprint.

## 7. Reference Metrics (data snapshot used to validate this blueprint)

| Metric | Reference value |
|---|---|
| Cleaned rows | 12,685 |
| Locations after grouping | 242 (including `Other`) |
| Median asking price | 70.00 lakh |
| Mean asking price | 97.33 lakh |
| Area-weighted price/sq.ft. | 6,428 INR |
| 2 BHK share | 43.2% |
| 3 BHK share | 37.4% |
| Random Forest OOF R² | 0.749 |
| OOF MAE | 24.48 lakh |
| OOF RMSE | 45.77 lakh |

These numbers are descriptive outputs of the provided pipeline on the Kaggle
`train.csv` snapshot. They are not a market forecast.
