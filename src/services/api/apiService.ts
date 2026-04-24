/**
 * API 服务 - 调用后端 LangGraph 服务
 */

import { useSettingsStore } from '../../stores/settingsStore';

// ========== API 配置 ==========

const API_BASE_URL = 'http://localhost:5000';

// ========== API 响应类型 ==========

export interface ApiSignal {
  agent: string;
  agent_id: string;
  signal: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  reasoning: string;
}

export interface ApiRecommendation {
  action: 'buy' | 'hold' | 'sell' | 'watch';
  confidence: number;
  entry_price?: number;
  exit_price?: number;
  stop_loss?: number;
  position_size?: number;
  timeframe: string;
  risks: string[];
}

export interface ApiAnalysisResponse {
  code: string;
  name: string;
  timestamp: number;
  duration_ms: number;
  iterations: number;
  signals: ApiSignal[];
  debate_result: {
    round: number;
    bullish: ApiSignal;
    bearish: ApiSignal;
    consensus_reached: boolean;
    final_confidence: number;
  } | null;
  summary: string;
  model: string;
  total_tokens: number;
  recommendation: ApiRecommendation;
  error: string | null;
}

export interface ApiQuoteResponse {
  code: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  prev_close: number;
  pe?: number;
  pb?: number;
  market_cap?: string;
}

// ========== API 服务 ==========

class APIService {
  private baseUrl = API_BASE_URL;
  private timeout = 120000; // 120秒超时

  /**
   * 检查后端服务是否可用
   */
  async checkHealth(): Promise<{ status: string; llm_configured: boolean; llm_provider: string } | null> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  }

  /**
   * 分析股票
   */
  async analyzeStock(
    code: string,
    name?: string,
    maxIterations: number = 3
  ): Promise<ApiAnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        name: name || `股票${code}`,
        include_history: false,
        max_iterations: maxIterations,
      }),
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`分析失败: ${response.status} - ${error}`);
    }

    return await response.json();
  }

  /**
   * 获取股票行情
   */
  async getQuote(code: string): Promise<ApiQuoteResponse> {
    const response = await fetch(`${this.baseUrl}/quote/${code}`, {
      method: 'GET',
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      throw new Error(`获取行情失败: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * 测试 LLM 连接
   */
  async testLLM(): Promise<{ success: boolean; content: string; model: string; tokens: number }> {
    const response = await fetch(`${this.baseUrl}/llm/test`, {
      method: 'GET',
      signal: AbortSignal.timeout(30000),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`LLM 测试失败: ${error}`);
    }

    return await response.json();
  }

  /**
   * 检查服务状态
   */
  isServiceAvailable(): boolean {
    // 可以添加检查逻辑
    return true;
  }
}

// ========== 单例导出 ==========

export const apiService = new APIService();
export default apiService;
