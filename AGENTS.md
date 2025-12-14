The task is to update this project to update this current project and build a time series data base, corrected for schema changes to allow us to track how capitation rates have changed. 

## Data Files
- './data/*.xls'

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

## Legacy Code 
- This code base includes some legacy code that may or may not be related to the current task. You may review it if is helpful, but this is a whole new project. Start over from scratch. 
