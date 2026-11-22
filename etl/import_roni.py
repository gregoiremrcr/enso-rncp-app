"""Import the local NOAA CPC RONI text file into PostgreSQL."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

SEASONS = ("DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ")
MONTHS = {season: i + 1 for i, season in enumerate(SEASONS)}
SOURCE_URL = "https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt"
logger = logging.getLogger(__name__)


def parse_raw(path: str | Path) -> pd.DataFrame:
    """Read whitespace-separated records while retaining malformed data for rejection."""
    records: list[dict[str, object]] = []
    header_seen = False
    for line_number, line in enumerate(
        Path(path).read_text(encoding="ascii").splitlines(), start=1
    ):
        fields = line.split()
        if not fields:
            continue
        if not header_seen and fields[:3] == ["SEAS", "YR", "ANOM"]:
            header_seen = True
            continue
        if len(fields) == 3:
            season, year, value = fields
        else:
            season = fields[0]
            year = fields[1] if len(fields) > 1 else ""
            value = fields[2] if len(fields) > 2 else ""
        records.append({"season": season, "year": year, "value": value, "line": line_number})
    return pd.DataFrame(records, columns=["season", "year", "value", "line"])


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separate valid rows from invalid rows with one clear rejection reason each."""
    valid: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    for row in df.to_dict(orient="records"):
        reason = ""
        season = str(row["season"]).strip().upper()
        try:
            year = int(str(row["year"]).strip())
            if not 1 <= year <= 9998:
                raise ValueError
        except (ValueError, TypeError):
            year = 0
            reason = "année invalide"
        try:
            value = Decimal(str(row["value"]).strip())
            if not value.is_finite():
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            value = Decimal(0)
            reason = reason or "valeur manquante ou non numérique"
        if season not in SEASONS:
            reason = reason or "saison inconnue"
        if not Decimal(-5) <= value <= Decimal(5):
            reason = reason or "valeur hors de [-5, 5]"
        normalized = {**row, "season": season, "year": year, "value": value}
        if reason:
            rejected.append({**normalized, "reason": reason})
        else:
            valid.append(normalized)
    clean = pd.DataFrame(valid)
    if not clean.empty:
        duplicates = clean.duplicated(subset=["year", "season"], keep="first")
        for row in clean.loc[duplicates].to_dict(orient="records"):
            rejected.append({**row, "reason": "doublon supprimé"})
        clean = clean.loc[~duplicates].reset_index(drop=True)
    return clean, pd.DataFrame(rejected)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Convert seasons to their center month and values to Decimal."""
    result = df.copy()
    result["year"] = result["year"].astype("int64")
    result["season"] = result["season"].astype("string")
    result["value"] = result["value"].map(
        lambda value: value if isinstance(value, Decimal) else Decimal(str(value))
    )
    result["center_date"] = result.apply(
        lambda row: date(int(row["year"]), MONTHS[str(row["season"])], 1), axis=1
    )
    return result


def source_metadata(path: str | Path, metadata_path: str | Path) -> dict[str, object]:
    content = Path(metadata_path).read_text(encoding="utf-8")
    version_match = re.search(r"Version\s*:\s*([^\n]+)", content, re.IGNORECASE)
    date_match = re.search(r"Date d'extraction\s*:\s*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)
    frame = parse_raw(path)
    seasons = [str(v) for v in frame["season"]]
    years = [int(v) for v in frame["year"] if str(v).isdigit()]
    first = date(min(years), MONTHS[seasons[0]], 1)
    last = date(max(years), MONTHS[seasons[-1]], 1)
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {
        "version": (
            version_match.group(1).strip().split("(")[0].strip() if version_match else "À confirmer"
        ),
        "extracted_at": date.fromisoformat(date_match.group(1)) if date_match else None,
        "period_start": first,
        "period_end": last,
        "file_sha256": digest,
    }


def load(
    conn: Connection,
    frame: pd.DataFrame,
    rejected: pd.DataFrame,
    metadata: dict[str, object],
    rows_read: int,
) -> int:
    """Insert import metadata and new observations in the caller's transaction."""
    start = datetime.now(UTC)
    conn.execute(
        text(
            "INSERT INTO source (name,url,index_code,version,extracted_at,file_sha256,period_start,period_end) VALUES (:name,:url,:index_code,:version,:extracted_at,:hash,:start,:end) ON CONFLICT (file_sha256) DO UPDATE SET url=EXCLUDED.url,index_code=EXCLUDED.index_code,version=EXCLUDED.version,extracted_at=EXCLUDED.extracted_at,period_start=EXCLUDED.period_start,period_end=EXCLUDED.period_end"
        ),
        {
            "name": "NOAA CPC RONI",
            "url": SOURCE_URL,
            "index_code": "RONI",
            "version": metadata["version"],
            "extracted_at": metadata["extracted_at"],
            "hash": metadata["file_sha256"],
            "start": metadata["period_start"],
            "end": metadata["period_end"],
        },
    )
    source_id = conn.execute(
        text("SELECT id FROM source WHERE file_sha256=:hash"), {"hash": metadata["file_sha256"]}
    ).scalar_one()
    conn.execute(
        text(
            "INSERT INTO index_definition (code,unit,region,description) VALUES (:code,:unit,:region,:description) ON CONFLICT (code) DO NOTHING"
        ),
        {
            "code": "RONI",
            "unit": "°C",
            "region": "Niño 3.4 (relatif)",
            "description": "Relative Oceanic Niño Index de la NOAA CPC",
        },
    )
    index_id = conn.execute(
        text("SELECT id FROM index_definition WHERE code=:code"), {"code": "RONI"}
    ).scalar_one()
    rejection_records = rejected.to_dict(orient="records")
    rejection_records = [
        {key: str(value) if isinstance(value, Decimal) else value for key, value in row.items()}
        for row in rejection_records
    ]
    run_id = conn.execute(
        text(
            "INSERT INTO import_run (source_id,started_at,status,rows_read,rows_inserted,rows_rejected,rejection_log) VALUES (:source,:started,'success',:read,0,:rejected,CAST(:log AS JSONB)) RETURNING id"
        ),
        {
            "source": source_id,
            "started": start,
            "read": rows_read,
            "rejected": len(rejected),
            "log": json.dumps(rejection_records, ensure_ascii=False),
        },
    ).scalar_one()
    inserted = 0
    for row in frame.to_dict(orient="records"):
        result = conn.execute(
            text(
                "INSERT INTO observation (index_id,import_id,year,season,center_date,value_celsius) VALUES (:index_id,:import_id,:year,:season,:center_date,:value) ON CONFLICT (index_id,year,season) DO NOTHING"
            ),
            {
                "index_id": index_id,
                "import_id": run_id,
                "year": row["year"],
                "season": row["season"],
                "center_date": row["center_date"],
                "value": row["value"],
            },
        )
        inserted += result.rowcount or 0
    conn.execute(
        text("UPDATE import_run SET rows_inserted=:inserted,finished_at=:finished WHERE id=:id"),
        {"inserted": inserted, "finished": datetime.now(UTC), "id": run_id},
    )
    return inserted


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    path = Path(os.environ.get("SOURCE_FILE", "/data/RONI.ascii.txt"))
    metadata_path = Path(os.environ.get("SOURCE_METADATA_FILE", "/data/SOURCE.md"))
    if not path.is_file() or not metadata_path.is_file():
        logger.error("Fichier source ou SOURCE.md absent")
        return 1
    try:
        raw = parse_raw(path)
        valid, rejected = validate(raw)
        transformed = transform(valid)
        metadata = source_metadata(path, metadata_path)
        engine = create_engine(os.environ["DATABASE_URL"])
        with engine.begin() as conn:
            inserted = load(conn, transformed, rejected, metadata, len(raw))
        logger.info("RONI: %d lus, %d insérés, %d rejetés", len(raw), inserted, len(rejected))
        return 0
    except Exception:
        logger.exception("Échec de l'import RONI")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
