import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';

export interface MacroData {
  gdp: number;
  cpi: number;
  pmi: number;
  lpr: number;
}

interface UseMacroDataResult {
  data: MacroData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useMacroData(): UseMacroDataResult {
  const [data, setData] = useState<MacroData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<MacroData>('load_macro_data');
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
