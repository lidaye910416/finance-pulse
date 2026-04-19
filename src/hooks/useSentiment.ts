import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';

export interface SentimentData {
  fear_greed_index: number;
  phase: string;
  limit_up_count: number;
  limit_down_count: number;
  volume: string;
  northbound_flow: string;
  margin_balance: string;
}

interface UseSentimentResult {
  data: SentimentData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useSentiment(): UseSentimentResult {
  const [data, setData] = useState<SentimentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<SentimentData>('load_sentiment_data');
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
