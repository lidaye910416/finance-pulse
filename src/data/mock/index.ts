import marketData from './marketData.json';
import sentimentData from './sentimentData.json';
import macroData from './macroData.json';
import newsData from './newsData.json';
import predictionMarketData from './predictionMarketData.json';

export const mockData = {
  marketData,
  sentimentData,
  macroData,
  newsData,
  predictionMarketData,
};

export type MockData = typeof mockData;
