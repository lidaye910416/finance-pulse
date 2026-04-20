/**
 * AI 分析系统 - 类型定义
 * 
 * 参考 AI Hedge Fund 和 ValueCell 架构
 */

// ========== 基础类型 ==========

export interface StockData {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  prevClose: number;
  pe?: number;
  pb?: number;
  marketCap?: string;
  timestamp: number;
}

// ========== Agent 信号 ==========

export type SignalType = 'bullish' | 'bearish' | 'neutral';

export interface AgentSignal {
  agent: string;           // Agent 名称
  signal: SignalType;      // 信号类型
  confidence: number;      // 置信度 0-100
  reasoning: string;       // 分析理由
  data: Record<string, unknown>; // 原始数据
}

// ========== 分析请求/响应 ==========

export interface AnalysisRequest {
  code: string;           // 股票/基金代码
  analystIds: string[];    // 分析师ID列表
  includeHistory: boolean; // 包含历史分析
}

export interface AnalysisResponse {
  code: string;
  timestamp: number;
  duration: number;        // 分析耗时(ms)
  
  // 各 Agent 信号
  signals: AgentSignal[];
  
  // LLM 综合分析
  summary: {
    text: string;         // 分析文本
    model: string;        // 使用的模型
    tokens: number;       // 消耗的 token 数
  };
  
  // 投资建议
  recommendation: {
    action: 'buy' | 'hold' | 'sell' | 'watch';
    confidence: number;   // 置信度 0-100
    entryPrice?: number;   // 建议买入价
    exitPrice?: number;    // 目标价
    stopLoss?: number;     // 止损价
    positionSize?: number; // 建议仓位
    timeframe: string;    // 投资周期
    risks: string[];      // 风险提示
  };
  
  // 错误信息
  error?: string;
}

// ========== Agent 接口 ==========

export interface BaseAgent {
  /** Agent 唯一标识 */
  id: string;
  /** Agent 名称 */
  name: string;
  /** 执行分析 */
  analyze(code: string): Promise<AgentSignal>;
}

// ========== LLM 配置 ==========

export type LLMProvider = 'openai' | 'anthropic' | 'deepseek';

export interface LLMConfig {
  provider: LLMProvider;
  apiKey: string;
  model: string;
  baseUrl?: string;        // 支持代理
}

export interface LLMMessage {
  role: string;
  content: string;
}

export interface LLMResponse {
  content: string;
  model: string;
  tokens: number;
  finishReason: 'stop' | 'length' | 'content_filter';
}

// ========== 工作流状态 ==========

export interface WorkflowState {
  status: 'idle' | 'running' | 'completed' | 'error';
  progress: number;        // 0-100
  currentStep: string;    // 当前步骤
  agentsCompleted: string[]; // 已完成的 Agent
  error?: string;
}

// ========== 缓存类型 ==========

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;             // 过期时间(ms)
}

export interface AnalysisCache {
  stockData: Map<string, CacheEntry<StockData>>;
  agentSignals: Map<string, CacheEntry<AgentSignal[]>>;
  analysisResults: Map<string, CacheEntry<AnalysisResponse>>;
}
