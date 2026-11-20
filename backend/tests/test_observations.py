from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_session
from app.main import app
from app.models import Base, ImportRun, IndexDefinition, Observation, Source


@pytest.fixture
def client():
    # Les six observations ci-dessous sont une fixture de test, jamais la série NOAA.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        source = Source(
            name="fixture",
            url="https://example.invalid/fixture",
            index_code="RONI",
            version="fixture",
            extracted_at=None,
            file_sha256="a" * 64,
            period_start=date(2000, 1, 1),
            period_end=date(2000, 6, 1),
        )
        definition = IndexDefinition(
            code="RONI", unit="°C", region="fixture", description="Fixture de test uniquement"
        )
        session.add_all([source, definition])
        session.flush()
        run = ImportRun(
            source_id=source.id,
            started_at=datetime.now(UTC),
            finished_at=datetime.now(UTC),
            status="success",
            rows_read=6,
            rows_inserted=6,
            rows_rejected=0,
            rejection_log=[],
        )
        session.add(run)
        session.flush()
        for index, (month, value) in enumerate(
            [(1, "0.10"), (2, "0.20"), (3, "0.30"), (4, "0.40"), (5, "0.50"), (6, "0.60")], start=1
        ):
            session.add(
                Observation(
                    index_id=definition.id,
                    import_id=run.id,
                    year=2000,
                    season=["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ"][index - 1],
                    center_date=date(2000, month, 1),
                    value_celsius=Decimal(value),
                )
            )
        session.commit()

    def override_session():
        with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_observations_filtered_and_invalid_dates(client):
    # Ce test protège les bornes de période, l'ordre et les statuts 400/422.
    response = client.get("/api/v1/observations?start=2000-02-01&end=2000-04-01")
    assert response.status_code == 200
    body = response.json()
    assert [item["value_celsius"] for item in body["observations"]] == [0.2, 0.3, 0.4]
    assert body["count"] == 3
    assert client.get("/api/v1/observations?start=2000-05-01&end=2000-02-01").status_code == 400
    assert client.get("/api/v1/observations?start=not-a-date").status_code == 422
