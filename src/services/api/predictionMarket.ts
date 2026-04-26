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

// ========== API 函数 ==========

/**
 * 获取 Polymarket 热门事件（API失败返回空数组）
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
    console.error('获取Polymarket事件失败:', error);
    return [];
  }
}

/**
 * 获取跨平台套利机会（API失败返回空数组）
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
    console.error('获取套利机会失败:', error);
    return [];
  }
}
