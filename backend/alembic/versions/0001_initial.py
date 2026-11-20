"""Create source, definition, import and observation tables."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

seasons = ("DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ")


def upgrade() -> None:
    op.create_table(
        "source",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("index_code", sa.String(20), nullable=False),
        sa.Column("version", sa.String(80), nullable=False),
        sa.Column("extracted_at", sa.Date(), nullable=True),
        sa.Column("file_sha256", sa.String(64), nullable=False, unique=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
    )
    op.create_table(
        "index_definition",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("unit", sa.String(10), nullable=False),
        sa.Column("region", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )
    op.create_table(
        "import_run",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("source.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("rows_read", sa.Integer(), nullable=False),
        sa.Column("rows_inserted", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("rejection_log", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.CheckConstraint("status IN ('success', 'failed')"),
    )
    op.create_table(
        "observation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("index_id", sa.Integer(), sa.ForeignKey("index_definition.id"), nullable=False),
        sa.Column("import_id", sa.Integer(), sa.ForeignKey("import_run.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("season", sa.CHAR(3), nullable=False),
        sa.Column("center_date", sa.Date(), nullable=False),
        sa.Column("value_celsius", sa.Numeric(4, 2), nullable=False),
        sa.UniqueConstraint("index_id", "year", "season", name="uq_observation_index_year_season"),
        sa.CheckConstraint(
            "season IN (" + ",".join("'" + s + "'" for s in seasons) + ")",
            name="ck_observation_season",
        ),
        sa.CheckConstraint("value_celsius BETWEEN -5 AND 5", name="ck_observation_value"),
    )
    op.create_index("ix_observation_index_center", "observation", ["index_id", "center_date"])


def downgrade() -> None:
    op.drop_index("ix_observation_index_center", table_name="observation")
    op.drop_table("observation")
    op.drop_table("import_run")
    op.drop_table("index_definition")
    op.drop_table("source")
