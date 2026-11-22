from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_serializer


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    year: int
    season: str
    center_date: date
    value_celsius: Decimal

    @field_serializer("value_celsius", when_used="json")
    def serialize_value(self, value: Decimal) -> float:
        return float(value)


class ObservationResponse(BaseModel):
    index: str
    unit: str
    count: int
    period_start: date | None
    period_end: date | None
    observations: list[ObservationOut]


class SourceResponse(BaseModel):
    index: str
    url: str
    version: str
    extracted_at: date | None
    period_start: date
    period_end: date
    file_sha256: str


class Episode(BaseModel):
    id: str
    type: Literal["warm", "cold"]
    start: date
    end: date
    duration_seasons: int


class EpisodePoint(BaseModel):
    season_index: int
    season: str
    center_date: date
    value_celsius: Decimal

    @field_serializer("value_celsius", when_used="json")
    def serialize_value(self, value: Decimal) -> float:
        return float(value)


class EpisodeStats(Episode):
    minimum: Decimal
    maximum: Decimal
    mean: Decimal
    peak_season: str
    point_count: int
    series: list[EpisodePoint]

    @field_serializer("minimum", "maximum", "mean", when_used="json")
    def serialize_stat(self, value: Decimal) -> float:
        return float(value)


class CompareResponse(BaseModel):
    a: EpisodeStats
    b: EpisodeStats
    limitations: str
