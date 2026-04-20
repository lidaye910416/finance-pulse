/**
 * 多智能体分析编排器
 * 
 * 参考 AI Hedge Fund 的 Portfolio Manager 设计
 * 协调多个 Agent 并行获取数据，通过 LLM 整合分析
 */

import type {
  StockData,
  AgentSignal,
  AnalysisRequest,
  AnalysisResponse,
  WorkflowState,
} from './types';
import { llmService } from './llmService';
import { analysts, Analyst } from '../analysts';

// ========== Agent 接口 ==========

interface BaseAgent {
  id: string;
  name: string;
  analyze(code: string, stockData: StockData): Promise<AgentSignal>;
}

// ========== 内置 Agent ==========

/**
 * 财务分析 Agent
 * 分析基本面数据
 */
const fundamentalAgent: BaseAgent = {
  id: 'fundamental',
  name: '财务分析',
  async analyze(_code: string, stockData: StockData): Promise<AgentSignal> {
    // 模拟财务数据分析
    // 实际应该调用东方财富API获取财务数据
    const pe = stockData.pe || Math.random() * 30 + 5;
    const pb = stockData.pb || Math.random() * 5 + 0.5;
    
    let signal: AgentSignal['signal'] = 'neutral';
    let confidence = 50;
    let reasoning = `PE: ${pe.toFixed(1)}, PB: ${pb.toFixed(1)}`;
    
    if (pe < 15 && pb < 1) {
      signal = 'bullish';
      confidence = 75;
      reasoning += ' | 低估值，价值凸显';
    } else if (pe > 40 || pb > 5) {
      signal = 'bearish';
      confidence = 65;
      reasoning += ' | 高估值，风险累积';
    }
    
    return {
      agent: this.name,
      signal,
      confidence,
      reasoning,
      data: { pe, pb, price: stockData.price },
    };
  },
};

/**
 * 技术分析 Agent
 * 分析K线和技术指标
 */
const technicalAgent: BaseAgent = {
  id: 'technical',
  name: '技术分析',
  async analyze(_code: string, stockData: StockData): Promise<AgentSignal> {
    // 模拟技术指标计算
    // 实际应该获取K线数据计算MA、MACD、RSI等
    const price = stockData.price;
    const change = stockData.changePercent;
    
    let signal: AgentSignal['signal'] = 'neutral';
    let confidence = 50;
    let reasoning = '';
    
    // 简单的趋势判断
    if (change > 2) {
      signal = 'bullish';
      confidence = 60 + Math.random() * 20;
      reasoning = '强势上涨，突破关键阻力位';
    } else if (change < -2) {
      signal = 'bearish';
      confidence = 60 + Math.random() * 20;
      reasoning = '破位下跌，短期趋势转弱';
    } else if (change > 0) {
      signal = 'neutral';
      confidence = 55;
      reasoning = '震荡整理，等待方向突破';
    } else {
      signal = 'neutral';
      confidence = 55;
      reasoning = '小幅调整，观望为主';
    }
    
    return {
      agent: this.name,
      signal,
      confidence,
      reasoning,
      data: { price, change, ma5: price * 0.99, ma10: price * 0.98 },
    };
  },
};

/**
 * 情绪分析 Agent
 * 分析新闻和市场情绪
 */
const sentimentAgent: BaseAgent = {
  id: 'sentiment',
  name: '情绪分析',
  async analyze(_code: string, _stockData: StockData): Promise<AgentSignal> {
    // 模拟情绪分析
    // 实际应该调用新闻API获取相关资讯
    const fearGreed = 26; // 从DashboardHome获取
    const northbound = 23.5; // 从DashboardHome获取
    
    let signal: AgentSignal['signal'] = 'neutral';
    let confidence = 50;
    let reasoning = `恐惧贪婪指数: ${fearGreed}, 北向资金: ${northbound}亿`;
    
    if (fearGreed < 30 && northbound > 0) {
      signal = 'bullish';
      confidence = 70;
      reasoning += ' | 极度恐惧区间 + 外资净买入';
    } else if (fearGreed > 70) {
      signal = 'bearish';
      confidence = 65;
      reasoning += ' | 过度贪婪，注意风险';
    }
    
    return {
      agent: this.name,
      signal,
      confidence,
      reasoning,
      data: { fearGreed, northbound },
    };
  },
};

/**
 * 宏观分析 Agent
 * 分析宏观经济影响
 */
const macroAgent: BaseAgent = {
  id: 'macro',
  name: '宏观分析',
  async analyze(_code: string, _stockData: StockData): Promise<AgentSignal> {
    // 模拟宏观分析
    // 实际应该从MacroData获取最新宏观数据
    const gdp = 5.0;
    const cpi = 1.1;
    const lpr = 3.45;
    const pmi = 49.2;
    
    let signal: AgentSignal['signal'] = 'neutral';
    let confidence = 50;
    let reasoning = `GDP: ${gdp}%, CPI: ${cpi}%, LPR: ${lpr}%, PMI: ${pmi}`;
    
    if (gdp >= 5 && cpi < 2 && lpr <= 3.5) {
      signal = 'bullish';
      confidence = 65;
      reasoning += ' | 宏观环境友好，政策空间充足';
    } else if (pmi < 50) {
      signal = 'bearish';
      confidence = 55;
      reasoning += ' | PMI低于荣枯线，制造业承压';
    }
    
    return {
      agent: this.name,
      signal,
      confidence,
      reasoning,
      data: { gdp, cpi, lpr, pmi },
    };
  },
};

// 所有 Agent 列表
const allAgents: BaseAgent[] = [
  fundamentalAgent,
  technicalAgent,
  sentimentAgent,
  macroAgent,
];

// ========== Orchestrator ==========

class AnalysisOrchestrator {
  private state: WorkflowState = {
    status: 'idle',
    progress: 0,
    currentStep: '',
    agentsCompleted: [],
  };

  getState(): WorkflowState {
    return { ...this.state };
  }

  /**
   * 执行完整分析流程
   */
  async analyze(request: AnalysisRequest): Promise<AnalysisResponse> {
    const startTime = Date.now();
    
    // 检查 LLM 配置
    if (!llmService.isConfigured()) {
      // 返回模拟响应
      return this.generateMockResponse(request.code, startTime);
    }

    try {
      this.updateState('running', 0, '准备分析数据...', []);

      // 1. 获取股票基础数据
      const stockData = await this.fetchStockData(request.code);
      this.updateState('running', 10, '获取股票数据...', []);

      // 2. 并行执行所有 Agent 分析
      const signals = await this.runAgents(stockData);
      this.updateState('running', 60, '执行多维度分析...', allAgents.map(a => a.id));

      // 3. 调用 LLM 整合分析
      const summary = await this.generateSummary(request, stockData, signals);
      this.updateState('running', 90, '生成投资建议...', allAgents.map(a => a.id));

      const duration = Date.now() - startTime;

      this.updateState('completed', 100, '分析完成', allAgents.map(a => a.id));

      return {
        code: request.code,
        timestamp: Date.now(),
        duration,
        signals,
        summary,
        recommendation: this.parseRecommendation(summary.text),
      };
    } catch (error) {
      this.updateState('error', 0, '', [], String(error));
      throw error;
    }
  }

  /**
   * 运行所有 Agent 并行分析
   */
  private async runAgents(stockData: StockData): Promise<AgentSignal[]> {
    const promises = allAgents.map(agent => 
      agent.analyze(stockData.code, stockData).catch(err => ({
        agent: agent.name,
        signal: 'neutral' as const,
        confidence: 0,
        reasoning: `分析失败: ${err}`,
        data: {},
      }))
    );

    return Promise.all(promises);
  }

  /**
   * 获取股票数据
   */
  private async fetchStockData(code: string): Promise<StockData> {
    // 模拟数据，实际应该调用API
    const mockData: Record<string, StockData> = {
      '600519': {
        code: '600519', name: '贵州茅台', price: 1688.0,
        change: -1.2, changePercent: -0.07, volume: 2345678,
        amount: 3.95e9, high: 1710, low: 1680, open: 1700, prevClose: 1690,
        pe: 28.5, pb: 8.2, marketCap: '2.1万亿', timestamp: Date.now(),
      },
      '000001': {
        code: '000001', name: '平安银行', price: 12.35,
        change: 0.08, changePercent: 0.65, volume: 45678901,
        amount: 5.64e8, high: 12.5, low: 12.2, open: 12.3, prevClose: 12.27,
        pe: 5.2, pb: 0.7, marketCap: '2400亿', timestamp: Date.now(),
      },
      '510300': {
        code: '510300', name: '沪深300ETF', price: 3.85,
        change: 0.02, changePercent: 0.52, volume: 78901234,
        amount: 3.04e8, high: 3.88, low: 3.82, open: 3.83, prevClose: 3.83,
        pe: 12.3, pb: 1.2, marketCap: '1150亿', timestamp: Date.now(),
      },
    };

    const data = mockData[code];
    if (data) return data;

    // 未知代码生成随机数据
    return {
      code,
      name: `股票 ${code}`,
      price: Math.random() * 100 + 10,
      change: (Math.random() - 0.5) * 10,
      changePercent: (Math.random() - 0.5) * 10,
      volume: Math.random() * 1e7,
      amount: Math.random() * 1e8,
      high: 0, low: 0, open: 0, prevClose: 0,
      pe: Math.random() * 30 + 5,
      pb: Math.random() * 5 + 0.5,
      marketCap: `${(Math.random() * 10000).toFixed(0)}亿`,
      timestamp: Date.now(),
    };
  }

  /**
   * 调用 LLM 生成综合分析
   */
  private async generateSummary(
    request: AnalysisRequest,
    stockData: StockData,
    signals: AgentSignal[]
  ): Promise<AnalysisResponse['summary']> {
    // 获取分析师配置
    const selectedAnalysts = request.analystIds
      .map(id => analysts.find(a => a.id === id))
      .filter(Boolean) as Analyst[];

    const analyst = selectedAnalysts[0] || analysts[0];

    // 构建 prompt
    const prompt = this.buildAnalysisPrompt(analyst, stockData, signals);

    const messages = [
      { role: 'system', content: analyst.systemPrompt },
      { role: 'user', content: prompt },
    ];

    const response = await llmService.complete(messages);

    return {
      text: response.content,
      model: response.model,
      tokens: response.tokens,
    };
  }

  /**
   * 构建分析 prompt
   */
  private buildAnalysisPrompt(
    analyst: Analyst,
    stockData: StockData,
    signals: AgentSignal[]
  ): string {
    return `
## 分析目标

股票代码: ${stockData.code}
股票名称: ${stockData.name}

## 基础数据

- 当前价格: ¥${stockData.price}
- 涨跌幅: ${stockData.changePercent > 0 ? '+' : ''}${stockData.changePercent.toFixed(2)}%
- 市盈率(PE): ${stockData.pe || 'N/A'}
- 市净率(PB): ${stockData.pb || 'N/A'}
- 总市值: ${stockData.marketCap || 'N/A'}

## 多维度分析结果

${signals.map(s => `### ${s.agent}
- 信号: ${s.signal}
- 置信度: ${s.confidence}%
- 分析: ${s.reasoning}
`).join('\n')}

## 你的任务

作为${analyst.name}（${analyst.style}风格），请基于以上数据给出分析：

1. **估值评估** - 当前估值是否合理
2. **风险因素** - 主要风险点
3. **投资建议** - 买入/持有/卖出建议及理由

请用中文回复，格式如下：
[估值评估]
...
[风险因素]
...
[投资建议]
...

*本分析仅供参考，不构成投资建议*
`.trim();
  }

  /**
   * 解析 LLM 回复，提取建议
   */
  private parseRecommendation(text: string): AnalysisResponse['recommendation'] {
    const defaultRec: AnalysisResponse['recommendation'] = {
      action: 'watch',
      confidence: 50,
      timeframe: '短期观望',
      risks: ['市场有风险，投资需谨慎'],
    };

    if (text.includes('买入') || text.includes('buy') || text.includes('增持')) {
      defaultRec.action = 'buy';
      defaultRec.confidence = 70;
      defaultRec.timeframe = '建议3-6个月持有';
    } else if (text.includes('卖出') || text.includes('sell') || text.includes('减持')) {
      defaultRec.action = 'sell';
      defaultRec.confidence = 65;
    } else if (text.includes('持有') || text.includes('hold') || text.includes('中性')) {
      defaultRec.action = 'hold';
      defaultRec.confidence = 55;
      defaultRec.timeframe = '建议持有观察';
    }

    return defaultRec;
  }

  /**
   * 生成模拟响应（LLM未配置时使用）
   */
  private generateMockResponse(code: string, startTime: number): AnalysisResponse {
    const signals: AgentSignal[] = allAgents.map(agent => ({
      agent: agent.name,
      signal: 'neutral' as const,
      confidence: Math.random() * 30 + 40,
      reasoning: '模拟数据 - 请配置 LLM API 以获取真实分析',
      data: {},
    }));

    return {
      code,
      timestamp: Date.now(),
      duration: Date.now() - startTime,
      signals,
      summary: {
        text: '⚠️ 当前使用模拟数据，请配置 LLM API 获取真实分析。\n\n支持的 LLM Provider:\n- OpenAI (GPT-4)\n- Anthropic (Claude)\n- DeepSeek\n\n请在设置中配置 API Key。',
        model: 'mock',
        tokens: 0,
      },
      recommendation: {
        action: 'watch',
        confidence: 50,
        timeframe: '请配置 LLM',
        risks: ['使用模拟数据，结论仅供参考'],
      },
    };
  }

  /**
   * 更新状态
   */
  private updateState(
    status: WorkflowState['status'],
    progress: number,
    currentStep: string,
    agentsCompleted: string[],
    error?: string
  ) {
    this.state = { status, progress, currentStep, agentsCompleted, error };
  }
}

// 单例导出
export const orchestrator = new AnalysisOrchestrator();
export default orchestrator;
