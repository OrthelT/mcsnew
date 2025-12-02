"""Database connection and initialization for NC Medicaid rates database."""

from pathlib import Path
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import (
    Base, Region, RateCell, CategoryOfService, FiscalYear
)

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "rates.db"


def get_engine(db_path: Path = DB_PATH):
    """Create SQLAlchemy engine for SQLite database."""
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session(engine=None) -> Session:
    """Create a new database session."""
    if engine is None:
        engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def init_db(engine=None):
    """Initialize database schema and seed reference data."""
    if engine is None:
        engine = get_engine()
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    session = get_session(engine)
    
    try:
        # Seed regions if empty
        if session.query(Region).count() == 0:
            regions = [
                Region(region_id=1, region_name="Region 1", region_abbrev="R1"),
                Region(region_id=2, region_name="Region 2", region_abbrev="R2"),
                Region(region_id=3, region_name="Region 3", region_abbrev="R3"),
                Region(region_id=4, region_name="Region 4", region_abbrev="R4"),
                Region(region_id=5, region_name="Region 5", region_abbrev="R5"),
                Region(region_id=6, region_name="Region 6", region_abbrev="R6"),
            ]
            session.add_all(regions)
        
        # Seed rate cells if empty
        if session.query(RateCell).count() == 0:
            rate_cells = [
                RateCell(rate_cell_id=1, rate_cell_name="Aged, Blind, Disabled", rate_cell_abbrev="ABD"),
                RateCell(rate_cell_id=2, rate_cell_name="TANF Newborn", rate_cell_abbrev="TANF Newborn"),
                RateCell(rate_cell_id=3, rate_cell_name="TANF Child", rate_cell_abbrev="TANF Child"),
                RateCell(rate_cell_id=4, rate_cell_name="TANF Adult", rate_cell_abbrev="TANF Adult"),
                RateCell(rate_cell_id=5, rate_cell_name="Maternity", rate_cell_abbrev="MAT"),
                RateCell(rate_cell_id=6, rate_cell_name="Newly Eligible 19-24", rate_cell_abbrev="NE (19 - 24)"),
                RateCell(rate_cell_id=7, rate_cell_name="Newly Eligible 25-34", rate_cell_abbrev="NE (25 - 34)"),
                RateCell(rate_cell_id=8, rate_cell_name="Newly Eligible 35-44", rate_cell_abbrev="NE (35 - 44)"),
                RateCell(rate_cell_id=9, rate_cell_name="Newly Eligible 45+", rate_cell_abbrev="NE (45+)"),
            ]
            session.add_all(rate_cells)
        
        # Seed fiscal years if empty
        if session.query(FiscalYear).count() == 0:
            fiscal_years = [
                FiscalYear(
                    sfy_id=2022, 
                    sfy_name="SFY 2022",
                    contract_start=date(2021, 7, 1),
                    contract_end=date(2022, 6, 30)
                ),
                FiscalYear(
                    sfy_id=2023, 
                    sfy_name="SFY 2023",
                    contract_start=date(2022, 7, 1),
                    contract_end=date(2023, 6, 30)
                ),
                FiscalYear(
                    sfy_id=2024, 
                    sfy_name="SFY 2024",
                    contract_start=date(2024, 1, 1),
                    contract_end=date(2024, 6, 30)
                ),
                FiscalYear(
                    sfy_id=2025, 
                    sfy_name="SFY 2025",
                    contract_start=date(2024, 7, 1),
                    contract_end=date(2025, 6, 30)
                ),
                FiscalYear(
                    sfy_id=2026, 
                    sfy_name="SFY 2026",
                    contract_start=date(2025, 7, 1),
                    contract_end=date(2025, 9, 30)
                ),
            ]
            session.add_all(fiscal_years)
        
        # Seed categories of service if empty
        if session.query(CategoryOfService).count() == 0:
            categories = [
                "Inpatient - PH",
                "Inpatient - BH",
                "Outpatient Hospital - Facility",
                "Outpatient Hospital - Professional",
                "Emergency Room - PH",
                "Emergency Room - BH",
                "Physician - Primary Care",
                "Physician - Specialty",
                "FQHC/RHC",
                "Other Clinic",
                "Family Planning Services",
                "Other Professional - PH",
                "Other Professional - BH",
                "Therapies - PT/OT/ST",
                "Prescribed Drugs",
                "LTSS Services",
                "Durable Medical Equipment",
                "Lab and X-ray",
                "Optical",
                "Limited Dental Services",
                "Transportation - Emergency",
                "Transportation - Non-Emergency",
                "Home Health Services",
                "Hospice",
                "Nursing Facility",
                "Other Services",
            ]
            for i, cat_name in enumerate(categories, start=1):
                session.add(CategoryOfService(cos_id=i, cos_name=cat_name))
        
        session.commit()
        print("Database initialized successfully.")
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def reset_db(engine=None):
    """Drop all tables and reinitialize database."""
    if engine is None:
        engine = get_engine()
    
    Base.metadata.drop_all(engine)
    init_db(engine)
    print("Database reset complete.")


if __name__ == "__main__":
    init_db()

