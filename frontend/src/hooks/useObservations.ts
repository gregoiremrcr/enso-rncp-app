import { useCallback, useEffect, useState } from "react";
import { getObservations } from "../api/client";
import type { ObservationResponse } from "../types";

export function useObservations(start: string, end: string, enabled = true) {
  const [data, setData] = useState<ObservationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reloadKey, setReloadKey] = useState(0);
  const retry = useCallback(() => setReloadKey((key) => key + 1), []);
  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      setError(null);
      return;
    }
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
  }, [start, end, enabled, reloadKey]);
  return { data, error, loading, retry };
}
