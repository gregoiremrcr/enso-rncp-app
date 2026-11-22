# ruff: noqa: B008
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db import get_session
from app.episodes import detect_episodes, episode_stats
from app.models import ImportRun, IndexDefinition, Observation, Source
from app.schemas import CompareResponse, Episode, ObservationResponse, SourceResponse

router = APIRouter()


@router.get("/health", summary="État de l'API et de la base")
def health(session: Session = Depends(get_session)) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Base de données indisponible") from exc


@router.get("/observations", response_model=ObservationResponse, summary="Série chronologique RONI")
def observations(
    start: date | None = Query(None, description="Date ISO minimale, incluse"),
    end: date | None = Query(None, description="Date ISO maximale, incluse"),
    session: Session = Depends(get_session),
) -> ObservationResponse:
    if start and end and start > end:
        raise HTTPException(
            status_code=400, detail="La date de début doit précéder la date de fin."
        )
    query = select(Observation).join(IndexDefinition).where(IndexDefinition.code == "RONI")
    if start:
        query = query.where(Observation.center_date >= start)
    if end:
        query = query.where(Observation.center_date <= end)
    rows = list(session.scalars(query.order_by(Observation.center_date)))
    return ObservationResponse(
        index="RONI",
        unit="°C",
        count=len(rows),
        period_start=rows[0].center_date if rows else None,
        period_end=rows[-1].center_date if rows else None,
        observations=rows,
    )


@router.get(
    "/source",
    response_model=SourceResponse,
    summary="Métadonnées de la dernière importation NOAA CPC",
)
def source(session: Session = Depends(get_session)) -> SourceResponse:
    latest = session.execute(
        select(Source, ImportRun)
        .join(ImportRun, ImportRun.source_id == Source.id)
        .where(ImportRun.status == "success")
        .order_by(ImportRun.finished_at.desc())
        .limit(1)
    ).first()
    if not latest:
        raise HTTPException(status_code=404, detail="Aucune importation disponible.")
    item, _run = latest
    return SourceResponse(
        index=item.index_code,
        url=item.url,
        version=item.version,
        extracted_at=item.extracted_at,
        period_start=item.period_start,
        period_end=item.period_end,
        file_sha256=item.file_sha256,
    )


def _episode_data(session: Session) -> tuple[list[Observation], list[Episode]]:
    rows = list(
        session.scalars(
            select(Observation)
            .join(IndexDefinition)
            .where(IndexDefinition.code == "RONI")
            .order_by(Observation.center_date)
        )
    )
    return rows, detect_episodes(rows)


@router.get(
    "/episodes",
    response_model=list[Episode],
    summary="Épisodes historiques selon les seuils CPC RONI",
)
def episodes(session: Session = Depends(get_session)) -> list[Episode]:
    return _episode_data(session)[1]


@router.get(
    "/episodes/compare", response_model=CompareResponse, summary="Comparer deux épisodes RONI"
)
def compare(
    a: str = Query(..., min_length=1),
    b: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> CompareResponse:
    rows, episodes_found = _episode_data(session)
    by_id = {episode.id: episode for episode in episodes_found}
    if a not in by_id or b not in by_id:
        raise HTTPException(status_code=404, detail="Un épisode demandé est inconnu.")
    return CompareResponse(
        a=episode_stats(rows, by_id[a]),
        b=episode_stats(rows, by_id[b]),
        limitations="RONI est un indice, pas une prévision. La comparaison décrit les valeurs et la durée selon le seuil CPC de ±0,5 °C pendant au moins cinq saisons glissantes consécutives. Des profils semblables ne démontrent aucune causalité et cette définition historique ne décrit pas toutes les dimensions de l'ENSO.",
    )
