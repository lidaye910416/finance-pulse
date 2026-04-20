/**
 * FinancePulse 数据类型定义
 * 
 * 统一管理所有数据类型，确保类型安全
 */

// ========== 市场数据 ==========

export interface Quote {
  code: string;           // 股票代码
  name: string;           // 股票名称
  price: number;          // 当前价格
  change: number;         // 涨跌额
  changePercent: number;  // 涨跌幅%
  volume: number;         // 成交量
  amount: number;        // 成交额
  high: number;          // 最高价
  low: number;           // 最低价
  open: number;          // 开盘价
  prevClose: number;     // 昨收
  timestamp: number;      // 更新时间戳
}

export interface KLine {
  time: number;           // 时间戳
  open: number;          // 开盘价
  high: number;          // 最高价
  low: number;           // 最低价
  close: number;         // 收盘价
  volume: number;        // 成交量
}

export interface NorthboundData {
  date: string;           // 日期
  hkStock: number;       // 沪股通净买入(亿)
  szStock: number;       // 深股通净买入(亿)
  total: number;          // 合计净买入(亿)
}

// ========== 宏观数据 ==========

export interface MacroIndicator {
  type: string;          // 指标类型: gdp, cpi, ppi, pmi, lpr, m2
  date: string;          // 日期
  value: number;         // 当前值
  yoy: number;           // 同比%
  mom?: number;          // 环比% (可选)
  unit: string;          // 单位
  source: string;        // 数据来源
  releaseTime: string;   // 发布时间
}

// ========== 情绪数据 ==========

export interface FearGreedIndex {
  value: number;         // 指数值 0-100
  phase: FearGreedPhase; // 阶段
  updateTime: string;    // 更新时间
}

export enum FearGreedPhase {
  EXTREME_FEAR = '极度恐惧',
  FEAR = '恐惧',
  NEUTRAL = '中性',
  GREED = '贪婪',
  EXTREME_GREED = '极度贪婪',
}

export interface SentimentSignal {
  label: string;         // 指标名称
  value: string | number; // 当前值
  status: string;       // 状态描述
  trend: 'up' | 'down' | 'neutral'; // 趋势
  variant: 'green' | 'yellow' | 'red' | 'blue' | 'gray'; // 样式变体
}

// ========== 资讯数据 ==========

export interface NewsItem {
  id: string;            // 唯一ID
  title: string;         // 标题
  content: string;       // 内容摘要
  source: string;        // 来源
  time: number;          // 发布时间戳
  tags: string[];        // 标签
  sentiment: 'positive' | 'negative' | 'neutral'; // 情感倾向
  relatedStocks: string[]; // 相关股票代码
}

export interface ResearchReport {
  id: string;
  title: string;
  institution: string;    // 券商名称
  analyst: string;        // 分析师
  stockCode: string;      // 股票代码
  stockName: string;      // 股票名称
  rating: ReportRating;    // 评级
  targetPrice?: number;   // 目标价
  publishDate: string;     // 发布日期
  summary: string;         // 摘要
}

export enum ReportRating {
  BUY = '买入',
  OUTPERFORM = '优于大市',
  NEUTRAL = '中性',
  UNDERPERFORM = '弱于大市',
  SELL = '卖出',
}

// ========== 用户数据 ==========

export interface WatchlistItem {
  code: string;           // 股票代码
  name: string;           // 股票名称
  addTime: number;        // 添加时间戳
  notes?: string;         // 备注
  targetPrice?: number;   // 目标价
  stopLoss?: number;      // 止损价
}

export interface Position {
  code: string;           // 股票代码
  name: string;           // 股票名称
  volume: number;         // 持仓数量
  cost: number;           // 成本价
  currentPrice: number;   // 当前价
  marketValue: number;    // 市值
  profit: number;         // 盈亏金额
  profitPercent: number;  // 盈亏比例
}

// ========== 分析数据 ==========

export interface AnalysisRequest {
  targetCode: string;     // 目标代码（股票/基金）
  analystId: string;      // 分析师ID
  includeHistorical: boolean; // 是否包含历史分析
}

export interface AnalysisResult {
  request: AnalysisRequest;
  signals: AnalysisSignal[];
  valuation?: ValuationData;
  risks: RiskAssessment;
  strategy: StrategySuggestion;
  generatedAt: number;     // 生成时间
  model?: string;         // 使用的AI模型
}

export interface AnalysisSignal {
  analyst: string;        // 分析师
  signal: 'bullish' | 'bearish' | 'neutral';
  confidence: number;     // 置信度 0-100
  reasoning: string;      // 分析理由
  keyFactors: string[];   // 关键因素
}

export interface ValuationData {
  currentPrice: number;
  intrinsicValue: number;
  marginOfSafety: number;
  peRatio: number;
  pbRatio: number;
  targetPrice: number;
}

export interface RiskAssessment {
  level: 'low' | 'medium' | 'high';
  factors: string[];
  maxDrawdown: number;
}

export interface StrategySuggestion {
  action: 'buy' | 'hold' | 'sell' | 'watch';
  entryPrice?: number;
  exitPrice?: number;
  stopLoss?: number;
  positionSize: number;
  timeframe: string;
}
