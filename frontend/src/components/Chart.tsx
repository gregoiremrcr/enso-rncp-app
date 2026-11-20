import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Observation } from "../types";

export function Chart({ rows }: { rows: Observation[] }) {
  const lowerBound = (minimum: number) =>
    Math.floor((Math.min(minimum, -0.5) - 0.25) * 2) / 2;
  const upperBound = (maximum: number) =>
    Math.ceil((Math.max(maximum, 0.5) + 0.25) * 2) / 2;
  return (
    <figure
      aria-labelledby="roni-chart-title"
      aria-describedby="roni-chart-description"
    >
      <h2 id="roni-chart-title">Évolution de la RONI</h2>
      <p id="roni-chart-description" className="sr-only">
        Courbe historique de l’indice RONI en degrés Celsius. Les pointillés
        signalent les seuils de plus ou moins 0,5 degré.
      </p>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={rows}
            margin={{ top: 12, right: 18, left: 0, bottom: 8 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="center_date" minTickGap={48} />
            <YAxis unit=" °C" domain={[lowerBound, upperBound]} />
            <Tooltip
              formatter={(value) => [`${value} °C`, "RONI"]}
              labelFormatter={(label) => `Date centrale : ${label}`}
            />
            <ReferenceLine
              y={0.5}
              stroke="#a54331"
              strokeDasharray="7 4"
              label={{
                value: "+0,5 °C",
                position: "insideTopRight",
                fill: "#a54331",
                fontSize: 12,
              }}
            />
            <ReferenceLine
              y={-0.5}
              stroke="#155c78"
              strokeDasharray="2 4"
              label={{
                value: "−0,5 °C",
                position: "insideBottomRight",
                fill: "#155c78",
                fontSize: 12,
              }}
            />
            <Line
              type="monotone"
              dataKey="value_celsius"
              name="RONI"
              stroke="#173f52"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <figcaption>
        Trait plein : RONI · pointillés longs : seuil chaud +0,5 °C · pointillés
        courts : seuil froid −0,5 °C.
      </figcaption>
    </figure>
  );
}
