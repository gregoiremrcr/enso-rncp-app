import { useCallback, useEffect, useState } from "react";
import { getEpisodes, getObservations, getSource } from "./api/client";
import type { Episode, ObservationResponse, SourceInfo } from "./types";

export function useObservations(start: string, end: string) {
  const [data, setData] = useState<ObservationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);
  const retry = useCallback(() => setReloadKey((key) => key + 1), []);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    getObservations(start, end, controller.signal)
      .then(setData)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted)
          setError(
            reason instanceof Error ? reason.message : "Erreur inattendue.",
          );
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [start, end, reloadKey]);
  return { data, error, loading, retry };
}

export function useMetadata() {
  const [source, setSource] = useState<SourceInfo | null>(null);
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([getSource(controller.signal), getEpisodes(controller.signal)])
      .then(([info, found]) => {
        setSource(info);
        setEpisodes(found);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted)
          setError(
            reason instanceof Error ? reason.message : "Erreur inattendue.",
          );
      });
    return () => controller.abort();
  }, []);
  return { source, episodes, error };
}
