/**
 * 回测引擎
 * 
 * 参考 ai-hedge-fund 的回测系统实现
 * 支持多种回测策略和性能指标计算
 */

import { akshareService } from '../dataProviders/akshareService';
import { executeAnalysis } from '../analysis/orchestrator';

export interface BacktestConfig {
  code: string;
  startDate: string;
  endDate: string;
  initialCapital: number;      // 初始资金
  commission: number;         // 佣金费率 (默认0.0003)
  slippage: number;          // 滑点 (默认0.0001)
  positionSize: number;        // 仓位比例 (默认0.3)
}

export interface BacktestResult {
  code: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalCapital: number;
  totalReturn: number;        // 总收益率 %
  annualReturn: number;       // 年化收益率 %
  sharpeRatio: number;       // 夏普比率
  maxDrawdown: number;       // 最大回撤 %
  winRate: number;           // 胜率 %
  totalTrades: number;       // 总交易次数
  winTrades: number;         // 盈利次数
  lossTrades: number;        // 亏损次数
  avgWin: number;            // 平均盈利
  avgLoss: number;           // 平均亏损
  equityCurve: EquityPoint[];
  trades: TradeRecord[];
}

export interface EquityPoint {
  date: string;
  equity: number;
  drawdown: number;
}

export interface TradeRecord {
  date: string;
  action: 'buy' | 'sell';
  price: number;
  quantity: number;
  amount: number;
  signal?: string;
  confidence?: number;
}

/**
 * 回测引擎类
 */
export class Backtester {
  private config: BacktestConfig;
  private klineData: any[] = [];
  private equityCurve: EquityPoint[] = [];
  private trades: TradeRecord[] = [];
  
  // 账户状态
  private cash: number = 0;
  private position: number = 0;

  constructor(config: BacktestConfig) {
    this.config = {
      ...config,
      commission: config.commission ?? 0.0003,
      slippage: config.slippage ?? 0.0001,
      positionSize: config.positionSize ?? 0.3,
    };
    this.cash = config.initialCapital;
  }

  /**
   * 加载历史数据
   */
  async loadData(): Promise<void> {
    console.log(`[Backtester] 加载 ${this.config.code} 历史数据...`);
    console.log(`[Backtester] 期间: ${this.config.startDate} - ${this.config.endDate}`);
    
    this.klineData = await akshareService.getKlineHistory(
      this.config.code,
      'daily',
      this.config.startDate,
      this.config.endDate
    );
    
    // 转换数据格式 (AKShare 返回格式)
    this.klineData = this.klineData.map(item => ({
      date: item[0],      // 交易日期
      open: parseFloat(item[1]),
      high: parseFloat(item[2]),
      low: parseFloat(item[3]),
      close: parseFloat(item[4]),
      volume: parseFloat(item[5]),
    }));
    
    // 按日期排序
    this.klineData.sort((a, b) => a.date.localeCompare(b.date));
    
    console.log(`[Backtester] 加载完成，共 ${this.klineData.length} 个交易日`);
  }

  /**
   * 运行回测
   */
  async run(): Promise<BacktestResult> {
    if (this.klineData.length === 0) {
      await this.loadData();
    }

    console.log(`[Backtester] 开始回测...`);
    
    let peak = this.config.initialCapital;
    
    for (let i = 0; i < this.klineData.length; i++) {
      const bar = this.klineData[i];
      const currentEquity = this.cash + this.position * bar.close;
      
      // 更新峰值和回撤
      if (currentEquity > peak) peak = currentEquity;
      const drawdown = peak > 0 ? (peak - currentEquity) / peak * 100 : 0;
      
      // 记录权益曲线
      this.equityCurve.push({
        date: bar.date,
        equity: currentEquity,
        drawdown,
      });

      // 跳过第一天 (没有信号)
      if (i === 0) continue;

      // 生成交易信号
      const signal = await this.generateSignal(bar, i);
      
      if (!signal) continue;

      // 执行交易
      if (signal.action === 'buy' && this.position === 0) {
        this.executeBuy(bar, signal);
      } else if (signal.action === 'sell' && this.position > 0) {
        this.executeSell(bar, signal);
      }
    }

    // 计算最终权益
    const finalBar = this.klineData[this.klineData.length - 1];
    const finalCapital = this.cash + this.position * finalBar.close;
    
    // 计算性能指标
    return this.calculateMetrics(finalCapital);
  }

  /**
   * 生成交易信号
   */
  private async generateSignal(bar: any, index: number): Promise<{
    action: 'buy' | 'sell';
    confidence: number;
    signal: string;
  } | null> {
    try {
      // 获取最近N天的数据作为历史
      const historyData = this.klineData.slice(Math.max(0, index - 30), index);
      if (historyData.length < 5) return null;

      // 调用 AI 分析
      const result = await executeAnalysis({
        code: this.config.code,
        analystIds: ['warren_buffett', 'technicals_agent', 'sentiment_agent'],
        includeHistory: false,
      });

      // 根据 AI 建议生成信号
      const action = result.recommendation.action;
      const confidence = result.recommendation.confidence;

      if (action === 'buy' && confidence > 60) {
        return {
          action: 'buy',
          confidence,
          signal: 'ai_buy',
        };
      } else if (action === 'sell' && confidence > 60) {
        return {
          action: 'sell',
          confidence,
          signal: 'ai_sell',
        };
      }

      // 技术指标信号
      const recentData = historyData.slice(-5);
      const ma5 = recentData.reduce((sum, d) => sum + d.close, 0) / 5;
      const ma20 = historyData.reduce((sum, d) => sum + d.close, 0) / Math.min(20, historyData.length);
      
      // 金叉买入
      if (ma5 > ma20 && bar.close > ma5) {
        return {
          action: 'buy',
          confidence: 55,
          signal: 'ma_cross',
        };
      }
      
      // 死叉卖出
      if (ma5 < ma20 && bar.close < ma5) {
        return {
          action: 'sell',
          confidence: 55,
          signal: 'ma_cross',
        };
      }

      return null;
    } catch (error) {
      console.error('[Backtester] 生成信号失败:', error);
      return null;
    }
  }

  /**
   * 执行买入
   */
  private executeBuy(bar: any, signal: { confidence: number; signal: string }): void {
    const availableCash = this.cash * this.config.positionSize;
    const costPerShare = bar.close * (1 + this.config.slippage);
    const quantity = Math.floor(availableCash / costPerShare / 100) * 100; // 整手
    
    if (quantity <= 0) return;

    const totalCost = quantity * costPerShare + quantity * costPerShare * this.config.commission;
    if (totalCost > this.cash) return;

    this.cash -= totalCost;
    this.position = quantity;

    this.trades.push({
      date: bar.date,
      action: 'buy',
      price: bar.close,
      quantity,
      amount: totalCost,
      signal: signal.signal,
      confidence: signal.confidence,
    });

    console.log(`[Backtester] ${bar.date} 买入 ${quantity} 股 @ ${bar.close}`);
  }

  /**
   * 执行卖出
   */
  private executeSell(bar: any, signal: { confidence: number; signal: string }): void {
    if (this.position <= 0) return;

    const revenue = this.position * bar.close * (1 - this.config.slippage - this.config.commission);
    
    this.trades.push({
      date: bar.date,
      action: 'sell',
      price: bar.close,
      quantity: this.position,
      amount: revenue,
      signal: signal.signal,
      confidence: signal.confidence,
    });

    console.log(`[Backtester] ${bar.date} 卖出 ${this.position} 股 @ ${bar.close}`);

    this.cash += revenue;
    this.position = 0;
  }

  /**
   * 计算性能指标
   */
  private calculateMetrics(finalCapital: number): BacktestResult {
    const totalReturn = (finalCapital - this.config.initialCapital) / this.config.initialCapital * 100;
    
    // 计算年化收益率
    const days = this.klineData.length;
    const years = days / 252;
    const annualReturn = (Math.pow(finalCapital / this.config.initialCapital, 1 / years) - 1) * 100;
    
    // 计算夏普比率
    const returns = this.equityCurve.slice(1).map((p, i) => 
      (p.equity - this.equityCurve[i].equity) / this.equityCurve[i].equity
    );
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const stdReturn = Math.sqrt(
      returns.map(r => (r - avgReturn) ** 2).reduce((a, b) => a + b, 0) / returns.length
    );
    const sharpeRatio = stdReturn > 0 ? (avgReturn / stdReturn) * Math.sqrt(252) : 0;

    // 计算最大回撤
    let maxDrawdown = 0;
    let peak = this.config.initialCapital;
    for (const point of this.equityCurve) {
      if (point.equity > peak) peak = point.equity;
      const drawdown = (peak - point.equity) / peak * 100;
      if (drawdown > maxDrawdown) maxDrawdown = drawdown;
    }

    // 计算胜率
    let winTrades = 0;
    let lossTrades = 0;
    let totalWin = 0;
    let totalLoss = 0;

    for (let i = 0; i < this.trades.length - 1; i += 2) {
      if (i + 1 < this.trades.length) {
        const buyAmount = this.trades[i].amount;
        const sellAmount = this.trades[i + 1].amount;
        
        if (sellAmount > buyAmount) {
          winTrades++;
          totalWin += sellAmount - buyAmount;
        } else {
          lossTrades++;
          totalLoss += buyAmount - sellAmount;
        }
      }
    }

    const winRate = this.trades.length > 0 ? (winTrades / Math.ceil(this.trades.length / 2)) * 100 : 0;
    const avgWin = winTrades > 0 ? totalWin / winTrades : 0;
    const avgLoss = lossTrades > 0 ? totalLoss / lossTrades : 0;

    return {
      code: this.config.code,
      startDate: this.config.startDate,
      endDate: this.config.endDate,
      initialCapital: this.config.initialCapital,
      finalCapital,
      totalReturn,
      annualReturn,
      sharpeRatio,
      maxDrawdown,
      winRate,
      totalTrades: Math.ceil(this.trades.length / 2),
      winTrades,
      lossTrades,
      avgWin,
      avgLoss,
      equityCurve: this.equityCurve,
      trades: this.trades,
    };
  }
}

/**
 * 运行回测的便捷函数
 */
export async function runBacktest(config: BacktestConfig): Promise<BacktestResult> {
  const backtester = new Backtester(config);
  return await backtester.run();
}

/**
 * 打印回测结果
 */
export function printBacktestResult(result: BacktestResult): void {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║                    回测结果报告                              ║');
  console.log('╠════════════════════════════════════════════════════════════╣');
  console.log(`║ 股票代码: ${result.code}`);
  console.log(`║ 回测期间: ${result.startDate} - ${result.endDate}`);
  console.log('╠════════════════════════════════════════════════════════════╣');
  console.log(`║ 初始资金: ¥${result.initialCapital.toLocaleString()}`);
  console.log(`║ 最终资金: ¥${result.finalCapital.toLocaleString()}`);
  console.log(`║ 总收益率: ${result.totalReturn >= 0 ? '+' : ''}${result.totalReturn.toFixed(2)}%`);
  console.log(`║ 年化收益: ${result.annualReturn >= 0 ? '+' : ''}${result.annualReturn.toFixed(2)}%`);
  console.log('╠════════════════════════════════════════════════════════════╣');
  console.log(`║ 夏普比率: ${result.sharpeRatio.toFixed(2)}`);
  console.log(`║ 最大回撤: -${result.maxDrawdown.toFixed(2)}%`);
  console.log(`║ 胜率: ${result.winRate.toFixed(2)}%`);
  console.log('╠════════════════════════════════════════════════════════════╣');
  console.log(`║ 总交易次数: ${result.totalTrades}`);
  console.log(`║ 盈利次数: ${result.winTrades}`);
  console.log(`║ 亏损次数: ${result.lossTrades}`);
  console.log(`║ 平均盈利: ¥${result.avgWin.toFixed(2)}`);
  console.log(`║ 平均亏损: ¥${result.avgLoss.toFixed(2)}`);
  console.log('╚════════════════════════════════════════════════════════════╝');
}
