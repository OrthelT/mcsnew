"""Extract data from NC Medicaid capitation rate Excel files."""

from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from .normalize import (
    parse_tab_name, get_rate_cell_id, get_sfy_from_filename, 
    get_column_config, ColumnConfig
)


def extract_sheet_data(
    df: pd.DataFrame, 
    config: ColumnConfig,
    region_id: int,
    rate_cell_id: int,
    sfy: int,
) -> List[Dict[str, Any]]:
    """
    Extract rate data from a single sheet DataFrame.
    
    Returns a list of dictionaries, one per category of service row.
    """
    records = []
    
    # Get member months from the configured cell location
    mm_row, mm_col = config.member_months_cell
    try:
        member_months = float(df.iloc[mm_row, mm_col])
    except (ValueError, TypeError):
        member_months = None
    
    # Extract data rows
    for row_idx in range(config.data_start_row, config.data_end_row):
        try:
            row = df.iloc[row_idx]
            
            # Get category name
            category = row.iloc[config.category_col]
            if pd.isna(category) or not isinstance(category, str) or category.strip() == "":
                continue
            
            category = category.strip()
            
            # Skip "Total" row in data section
            if category.lower() in ["total", "total medical"]:
                continue
            
            # Extract values, handling NaN
            def safe_float(val):
                try:
                    if pd.isna(val):
                        return None
                    return float(val)
                except (ValueError, TypeError):
                    return None
            
            record = {
                "sfy_id": sfy,
                "region_id": region_id,
                "rate_cell_id": rate_cell_id,
                "category_name": category,
                "member_months": member_months,
                "base_pmpm": safe_float(row.iloc[config.base_pmpm_col]),
                "base_unit_cost": safe_float(row.iloc[config.base_unit_cost_col]),
                "base_util": safe_float(row.iloc[config.base_util_col]),
                "trend_pmpm": safe_float(row.iloc[config.trend_pmpm_col]),
                "trend_unit_cost": safe_float(row.iloc[config.trend_unit_cost_col]),
                "trend_util": safe_float(row.iloc[config.trend_util_col]),
                "program_changes_pmpm": safe_float(row.iloc[config.program_changes_col]),
                "mcs_adjustment": safe_float(row.iloc[config.mcs_adjustment_col]),
                "total_medical_pmpm": safe_float(row.iloc[config.total_medical_pmpm_col]),
                "total_medical_unit_cost": safe_float(row.iloc[config.total_medical_unit_cost_col]),
                "total_medical_util": safe_float(row.iloc[config.total_medical_util_col]),
            }
            
            records.append(record)
            
        except Exception as e:
            print(f"Warning: Error extracting row {row_idx}: {e}")
            continue
    
    return records


def extract_file(filepath: Path) -> List[Dict[str, Any]]:
    """
    Extract all rate data from a single Excel file.
    
    Returns a list of all records from all valid sheets.
    """
    filename = filepath.name
    sfy = get_sfy_from_filename(filename)
    config = get_column_config(sfy)
    
    print(f"Extracting SFY {sfy} from {filename}...")
    
    all_records = []
    
    # Load Excel file
    xl = pd.ExcelFile(filepath)
    
    for sheet_name in xl.sheet_names:
        # Parse tab name to get region and rate cell
        parsed = parse_tab_name(sheet_name)
        if parsed is None:
            continue
        
        region_id, rate_cell_abbrev = parsed
        rate_cell_id = get_rate_cell_id(rate_cell_abbrev)
        
        if rate_cell_id == 0:
            print(f"  Warning: Unknown rate cell '{rate_cell_abbrev}' in sheet '{sheet_name}'")
            continue
        
        # Read sheet without headers (we'll extract using indices)
        df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
        
        # Extract data from sheet
        records = extract_sheet_data(df, config, region_id, rate_cell_id, sfy)
        
        print(f"  Extracted {len(records)} records from '{sheet_name}'")
        all_records.extend(records)
    
    print(f"  Total: {len(all_records)} records from SFY {sfy}")
    return all_records


def extract_all_files(data_dir: Path) -> List[Dict[str, Any]]:
    """
    Extract data from all Excel files in the data directory.
    
    Returns combined list of all records.
    """
    all_records = []
    
    # Find all xlsx files
    xlsx_files = list(data_dir.glob("*.xlsx"))
    
    if not xlsx_files:
        raise ValueError(f"No .xlsx files found in {data_dir}")
    
    for filepath in sorted(xlsx_files):
        try:
            records = extract_file(filepath)
            all_records.extend(records)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            raise
    
    print(f"\nTotal extracted: {len(all_records)} records from {len(xlsx_files)} files")
    return all_records


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "data"
    records = extract_all_files(data_dir)
    
    # Preview first few records
    print("\nSample records:")
    for r in records[:3]:
        print(r)

