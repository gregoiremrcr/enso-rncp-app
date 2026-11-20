import { useEffect, useState } from "react";
import { getSource } from "../api/client";
import type { SourceInfo } from "../types";

export function useSource() {
  const [source, setSource] = useState<SourceInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const controller = new AbortController();
    getSource(controller.signal)
      .then(setSource)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted)
          setError(
            reason instanceof Error ? reason.message : "Erreur inattendue.",
          );
      });
    return () => controller.abort();
  }, []);
  return { source, error };
}
