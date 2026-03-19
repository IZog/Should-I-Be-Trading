import { useState, useEffect, useCallback, useRef } from 'react';

export function useMarketData(mode = 'swing', interval = 45000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const abortRef = useRef(null);

  const fetchData = useCallback(async (isManual = false) => {
    if (isManual) setIsRefreshing(true);

    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`/api/scores?mode=${mode}`, {
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setLastUpdated(new Date().toISOString());
      setError(null);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [mode]);

  useEffect(() => {
    fetchData();
    const timer = setInterval(() => fetchData(), interval);
    return () => {
      clearInterval(timer);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [fetchData, interval]);

  const refresh = useCallback(() => fetchData(true), [fetchData]);

  return { data, loading, error, lastUpdated, isRefreshing, refresh };
}
