"""SQLAlchemy ORM models for NC Medicaid capitation rates database."""

from sqlalchemy import (
    Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Region(Base):
    """Reference table for NC Medicaid regions (1-6)."""
    __tablename__ = "regions"

    region_id = Column(Integer, primary_key=True)
    region_name = Column(String(50), nullable=False, unique=True)
    region_abbrev = Column(String(10), nullable=False, unique=True)

    rate_data = relationship("RateData", back_populates="region")

    def __repr__(self):
        return f"<Region({self.region_id}, {self.region_abbrev})>"


class RateCell(Base):
    """Reference table for rate cell types (ABD, TANF, etc.)."""
    __tablename__ = "rate_cells"

    rate_cell_id = Column(Integer, primary_key=True)
    rate_cell_name = Column(String(100), nullable=False, unique=True)
    rate_cell_abbrev = Column(String(50), nullable=False, unique=True)

    rate_data = relationship("RateData", back_populates="rate_cell")

    def __repr__(self):
        return f"<RateCell({self.rate_cell_id}, {self.rate_cell_abbrev})>"


class CategoryOfService(Base):
    """Reference table for categories of service."""
    __tablename__ = "categories_of_service"

    cos_id = Column(Integer, primary_key=True)
    cos_name = Column(String(100), nullable=False, unique=True)

    rate_data = relationship("RateData", back_populates="category_of_service")

    def __repr__(self):
        return f"<CategoryOfService({self.cos_id}, {self.cos_name})>"


class FiscalYear(Base):
    """Reference table for state fiscal years."""
    __tablename__ = "fiscal_years"

    sfy_id = Column(Integer, primary_key=True)
    sfy_name = Column(String(20), nullable=False, unique=True)
    contract_start = Column(Date, nullable=True)
    contract_end = Column(Date, nullable=True)

    rate_periods = relationship("RatePeriod", back_populates="fiscal_year")
    rate_data = relationship("RateData", back_populates="fiscal_year")

    def __repr__(self):
        return f"<FiscalYear({self.sfy_id}, {self.sfy_name})>"


class RatePeriod(Base):
    """
    A single rate-setting period within a fiscal year.

    Most fiscal years have one period (the full year).  SFY 2024 has three
    sub-periods because program changes mid-year materially altered rates.
    """
    __tablename__ = "rate_periods"

    period_id = Column(Integer, primary_key=True)
    sfy_id = Column(Integer, ForeignKey("fiscal_years.sfy_id"), nullable=False)
    period_name = Column(String(50), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    months_in_period = Column(Integer, nullable=False)
    trend_months = Column(Integer, nullable=False)   # Actuarial trend months in this file
    source_filename = Column(String(200), nullable=True)

    fiscal_year = relationship("FiscalYear", back_populates="rate_periods")
    rate_data = relationship("RateData", back_populates="rate_period")

    def __repr__(self):
        return f"<RatePeriod({self.period_id}, sfy={self.sfy_id}, '{self.period_name}')>"


class RateData(Base):
    """Main fact table storing capitation rate data by period, region, rate cell, and category."""
    __tablename__ = "rate_data"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # period_id is the primary key for "which rate file does this row come from".
    # sfy_id is kept as a convenience denormalization for simpler aggregation queries.
    period_id = Column(Integer, ForeignKey("rate_periods.period_id"), nullable=False)
    sfy_id = Column(Integer, ForeignKey("fiscal_years.sfy_id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    rate_cell_id = Column(Integer, ForeignKey("rate_cells.rate_cell_id"), nullable=False)
    cos_id = Column(Integer, ForeignKey("categories_of_service.cos_id"), nullable=False)

    # Member months for this rate cell in this rate period
    member_months = Column(Float, nullable=True)

    # Base data columns
    base_pmpm = Column(Float, nullable=True)
    base_unit_cost = Column(Float, nullable=True)
    base_util = Column(Float, nullable=True)

    # Trend columns (trend_pmpm stores the annual trend RATE, e.g. 0.034 = 3.4%)
    trend_pmpm = Column(Float, nullable=True)
    trend_unit_cost = Column(Float, nullable=True)
    trend_util = Column(Float, nullable=True)

    # Program changes and MCS adjustment (stored as decimal factors, e.g. -0.089)
    program_changes_pmpm = Column(Float, nullable=True)
    mcs_adjustment = Column(Float, nullable=True)

    # Total medical columns
    total_medical_pmpm = Column(Float, nullable=True)
    total_medical_unit_cost = Column(Float, nullable=True)
    total_medical_util = Column(Float, nullable=True)

    # Relationships
    rate_period = relationship("RatePeriod", back_populates="rate_data")
    fiscal_year = relationship("FiscalYear", back_populates="rate_data")
    region = relationship("Region", back_populates="rate_data")
    rate_cell = relationship("RateCell", back_populates="rate_data")
    category_of_service = relationship("CategoryOfService", back_populates="rate_data")

    # Unique per period — allows multiple SFY2024 sub-periods for the same region/cell/category
    __table_args__ = (
        UniqueConstraint('period_id', 'region_id', 'rate_cell_id', 'cos_id',
                         name='uix_rate_data_composite'),
    )

    def __repr__(self):
        return f"<RateData(period={self.period_id}, R{self.region_id}, {self.rate_cell_id}, {self.cos_id})>"
