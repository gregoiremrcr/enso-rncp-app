from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "source"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(Text)
    index_code: Mapped[str] = mapped_column(String(20))
    version: Mapped[str] = mapped_column(String(80))
    extracted_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    file_sha256: Mapped[str] = mapped_column(String(64), unique=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)


class IndexDefinition(Base):
    __tablename__ = "index_definition"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    unit: Mapped[str] = mapped_column(String(10))
    region: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)


class ImportRun(Base):
    __tablename__ = "import_run"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(10))
    rows_read: Mapped[int] = mapped_column(Integer)
    rows_inserted: Mapped[int] = mapped_column(Integer)
    rows_rejected: Mapped[int] = mapped_column(Integer)
    rejection_log: Mapped[list[dict]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    __table_args__ = (CheckConstraint("status IN ('success', 'failed')"),)


class Observation(Base):
    __tablename__ = "observation"
    id: Mapped[int] = mapped_column(primary_key=True)
    index_id: Mapped[int] = mapped_column(ForeignKey("index_definition.id"))
    import_id: Mapped[int] = mapped_column(ForeignKey("import_run.id"))
    year: Mapped[int] = mapped_column(Integer)
    season: Mapped[str] = mapped_column(String(3))
    center_date: Mapped[date] = mapped_column(Date)
    value_celsius: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    __table_args__ = (
        UniqueConstraint("index_id", "year", "season", name="uq_observation_index_year_season"),
        CheckConstraint(
            "season IN ('DJF','JFM','FMA','MAM','AMJ','MJJ','JJA','JAS','ASO','SON','OND','NDJ')",
            name="ck_observation_season",
        ),
        CheckConstraint("value_celsius BETWEEN -5 AND 5", name="ck_observation_value"),
        Index("ix_observation_index_center", "index_id", "center_date"),
    )
