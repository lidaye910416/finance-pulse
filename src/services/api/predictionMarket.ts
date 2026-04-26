/**
 * 预测市场 API 服务
 */

import { API_BASE_URL } from './apiService';

// ========== 类型定义 ==========

export interface PolymarketEvent {
  id: string;
  question: string;
  probability: number;
  volume: string;
  trend?: 'up' | 'down';
  markets: string[];
}

export interface PolymarketResponse {
  items: PolymarketEvent[];
  updateTime: string;
}

export interface ArbitragePlatform {
  name: string;
  probability: number;
}

export interface ArbitrageOpportunity {
  event: string;
  platforms: ArbitragePlatform[];
  difference: number;
  suggestion: string;
}

export interface ArbitrageResponse {
  items: ArbitrageOpportunity[];
  updateTime: string;
}

// ========== Fallback 数据 ==========

const FALLBACK_POLYMARKET_EVENTS: PolymarketEvent[] = [
  { id: '1', question: 'Will Bitcoin exceed $100,000 by end of 2026?', probability: 65, volume: '$45M', trend: 'up', markets: [] },
  { id: '2', question: 'Will the Fed cut rates in June 2026?', probability: 58, volume: '$28M', trend: 'down', markets: [] },
  { id: '3', question: 'Will ETH flip BTC market cap by 2027?', probability: 35, volume: '$12M', trend: undefined, markets: [] },
  { id: '4', question: 'Will S&P 500 exceed 6000 by end of 2026?', probability: 62, volume: '$18M', trend: 'up', markets: [] },
];

const FALLBACK_ARBITRAGE: ArbitrageOpportunity[] = [
  {
    event: '美联储6月降息',
    platforms: [
      { name: 'Polymarket', probability: 68 },
      { name: 'Metaculus', probability: 71 },
      { name: 'Kalshi', probability: 65 },
    ],
    difference: 6,
    suggestion: '套利空间 6%，建议等待 >5% 差异时操作',
  },
  {
    event: 'BTC突破$100K在2026年内',
    platforms: [
      { name: 'Polymarket', probability: 55 },
      { name: 'Metaculus', probability: 60 },
      { name: 'Kalshi', probability: 52 },
    ],
    difference: 8,
    suggestion: '套利空间 8%，可考虑小仓布局',
  },
  {
    event: '标普500突破6000点',
    platforms: [
      { name: 'Polymarket', probability: 62 },
      { name: 'Metaculus', probability: 58 },
      { name: 'Kalshi', probability: 65 },
    ],
    difference: 7,
    suggestion: '套利空间 7%，市场共识偏向突破',
  },
  {
    event: '黄金突破$3000/盎司',
    platforms: [
      { name: 'Polymarket', probability: 48 },
      { name: 'Metaculus', probability: 55 },
      { name: 'Kalshi', probability: 50 },
    ],
    difference: 7,
    suggestion: '套利空间 7%，分歧较大需谨慎',
  },
];

// ========== API 函数 ==========

/**
 * 获取 Polymarket 热门事件
 */
export async function fetchPolymarketEvents(limit: number = 10): Promise<PolymarketEvent[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/polymarket?limit=${limit}`, {
      method: 'GET',
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      throw new Error(`获取失败: ${response.status}`);
    }

    const data: PolymarketResponse = await response.json();
    return data.items;
  } catch (error) {
    console.warn('获取Polymarket事件失败，使用fallback数据:', error);
    return FALLBACK_POLYMARKET_EVENTS;
  }
}

/**
 * 获取跨平台套利机会
 */
export async function fetchArbitrageOpportunities(): Promise<ArbitrageOpportunity[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/arbitrage`, {
      method: 'GET',
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      throw new Error(`获取失败: ${response.status}`);
    }

    const data: ArbitrageResponse = await response.json();
    return data.items;
  } catch (error) {
    console.warn('获取套利机会失败，使用fallback数据:', error);
    return FALLBACK_ARBITRAGE;
  }
}
