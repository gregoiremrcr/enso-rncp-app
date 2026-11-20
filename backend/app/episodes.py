from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from app.models import Observation
from app.schemas import Episode, EpisodePoint, EpisodeStats

# Définition historique CPC pour RONI : seuil de ±0,5 °C pendant 5 saisons
# glissantes consécutives. Elle ne prédit pas les conditions futures.
# Référence : https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/
RONI_THRESHOLD = Decimal("0.5")
MIN_CONSECUTIVE_SEASONS = 5


def detect_episodes(rows: Sequence[Observation]) -> list[Episode]:
    ordered = sorted(rows, key=lambda row: row.center_date)
    episodes: list[Episode] = []
    active: list[Observation] = []
    active_type: str | None = None
    previous: date | None = None

    def save() -> None:
        if len(active) >= MIN_CONSECUTIVE_SEASONS and active_type:
            first, last = active[0].center_date, active[-1].center_date
            label = "el-nino" if active_type == "warm" else "la-nina"
            episodes.append(
                Episode(
                    id=f"{label}-{first.year}-{first.month:02d}-{last.year}-{last.month:02d}",
                    type=active_type,
                    start=first,
                    end=last,
                    duration_seasons=len(active),
                )
            )

    for row in ordered:
        kind = (
            "warm"
            if row.value_celsius >= RONI_THRESHOLD
            else "cold" if row.value_celsius <= -RONI_THRESHOLD else None
        )
        consecutive = (
            previous is not None
            and (row.center_date.year * 12 + row.center_date.month)
            - (previous.year * 12 + previous.month)
            == 1
        )
        if kind != active_type or not consecutive:
            save()
            active = []
        active_type = kind
        if kind:
            active.append(row)
        previous = row.center_date
    save()
    return episodes


def episode_stats(rows: Sequence[Observation], episode: Episode) -> EpisodeStats:
    points = sorted(
        (row for row in rows if episode.start <= row.center_date <= episode.end),
        key=lambda row: row.center_date,
    )
    values = [row.value_celsius for row in points]
    peak = max(
        points, key=lambda row: row.value_celsius if episode.type == "warm" else -row.value_celsius
    )
    return EpisodeStats(
        **episode.model_dump(),
        minimum=min(values),
        maximum=max(values),
        mean=(sum(values) / len(values)).quantize(Decimal("0.01")),
        peak_season=peak.season,
        point_count=len(points),
        series=[
            EpisodePoint(
                season_index=i,
                season=row.season,
                center_date=row.center_date,
                value_celsius=row.value_celsius,
            )
            for i, row in enumerate(points)
        ],
    )
