/**
 * FinancePulse CLI 工具
 * 
 * 命令行界面，支持:
 * - 股票行情查询
 * - AI 分析
 * - 模拟交易
 * - 回测运行
 */

import { akshareService } from '../services/dataProviders/akshareService';
import { Backtester } from '../services/backtester';
import { tradeSimulator } from '../services/simulator/tradeSimulator';
import { llmService } from '../services/analysis/llmService';
import type { KLinePeriod } from '../services/dataProviders/akshareService';

// ========== CLI 命令类型 ==========

export interface CLICommand {
  name: string;
  description: string;
  execute: (args: string[]) => Promise<void>;
}

export interface CLIRunnerOptions {
  prompt?: string;
}

// ========== 股票命令 ==========

const stockCommands: CLICommand[] = [
  {
    name: 'quote',
    description: '查询股票行情 (用法: quote 600519)',
    execute: async (args: string[]) => {
      const code = args[0] || '';
      if (!code) {
        console.error('请提供股票代码');
        return;
      }
      
      console.log(`正在查询 ${code} ...`);
      const quotes = await akshareService.getRealtimeQuote([code]);
      const quote = quotes[code];
      
      if (!quote) {
        console.error(`未找到股票 ${code}`);
        return;
      }
      
      console.log('\n📊 股票行情');
      console.log(`代码: ${quote.code}`);
      console.log(`名称: ${quote.name}`);
      console.log(`价格: ¥${quote.price}`);
      console.log(`涨跌: ${quote.change >= 0 ? '+' : ''}${quote.change} (${quote.changePercent.toFixed(2)}%)`);
      console.log(`成交量: ${(quote.volume / 10000).toFixed(2)}万`);
      console.log(`成交额: ${(quote.amount / 100000000).toFixed(2)}亿`);
      console.log(`最高: ¥${quote.high} | 最低: ¥${quote.low}`);
      console.log(`今开: ¥${quote.open} | 昨收: ¥${quote.prevClose}`);
    },
  },
  {
    name: 'quotes',
    description: '批量查询股票行情 (用法: quotes 600519 000858 300750)',
    execute: async (args: string[]) => {
      const codes = args.length > 0 ? args : ['600519', '000858', '300750'];
      
      console.log(`正在查询 ${codes.length} 只股票...`);
      const quotes = await akshareService.getRealtimeQuote(codes);
      
      console.log('\n📊 股票行情列表');
      console.log('─'.repeat(60));
      
      Object.entries(quotes).forEach(([code, quote]) => {
        const changeSign = quote.change >= 0 ? '+' : '';
        console.log(
          `${quote.name.padEnd(8)} ${code.padEnd(8)} ` +
          `¥${quote.price.toFixed(2).padStart(8)} ` +
          `${changeSign}${quote.change.toFixed(2)} (${changeSign}${quote.changePercent.toFixed(2)}%)`
        );
      });
    },
  },
  {
    name: 'kline',
    description: '获取K线数据 (用法: kline 600519 daily 2024-01-01 2024-12-31)',
    execute: async (args: string[]) => {
      const [code, period = 'daily', startDate, endDate] = args;
      
      if (!code) {
        console.error('请提供股票代码');
        return;
      }
      
      console.log(`正在获取 ${code} K线数据...`);
      const klines = await akshareService.getKlineHistory(code, period as KLinePeriod, startDate, endDate);
      
      console.log(`\n📈 ${code} K线数据 (${klines.length} 条)`);
      console.log('─'.repeat(80));
      
      klines.slice(-10).forEach(k => {
        console.log(
          `${k.date} 开:${k.open} 高:${k.high} 低:${k.low} 收:${k.close} 量:${k.volume}`
        );
      });
    },
  },
];

// ========== AI 分析命令 ==========

const aiCommands: CLICommand[] = [
  {
    name: 'analyze',
    description: 'AI 分析股票 (用法: analyze 600519)',
    execute: async (args: string[]) => {
      const code = args[0] || '';
      if (!code) {
        console.error('请提供股票代码');
        return;
      }
      
      // 检查 LLM 配置
      if (!llmService.isConfigured()) {
        console.error('⚠️ LLM 未配置，请先在设置中输入 API Key');
        console.error('或使用 mock 模式进行测试');
        return;
      }
      
      console.log(`🔍 正在分析 ${code}...`);
      
      // 获取数据
      const quotes = await akshareService.getRealtimeQuote([code]);
      const quote = quotes[code];
      
      if (!quote) {
        console.error(`未找到股票 ${code}`);
        return;
      }
      
      // 调用 LLM 分析
      const response = await llmService.complete([
        {
          role: 'user',
          content: `请分析股票 ${quote.name}(${code})：
            当前价: ¥${quote.price}
            涨跌幅: ${quote.changePercent.toFixed(2)}%
            成交量: ${(quote.volume / 10000).toFixed(2)}万
            换手率: ${((quote.volume / (quote.amount / quote.price)) * 100).toFixed(2)}%
            
            请给出简短的投资建议。`,
        },
      ]);
      
      console.log('\n🤖 AI 分析结果:');
      console.log('─'.repeat(60));
      console.log(response.content);
      console.log('─'.repeat(60));
      console.log(`模型: ${response.model} | Token: ${response.tokens}`);
    },
  },
  {
    name: 'test-llm',
    description: '测试 LLM 连接 (用法: test-llm)',
    execute: async () => {
      if (!llmService.isConfigured()) {
        console.error('⚠️ LLM 未配置，请先在设置中输入 API Key');
        return;
      }
      
      console.log('🔄 正在测试 LLM 连接...');
      
      try {
        const response = await llmService.complete([
          { role: 'user', content: '请回复"连接成功"' },
        ], { maxTokens: 50 });
        
        console.log('\n✅ LLM 连接成功!');
        console.log(`回复: ${response.content}`);
        console.log(`模型: ${response.model}`);
        console.log(`Token: ${response.tokens}`);
      } catch (error) {
        console.error('\n❌ LLM 连接失败:', error);
      }
    },
  },
];

// ========== 模拟交易命令 ==========

const tradeCommands: CLICommand[] = [
  {
    name: 'account',
    description: '查看账户信息 (用法: account)',
    execute: async () => {
      const account = tradeSimulator.getAccount();
      
      console.log('\n💰 账户信息');
      console.log('─'.repeat(40));
      console.log(`可用资金: ¥${account.cash.toLocaleString()}`);
      console.log(`总资产:   ¥${account.totalAssets.toLocaleString()}`);
      console.log(`市值:     ¥${account.marketValue.toLocaleString()}`);
      console.log(`总盈亏:   ${account.totalProfit >= 0 ? '+' : ''}¥${account.totalProfit.toLocaleString()}`);
      console.log(`收益率:   ${account.profitPercent >= 0 ? '+' : ''}${account.profitPercent.toFixed(2)}%`);
    },
  },
  {
    name: 'positions',
    description: '查看持仓 (用法: positions)',
    execute: async () => {
      const positions = tradeSimulator.getPositions();
      
      if (positions.length === 0) {
        console.log('暂无持仓');
        return;
      }
      
      console.log('\n📦 持仓信息');
      console.log('─'.repeat(60));
      
      positions.forEach(p => {
        console.log(
          `${p.name.padEnd(8)} ${p.code.padEnd(8)} ` +
          `数量:${p.quantity.toString().padStart(4)} ` +
          `成本:¥${p.avgCost.toFixed(2)} ` +
          `浮动:${p.unrealizedPnL >= 0 ? '+' : ''}¥${p.unrealizedPnL.toFixed(2)}`
        );
      });
    },
  },
  {
    name: 'buy',
    description: '市价买入 (用法: buy 600519 贵州茅台 100)',
    execute: async (args: string[]) => {
      const [code, name = '', quantityStr = ''] = args;
      const quantity = parseInt(quantityStr) || 0;
      
      if (!code || !quantity) {
        console.error('请提供股票代码、名称和数量');
        return;
      }
      
      console.log(`📝 市价买入 ${name} ${quantity}股...`);
      const order = tradeSimulator.buyMarket(code, name, quantity);
      
      if (order.status === 'rejected') {
        console.error(`❌ 下单失败: ${order.reason}`);
      } else {
        console.log(`✅ 成交: ${order.name} ${order.filledQty}股 @ ¥${order.avgPrice}`);
      }
    },
  },
  {
    name: 'sell',
    description: '市价卖出 (用法: sell 600519 贵州茅台 100)',
    execute: async (args: string[]) => {
      const [code, name = '', quantityStr = ''] = args;
      const quantity = parseInt(quantityStr) || 0;
      
      if (!code || !quantity) {
        console.error('请提供股票代码、名称和数量');
        return;
      }
      
      console.log(`📝 市价卖出 ${name} ${quantity}股...`);
      const order = tradeSimulator.sellMarket(code, name, quantity);
      
      if (order.status === 'rejected') {
        console.error(`❌ 下单失败: ${order.reason}`);
      } else {
        console.log(`✅ 成交: ${order.name} ${order.filledQty}股 @ ¥${order.avgPrice}`);
      }
    },
  },
  {
    name: 'clear',
    description: '一键清仓 (用法: clear)',
    execute: async () => {
      const orders = tradeSimulator.clearAllPositions();
      console.log(`✅ 已清仓 ${orders.length} 只股票`);
    },
  },
  {
    name: 'reset',
    description: '重置账户 (用法: reset)',
    execute: async () => {
      tradeSimulator.reset();
      console.log('✅ 账户已重置');
    },
  },
  {
    name: 'history',
    description: '查看交易历史 (用法: history)',
    execute: async () => {
      const history = tradeSimulator.getTradeHistory();
      
      if (history.length === 0) {
        console.log('暂无交易记录');
        return;
      }
      
      console.log('\n📜 交易历史');
      console.log('─'.repeat(60));
      
      history.forEach(h => {
        console.log(
          `${h.date} ${h.side === 'buy' ? '买入' : '卖出'} ${h.name.padEnd(8)} ` +
          `${h.quantity}股 @ ¥${h.price} ` +
          `手续费: ¥${h.commission.toFixed(2)}`
        );
      });
    },
  },
];

// ========== 回测命令 ==========

const backtestCommands: CLICommand[] = [
  {
    name: 'backtest',
    description: '运行回测 (用法: backtest 600519 2024-01-01 2024-12-31)',
    execute: async (args: string[]) => {
      const [code = '600519', startDate = '2024-01-01', endDate = '2024-12-31'] = args;
      
      console.log(`🔄 正在运行回测...`);
      console.log(`股票: ${code}`);
      console.log(`时间: ${startDate} ~ ${endDate}`);
      
      const backtester = new Backtester({
        code,
        startDate,
        endDate,
        initialCapital: 100000,
        commission: 0.0003,
        slippage: 0.001,
        positionSize: 0.3,
      });
      
      try {
        await backtester.loadData();
        const result = await backtester.run();
        
        console.log('\n📊 回测结果');
        console.log('─'.repeat(40));
        console.log(`总收益率: ${result.totalReturn >= 0 ? '+' : ''}${result.totalReturn.toFixed(2)}%`);
        console.log(`年化收益率: ${result.annualReturn >= 0 ? '+' : ''}${result.annualReturn.toFixed(2)}%`);
        console.log(`夏普比率: ${result.sharpeRatio.toFixed(2)}`);
        console.log(`最大回撤: ${result.maxDrawdown.toFixed(2)}%`);
        console.log(`胜率: ${result.winRate.toFixed(2)}%`);
        console.log(`交易次数: ${result.trades.length}`);
      } catch (error) {
        console.error('回测失败:', error);
      }
    },
  },
];

// ========== 帮助命令 ==========

const helpCommands: CLICommand[] = [
  {
    name: 'help',
    description: '显示帮助信息',
    execute: async () => {
      console.log('\n📖 FinancePulse CLI 帮助');
      console.log('─'.repeat(40));
      console.log('\n【股票命令】');
      stockCommands.forEach(cmd => {
        console.log(`  ${cmd.name.padEnd(12)} ${cmd.description}`);
      });
      
      console.log('\n【AI 命令】');
      aiCommands.forEach(cmd => {
        console.log(`  ${cmd.name.padEnd(12)} ${cmd.description}`);
      });
      
      console.log('\n【交易命令】');
      tradeCommands.forEach(cmd => {
        console.log(`  ${cmd.name.padEnd(12)} ${cmd.description}`);
      });
      
      console.log('\n【回测命令】');
      backtestCommands.forEach(cmd => {
        console.log(`  ${cmd.name.padEnd(12)} ${cmd.description}`);
      });
      
      console.log('\n💡 示例:');
      console.log('  npx ts-node src/cli/index.ts quote 600519');
      console.log('  npx ts-node src/cli/index.ts buy 600519 贵州茅台 100');
      console.log('  npx ts-node src/cli/index.ts backtest 600519');
    },
  },
];

// ========== 命令注册表 ==========

const commands: Record<string, CLICommand> = {};

// 注册所有命令
[...stockCommands, ...aiCommands, ...tradeCommands, ...backtestCommands, ...helpCommands].forEach(cmd => {
  commands[cmd.name] = cmd;
});

// ========== CLI 运行器 ==========

class CLIRunner {
  private commands = commands;

  // 运行命令
  async run(command: string, args: string[]): Promise<void> {
    const cmd = this.commands[command];
    
    if (!cmd) {
      console.error(`未知命令: ${command}`);
      console.error(`输入 'help' 查看可用命令`);
      return;
    }
    
    await cmd.execute(args);
  }

  // 交互模式 - 在浏览器环境不可用
  async interactive(_prompt = '> '): Promise<void> {
    console.log('交互模式仅在 Node.js 环境中可用');
    console.log('请使用命令行参数执行命令，例如:');
    console.log('  npx ts-node src/cli/index.ts quote 600519');
    console.log('  npx ts-node src/cli/index.ts help');
  }

  // 获取所有命令
  getCommands(): CLICommand[] {
    return Object.values(this.commands);
  }
}

// ========== 单例导出 ==========

export const cliRunner = new CLIRunner();
export default cliRunner;

// ========== 直接执行 ==========

// 如果直接运行此文件 (仅 Node.js 环境)
// if (require.main === module) {
//   const [, , command, ...args] = process.argv;
//
//   if (!command || command === 'help') {
//     commands.help.execute([]);
//   } else {
//     cliRunner.run(command, args);
//   }
// }
