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
    
    rate_data = relationship("RateData", back_populates="fiscal_year")
    
    def __repr__(self):
        return f"<FiscalYear({self.sfy_id}, {self.sfy_name})>"


class RateData(Base):
    """Main fact table storing capitation rate data by region, rate cell, and category."""
    __tablename__ = "rate_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sfy_id = Column(Integer, ForeignKey("fiscal_years.sfy_id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    rate_cell_id = Column(Integer, ForeignKey("rate_cells.rate_cell_id"), nullable=False)
    cos_id = Column(Integer, ForeignKey("categories_of_service.cos_id"), nullable=False)
    
    # Member months for the rate cell
    member_months = Column(Float, nullable=True)
    
    # Base data columns
    base_pmpm = Column(Float, nullable=True)
    base_unit_cost = Column(Float, nullable=True)
    base_util = Column(Float, nullable=True)
    
    # Trend columns
    trend_pmpm = Column(Float, nullable=True)
    trend_unit_cost = Column(Float, nullable=True)
    trend_util = Column(Float, nullable=True)
    
    # Program changes and MCS adjustment
    program_changes_pmpm = Column(Float, nullable=True)
    mcs_adjustment = Column(Float, nullable=True)
    
    # Total medical columns
    total_medical_pmpm = Column(Float, nullable=True)
    total_medical_unit_cost = Column(Float, nullable=True)
    total_medical_util = Column(Float, nullable=True)
    
    # Relationships
    fiscal_year = relationship("FiscalYear", back_populates="rate_data")
    region = relationship("Region", back_populates="rate_data")
    rate_cell = relationship("RateCell", back_populates="rate_data")
    category_of_service = relationship("CategoryOfService", back_populates="rate_data")
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        UniqueConstraint('sfy_id', 'region_id', 'rate_cell_id', 'cos_id', 
                         name='uix_rate_data_composite'),
    )
    
    def __repr__(self):
        return f"<RateData(SFY{self.sfy_id}, R{self.region_id}, {self.rate_cell_id}, {self.cos_id})>"

