"""Tab name normalization and column mapping for NC Medicaid rate files."""

from typing import Dict, Tuple, Optional
import re

# Tab name normalization patterns
# Maps various tab naming conventions to standardized (region_id, rate_cell_abbrev) tuples

# SFY2024 uses: "Region X - Rate Cell" format
# SFY2025 uses: "RX Rate Cell" format with abbreviations  
# SFY2026 uses: "RX Rate Cell" format (standard)

# Rate cell name mappings to standard abbreviations
RATE_CELL_MAPPINGS = {
    # ABD variations
    "ABD": "ABD",
    "Aged, Blind, Disabled": "ABD",
    
    # TANF Newborn variations
    "TANF Newborn": "TANF Newborn",
    "TANF NB": "TANF Newborn",
    
    # TANF Child variations
    "TANF Children": "TANF Child",
    "TANF Child": "TANF Child",
    "TANF C": "TANF Child",
    
    # TANF Adult variations
    "TANF Adult": "TANF Adult",
    "TANF A": "TANF Adult",
    
    # Maternity variations
    "Maternity": "MAT",
    "MAT": "MAT",
    
    # Newly Eligible variations
    "Newly Elig 19-24": "NE (19 - 24)",
    "NE (19 - 24)": "NE (19 - 24)",
    
    "Newly Elig 25-34": "NE (25 - 34)",
    "NE (25 - 34)": "NE (25 - 34)",
    
    "Newly Elig 35-44": "NE (35 - 44)",
    "NE (35 - 44)": "NE (35 - 44)",
    
    "Newly Elig 45+": "NE (45+)",
    "NE (45+)": "NE (45+)",
}

# Standard abbreviation to rate_cell_id mapping
RATE_CELL_ID_MAP = {
    "ABD": 1,
    "TANF Newborn": 2,
    "TANF Child": 3,
    "TANF Adult": 4,
    "MAT": 5,
    "NE (19 - 24)": 6,
    "NE (25 - 34)": 7,
    "NE (35 - 44)": 8,
    "NE (45+)": 9,
}


def parse_tab_name(tab_name: str) -> Optional[Tuple[int, str]]:
    """
    Parse a tab name and return (region_id, rate_cell_abbrev).
    
    Handles formats:
    - SFY2024: "Region 1 - TANF Newborn", "Region 1 Newly Elig 19-24"
    - SFY2025: "R1 TANF NB", "R1 NE (19 - 24)"
    - SFY2026: "R1 TANF Newborn", "R1 NE (19 - 24)"
    
    Returns None for non-rate sheets (e.g., "Disclosures", "Rate Summary").
    """
    # Skip non-rate sheets
    skip_patterns = ["Disclosures", "Rate Summary", "Exhibit"]
    if any(skip in tab_name for skip in skip_patterns):
        return None
    
    # Pattern 1: SFY2024 "Region X - Rate Cell" or "Region X Rate Cell"
    match = re.match(r"Region\s*(\d)\s*[-]?\s*(.+)", tab_name, re.IGNORECASE)
    if match:
        region_id = int(match.group(1))
        rate_cell_raw = match.group(2).strip()
        rate_cell_abbrev = RATE_CELL_MAPPINGS.get(rate_cell_raw)
        if rate_cell_abbrev:
            return (region_id, rate_cell_abbrev)
    
    # Pattern 2: SFY2025/2026 "RX Rate Cell"
    match = re.match(r"R(\d)\s+(.+)", tab_name)
    if match:
        region_id = int(match.group(1))
        rate_cell_raw = match.group(2).strip()
        rate_cell_abbrev = RATE_CELL_MAPPINGS.get(rate_cell_raw)
        if rate_cell_abbrev:
            return (region_id, rate_cell_abbrev)
    
    return None


def get_rate_cell_id(rate_cell_abbrev: str) -> int:
    """Get the rate_cell_id for a standardized rate cell abbreviation."""
    return RATE_CELL_ID_MAP.get(rate_cell_abbrev, 0)


# Column mappings for each SFY file
# Using 0-based indices for pandas DataFrame columns

class ColumnConfig:
    """Column configuration for a specific SFY file."""
    
    def __init__(
        self,
        sfy: int,
        member_months_cell: Tuple[int, int],  # (row, col) for member months
        header_row: int,  # Row index where headers are located
        data_start_row: int,  # First data row
        data_end_row: int,  # Last data row (exclusive)
        total_row: int,  # Row with totals
        category_col: int,
        base_pmpm_col: int,
        base_unit_cost_col: int,
        base_util_col: int,
        trend_pmpm_col: int,
        trend_unit_cost_col: int,
        trend_util_col: int,
        program_changes_col: int,
        mcs_adjustment_col: int,
        total_medical_pmpm_col: int,
        total_medical_unit_cost_col: int,
        total_medical_util_col: int,
    ):
        self.sfy = sfy
        self.member_months_cell = member_months_cell
        self.header_row = header_row
        self.data_start_row = data_start_row
        self.data_end_row = data_end_row
        self.total_row = total_row
        self.category_col = category_col
        self.base_pmpm_col = base_pmpm_col
        self.base_unit_cost_col = base_unit_cost_col
        self.base_util_col = base_util_col
        self.trend_pmpm_col = trend_pmpm_col
        self.trend_unit_cost_col = trend_unit_cost_col
        self.trend_util_col = trend_util_col
        self.program_changes_col = program_changes_col
        self.mcs_adjustment_col = mcs_adjustment_col
        self.total_medical_pmpm_col = total_medical_pmpm_col
        self.total_medical_unit_cost_col = total_medical_unit_cost_col
        self.total_medical_util_col = total_medical_util_col


# Column configurations for each SFY
# Note: Using 0-based column indices

SFY_CONFIGS: Dict[int, ColumnConfig] = {
    2024: ColumnConfig(
        sfy=2024,
        member_months_cell=(7, 1),  # Row 8, Column B (0-indexed: row 7, col 1)
        header_row=14,  # Headers are on row 15 (0-indexed: 14)
        data_start_row=16,  # Data starts row 17 (0-indexed: 16)
        data_end_row=42,   # Data ends row 42 (0-indexed: 41, exclusive: 42)
        total_row=42,      # Total row is row 43 (0-indexed: 42)
        category_col=0,    # Column A - Category of Service
        base_pmpm_col=1,   # Column B - Base PMPM
        base_unit_cost_col=2,  # Column C - Base Unit Cost
        base_util_col=3,   # Column D - Base Util
        trend_pmpm_col=4,  # Column E - Trend factor
        trend_unit_cost_col=5,  # Column F - Trend Unit Cost
        trend_util_col=6,  # Column G - Trend Util
        program_changes_col=7,  # Column H - Program Changes
        mcs_adjustment_col=8,   # Column I - Managed Care Adjustment Impacts
        total_medical_pmpm_col=9,  # Column J - Total Medical PMPM
        total_medical_unit_cost_col=10,  # Column K - Total Medical Unit Cost
        total_medical_util_col=11,  # Column L - Total Medical Util
    ),
    2025: ColumnConfig(
        sfy=2025,
        member_months_cell=(6, 2),  # Row 7, Column C (0-indexed: row 6, col 2)
        header_row=13,
        data_start_row=15,  # First data row (Inpatient - PH)
        data_end_row=41,    # End before Total row
        total_row=41,
        category_col=1,    # Column B
        base_pmpm_col=2,   # Column C
        base_unit_cost_col=3,  # Column D
        base_util_col=4,   # Column E
        trend_pmpm_col=5,  # Column F
        trend_unit_cost_col=6,  # Column G
        trend_util_col=7,  # Column H
        program_changes_col=8,  # Column I
        mcs_adjustment_col=28,  # Managed Care Adjustment
        total_medical_pmpm_col=29,  # Total Medical PMPM
        total_medical_unit_cost_col=30,  # Total Medical Unit Cost
        total_medical_util_col=31,  # Total Medical Util
    ),
    2026: ColumnConfig(
        sfy=2026,
        member_months_cell=(6, 2),  # Row 7, Column C (0-indexed: row 6, col 2)
        header_row=13,
        data_start_row=15,  # First data row
        data_end_row=41,    # End before Total row
        total_row=41,
        category_col=1,    # Column B
        base_pmpm_col=2,   # Column C
        base_unit_cost_col=3,  # Column D
        base_util_col=4,   # Column E
        trend_pmpm_col=5,  # Column F
        trend_unit_cost_col=6,  # Column G
        trend_util_col=7,  # Column H
        program_changes_col=8,  # Column I
        mcs_adjustment_col=22,  # Managed Care Adjustment
        total_medical_pmpm_col=23,  # Total Medical PMPM
        total_medical_unit_cost_col=24,  # Total Medical Unit Cost
        total_medical_util_col=25,  # Total Medical Util
    ),
}


def get_sfy_from_filename(filename: str) -> int:
    """Extract SFY year from filename."""
    # Check for SFY2026 first (most specific patterns)
    if "SFY_2026" in filename or "SFY26" in filename:
        return 2026
    # Check for SFY2025 
    elif "SFY_2025" in filename or "SFY25" in filename:
        return 2025
    # Check for SFY2024 (be careful not to match publication dates)
    elif "SFY24" in filename or "SFY_24" in filename:
        return 2024
    raise ValueError(f"Cannot determine SFY from filename: {filename}")


def get_column_config(sfy: int) -> ColumnConfig:
    """Get column configuration for a specific SFY."""
    if sfy not in SFY_CONFIGS:
        raise ValueError(f"No column configuration for SFY {sfy}")
    return SFY_CONFIGS[sfy]

