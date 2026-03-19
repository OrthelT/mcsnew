"""Extract data from NC Medicaid capitation rate Excel files."""

from pathlib import Path
from typing import List, Dict, Any, Union
import pandas as pd

from .normalize import (
    parse_tab_name, get_rate_cell_id, get_column_config, ColumnConfig,
    FILENAME_TO_PERIOD,
)


def extract_sheet_data(
    df: pd.DataFrame,
    config: ColumnConfig,
    region_id: int,
    rate_cell_id: int,
    sfy: int,
    period_id: int,
    source_filename: str,
    months_in_period: int = 12,
) -> List[Dict[str, Any]]:
    """
    Extract rate data from a single sheet DataFrame.

    Rate files always store annualised enrollment (member months for a full
    12-month year).  For sub-year rate periods the annualised figure is prorated
    to match the actual period length before storing it in the database.

    Returns a list of dictionaries, one per category of service row.
    """
    records = []

    mm_row, mm_col = config.member_months_cell
    try:
        raw_member_months = float(df.iloc[mm_row, mm_col])
        # Prorate annual enrollment to the actual rate-period length
        member_months = raw_member_months * months_in_period / 12
    except (ValueError, TypeError):
        member_months = None

    for row_idx in range(config.data_start_row, config.data_end_row):
        try:
            row = df.iloc[row_idx]

            category = row.iloc[config.category_col]
            if pd.isna(category) or not isinstance(category, str) or category.strip() == "":
                continue

            category = category.strip()

            if category.lower() in ["total", "total medical"]:
                continue

            def safe_float(val):
                try:
                    if pd.isna(val):
                        return None
                    return float(val)
                except (ValueError, TypeError):
                    return None

            record = {
                "period_id": period_id,
                "sfy_id": sfy,
                "source_filename": source_filename,
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

    Only processes files listed in FILENAME_TO_PERIOD.  Returns an empty list
    and logs a warning for unrecognised files.
    """
    filename = filepath.name

    period_info = FILENAME_TO_PERIOD.get(filename)
    if period_info is None:
        print(f"  Skipping unrecognised file: {filename}")
        return []

    sfy = period_info.sfy_id
    period_id = period_info.period_id
    config = get_column_config(sfy)

    print(f"Extracting period {period_id} ({period_info.period_name}) from {filename}...")

    all_records = []
    xl = pd.ExcelFile(filepath)

    for sheet_name in xl.sheet_names:
        parsed = parse_tab_name(sheet_name)
        if parsed is None:
            continue

        region_id, rate_cell_abbrev = parsed
        rate_cell_id = get_rate_cell_id(rate_cell_abbrev)

        if rate_cell_id == 0:
            print(f"  Warning: Unknown rate cell '{rate_cell_abbrev}' in sheet '{sheet_name}'")
            continue

        df = pd.read_excel(xl, sheet_name=sheet_name, header=None)

        records = extract_sheet_data(
            df, config, region_id, rate_cell_id, sfy, period_id, filename,
            months_in_period=period_info.months_in_period,
        )

        print(f"  Extracted {len(records)} records from '{sheet_name}'")
        all_records.extend(records)

    print(f"  Total: {len(all_records)} records from period {period_id}")
    return all_records


def extract_all_files(data_dirs: Union[Path, List[Path]]) -> List[Dict[str, Any]]:
    """
    Extract data from all known Excel files found in one or more directories.

    Deduplicates by filename so that the same file appearing in multiple
    directories (e.g. archive copies) is only processed once.
    """
    if isinstance(data_dirs, Path):
        data_dirs = [data_dirs]

    all_records = []
    seen_filenames: set = set()

    for data_dir in data_dirs:
        if not data_dir.exists():
            print(f"Directory not found, skipping: {data_dir}")
            continue

        for filepath in sorted(data_dir.glob("*.xlsx")):
            if filepath.name in seen_filenames:
                print(f"Skipping duplicate: {filepath.name}")
                continue

            # Only process files we know about
            if filepath.name not in FILENAME_TO_PERIOD:
                continue

            seen_filenames.add(filepath.name)
            try:
                records = extract_file(filepath)
                all_records.extend(records)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                raise

    print(f"\nTotal extracted: {len(all_records)} records from {len(seen_filenames)} files")
    return all_records
