export type Observation = {
  year: number;
  season: string;
  center_date: string;
  value_celsius: number;
};
export type ObservationResponse = {
  index: "RONI";
  unit: string;
  count: number;
  period_start: string | null;
  period_end: string | null;
  observations: Observation[];
};
export type SourceInfo = {
  index: string;
  url: string;
  version: string;
  extracted_at: string | null;
  period_start: string;
  period_end: string;
  file_sha256: string;
};
export type Episode = {
  id: string;
  type: "warm" | "cold";
  start: string;
  end: string;
  duration_seasons: number;
};
export type EpisodeStats = Episode & {
  minimum: number;
  maximum: number;
  mean: number;
  peak_season: string;
  point_count: number;
  series: {
    season_index: number;
    season: string;
    center_date: string;
    value_celsius: number;
  }[];
};
export type CompareResponse = {
  a: EpisodeStats;
  b: EpisodeStats;
  limitations: string;
};
