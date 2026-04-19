import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';

export interface MarketQuote {
  symbol: string;
  name: string;
  price: string;
  change: string;
  change_percent: number;
}

export interface ForexRate {
  [key: string]: number;
}

export interface MarketData {
  quotes: MarketQuote[];
  forex_rates: ForexRate;
  fear_greed_index: number;
}

interface UseMarketDataResult {
  data: MarketData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useMarketData(): UseMarketDataResult {
  const [data, setData] = useState<MarketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<MarketData>('load_market_data');
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
