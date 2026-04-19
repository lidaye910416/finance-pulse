// Market data types
export interface MarketQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

// Sentiment data types
export interface SentimentData {
  fearGreedIndex: number;
  phase: 'ice' | 'recovery' | 'divergence' | 'euphoria';
  signals: {
    limitUpCount: number;
    limitDownCount: number;
    volume: number;
    northboundFlow: number;
  };
}

// Macro data types
export interface MacroData {
  gdp: number;
  cpi: number;
  pmi: number;
  lpr: number;
  exchangeRates: Record<string, number>;
  moneySupply: {
    m0: number;
    m1: number;
    m2: number;
  };
}

// News types
export interface NewsItem {
  id: string;
  category: 'us-stock' | 'a-stock' | 'commodity' | 'crypto' | 'tech';
  title: string;
  summary: string;
  source: string;
  time: string;
  impact?: 'positive' | 'negative' | 'neutral';
}

// Prediction market types
export interface PredictionEvent {
  id: string;
  question: string;
  probability: number;
  volume: number;
  platform: string;
}

// Position management types
export interface PositionRecommendation {
  currentRange: string;
  percentage: number;
  phase: string;
  rules: string[];
}
