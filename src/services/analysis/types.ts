/**
 * AI 分析系统 - 类型定义
 * 
 * 参考 AI Hedge Fund 和 ValueCell 架构
 */

// ========== Agent 分类 ==========

export enum AgentCategory {
  /** 投资大师 */
  INVESTMENT_MASTER = 'investment_master',
  /** 行业专家 */
  INDUSTRY_EXPERT = 'industry_expert',
  /** 量化分析师 */
  QUANT_ANALYST = 'quant_analyst',
  /** 风控专家 */
  RISK_MANAGER = 'risk_manager',
  /** 辩论专家 */
  DEBATE_EXPERT = 'debate_expert',
}

// ========== Agent 类型 ==========

export enum AgentType {
  // 投资大师类型
  VALUE_INVESTOR = 'value_investor',
  GROWTH_INVESTOR = 'growth_investor',
  CONTRARIAN = 'contrarian',
  SECURITY_ANALYST = 'security_analyst',
  MULTI_DISCIPLINARY = 'multi_disciplinary',
  RISK_ANALYST = 'risk_analyst',
  
  // 行业专家类型
  ACTIVIST = 'activist',
  MACRO_INVESTOR = 'macro_investor',
  VALUATION_EXPERT = 'valuation_expert',
  
  // 量化分析师类型
  VALUATION = 'valuation',
  TECHNICAL = 'technical',
  SENTIMENT = 'sentiment',
  FUNDAMENTAL = 'fundamental',
  
  // 风控专家类型
  RISK_MANAGER = 'risk_manager',
  PORTFOLIO_MANAGER = 'portfolio_manager',
  
  // 辩论专家类型
  BULLISH_RESEARCHER = 'bullish_researcher',
  BEARISH_RESEARCHER = 'bearish_researcher',
  
  // 通用类型
  GENERALIST = 'generalist',
}

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
  agentId: string;          // Agent ID
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

export type LLMProvider = 'minimax' | 'openai' | 'anthropic' | 'deepseek' | 'mock';

export interface LLMConfig {
  provider: LLMProvider;
  apiKey: string;
  model: string;
  baseUrl?: string;        // 支持代理
}

export interface LLMMessage {
  role: 'system' | 'user' | 'assistant';
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

// ========== 分析师选择器配置 ==========

export interface AnalystSelectorOption {
  id: string;
  name: string;
  nameCn: string;
  category: AgentCategory;
  style: string;
  avatar: string;
  description: string;
}
