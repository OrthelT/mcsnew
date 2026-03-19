"""Load extracted data into the SQLite database."""

from typing import List, Dict, Any
from sqlalchemy.orm import Session

from .models import RateData, CategoryOfService
from .db import get_session, init_db


def get_or_create_category(session: Session, category_name: str) -> int:
    """Get or create a category of service, returning its ID."""
    category = session.query(CategoryOfService).filter(
        CategoryOfService.cos_name == category_name
    ).first()

    if category:
        return category.cos_id

    max_id = session.query(CategoryOfService.cos_id).order_by(
        CategoryOfService.cos_id.desc()
    ).first()

    new_id = (max_id[0] + 1) if max_id else 1
    new_category = CategoryOfService(cos_id=new_id, cos_name=category_name)
    session.add(new_category)
    session.flush()
    return new_id


def load_records(records: List[Dict[str, Any]], session: Session = None) -> int:
    """
    Load extracted records into the database.

    Uniqueness is keyed on (period_id, region_id, rate_cell_id, cos_id).
    Existing rows are updated in place; new rows are inserted.

    Returns the number of new records inserted.
    """
    close_session = False
    if session is None:
        session = get_session()
        close_session = True

    loaded_count = 0
    updated_count = 0

    try:
        for record in records:
            cos_id = get_or_create_category(session, record["category_name"])

            existing = session.query(RateData).filter(
                RateData.period_id == record["period_id"],
                RateData.region_id == record["region_id"],
                RateData.rate_cell_id == record["rate_cell_id"],
                RateData.cos_id == cos_id,
            ).first()

            if existing:
                existing.member_months = record["member_months"]
                existing.base_pmpm = record["base_pmpm"]
                existing.base_unit_cost = record["base_unit_cost"]
                existing.base_util = record["base_util"]
                existing.trend_pmpm = record["trend_pmpm"]
                existing.trend_unit_cost = record["trend_unit_cost"]
                existing.trend_util = record["trend_util"]
                existing.program_changes_pmpm = record["program_changes_pmpm"]
                existing.mcs_adjustment = record["mcs_adjustment"]
                existing.total_medical_pmpm = record["total_medical_pmpm"]
                existing.total_medical_unit_cost = record["total_medical_unit_cost"]
                existing.total_medical_util = record["total_medical_util"]
                updated_count += 1
            else:
                session.add(RateData(
                    period_id=record["period_id"],
                    sfy_id=record["sfy_id"],
                    region_id=record["region_id"],
                    rate_cell_id=record["rate_cell_id"],
                    cos_id=cos_id,
                    member_months=record["member_months"],
                    base_pmpm=record["base_pmpm"],
                    base_unit_cost=record["base_unit_cost"],
                    base_util=record["base_util"],
                    trend_pmpm=record["trend_pmpm"],
                    trend_unit_cost=record["trend_unit_cost"],
                    trend_util=record["trend_util"],
                    program_changes_pmpm=record["program_changes_pmpm"],
                    mcs_adjustment=record["mcs_adjustment"],
                    total_medical_pmpm=record["total_medical_pmpm"],
                    total_medical_unit_cost=record["total_medical_unit_cost"],
                    total_medical_util=record["total_medical_util"],
                ))
                loaded_count += 1

        session.commit()
        print(f"Loaded {loaded_count} new records, updated {updated_count} existing records")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        if close_session:
            session.close()

    return loaded_count


def clear_rate_data(session: Session = None):
    """Clear all rate data from the database (but keep reference tables)."""
    close_session = False
    if session is None:
        session = get_session()
        close_session = True

    try:
        deleted = session.query(RateData).delete()
        session.commit()
        print(f"Deleted {deleted} rate data records")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if close_session:
            session.close()
