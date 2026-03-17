The task is to update this project to update this current project and build a time series data base, corrected for schema changes to allow us to track how capitation rates have changed. 

## Data Files
- './cap_rates/*.xls'
- note SFY 2024 split into three files due to program changes that material affected rates throughout the period. 

## Data Description
Capitation rate files (.xlxs) for NC Medicaid managed care plans from SFY 2024 to SFY 2026 prepared by Mercer, the actuaries for the State of North Carolina's Medicaid program. 
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
These figures are calculated from the managed care savings factors given in Mercer’s rate calculation for each fiscal year. Note that this refers to the schema for the SFY2026 file. SFY24 and SFY25 may be slightly different. Ensure that data us mapped consistently across each file. 

**Important:** The trend period varies by fiscal year:
- SFY 2022 & 2023: Use 42 months of trend
- SFY >= 2024: Use 24 months of trend

For each region-COA sheet we:
1. Start with the Current Year base PMPM in column C.  
2. Apply trend based on SFY:
   - SFY 2022 & 2023: `Base × (1 + Trend)^(42/12)` (column F)
   - SFY >= 2024: `Base × (1 + Trend)^(24/12)` (column F)  
3. Layer in program changes: multiply by `(1 + PC)` (column I).  
4. The result is the *pre-MCS* PMPM.  
Multiplying that amount by the MCS percentage in column W yields the PMPM reduction attributable to managed-care efficiencies.  
5. Dollar savings = PMPM reduction × member-months for the fiscal year.  
   We perform this calculation for every category and sum across regions.

Formula reference:  
- SFY >= 2024: Capitation Rate = Base × (1 + Trend)^(24/12) × (1 + PC) × (1 + MCS)
- SFY 2022 & 2023: Capitation Rate = Base × (1 + Trend)^(42/12) × (1 + PC) × (1 + MCS)

This calculation is applied to medical costs prior to application of continuous coverage unwinding acuity adjustment, care management, premium taxes, and non-benefit expenses. 

## Cost Factor Contribution Analysis

**New Functionality Added:** The system now tracks and analyzes the individual contribution of each cost factor (Trend, Program Changes, MCS) to overall capitation rate changes.

### Overview
While the Managed Care Savings analysis focuses on quantifying MCS-driven savings, the Cost Factor Contribution Analysis decomposes the entire capitation rate formula to show how much each factor (Trend, Program Changes, and MCS) contributes to the total rate change from base PMPM.

### Methodology
The capitation rate formula applies three factors sequentially:
```
Final PMPM = Base PMPM × (1 + Trend)^(months/12) × (1 + PC) × (1 + MCS)
```

The contribution analysis decomposes this into incremental impacts:

1. **Trend Contribution**
   - PMPM Impact: `Base × [(1 + Trend)^(months/12) - 1]`
   - Dollar Impact: `Trend PMPM Impact × member_months`
   - Shows how much medical cost inflation adds to rates

2. **Program Changes (PC) Contribution**
   - PMPM Impact: `Trended_PMPM × PC_factor`
   - Dollar Impact: `PC PMPM Impact × member_months`
   - Shows impact of policy/benefit changes

3. **Managed Care Savings (MCS) Contribution**
   - PMPM Impact: `Pre_MCS_PMPM × MCS_factor` (typically negative)
   - Dollar Impact: `MCS PMPM Impact × member_months`
   - Shows cost reductions from managed care efficiencies

4. **Net Change**
   - Sum of all three contributions
   - Represents total change from base to final capitation rates

5. **Percentage Contributions**
   - Calculated using absolute values to show relative magnitude
   - `Trend % = |Trend $| / (|Trend $| + |PC $| + |MCS $|) × 100`
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
python main.py              # Full pipeline: ETL → Analysis → Visualizations
python main.py --analyze    # Analysis only (includes both MCS and contribution analysis)
python main.py --visualize  # Visualizations only (includes all charts)
```

Console output includes both the Managed Care Savings Analysis and the Cost Factor Contribution Analysis sections.

## Legacy Code
- This code base includes some legacy code that may or may not be related to the current task. You may review it if is helpful, but this is a whole new project. Start over from scratch. 
