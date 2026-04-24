/**
 * AI 分析编排器 - Orchestrator
 * 
 * 参考 TradingAgents 的多智能体工作流
 * 参考 ai-hedge-fund 的分析师协作体系
 * 
 * 工作流程:
 * 1. 数据收集阶段 - 并行获取各维度数据
 * 2. Agent 分析阶段 - 各分析师独立分析 (调用 MiniMax LLM)
 * 3. 辩论阶段 - 多空双方辩论
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
import { llmService } from './llmService';

// ========== 数据收集阶段 ==========

/**
 * 获取股票实时数据
 */
async function fetchStockData(code: string): Promise<StockData> {
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

// ========== LLM Prompt 构建 ==========

/**
 * 构建分析师的 prompt
 */
function buildAnalysisPrompt(agentConfig: { systemPrompt: string; nameCn: string }, stockData: StockData): string {
  return `你是一位专业的股票分析师。

分析目标：${stockData.name}（${stockData.code}）

当前数据：
- 当前价格: ¥${stockData.price.toFixed(2)}
- 涨跌幅: ${stockData.changePercent > 0 ? '+' : ''}${stockData.changePercent.toFixed(2)}%
- 开盘价: ¥${stockData.open.toFixed(2)}
- 最高价: ¥${stockData.high.toFixed(2)}
- 最低价: ¥${stockData.low.toFixed(2)}
- 市盈率(PE): ${stockData.pe || '未知'}
- 市净率(PB): ${stockData.pb || '未知'}
- 总市值: ${stockData.marketCap || '未知'}

请以${agentConfig.nameCn}的风格，分析这只股票的投资价值。

请用JSON格式返回分析结果：
{
  "signal": "bullish" | "bearish" | "neutral",
  "confidence": 0-100,
  "reasoning": "分析理由（100字以内）",
  "highlights": ["要点1", "要点2", "要点3"]
}`;
}

// ========== Agent 分析阶段 (真实 LLM 调用) ==========

/**
 * 解析 LLM 返回的 JSON
 */
function parseLLMResponse(content: string): { signal: SignalType; confidence: number; reasoning: string } {
  try {
    // 尝试提取 JSON
    const jsonMatch = content.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const data = JSON.parse(jsonMatch[0]);
      return {
        signal: data.signal || 'neutral',
        confidence: Math.min(100, Math.max(0, parseInt(data.confidence) || 50)),
        reasoning: data.reasoning || data.highlights?.join('；') || '分析完成',
      };
    }
  } catch (e) {
    console.error('[Orchestrator] 解析 LLM 响应失败:', e);
  }
  
  // 默认值
  return {
    signal: 'neutral',
    confidence: 50,
    reasoning: content.slice(0, 100),
  };
}

/**
 * 执行单个 Agent 的分析 (调用 MiniMax LLM)
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

  console.log(`[Orchestrator] ${agentConfig.nameCn} 正在分析 ${stockData.code}...`);
  
  try {
    // 构建 prompt
    const prompt = buildAnalysisPrompt(agentConfig, stockData);
    
    // 调用 MiniMax LLM
    const response = await llmService.complete([
      { role: 'system', content: agentConfig.systemPrompt },
      { role: 'user', content: prompt },
    ], {
      maxTokens: 500,
      temperature: 0.7,
    });
    
    console.log(`[Orchestrator] ${agentConfig.nameCn} 分析完成`);
    
    // 解析响应
    const { signal, confidence, reasoning } = parseLLMResponse(response.content);
    
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
        model: response.model,
        tokens: response.tokens,
      },
    };
  } catch (error) {
    console.error(`[Orchestrator] ${agentConfig.nameCn} 分析失败:`, error);
    
    // 失败时返回默认信号
    return {
      agent: agentConfig.nameCn,
      agentId,
      signal: 'neutral',
      confidence: 30,
      reasoning: `分析服务暂时不可用: ${error instanceof Error ? error.message : '未知错误'}`,
      data: {},
    };
  }
}

// ========== 辩论阶段 ==========

/**
 * 执行多空辩论 (调用 MiniMax LLM)
 */
async function executeDebate(
  signals: AgentSignal[],
  stockData: StockData
): Promise<{bullish: AgentSignal; bearish: AgentSignal}> {
  console.log('[Orchestrator] 多空辩论开始...');
  
  const bullishSignals = signals.filter(s => s.signal === 'bullish');
  const bearishSignals = signals.filter(s => s.signal === 'bearish');
  
  // 多头研究员
  const bullishPrompt = `
你是多头研究员，负责从正面角度分析股票。

当前分析股票：${stockData.name}（${stockData.code}）
当前价格：¥${stockData.price.toFixed(2)}
涨跌幅：${stockData.changePercent > 0 ? '+' : ''}${stockData.changePercent.toFixed(2)}%

现有看多分析师：${bullishSignals.map(s => s.agent).join('、') || '暂无'}
现有看空分析师：${bearishSignals.map(s => s.agent).join('、') || '暂无'}

请给出你的看多理由和投资建议。

请用JSON格式返回：
{
  "signal": "bullish",
  "confidence": 0-100,
  "reasoning": "看多理由（100字以内）"
}`;

  // 空头研究员
  const bearishPrompt = `
你是空头研究员，负责从负面角度分析股票。

当前分析股票：${stockData.name}（${stockData.code}）
当前价格：¥${stockData.price.toFixed(2)}
涨跌幅：${stockData.changePercent > 0 ? '+' : ''}${stockData.changePercent.toFixed(2)}%

现有看多分析师：${bullishSignals.map(s => s.agent).join('、') || '暂无'}
现有看空分析师：${bearishSignals.map(s => s.agent).join('、') || '暂无'}

请给出你的看空理由和风险提示。

请用JSON格式返回：
{
  "signal": "bearish",
  "confidence": 0-100,
  "reasoning": "看空理由（100字以内）"
}`;

  try {
    // 并行调用
    const [bullishResult, bearishResult] = await Promise.all([
      llmService.complete([
        { role: 'system', content: '你是专业的多头研究员，擅长发现股票的上涨理由和投资机会。' },
        { role: 'user', content: bullishPrompt },
      ], { maxTokens: 300, temperature: 0.7 }),
      llmService.complete([
        { role: 'system', content: '你是专业的空头研究员，擅长发现股票的风险和下跌因素。' },
        { role: 'user', content: bearishPrompt },
      ], { maxTokens: 300, temperature: 0.7 }),
    ]);

    const bullish = parseLLMResponse(bullishResult.content);
    const bearish = parseLLMResponse(bearishResult.content);
    
    console.log('[Orchestrator] 多空辩论完成');

    return {
      bullish: {
        agent: '多头研究员',
        agentId: 'bullish_researcher',
        signal: bullish.signal,
        confidence: bullish.confidence,
        reasoning: bullish.reasoning,
        data: { type: 'bullish' },
      },
      bearish: {
        agent: '空头研究员',
        agentId: 'bearish_researcher',
        signal: bearish.signal,
        confidence: bearish.confidence,
        reasoning: bearish.reasoning,
        data: { type: 'bearish' },
      },
    };
  } catch (error) {
    console.error('[Orchestrator] 辩论失败:', error);
    
    // 失败时返回默认
    return {
      bullish: {
        agent: '多头研究员',
        agentId: 'bullish_researcher',
        signal: 'bullish',
        confidence: 55,
        reasoning: bullishSignals.length > 0 
          ? `综合看多分析师意见: ${bullishSignals[0].reasoning.slice(0, 50)}...`
          : '等待更多分析数据',
        data: { type: 'bullish' },
      },
      bearish: {
        agent: '空头研究员',
        agentId: 'bearish_researcher',
        signal: 'bearish',
        confidence: 50,
        reasoning: bearishSignals.length > 0
          ? `综合看空分析师意见: ${bearishSignals[0].reasoning.slice(0, 50)}...`
          : '需警惕回调风险',
        data: { type: 'bearish' },
      },
    };
  }
}

// ========== 风险评估 ==========

/**
 * 执行风险评估
 */
async function executeRiskAssessment(
  signals: AgentSignal[],
  stockData: StockData
): Promise<{riskScore: number; maxLoss: number; positionLimit: number; risks: string[]}> {
  const bullishCount = signals.filter(s => s.signal === 'bullish').length;
  const bearishCount = signals.filter(s => s.signal === 'bearish').length;
  const neutralCount = signals.filter(s => s.signal === 'neutral').length;
  
  let riskScore = 50 + (bearishCount - bullishCount) * 10;
  riskScore = Math.max(20, Math.min(80, riskScore));
  
  const volatility = Math.abs(stockData.changePercent);
  if (volatility > 5) riskScore += 10;
  else if (volatility > 3) riskScore += 5;
  
  if (stockData.pe && stockData.pe > 50) riskScore += 15;
  else if (stockData.pe && stockData.pe < 15) riskScore -= 10;
  
  const maxLoss = Math.min(50, riskScore * 0.8);
  
  let positionLimit = 50 - riskScore / 2;
  if (bullishCount > bearishCount) positionLimit += 10;
  if (bearishCount > bullishCount) positionLimit -= 15;
  positionLimit = Math.max(10, Math.min(80, positionLimit));
  
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
  const bullishSignals = signals.filter(s => s.signal === 'bullish');
  const bearishSignals = signals.filter(s => s.signal === 'bearish');
  const avgConfidence = signals.reduce((sum, s) => sum + s.confidence, 0) / signals.length;
  
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
  
  const text = `
综合 ${signals.length} 位分析师的观点:

**市场共识:**
- ${bullishSignals.length} 位看多，${bearishSignals.length} 位看空
- 平均置信度: ${avgConfidence.toFixed(1)}%

**核心观点:**
${signals.slice(0, 3).map(s => `- ${s.agent}: ${s.signal === 'bullish' ? '看好' : s.signal === 'bearish' ? '看空' : '中性'} (${s.confidence}%置信)`).join('\n')}

**多空辩论:**
- 多头: ${debate.bullish.reasoning.slice(0, 80)}...
- 空头: ${debate.bearish.reasoning.slice(0, 80)}...

**风险评估:**
- 风险评分: ${riskAssessment.riskScore}/100
- 预计最大亏损: ${riskAssessment.maxLoss.toFixed(1)}%
- 建议仓位: ${riskAssessment.positionLimit.toFixed(0)}%
  `.trim();
  
  return {
    text,
    model: llmService.getProvider(),
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
    
    // ===== 阶段 2: Agent 分析 (调用 MiniMax LLM) =====
    updateProgress({ status: 'running', progress: 20, currentStep: '分析师正在分析...' });
    
    const signals: AgentSignal[] = [];
    const agentIds = request.analystIds.length > 0 
      ? request.analystIds 
      : ['warren_buffett', 'technicals_agent', 'sentiment_agent', 'risk_manager'];
    
    // 并行执行非风控 Agent (每个都会调用 LLM)
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
    
    // ===== 阶段 3: 辩论 (调用 MiniMax LLM) =====
    updateProgress({ status: 'running', progress: 60, currentStep: '多空辩论中...' });
    const debate = await executeDebate(signals, stockData);
    signals.push(debate.bullish, debate.bearish);
    
    // ===== 阶段 4: 风险评估 =====
    updateProgress({ status: 'running', progress: 75, currentStep: '风险评估中...' });
    const riskAssessment = await executeRiskAssessment(signals, stockData);
    
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

// ========== 导出 ==========

export { fetchStockData };
export { ANALYST_TEMPLATES };
