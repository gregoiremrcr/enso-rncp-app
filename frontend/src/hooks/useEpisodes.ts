import { useEffect, useState } from "react";
import { getEpisodes } from "../api/client";
import type { Episode } from "../types";

export function useEpisodes() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    getEpisodes(controller.signal)
      .then(setEpisodes)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted)
          setError(
            reason instanceof Error ? reason.message : "Erreur inattendue.",
          );
      });
    return () => controller.abort();
  }, []);
  return { episodes, error };
}
