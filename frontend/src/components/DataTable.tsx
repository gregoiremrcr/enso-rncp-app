import type { Observation } from "../types";
export function DataTable({ rows }: { rows: Observation[] }) {
  return (
    <details>
      <summary>Afficher les données en tableau</summary>
      <div className="table-scroll">
        <table>
          <caption>Observations RONI affichées sur le graphique</caption>
          <thead>
            <tr>
              <th scope="col">Date centrale</th>
              <th scope="col">Saison</th>
              <th scope="col">RONI (°C)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.year}-${row.season}`}>
                <td>{row.center_date}</td>
                <td>{row.season}</td>
                <td>{row.value_celsius.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}
