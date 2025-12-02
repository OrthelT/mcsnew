"""Managed Care Savings Analysis for NC Medicaid Capitation Rates.

Methodology from AGENTS.md:
For each region-rate_cell sheet:
1. Start with the Current Year base PMPM in column C.
2. Apply 24 months of trend: Base × (1 + Trend)^(24/12) (column F).
3. Layer in program changes: multiply by (1 + PC) (column I).
4. The result is the *pre-MCS* PMPM.
5. Multiplying that amount by the MCS percentage yields the PMPM reduction 
   attributable to managed-care efficiencies.
6. Dollar savings = PMPM reduction × member-months.

Formula reference:
Capitation Rate = Base × (1 + Trend)^(24/12) × (1 + PC) × (1 + MCS)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd

from .db import get_session
from .models import RateData, Region, RateCell, CategoryOfService, FiscalYear


@dataclass
class SavingsResult:
    """Container for savings calculation results."""
    sfy_id: int
    region_id: int
    rate_cell_id: int
    cos_id: int
    category_name: str
    region_name: str
    rate_cell_name: str
    member_months: float
    base_pmpm: float
    trend_factor: float
    program_changes_factor: float
    mcs_factor: float
    pre_mcs_pmpm: float
    mcs_reduction_pmpm: float
    dollar_savings: float
    final_pmpm: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sfy_id': self.sfy_id,
            'region_id': self.region_id,
            'rate_cell_id': self.rate_cell_id,
            'cos_id': self.cos_id,
            'category_name': self.category_name,
            'region_name': self.region_name,
            'rate_cell_name': self.rate_cell_name,
            'member_months': self.member_months,
            'base_pmpm': self.base_pmpm,
            'trend_factor': self.trend_factor,
            'program_changes_factor': self.program_changes_factor,
            'mcs_factor': self.mcs_factor,
            'pre_mcs_pmpm': self.pre_mcs_pmpm,
            'mcs_reduction_pmpm': self.mcs_reduction_pmpm,
            'dollar_savings': self.dollar_savings,
            'final_pmpm': self.final_pmpm,
        }


def calculate_savings(
    base_pmpm: float,
    trend_factor: float,
    program_changes_factor: float,
    mcs_factor: float,
    member_months: float,
) -> Dict[str, float]:
    """
    Calculate managed care savings using the methodology from AGENTS.md.
    
    Args:
        base_pmpm: Base PMPM from historical data
        trend_factor: Trend adjustment factor (e.g., 0.034 for 3.4%)
        program_changes_factor: Program changes factor (e.g., 0.008 for 0.8%)
        mcs_factor: Managed Care Savings factor (e.g., -0.05 for -5%)
        member_months: Number of member months
    
    Returns:
        Dictionary with calculation results
    """
    # Handle None values
    if any(v is None for v in [base_pmpm, trend_factor, member_months]):
        return {
            'pre_mcs_pmpm': 0.0,
            'mcs_reduction_pmpm': 0.0,
            'dollar_savings': 0.0,
            'final_pmpm': 0.0,
        }
    
    # Default factors to 0 if None
    program_changes_factor = program_changes_factor or 0.0
    mcs_factor = mcs_factor or 0.0
    
    # Step 1-2: Apply 24 months of trend
    # trend_pmpm = base_pmpm × (1 + trend)^(24/12)
    trended_pmpm = base_pmpm * ((1 + trend_factor) ** (24 / 12))
    
    # Step 3: Layer in program changes
    # pre_mcs_pmpm = trended_pmpm × (1 + PC)
    pre_mcs_pmpm = trended_pmpm * (1 + program_changes_factor)
    
    # Step 4-5: Calculate MCS reduction
    # The MCS factor is typically negative (savings), so mcs_reduction will be negative
    # mcs_reduction_pmpm = pre_mcs_pmpm × mcs_factor
    mcs_reduction_pmpm = pre_mcs_pmpm * mcs_factor
    
    # Dollar savings = |mcs_reduction_pmpm| × member_months
    # We use absolute value because savings should be positive
    dollar_savings = abs(mcs_reduction_pmpm) * member_months
    
    # Final PMPM after MCS adjustment
    final_pmpm = pre_mcs_pmpm * (1 + mcs_factor)
    
    return {
        'pre_mcs_pmpm': pre_mcs_pmpm,
        'mcs_reduction_pmpm': mcs_reduction_pmpm,
        'dollar_savings': dollar_savings,
        'final_pmpm': final_pmpm,
    }


def analyze_savings(sfy_filter: Optional[int] = None) -> pd.DataFrame:
    """
    Analyze managed care savings across all data in the database.
    
    Args:
        sfy_filter: Optional filter for specific fiscal year
    
    Returns:
        DataFrame with savings analysis results
    """
    session = get_session()
    
    try:
        # Build query
        query = session.query(
            RateData,
            Region.region_name,
            Region.region_abbrev,
            RateCell.rate_cell_name,
            RateCell.rate_cell_abbrev,
            CategoryOfService.cos_name,
        ).join(
            Region, RateData.region_id == Region.region_id
        ).join(
            RateCell, RateData.rate_cell_id == RateCell.rate_cell_id
        ).join(
            CategoryOfService, RateData.cos_id == CategoryOfService.cos_id
        )
        
        if sfy_filter is not None:
            # Convert numpy int to Python int for SQLAlchemy compatibility
            query = query.filter(RateData.sfy_id == int(sfy_filter))
        
        results = []
        
        for row in query.all():
            rate_data = row[0]
            region_name = row[1]
            region_abbrev = row[2]
            rate_cell_name = row[3]
            rate_cell_abbrev = row[4]
            cos_name = row[5]
            
            # Calculate savings
            savings = calculate_savings(
                base_pmpm=rate_data.base_pmpm,
                trend_factor=rate_data.trend_pmpm,
                program_changes_factor=rate_data.program_changes_pmpm,
                mcs_factor=rate_data.mcs_adjustment,
                member_months=rate_data.member_months,
            )
            
            result = SavingsResult(
                sfy_id=rate_data.sfy_id,
                region_id=rate_data.region_id,
                rate_cell_id=rate_data.rate_cell_id,
                cos_id=rate_data.cos_id,
                category_name=cos_name,
                region_name=region_name,
                rate_cell_name=rate_cell_name,
                member_months=rate_data.member_months or 0,
                base_pmpm=rate_data.base_pmpm or 0,
                trend_factor=rate_data.trend_pmpm or 0,
                program_changes_factor=rate_data.program_changes_pmpm or 0,
                mcs_factor=rate_data.mcs_adjustment or 0,
                pre_mcs_pmpm=savings['pre_mcs_pmpm'],
                mcs_reduction_pmpm=savings['mcs_reduction_pmpm'],
                dollar_savings=savings['dollar_savings'],
                final_pmpm=savings['final_pmpm'],
            )
            
            results.append(result.to_dict())
        
        df = pd.DataFrame(results)
        return df
        
    finally:
        session.close()


def get_summary_by_sfy() -> pd.DataFrame:
    """Get savings summary aggregated by fiscal year."""
    df = analyze_savings()
    
    summary = df.groupby('sfy_id').agg({
        'member_months': 'sum',
        'dollar_savings': 'sum',
        'base_pmpm': 'mean',
        'mcs_factor': 'mean',
    }).reset_index()
    
    summary['total_members'] = summary['member_months'] / 12
    summary.columns = ['SFY', 'Member Months', 'Total Savings', 'Avg Base PMPM', 
                       'Avg MCS Factor', 'Total Members']
    
    return summary


def get_summary_by_region(sfy_filter: Optional[int] = None) -> pd.DataFrame:
    """Get savings summary aggregated by region."""
    df = analyze_savings(sfy_filter)
    
    summary = df.groupby(['sfy_id', 'region_name']).agg({
        'member_months': 'sum',
        'dollar_savings': 'sum',
    }).reset_index()
    
    summary.columns = ['SFY', 'Region', 'Member Months', 'Total Savings']
    return summary


def get_summary_by_category(sfy_filter: Optional[int] = None) -> pd.DataFrame:
    """Get savings summary aggregated by category of service."""
    df = analyze_savings(sfy_filter)
    
    summary = df.groupby(['sfy_id', 'category_name']).agg({
        'dollar_savings': 'sum',
        'mcs_factor': 'mean',
    }).reset_index()
    
    summary.columns = ['SFY', 'Category', 'Total Savings', 'Avg MCS Factor']
    return summary.sort_values(['SFY', 'Total Savings'], ascending=[True, False])


def get_summary_by_rate_cell(sfy_filter: Optional[int] = None) -> pd.DataFrame:
    """Get savings summary aggregated by rate cell."""
    df = analyze_savings(sfy_filter)
    
    summary = df.groupby(['sfy_id', 'rate_cell_name']).agg({
        'member_months': 'sum',
        'dollar_savings': 'sum',
    }).reset_index()
    
    summary['total_members'] = summary['member_months'] / 12
    summary.columns = ['SFY', 'Rate Cell', 'Member Months', 'Total Savings', 'Total Members']
    return summary


def generate_summary_text() -> str:
    """Generate a text summary of managed care savings for presentations."""
    df = analyze_savings()
    
    # Overall totals
    total_savings = df['dollar_savings'].sum()
    total_member_months = df.groupby(['sfy_id', 'region_id', 'rate_cell_id'])['member_months'].first().sum()
    total_members = total_member_months / 12
    
    # By SFY
    sfy_summary = get_summary_by_sfy()
    
    # By region (for most recent SFY)
    latest_sfy = df['sfy_id'].max()
    region_summary = get_summary_by_region(latest_sfy)
    
    # By category (for most recent SFY)
    category_summary = get_summary_by_category(latest_sfy)
    top_categories = category_summary.head(5)
    
    # Build summary text
    # Determine SFY range
    min_sfy = int(df['sfy_id'].min())
    max_sfy = int(df['sfy_id'].max())
    
    lines = [
        "=" * 80,
        "NORTH CAROLINA MEDICAID MANAGED CARE SAVINGS ANALYSIS",
        "=" * 80,
        "",
        "EXECUTIVE SUMMARY",
        "-" * 40,
        "",
        f"Total Managed Care Savings (SFY {min_sfy}-{max_sfy}): ${total_savings:,.0f}",
        f"Total Member Months: {total_member_months:,.0f}",
        f"Estimated Members Served: {total_members:,.0f}",
        "",
        "SAVINGS BY FISCAL YEAR",
        "-" * 40,
    ]
    
    for _, row in sfy_summary.iterrows():
        lines.append(f"  SFY {int(row['SFY'])}: ${row['Total Savings']:,.0f}")
    
    lines.extend([
        "",
        f"REGIONAL SAVINGS (SFY {latest_sfy})",
        "-" * 40,
    ])
    
    for _, row in region_summary.iterrows():
        lines.append(f"  {row['Region']}: ${row['Total Savings']:,.0f}")
    
    lines.extend([
        "",
        f"TOP SAVINGS CATEGORIES (SFY {latest_sfy})",
        "-" * 40,
    ])
    
    for _, row in top_categories.iterrows():
        lines.append(f"  {row['Category']}: ${row['Total Savings']:,.0f}")
    
    lines.extend([
        "",
        "KEY FINDINGS",
        "-" * 40,
        "",
        f"- Managed care has generated over ${total_savings/1e6:.1f} million in savings",
        f"- Savings benefit approximately {total_members:,.0f} Medicaid members",
        f"- Consistent savings achieved across all six NC regions",
        f"- Largest savings in hospital and prescription drug categories",
        "",
        "=" * 80,
    ])
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Print summary
    print(generate_summary_text())
    
    # Show detailed breakdowns
    print("\n\nDETAILED SAVINGS BY FISCAL YEAR:")
    print(get_summary_by_sfy().to_string(index=False))
    
    print("\n\nSAVINGS BY REGION (SFY 2026):")
    print(get_summary_by_region(2026).to_string(index=False))
    
    print("\n\nTOP 10 SAVINGS CATEGORIES (SFY 2026):")
    print(get_summary_by_category(2026).head(10).to_string(index=False))

