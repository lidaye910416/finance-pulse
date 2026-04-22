/**
 * AI 分析编排器 - Orchestrator
 * 
 * 参考 TradingAgents 的多智能体工作流
 * 参考 ai-hedge-fund 的分析师协作体系
 * 
 * 工作流程:
 * 1. 数据收集阶段 - 并行获取各维度数据
 * 2. Agent 分析阶段 - 各分析师独立分析
 * 3. 辩论阶段 (可选) - 多空双方辩论
 * 4. 综合阶段 - 汇总各 Agent 意见
 * 5. 风险评估 - 风控 Agent 出具风险报告
 * 6. 最终决策 - Portfolio Manager 给出最终建议
 */

import {
  AnalysisRequest,
  AnalysisResponse,
  AgentSignal,
  StockData,
  SignalType,
  WorkflowState,
} from './types';
import {
  getAgentConfig,
  ANALYST_TEMPLATES,
} from './agentConfig';

// ========== 数据收集阶段 ==========

/**
 * 获取股票实时数据
 */
async function fetchStockData(code: string): Promise<StockData> {
  // 实际应用中应该调用真实 API
  // 这里使用模拟数据
  const mockData: Record<string, StockData> = {
    '600519': {
      code: '600519',
      name: '贵州茅台',
      price: 1688.0,
      change: -20.16,
      changePercent: -1.18,
      volume: 2356789,
      amount: 3978567890,
      high: 1712.0,
      low: 1675.0,
      open: 1710.0,
      prevClose: 1708.16,
      pe: 28.5,
      pb: 11.2,
      marketCap: '2.12万亿',
      timestamp: Date.now(),
    },
    '000858': {
      code: '000858',
      name: '五粮液',
      price: 145.6,
      change: -1.31,
      changePercent: -0.89,
      volume: 5678901,
      amount: 826789012,
      high: 147.5,
      low: 144.2,
      open: 147.0,
      prevClose: 146.91,
      pe: 22.3,
      pb: 5.8,
      marketCap: '5658亿',
      timestamp: Date.now(),
    },
    '300750': {
      code: '300750',
      name: '宁德时代',
      price: 186.5,
      change: 4.2,
      changePercent: 2.31,
      volume: 12345678,
      amount: 2289012345,
      high: 188.0,
      low: 182.3,
      open: 183.0,
      prevClose: 182.3,
      pe: 35.2,
      pb: 8.5,
      marketCap: '8215亿',
      timestamp: Date.now(),
    },
  };

  return mockData[code] || {
    code,
    name: `股票 ${code}`,
    price: Math.random() * 100 + 10,
    change: (Math.random() - 0.5) * 10,
    changePercent: (Math.random() - 0.5) * 5,
    volume: Math.floor(Math.random() * 10000000),
    amount: Math.floor(Math.random() * 1000000000),
    high: Math.random() * 100 + 100,
    low: Math.random() * 50 + 50,
    open: Math.random() * 80 + 60,
    prevClose: Math.random() * 80 + 60,
    timestamp: Date.now(),
  };
}

// ========== Agent 分析阶段 ==========

/**
 * 执行单个 Agent 的分析
 */
async function executeAgent(
  agentId: string,
  stockData: StockData
): Promise<AgentSignal> {
  const agentConfig = getAgentConfig(agentId);
  if (!agentConfig) {
    return {
      agent: agentId,
      agentId,
      signal: 'neutral',
      confidence: 0,
      reasoning: '未找到该分析师',
      data: {},
    };
  }

  // 模拟 Agent 分析过程
  // 实际应用中应该调用 LLM API
  await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200));

  // 根据分析师风格生成模拟信号
  let signal: SignalType = 'neutral';
  let confidence = Math.floor(Math.random() * 30) + 40; // 40-70%
  let reasoning = '';

  // 技术面分析
  if (stockData.changePercent > 2) {
    signal = 'bullish';
    confidence = Math.min(90, confidence + 15);
    reasoning = `近期上涨${stockData.changePercent.toFixed(2)}%，趋势向好`;
  } else if (stockData.changePercent < -2) {
    signal = 'bearish';
    confidence = Math.min(85, confidence + 10);
    reasoning = `近期下跌${Math.abs(stockData.changePercent).toFixed(2)}%，需谨慎`;
  }

  // PE 估值分析
  if (stockData.pe && stockData.pe < 20) {
    reasoning += `\n市盈率${stockData.pe}，估值偏低`;
  } else if (stockData.pe && stockData.pe > 40) {
    signal = stockData.changePercent > 0 ? 'neutral' : 'bearish';
    reasoning += `\n市盈率${stockData.pe}，估值偏高`;
  }

  // 根据分析师特性调整
  if (agentConfig.category === 'investment_master') {
    reasoning += `\n从${agentConfig.nameCn}的${agentConfig.style}角度来看，`;
    reasoning += stockData.pe && stockData.pe < 25 
      ? '当前估值具有安全边际，适合长期持有' 
      : '需要等待更好的买入时机';
  } else if (agentConfig.type === 'technical') {
    reasoning += `\n技术面显示`;
    reasoning += stockData.changePercent > 0 ? '短期动能较强' : '短期动能较弱';
  }

  return {
    agent: agentConfig.nameCn,
    agentId,
    signal,
    confidence,
    reasoning,
    data: {
      price: stockData.price,
      change: stockData.changePercent,
      pe: stockData.pe,
      pb: stockData.pb,
    },
  };
}

// ========== 辩论阶段 ==========

/**
 * 执行多空辩论
 */
async function executeDebate(
  signals: AgentSignal[],
  stockData: StockData
): Promise<{bullish: AgentSignal; bearish: AgentSignal}> {
  // 模拟辩论过程
  await new Promise(resolve => setTimeout(resolve, 500));

  const bullishSignal = signals.find(s => s.signal === 'bullish');
  const bearishSignal = signals.find(s => s.signal === 'bearish');

  return {
    bullish: {
      agent: '多头研究员',
      agentId: 'bullish_researcher',
      signal: 'bullish',
      confidence: bullishSignal 
        ? Math.min(90, bullishSignal.confidence + 10)
        : 55,
      reasoning: bullishSignal 
        ? `看多理由：${bullishSignal.reasoning}`
        : `基于当前价格${stockData.price}元，建议关注买入机会`,
      data: { type: 'bullish' },
    },
    bearish: {
      agent: '空头研究员',
      agentId: 'bearish_researcher',
      signal: 'bearish',
      confidence: bearishSignal 
        ? Math.min(85, bearishSignal.confidence + 10)
        : 50,
      reasoning: bearishSignal 
        ? `看空理由：${bearishSignal.reasoning}`
        : `需警惕回调风险，建议观望`,
      data: { type: 'bearish' },
    },
  };
}

// ========== 风险评估 ==========

/**
 * 执行风险评估
 */
async function executeRiskAssessment(
  signals: AgentSignal[],
  stockData: StockData
): Promise<{riskScore: number; maxLoss: number; positionLimit: number; risks: string[]}> {
  // 统计信号分布
  const bullishCount = signals.filter(s => s.signal === 'bullish').length;
  const bearishCount = signals.filter(s => s.signal === 'bearish').length;
  const neutralCount = signals.filter(s => s.signal === 'neutral').length;
  
  // 计算风险评分
  let riskScore = 50 + (bearishCount - bullishCount) * 10;
  riskScore = Math.max(20, Math.min(80, riskScore));
  
  // 波动性风险
  const volatility = Math.abs(stockData.changePercent);
  if (volatility > 5) riskScore += 10;
  else if (volatility > 3) riskScore += 5;
  
  // 估值风险
  if (stockData.pe && stockData.pe > 50) riskScore += 15;
  else if (stockData.pe && stockData.pe < 15) riskScore -= 10;
  
  // 最大亏损估算
  const maxLoss = Math.min(50, riskScore * 0.8);
  
  // 仓位建议
  let positionLimit = 50 - riskScore / 2;
  if (bullishCount > bearishCount) positionLimit += 10;
  if (bearishCount > bullishCount) positionLimit -= 15;
  positionLimit = Math.max(10, Math.min(80, positionLimit));
  
  // 风险因素
  const risks: string[] = [];
  if (volatility > 3) risks.push('价格波动较大');
  if (stockData.pe && stockData.pe > 40) risks.push('估值偏高');
  if (bearishCount > bullishCount) risks.push('看空信号较多');
  if (neutralCount > bullishCount + bearishCount) risks.push('市场分歧较大');
  
  return { riskScore, maxLoss, positionLimit, risks };
}

// ========== 综合分析与决策 ==========

/**
 * 生成最终分析报告
 */
async function generateSummary(
  signals: AgentSignal[],
  stockData: StockData,
  debate: {bullish: AgentSignal; bearish: AgentSignal},
  riskAssessment: {riskScore: number; maxLoss: number; positionLimit: number; risks: string[]}
): Promise<AnalysisResponse['summary'] & { recommendation: AnalysisResponse['recommendation'] }> {
  // 统计信号
  const bullishSignals = signals.filter(s => s.signal === 'bullish');
  const bearishSignals = signals.filter(s => s.signal === 'bearish');
  const avgConfidence = signals.reduce((sum, s) => sum + s.confidence, 0) / signals.length;
  
  // 决定操作
  let action: 'buy' | 'hold' | 'sell' | 'watch' = 'hold';
  let confidence = Math.round(avgConfidence);
  
  if (bullishSignals.length > bearishSignals.length * 1.5 && riskAssessment.riskScore < 60) {
    action = 'buy';
    confidence = Math.min(95, confidence + 10);
  } else if (bearishSignals.length > bullishSignals.length * 1.5 || riskAssessment.riskScore > 70) {
    action = 'sell';
    confidence = Math.min(90, confidence + 5);
  } else if (bullishSignals.length > bearishSignals.length) {
    action = 'hold';
  } else if (riskAssessment.riskScore > 65) {
    action = 'watch';
    confidence = Math.max(40, confidence - 15);
  }
  
  // 生成分析文本
  const text = `
综合 ${signals.length} 位分析师的观点:

**市场共识:**
- ${bullishSignals.length} 位看多，${bearishSignals.length} 位看空
- 平均置信度: ${avgConfidence.toFixed(1)}%

**核心观点:**
${signals.slice(0, 3).map(s => `- ${s.agent}: ${s.signal === 'bullish' ? '看好' : s.signal === 'bearish' ? '看空' : '中性'} (${s.confidence}%置信)`).join('\n')}

**多空辩论:**
- 多头: ${debate.bullish.reasoning.slice(0, 50)}...
- 空头: ${debate.bearish.reasoning.slice(0, 50)}...

**风险评估:**
- 风险评分: ${riskAssessment.riskScore}/100
- 预计最大亏损: ${riskAssessment.maxLoss.toFixed(1)}%
- 建议仓位: ${riskAssessment.positionLimit.toFixed(0)}%
  `.trim();
  
  return {
    text,
    model: 'mock-v1.0',
    tokens: Math.floor(text.length / 4),
    recommendation: {
      action,
      confidence,
      entryPrice: action === 'buy' ? stockData.price * 0.98 : undefined,
      exitPrice: stockData.price * (action === 'buy' ? 1.15 : 0.85),
      stopLoss: stockData.price * 0.95,
      positionSize: riskAssessment.positionLimit,
      timeframe: '1-3个月',
      risks: riskAssessment.risks,
    },
  };
}

// ========== 主编排器 ==========

/**
 * 执行完整的分析工作流
 */
export async function executeAnalysis(
  request: AnalysisRequest,
  onProgress?: (state: WorkflowState) => void
): Promise<AnalysisResponse> {
  const startTime = Date.now();
  
  const updateProgress = (state: Omit<WorkflowState, 'agentsCompleted'> & { agentsCompleted?: string[] }) => {
    onProgress?.({
      ...state,
      agentsCompleted: state.agentsCompleted || [],
    });
  };
  
  try {
    // ===== 阶段 1: 数据收集 =====
    updateProgress({ status: 'running', progress: 5, currentStep: '获取股票数据' });
    const stockData = await fetchStockData(request.code);
    
    // ===== 阶段 2: Agent 分析 =====
    updateProgress({ status: 'running', progress: 20, currentStep: '分析师正在分析...' });
    
    const signals: AgentSignal[] = [];
    const agentIds = request.analystIds.length > 0 
      ? request.analystIds 
      : ['warren_buffett', 'technicals_agent', 'sentiment_agent', 'risk_manager'];
    
    // 并行执行非风控 Agent
    const agentPromises = agentIds
      .filter(id => !id.includes('risk_manager') && !id.includes('portfolio'))
      .map(async (agentId, index) => {
        const signal = await executeAgent(agentId, stockData);
        updateProgress({ 
          status: 'running', 
          progress: 20 + Math.floor((index + 1) / agentIds.length * 40),
          currentStep: `${getAgentConfig(agentId)?.nameCn || agentId} 正在分析...`,
          agentsCompleted: signals.map(s => s.agentId),
        });
        return signal;
      });
    
    const agentResults = await Promise.all(agentPromises);
    signals.push(...agentResults);
    
    // ===== 阶段 3: 辩论 =====
    updateProgress({ status: 'running', progress: 60, currentStep: '多空辩论中...' });
    const debate = await executeDebate(signals, stockData);
    signals.push(debate.bullish, debate.bearish);
    
    // ===== 阶段 4: 风险评估 =====
    updateProgress({ status: 'running', progress: 75, currentStep: '风险评估中...' });
    const riskAssessment = await executeRiskAssessment(signals, stockData);
    
    // 添加风控 Agent 信号
    signals.push({
      agent: '风险管理师',
      agentId: 'risk_manager',
      signal: riskAssessment.riskScore > 60 ? 'bearish' : riskAssessment.riskScore < 40 ? 'bullish' : 'neutral',
      confidence: 100 - riskAssessment.riskScore,
      reasoning: `风险评分: ${riskAssessment.riskScore}/100，建议仓位: ${riskAssessment.positionLimit.toFixed(0)}%`,
      data: riskAssessment,
    });
    
    // ===== 阶段 5: 综合分析 =====
    updateProgress({ status: 'running', progress: 90, currentStep: '生成分析报告...' });
    const summaryResult = await generateSummary(signals, stockData, debate, riskAssessment);
    
    // ===== 完成 =====
    updateProgress({ status: 'completed', progress: 100, currentStep: '分析完成' });
    
    return {
      code: request.code,
      timestamp: Date.now(),
      duration: Date.now() - startTime,
      signals,
      summary: {
        text: summaryResult.text,
        model: summaryResult.model,
        tokens: summaryResult.tokens,
      },
      recommendation: summaryResult.recommendation,
    };
    
  } catch (error) {
    updateProgress({ 
      status: 'error', 
      progress: 0, 
      currentStep: '分析失败',
      error: error instanceof Error ? error.message : String(error),
    });
    
    return {
      code: request.code,
      timestamp: Date.now(),
      duration: Date.now() - startTime,
      signals: [],
      summary: { text: '', model: '', tokens: 0 },
      recommendation: {
        action: 'watch',
        confidence: 0,
        timeframe: '未知',
        risks: [error instanceof Error ? error.message : '未知错误'],
      },
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

// ========== 导出快捷函数 ==========

export { fetchStockData };

// 导出分析师模板
export { ANALYST_TEMPLATES };
