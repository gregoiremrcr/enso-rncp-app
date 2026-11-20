import { useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useCompare } from "../hooks/useCompare";
import type { Episode } from "../types";

export function EpisodeCompare({ episodes }: { episodes: Episode[] }) {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const { data, error, loading } = useCompare(a, b);
  const chartRows = data
    ? Array.from(
        { length: Math.max(data.a.series.length, data.b.series.length) },
        (_, index) => ({
          index,
          a: data.a.series[index]?.value_celsius,
          b: data.b.series[index]?.value_celsius,
        }),
      )
    : [];
  const label = (episode: Episode) =>
    `${episode.type === "warm" ? "El Niño" : "La Niña"} · ${episode.start.slice(0, 4)}–${episode.end.slice(0, 4)} (${episode.duration_seasons} saisons)`;
  return (
    <section aria-labelledby="compare-heading">
      <h2 id="compare-heading">Comparer deux épisodes</h2>
      <div className="select-row">
        <label htmlFor="episode-a">Épisode A</label>
        <select
          id="episode-a"
          value={a}
          onChange={(event) => setA(event.target.value)}
        >
          <option value="">Choisir un épisode</option>
          {episodes.map((ep) => (
            <option key={ep.id} value={ep.id}>
              {label(ep)}
            </option>
          ))}
        </select>
        <label htmlFor="episode-b">Épisode B</label>
        <select
          id="episode-b"
          value={b}
          onChange={(event) => setB(event.target.value)}
        >
          <option value="">Choisir un épisode</option>
          {episodes.map((ep) => (
            <option key={ep.id} value={ep.id}>
              {label(ep)}
            </option>
          ))}
        </select>
      </div>
      {loading && <p role="status">Comparaison en cours…</p>}
      {error && <p role="alert">{error}</p>}
      {data && (
        <>
          <div className="table-scroll">
            <table>
              <caption>Statistiques des épisodes sélectionnés</caption>
              <thead>
                <tr>
                  <th>Statistique</th>
                  <th>Épisode A</th>
                  <th>Épisode B</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th>Début – fin</th>
                  <td>
                    {data.a.start} – {data.a.end}
                  </td>
                  <td>
                    {data.b.start} – {data.b.end}
                  </td>
                </tr>
                <tr>
                  <th>Durée</th>
                  <td>{data.a.duration_seasons} saisons</td>
                  <td>{data.b.duration_seasons} saisons</td>
                </tr>
                <tr>
                  <th>Min / max</th>
                  <td>
                    {data.a.minimum} / {data.a.maximum} °C
                  </td>
                  <td>
                    {data.b.minimum} / {data.b.maximum} °C
                  </td>
                </tr>
                <tr>
                  <th>Moyenne</th>
                  <td>{data.a.mean} °C</td>
                  <td>{data.b.mean} °C</td>
                </tr>
                <tr>
                  <th>Saison du pic</th>
                  <td>{data.a.peak_season}</td>
                  <td>{data.b.peak_season}</td>
                </tr>
                <tr>
                  <th>Nombre de points</th>
                  <td>{data.a.point_count}</td>
                  <td>{data.b.point_count}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div
            className="chart compare-chart"
            role="img"
            aria-label="Comparaison des valeurs RONI par saison relative, série A en trait plein et série B en tirets"
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartRows}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="index"
                  label={{
                    value: "Saison relative",
                    position: "insideBottom",
                    offset: -2,
                  }}
                />
                <YAxis unit=" °C" />
                <Tooltip />
                <Legend />
                <Line
                  dataKey="a"
                  name="Épisode A — trait plein"
                  stroke="#173f52"
                  dot={false}
                  connectNulls
                  isAnimationActive={false}
                />
                <Line
                  dataKey="b"
                  name="Épisode B — tirets"
                  stroke="#a54331"
                  strokeDasharray="7 4"
                  dot={false}
                  connectNulls
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <h3>Interprétation et limites</h3>
          <p>{data.limitations}</p>
        </>
      )}
    </section>
  );
}
