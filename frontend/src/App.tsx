import { useState } from "react";
import { Chart } from "./components/Chart";
import { DataTable } from "./components/DataTable";
import { EpisodeCompare } from "./components/EpisodeCompare";
import { PeriodFilter } from "./components/PeriodFilter";
import { useObservations } from "./hooks/useObservations";
import { useEpisodes } from "./hooks/useEpisodes";
import { useSource } from "./hooks/useSource";
import { ErrorState } from "./components/ErrorState";
import { Loading } from "./components/Loading";

export default function App() {
  const [draftStart, setDraftStart] = useState("");
  const [draftEnd, setDraftEnd] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const invalid = Boolean(draftStart && draftEnd && draftStart > draftEnd);
  const { data, error, loading, retry } = useObservations(start, end);
  const { source, error: metadataError } = useSource();
  const { episodes, error: episodesError } = useEpisodes();
  return (
    <main>
      <header className="hero">
        <div className="hero-content">
          <p className="eyebrow">CLIMAT · DONNÉES HISTORIQUES</p>
          <h1>ENSO Monitor</h1>
          <p>
            Explorer la Relative Oceanic Niño Index (RONI) publiée par la NOAA
            CPC.
          </p>
          <div className="hero-tags" aria-label="Résumé de la série">
            <span>NOAA CPC</span>
            <span>1950 — 2026</span>
            <span>RONI · °C</span>
          </div>
        </div>
        <div className="hero-orb" aria-hidden="true" />
      </header>
      <section className="panel" aria-labelledby="data-heading">
        <h2 id="data-heading">Série temporelle</h2>
        <PeriodFilter
          start={draftStart}
          end={draftEnd}
          onStart={setDraftStart}
          onEnd={setDraftEnd}
          onApply={() => {
            setStart(draftStart);
            setEnd(draftEnd);
          }}
          invalid={invalid}
        />
        {source && (
          <p className="source-line">
            Source : <a href={source.url}>NOAA CPC — RONI</a> · {source.version}{" "}
            · extraction : {source.extracted_at ?? "date non indiquée"}
          </p>
        )}
        {metadataError && (
          <ErrorState
            message={`Métadonnées source indisponibles : ${metadataError}`}
          />
        )}
        {loading && <Loading>Chargement des observations…</Loading>}
        {error && <ErrorState message={error} onRetry={retry} />}
        {!loading && !error && !invalid && data?.count === 0 && (
          <p>Aucune observation pour cette période.</p>
        )}
        {data && data.count > 0 && !invalid && (
          <>
            <Chart rows={data.observations} />
            <p className="point-count">
              {data.count} points · du {data.period_start} au {data.period_end}
            </p>
            <DataTable rows={data.observations} />
          </>
        )}
      </section>
      <div className="panel">
        {episodesError ? (
          <ErrorState message={episodesError} />
        ) : (
          <EpisodeCompare episodes={episodes} />
        )}
      </div>
      <footer>
        <p>
          RONI et ONI sont deux indices distincts. Les épisodes décrivent des
          seuils historiques ; aucune prévision n’est fournie.
        </p>
        <p>
          Épisodes : seuil RONI ≥ +0,5 °C ou ≤ −0,5 °C pendant au moins 5
          saisons glissantes consécutives.
        </p>
      </footer>
    </main>
  );
}
