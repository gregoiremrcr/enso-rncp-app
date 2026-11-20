from decimal import Decimal

import pandas as pd

from import_roni import transform, validate


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
