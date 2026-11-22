from datetime import date
from decimal import Decimal
import sqlite3

import pandas as pd
from sqlalchemy import create_engine, text

from import_roni import load, source_metadata, transform, validate


def test_validate_and_transform_fixture():
    # Ce test protège le rejet des lignes invalides, la déduplication et les types/date attendus.
    fixture = pd.DataFrame(
        [
            {"season": "DJF", "year": "1950", "value": "-1.47", "line": 2},
            {"season": "DJF", "year": "1950", "value": "-1.47", "line": 3},
            {"season": "BAD", "year": "1950", "value": "0.2", "line": 4},
            {"season": "JFM", "year": "1950", "value": "abc", "line": 5},
            {"season": "FMA", "year": "1950", "value": "5.1", "line": 6},
        ]
    )
    valid, rejected = validate(fixture)
    converted = transform(valid)
    assert len(converted) == 1
    assert converted.iloc[0]["value"] == Decimal("-1.47")
    assert converted.iloc[0]["center_date"].isoformat() == "1950-01-01"
    assert len(rejected) == 4
    assert set(rejected["reason"]) == {
        "doublon supprimé",
        "saison inconnue",
        "valeur manquante ou non numérique",
        "valeur hors de [-5, 5]",
    }


def test_metadata_date_and_reimport_are_idempotent(tmp_path):
    raw_path = tmp_path / "RONI.ascii.txt"
    raw_path.write_text("SEAS   YR  ANOM\nDJF  1950 -1.19\n", encoding="ascii")
    metadata_path = tmp_path / "SOURCE.md"
    metadata_path.write_text(
        "- Version : ERSSTv6\n- Date d'extraction : 2026-11-11.\n",
        encoding="utf-8",
    )
    metadata = source_metadata(raw_path, metadata_path)
    assert metadata["extracted_at"] == date(2026, 11, 11)

    engine = create_engine("sqlite://")
    sqlite3.register_adapter(Decimal, str)
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE source (id INTEGER PRIMARY KEY, name TEXT, url TEXT, index_code TEXT, version TEXT, extracted_at DATE, file_sha256 TEXT UNIQUE, period_start DATE, period_end DATE)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE index_definition (id INTEGER PRIMARY KEY, code TEXT UNIQUE, unit TEXT, region TEXT, description TEXT)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE import_run (id INTEGER PRIMARY KEY, source_id INTEGER, started_at TEXT, finished_at TEXT, status TEXT, rows_read INTEGER, rows_inserted INTEGER, rows_rejected INTEGER, rejection_log TEXT)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE observation (id INTEGER PRIMARY KEY, index_id INTEGER, import_id INTEGER, year INTEGER, season TEXT, center_date DATE, value_celsius NUMERIC, UNIQUE(index_id, year, season))"
        )
        raw = pd.DataFrame(
            [
                {
                    "season": "DJF",
                    "year": 1950,
                    "value": Decimal("-1.19"),
                    "line": 2,
                    "center_date": date(1950, 1, 1),
                }
            ]
        )
        rejected = pd.DataFrame()
        existing_metadata = {**metadata, "extracted_at": None}
        assert load(conn, raw, rejected, existing_metadata, 1) == 1
        assert load(conn, raw, rejected, metadata, 1) == 0
        assert conn.execute(text("SELECT COUNT(*) FROM observation")).scalar_one() == 1
        assert conn.execute(text("SELECT extracted_at FROM source")).scalar_one() == "2026-11-11"
