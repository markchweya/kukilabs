import { useCallback, useEffect, useRef, useState } from "react";

export interface Resource<T> {
  data: T | undefined;
  error: string | null;
  loading: boolean;
  reload: () => Promise<void>;
  setData: (value: T) => void;
}

/**
 * Load data on mount (and when `deps` change), with an optional polling
 * interval. Kept deliberately small instead of pulling in a data library:
 * Kuki talks to one local server with a handful of endpoints.
 *
 * Pass `pollMs` as a function to decide per-result whether to keep polling,
 * e.g. only while a document is still being processed.
 */
export function useResource<T>(
  load: () => Promise<T>,
  deps: unknown[],
  pollMs?: number | ((data: T | undefined) => number | null),
): Resource<T> {
  const [data, setData] = useState<T>();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const loadRef = useRef(load);
  loadRef.current = load;

  const reload = useCallback(async () => {
    try {
      setData(await loadRef.current());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    void reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    const interval = typeof pollMs === "function" ? pollMs(data) : pollMs;
    if (!interval) return;
    const timer = window.setTimeout(() => void reload(), interval);
    return () => window.clearTimeout(timer);
  }, [data, pollMs, reload]);

  return { data, error, loading, reload, setData };
}
