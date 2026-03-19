#!/usr/bin/env python3
"""
NC Medicaid Managed Care Capitation Rates Time-Series Database
Main Pipeline Orchestration Script

This script orchestrates the complete data pipeline:
1. Initialize/reset database
2. Extract data from Excel files
3. Load data into SQLite database
4. Generate managed care savings analysis
5. Create visualizations and summary reports

Usage:
    python main.py              # Run full pipeline
    python main.py --reset      # Reset database and reload all data
    python main.py --analyze    # Only run analysis (skip data load)
    python main.py --visualize  # Only generate visualizations
"""

import argparse
from pathlib import Path

from src.db import init_db, reset_db, get_session
from src.extract import extract_all_files
from src.load import load_records, clear_rate_data
from src.analysis import (
    generate_summary_text,
    get_summary_by_sfy,
    get_summary_by_period,
    generate_contribution_summary_text,
    get_contribution_summary_by_sfy,
)
from src.visualize import generate_all_visualizations
from src.models import RateData

# Current-year files (SFY 2024-2026)
CAP_RATES_DIR = Path(__file__).parent / "cap_rates"
# Archive files (SFY 2022-2023)
ARCHIVE_DIR = Path(__file__).parent / "archive" / "data"


def run_etl(reset: bool = False):
    """Run the ETL pipeline to extract, transform, and load data."""
    print("=" * 60)
    print("NC Medicaid Capitation Rates - Data Pipeline")
    print("=" * 60)
    
    if reset:
        print("\nResetting database...")
        reset_db()
    else:
        print("\nInitializing database...")
        init_db()
    
    # Check if data already loaded
    session = get_session()
    existing_count = session.query(RateData).count()
    session.close()
    
    if existing_count > 0 and not reset:
        print(f"\nDatabase already contains {existing_count} records.")
        print("Use --reset to reload data, or --analyze to run analysis only.")
        return
    
    # Extract data from Excel files
    print("\n" + "-" * 40)
    print("Extracting data from Excel files...")
    print("-" * 40)
    
    records = extract_all_files([CAP_RATES_DIR, ARCHIVE_DIR])
    
    # Load into database
    print("\n" + "-" * 40)
    print("Loading data into database...")
    print("-" * 40)
    
    load_records(records)
    
    print("\nETL pipeline complete!")


def run_analysis():
    """Run the managed care savings analysis."""
    print("\n" + "=" * 60)
    print("Managed Care Savings Analysis")
    print("=" * 60)
    
    # Print summary
    print(generate_summary_text())
    
    # Show SFY breakdown
    print("\nDETAILED BREAKDOWN BY FISCAL YEAR:")
    print("-" * 40)
    sfy_summary = get_summary_by_sfy()

    for _, row in sfy_summary.iterrows():
        sfy = int(row['SFY'])
        savings = row['Total Savings']
        members = row['Total Members']
        print(f"  SFY {sfy}:")
        print(f"    Total Savings: ${savings:,.0f}")
        print(f"    Members Served: {members:,.0f}")
        print()

    # Show SFY 2024 sub-period breakdown
    print("SFY 2024 RATE PERIOD BREAKDOWN:")
    print("-" * 40)
    period_summary = get_summary_by_period()
    sfy2024_periods = period_summary[period_summary['SFY'] == 2024]
    for _, row in sfy2024_periods.iterrows():
        print(f"  {row['Period']}: ${row['Total Savings']:,.0f}  ({row['Member Months']:,.0f} member-months)")
    print()

    # NEW: Add contribution analysis
    print("\n" + "=" * 60)
    print("Cost Factor Contribution Analysis")
    print("=" * 60)

    print(generate_contribution_summary_text())

    print("\nDETAILED CONTRIBUTION BREAKDOWN:")
    print("-" * 40)
    contrib_summary = get_contribution_summary_by_sfy()
    print(contrib_summary.to_string(index=False))


def run_visualizations():
    """Generate all visualizations."""
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)
    
    generate_all_visualizations()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NC Medicaid Managed Care Capitation Rates Pipeline"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database and reload all data"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Only run analysis (skip data load)"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Only generate visualizations"
    )
    
    args = parser.parse_args()
    
    # Run appropriate steps
    if args.analyze:
        run_analysis()
    elif args.visualize:
        run_visualizations()
    else:
        run_etl(reset=args.reset)
        run_analysis()
        run_visualizations()
    
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

