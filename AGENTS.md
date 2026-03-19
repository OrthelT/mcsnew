The task is to update this project to update this current project and build a time series data base, corrected for schema changes to allow us to track how capitation rates have changed.

## Data Files
- './cap_rates/*.xls'
- note SFY 2024 split into three files due to program changes that material affected rates throughout the period.

## Data Description
Capitation rate files (.xlxs) for NC Medicaid managed care plans from SFY 2022 to SFY 2026 prepared by Mercer, the actuaries for the State of North Carolina's Medicaid program.
- Note that there SFY24 contains fewer columns.The important columns are Base Data (PMPM, Unit Cost, Unit/1000), Managed Care Savings Adjustment, and Total Medical (PMPM, Unit Cost, Unit/1000) for now, just tally these into the DB.
- Rate information is provided for each rate cell and region by category of service in separate sheets.
- The tab names follow a naming convention '<Region> <Rate_Cell>'.
- Tab Names are not consistent across SFY and must be normalized: 'Region 1 - TANF Newborn' = 'R1 TANF Newborn' = 'R1 TANF NB'

## Tasks
### Data Pipeline
- Review the data structure.
- Normalize region/Rate_Cell names to match SFY2026
- Develop a DB schema to store the data referenced above to enable further analysis in time-series.
- Store region and rate cell labels, but also create numeric keys we can use so that data can be reliably compared.

### Managed Care Savings analysis
- Produce an analysis of total managed care savings, translated into dollar amounts assumed in capitation rates for each year.
- Include a summary of key statistics in a text file for use in presentations.
- Produce data visualizations that illustrate the amount of money that Managed Care has saved the state of North Carolina both in total and over time.
- Utilize the Methodology outlined below. All columns and cells referenced are for the SFY2026 capitation rate file. Please determine the equivalent data elements for each SFY file. Produce a mapping as part of your planning for me to verify before proceeding.

### Methodology for Managed Care Savings Analysis
These figures are calculated from the managed care savings factors given in Mercer's rate calculation for each fiscal year. Note that this refers to the schema for the SFY2026 file. SFY24 and SFY25 may be slightly different. Ensure that data us mapped consistently across each file.

**Important:** The trend period varies by fiscal year (read from row 11 of each Excel file):
- SFY 2022: Use 30 months of trend
- SFY 2023: Use 42 months of trend
- SFY >= 2024: Use 24 months of trend

For each region-COA sheet we:
1. Start with the Current Year base PMPM in column C.
2. Apply trend based on SFY:
   - SFY 2022: `Base x (1 + Trend)^(30/12)` (column F)
   - SFY 2023: `Base x (1 + Trend)^(42/12)` (column F)
   - SFY >= 2024: `Base x (1 + Trend)^(24/12)` (column F)
3. Layer in program changes: multiply by `(1 + PC)` (column I).
4. The result is the *pre-MCS* PMPM.
Multiplying that amount by the MCS percentage in column W yields the PMPM reduction attributable to managed-care efficiencies.
5. Dollar savings = PMPM reduction x member-months for the fiscal year.
   We perform this calculation for every category and sum across regions.

Formula reference:
- SFY 2022: Capitation Rate = Base x (1 + Trend)^(30/12) x (1 + PC) x (1 + MCS)
- SFY 2023: Capitation Rate = Base x (1 + Trend)^(42/12) x (1 + PC) x (1 + MCS)
- SFY >= 2024: Capitation Rate = Base x (1 + Trend)^(24/12) x (1 + PC) x (1 + MCS)

This calculation is applied to medical costs prior to application of continuous coverage unwinding acuity adjustment, care management, premium taxes, and non-benefit expenses.

## Understanding MCS Factor Magnitude Across Years

**Critical context for interpreting MCS savings figures:** The MCS adjustment column in Mercer's rate files represents an *incremental* adjustment relative to the base data period, not the cumulative managed care savings. As the program matures, the base data itself shifts from FFS claims to managed care encounter data, absorbing prior savings.

### Mercer's MCS Phase-In Schedule (from SFY 2025 Rate Book, Section 11.1)
NC Medicaid managed care launched July 2021 (SFY 2022). Mercer assumed a phase-in to "ultimate" managed care savings:

| SFY | Contract Year | Base Data Source | MCS Phase-In | What MCS Column Represents | Avg MCS Factor |
|-----|--------------|-----------------|-------------|-------------------------------|----------------|
| 2022 | Year 1 | FFS claims | Initial | Full FFS-to-MC gap | -4.0% |
| 2023 | Year 2 | FFS claims (adjusted) | ~95% of ultimate | Large incremental | -5.7% |
| 2024 | Year 3 | Transitional | Continuing | Moderate incremental | -1.4% |
| 2025 | Year 4 | SFY 2023 MC encounter data | 100% non-expansion | Only remaining 5% (95% to 100%) | -0.2% |
| 2026 | Year 5 | MC encounter data | 100%+ | New savings identified (e.g., IP-PH -8.9%) | -0.1% |

**Key finding:** SFY 2025's low MCS ($42M) vs SFY 2022 ($482M) does NOT mean managed care stopped saving money. The prior savings are embedded in the base PMPM. Mercer's SFY 2025 base data is actual managed care encounter data from SFY 2023, which already reflects managed care utilization patterns. The MCS column only captures the *incremental* adjustment beyond what is already in the base.

### SFY 2025 Inpatient PH Efficiency Analysis (Rate Book Section 11.2.2)
Mercer performed PPA and readmission analyses on SFY 2023 encounter data:
- **PPA**: 4% TANF / 14% ABD of IP spend is PPA-related; refined to 3% TANF / 10% ABD after exclusions
- **Readmissions**: 3% TANF / 9% ABD 30-day readmission rate (other states: 7-10%)
- These supported only -0.7% Inpatient PH MCS for SFY 2025 (incremental from 95% to 100%)

### SFY 2026 Inpatient PH Efficiency Analysis (Rate Book Section 11)
SFY 2026 represents a methodological shift: Mercer conducted a ground-up efficiency analysis using SFY 2024 encounter data rather than relying on the phase-in schedule. Four components drive the MCS factors:

1. **PPA (Potentially Preventable Admissions)** - Table 24:
   - ABD: -7.9% on Inpatient COS (before TEL)
   - TANF Adults: -6.0%, TANF Children: -3.7%
   - After 75% TEL: ABD ~-5.9%, TANF Adults ~-4.5%

2. **LANE (Low Acuity Non-Emergent ED)** - Table 23:
   - ABD: -1.5% on ED COS, TANF NB: -6.4%, TANF Children: -5.1%

3. **HOP (Healthy Opportunities Pilot)** - Tables 25a/25b:
   - Applies only to Regions 1, 5, 6 (pilot regions)
   - Additional inpatient savings: $111.26 PMPM (ABD), $54.20 (TANF Adults)
   - Adds approximately -1.0% to -2.3% on Inpatient COS in pilot regions

4. **Pharmacy (Clinical Edits + DxRx)** - Table 26:
   - ABD: -0.7% on Rx COS, TANF Adults: -1.5%

**Explaining the -8.9% Inpatient PH factor:** For ABD in HOP pilot regions, PPA (-7.9% x 75% TEL = -5.9%) + HOP savings (-2.3%) approaches -8.2%. Region/rate-cell specific values can exceed the statewide average of -3.0% (Table 22). The combination of PPA and HOP fully accounts for the large Inpatient PH factors seen in certain region-rate cell combinations.

**Sources:** SFY 2025 Standard Plan Rate Book (June 10, 2024), Section 11. SFY 2026 Standard Plan Rate Book (June 4, 2025), Section 11. Rate methodology overview (April 3, 2024), slide 12.

## Cost Factor Contribution Analysis

**New Functionality Added:** The system now tracks and analyzes the individual contribution of each cost factor (Trend, Program Changes, MCS) to overall capitation rate changes.

### Overview
While the Managed Care Savings analysis focuses on quantifying MCS-driven savings, the Cost Factor Contribution Analysis decomposes the entire capitation rate formula to show how much each factor (Trend, Program Changes, and MCS) contributes to the total rate change from base PMPM.

### Methodology
The capitation rate formula applies three factors sequentially:
```
Final PMPM = Base PMPM x (1 + Trend)^(months/12) x (1 + PC) x (1 + MCS)
```

The contribution analysis decomposes this into incremental impacts:

1. **Trend Contribution**
   - PMPM Impact: `Base x [(1 + Trend)^(months/12) - 1]`
   - Dollar Impact: `Trend PMPM Impact x member_months`
   - Shows how much medical cost inflation adds to rates

2. **Program Changes (PC) Contribution**
   - PMPM Impact: `Trended_PMPM x PC_factor`
   - Dollar Impact: `PC PMPM Impact x member_months`
   - Shows impact of policy/benefit changes

3. **Managed Care Savings (MCS) Contribution**
   - PMPM Impact: `Pre_MCS_PMPM x MCS_factor` (typically negative)
   - Dollar Impact: `MCS PMPM Impact x member_months`
   - Shows cost reductions from managed care efficiencies

4. **Net Change**
   - Sum of all three contributions
   - Represents total change from base to final capitation rates

5. **Percentage Contributions**
   - Calculated using absolute values to show relative magnitude
   - `Trend % = |Trend $| / (|Trend $| + |PC $| + |MCS $|) x 100`
   - Shows which factors drive the most movement in rates

### Implementation Details

**Analysis Functions** (`src/analysis.py`):
- `ContributionResult` - Dataclass storing detailed contribution calculations
- `calculate_factor_contributions()` - Core decomposition logic
- `analyze_contributions()` - Calculates contributions for all records
- `get_contribution_summary_by_sfy()` - Aggregates by fiscal year with percentages
- `get_contribution_summary_by_region()` - Regional breakdown
- `get_contribution_summary_by_category()` - Category breakdown
- `generate_contribution_summary_text()` - Formatted text report for presentations

**Visualizations** (`src/visualize.py`):
- `plot_factor_contributions_by_year()` - Stacked bar chart of dollar impacts by year
- `plot_percentage_contributions_by_year()` - 100% stacked bar showing relative contribution
- `plot_factor_waterfall()` - Waterfall chart showing sequential PMPM build-up for a specific year
- `plot_regional_factor_contributions()` - Regional comparison by factor
- `create_contribution_dashboard()` - Comprehensive 6-panel dashboard
- `save_contribution_summary_text()` - Exports text summary to file

### Output Files
Generated in `/output` directory when running the pipeline:
- `contribution_summary.txt` - Executive summary with overall and annual breakdowns
- `factor_contributions_by_year.png` - Stacked bar chart showing dollar impacts
- `percentage_contributions_by_year.png` - Relative % contribution by year
- `factor_waterfall_sfy2026.png` - PMPM waterfall for latest year
- `regional_factor_contributions_sfy2026.png` - Regional comparison for latest year
- `contribution_dashboard.png` - Comprehensive 6-panel dashboard

### Key Findings (SFY 2022-2026)
Based on analysis of data across all fiscal years:
- **Cost Trend**: $3.74B (40.3% of total movement) - Primary driver of rate increases
- **Program Changes**: $4.21B (45.4% of total movement) - Largest contributor overall
- **Managed Care Savings**: -$1.33B (14.3% of total movement) - Offsets cost increases
- **Net Change**: $6.62B total change from base capitation rates

**Temporal Patterns**:
- **SFY 2022-2023**: Program Changes dominated (59% and 55% of movement)
- **SFY 2024-2026**: Cost Trend became primary driver (55-74% of movement)
- MCS savings effectiveness varies significantly by year (7-22% of movement)

### Usage
The contribution analysis runs automatically as part of the main pipeline:
```bash
python main.py              # Full pipeline: ETL -> Analysis -> Visualizations
python main.py --analyze    # Analysis only (includes both MCS and contribution analysis)
python main.py --visualize  # Visualizations only (includes all charts)
```

Console output includes both the Managed Care Savings Analysis and the Cost Factor Contribution Analysis sections.

## Rate Documentation
- SFY 2025 rate methodology and base data documents are in `rate_info/sfy2025/`
- SFY 2026 rate documents are in `rate_info/sfy26/` (Standard Plan Rate Book, June 4, 2025)

## Legacy Code
- This code base includes some legacy code that may or may not be related to the current task. You may review it if is helpful, but this is a whole new project. Start over from scratch.
