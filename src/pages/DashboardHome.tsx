import { useState } from 'react';
import { MetricCard, Card, Badge } from '../components';
import { useNavigate } from 'react-router-dom';

// 指标详细解释数据
export type MetricExplanationKeys = 'fearGreed' | 'position' | 'northbound' | 'sentiment';

export const metricExplanations: Record<MetricExplanationKeys, {
  title: string;
  calculation: string;
  interpretation: string;
  currentValue: string | number;
  phase: string;
  suggestion: string;
}> = {
  fearGreed: {
    title: '恐惧贪婪指数',
    calculation: '由 AlternativeMe 计算，综合分析：\n• 波动率 (25%) - VIX 恐慌指数\n• 做空/做多比率 (25%) - 期权市场情绪\n• 垃圾债券需求 (10%) - 风险偏好指标\n• 黄金/股票比率 (10%) - 避险需求\n• 期权博客 (15%) - 社交媒体情绪\n• 调查 (15%) - 投资者调查问卷',
    interpretation: '• 0-25: 极度恐惧 (Possible Bargain)\n• 25-45: 恐惧 (Buying Opportunity)\n• 45-55: 中性 (Hold)\n• 55-75: 贪婪 (Bubbles Forming)\n• 75-100: 极度贪婪 (Fomo)',
    currentValue: 26,
    phase: '极度恐惧',
    suggestion: '历史上，极度恐惧时期往往是买入机会',
  },
  position: {
    title: '仓位管理建议',
    calculation: '基于市场阶段综合评估：\n① 恐惧贪婪指数权重 30%\n② 涨停数量权重 20%\n③ 北向资金流向权重 25%\n④ 成交额变化权重 15%\n⑤ 宏观政策环境权重 10%\n\n公式：仓位 = f(各指标加权得分)',
    interpretation: '• 0-30%: 冰点期 - 极度谨慎，极少量仓位\n• 30-50%: 修复期 - 逐步建仓，30-50%\n• 50-70%: 分歧期 - 动态调整，50-70%\n• 70-90%: 亢奋期 - 逐步减仓，70-90%\n• 90-100%: 顶部区 - 清仓离场',
    currentValue: '40-60%',
    phase: '修复期',
    suggestion: '当前处于修复期，建议轻仓试错，不追涨杀跌',
  },
  northbound: {
    title: '北向资金',
    calculation: '北向资金 = 沪深港通北向合计净买入额\n\n数据来源：沪深交易所每日公布的陆股通数据\n• 净买入 = 买入额 - 卖出额\n• 统计口径：当日所有北向渠道总和\n• 更新频率：每个交易日收盘后15:30',
    interpretation: '• 单日净买入 > 50亿：强烈看多信号\n• 单日净买入 > 30亿：积极信号\n• 单日净买入 > 10亿：中性偏好\n• 单日净卖出 > 30亿：谨慎信号\n• 连续3日净买入：主力建仓信号',
    currentValue: '+23.5亿',
    phase: '3日净买入',
    suggestion: '北向资金连续3日净买入，显示外资对A股信心增强',
  },
  sentiment: {
    title: 'A股市场情绪',
    calculation: '四阶段量化模型：\n\n① 涨停数量 (30%权重)\n  - 冰点: < 60家\n  - 修复: 60-100家\n  - 分歧: 100-150家\n  - 亢奋: > 150家\n\n② 跌停数量 (20%权重)\n  - 正常: < 10家\n  - 谨慎: 10-30家\n  - 恐慌: > 30家\n\n③ 成交额变化 (25%权重)\n④ 板块轮动速度 (25%权重)',
    interpretation: '• 冰点：市场极度悲观，赚钱效应差\n• 修复：情绪逐步回暖，机会开始出现\n• 分歧：多空博弈激烈，板块分化\n• 亢奋：市场过度乐观，风险累积',
    currentValue: '修复期',
    phase: 'Phase 2',
    suggestion: '当前处于修复初期，建议精选赛道，控制仓位',
  },
};

function MetricModal({ metricKey, onClose }: { metricKey: string; onClose: () => void }) {
  const data = metricExplanations[metricKey as keyof typeof metricExplanations];
  if (!data) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-lg bg-surface-100 rounded-t-3xl p-6 animate-slide-up max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Handle */}
        <div className="absolute top-3 left-1/2 -translate-x-1/2 w-10 h-1 bg-gray-600 rounded-full" />

        {/* Header */}
        <div className="flex items-center justify-between mb-4 mt-2">
          <h2 className="text-lg font-display font-bold text-white">{data.title}</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>

        {/* Current Status */}
        <div className="bg-gradient-to-r from-accent-blue/20 to-accent-green/20 rounded-xl p-4 mb-4 border border-accent-blue/20">
          <div className="text-xs text-gray-400 mb-1">当前值</div>
          <div className="text-2xl font-display font-bold text-white">{data.currentValue}</div>
          <div className="text-sm text-accent-green mt-1">{data.phase}</div>
        </div>

        {/* Calculation */}
        <div className="mb-4">
          <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            <span className="w-5 h-5 rounded bg-accent-blue/20 text-accent-blue text-xs flex items-center justify-center">📐</span>
            计算方法
          </h3>
          <div className="bg-surface-200/50 rounded-xl p-4 text-sm text-gray-300 whitespace-pre-line font-mono leading-relaxed">
            {data.calculation}
          </div>
        </div>

        {/* Interpretation */}
        <div className="mb-4">
          <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            <span className="w-5 h-5 rounded bg-accent-green/20 text-accent-green text-xs flex items-center justify-center">📊</span>
            解读指南
          </h3>
          <div className="bg-surface-200/50 rounded-xl p-4 text-sm text-gray-300 whitespace-pre-line leading-relaxed">
            {data.interpretation}
          </div>
        </div>

        {/* Suggestion */}
        <div className="bg-accent-yellow/10 rounded-xl p-4 border border-accent-yellow/20">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-accent-yellow">💡</span>
            <span className="text-sm font-display font-semibold text-accent-yellow">投资建议</span>
          </div>
          <p className="text-sm text-gray-300">{data.suggestion}</p>
        </div>

        {/* Navigation Hint */}
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-xs text-gray-500 text-center">
            点击查看更多详细分析 → A股情绪 / 仓位管理 页面
          </p>
        </div>
      </div>
    </div>
  );
}

const fearGreedData = { value: 26, label: '恐惧贪婪', subValue: '极度恐惧', trend: 'down' as const };
const positionData = { value: '40-60%', label: '仓位建议', subValue: '轻仓试错', trend: 'neutral' as const };
const northboundData = { value: '+23.5亿', label: '北向资金', subValue: '连续3日净买', trend: 'up' as const };
const sentimentData = { value: '修复期', label: '市场情绪', subValue: 'Phase 2', trend: 'up' as const };

const marketQuotes = [
  { symbol: '标普500', price: '7,126', change: '+1.20%', trend: 'up' as const, path: '/prediction' },
  { symbol: '沪深300', price: '3,892', change: '+0.83%', trend: 'up' as const, path: '/a-stock' },
  { symbol: '现货黄金', price: '$4,879', change: '+1.48%', trend: 'up' as const, path: '/macro' },
  { symbol: 'WTI原油', price: '$82.59', change: '-9.41%', trend: 'down' as const, path: '/macro' },
  { symbol: '比特币', price: '$75,951', change: '-1.86%', trend: 'down' as const, path: '/prediction' },
  { symbol: '道琼斯', price: '49,447', change: '+1.79%', trend: 'up' as const, path: '/prediction' },
  { symbol: '纳斯达克', price: '24,468', change: '+1.52%', trend: 'up' as const, path: '/prediction' },
  { symbol: '上证指数', price: '3,241', change: '+0.45%', trend: 'up' as const, path: '/a-stock' },
];

const newsItems = [
  { category: '美股', color: 'green' as const, title: '特斯拉Q1交付量超预期，股价+5.2%', path: '/news' },
  { category: '大宗', color: 'red' as const, title: '霍尔木兹局势紧张，原油-9.41%', path: '/news' },
  { category: '科技', color: 'blue' as const, title: '字节跳动发布Gauss 2.0，推理速度+40%', path: '/news' },
  { category: 'A股', color: 'yellow' as const, title: 'AI芯片板块爆发，多股涨停', path: '/news' },
  { category: '加密', color: 'purple' as const, title: 'BTC $75,951 (-1.86%)，恐慌缓解', path: '/prediction' },
];

const forexRates = [
  { pair: 'USD/CNY', rate: '6.8324', path: '/tools' },
  { pair: 'USD/EUR', rate: '0.8478', path: '/tools' },
  { pair: 'USD/JPY', rate: '158.62', path: '/tools' },
  { pair: 'USD/GBP', rate: '0.7918', path: '/tools' },
];

const quickNavItems = [
  { icon: '📊', title: 'A股行情', desc: '情绪仪表盘', path: '/a-stock', color: 'blue' },
  { icon: '📈', title: '宏观数据', desc: 'GDP/CPI/PMI', path: '/macro', color: 'green' },
  { icon: '🎯', title: '仓位管理', desc: '风险控制', path: '/position', color: 'yellow' },
  { icon: '🔮', title: '预测市场', desc: 'Polymarket', path: '/prediction', color: 'purple' },
];

function QuoteCard({ quote, index, onClick }: { quote: typeof marketQuotes[0]; index: number; onClick?: () => void }) {
  const isUp = quote.trend === 'up';
  return (
    <button
      onClick={onClick}
      className="bg-surface-100/50 rounded-xl p-3 border border-white/5 hover:bg-surface-200 hover:border-white/10 transition-all duration-200 animate-fade-in-up text-left btn-press w-full"
      style={{ animationDelay: `${200 + index * 50}ms` }}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] font-display font-medium text-gray-500 uppercase tracking-wider">{quote.symbol}</span>
        <span className={`text-[10px] font-mono ${isUp ? 'text-accent-green' : 'text-accent-red'}`}>
          {isUp ? '▲' : '▼'}
        </span>
      </div>
      <div className="text-base font-display font-bold text-white font-mono">{quote.price}</div>
      <div className={`text-xs font-mono ${isUp ? 'text-accent-green' : 'text-accent-red'}`}>
        {quote.change}
      </div>
    </button>
  );
}

export function DashboardHome() {
  const navigate = useNavigate();
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      {/* Metric Detail Modal */}
      {selectedMetric && (
        <MetricModal metricKey={selectedMetric} onClose={() => setSelectedMetric(null)} />
      )}

      {/* Market Overview - Hero Section */}
      <div
        className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-surface-100 via-surface to-surface-100 p-4 border border-white/5 cursor-pointer"
        onClick={() => setSelectedMetric('sentiment')}
      >
        <div className="absolute inset-0 bg-gradient-to-br from-accent-green/5 via-transparent to-accent-blue/5" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
            <span className="text-xs font-display text-gray-500 uppercase tracking-wider">市场状态</span>
            <span className="text-xs text-gray-600">（点击了解详情）</span>
          </div>
          <div className="text-2xl font-display font-bold text-white mb-1">
            早上好
          </div>
          <div className="text-sm text-gray-400">
            A股市场处于 <span className="text-accent-green font-semibold">修复期</span>
          </div>
        </div>
      </div>

      {/* Quick Navigation */}
      <div className="grid grid-cols-4 gap-2 stagger-children">
        {quickNavItems.map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className={`
              bg-surface-100/50 rounded-xl p-3
              border border-white/5
              hover:bg-surface-200
              hover:border-white/10
              transition-all duration-200
              btn-press
              flex flex-col items-center text-center
            `}
          >
            <span className="text-xl mb-1">{item.icon}</span>
            <span className="text-xs font-display font-medium text-white">{item.title}</span>
            <span className="text-[10px] text-gray-500 mt-0.5">{item.desc}</span>
          </button>
        ))}
      </div>

      {/* Key Metrics - Clickable */}
      <div className="grid grid-cols-2 gap-3 stagger-children">
        <button
          onClick={() => setSelectedMetric('fearGreed')}
          className="text-left"
        >
          <MetricCard {...fearGreedData} icon="😰" animationDelay={0} />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
        <button
          onClick={() => setSelectedMetric('position')}
          className="text-left"
        >
          <MetricCard {...positionData} icon="📊" animationDelay={50} />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
        <button
          onClick={() => setSelectedMetric('northbound')}
          className="text-left"
        >
          <MetricCard {...northboundData} icon="🌊" animationDelay={100} />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
        <button
          onClick={() => setSelectedMetric('sentiment')}
          className="text-left"
        >
          <MetricCard {...sentimentData} icon="📈" animationDelay={150} />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
      </div>

      {/* Market Quotes */}
      <Card title="行情一览" animationDelay={200}>
        <div className="grid grid-cols-4 gap-2">
          {marketQuotes.slice(0, 4).map((q, i) => (
            <QuoteCard
              key={q.symbol}
              quote={q}
              index={i}
              onClick={() => navigate(q.path)}
            />
          ))}
        </div>
        <div className="grid grid-cols-4 gap-2 mt-2">
          {marketQuotes.slice(4).map((q, i) => (
            <QuoteCard
              key={q.symbol}
              quote={q}
              index={i + 4}
              onClick={() => navigate(q.path)}
            />
          ))}
        </div>
      </Card>

      {/* News Feed */}
      <Card title="今日资讯" animationDelay={300}>
        <div className="space-y-2">
          {newsItems.map((news, index) => (
            <button
              key={index}
              onClick={() => navigate(news.path)}
              className="w-full flex items-center gap-3 py-2.5 border-b border-white/5 last:border-0 animate-slide-in text-left"
              style={{ animationDelay: `${350 + index * 50}ms` }}
            >
              <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                news.color === 'green' ? 'bg-accent-green shadow-[0_0_8px_rgba(16,185,129,0.5)]' :
                news.color === 'red' ? 'bg-accent-red shadow-[0_0_8px_rgba(239,68,68,0.5)]' :
                news.color === 'blue' ? 'bg-accent-blue shadow-[0_0_8px_rgba(59,130,246,0.5)]' :
                news.color === 'yellow' ? 'bg-accent-yellow shadow-[0_0_8px_rgba(245,158,11,0.5)]' :
                'bg-accent-purple shadow-[0_0_8px_rgba(139,92,246,0.5)]'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">{news.title}</p>
              </div>
              <Badge text={news.category} variant={news.color} />
            </button>
          ))}
        </div>
      </Card>

      {/* Forex Rates */}
      <Card title="实时汇率" animationDelay={400}>
        <div className="grid grid-cols-4 gap-2">
          {forexRates.map((forex, index) => (
            <button
              key={forex.pair}
              onClick={() => navigate(forex.path)}
              className="bg-surface-100/30 rounded-xl py-2.5 px-1 text-center animate-fade-in-up btn-press hover:bg-surface-200 transition-colors"
              style={{ animationDelay: `${450 + index * 50}ms` }}
            >
              <div className="text-[10px] font-mono text-gray-500">{forex.pair}</div>
              <div className="text-sm font-mono font-medium text-white">{forex.rate}</div>
            </button>
          ))}
        </div>
      </Card>

      {/* Trading Signals */}
      <Card title="交易信号" variant="highlighted" animationDelay={500}>
        <div className="space-y-3">
          {/* Signal Strength */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">信号强度</span>
              <span className="text-accent-yellow font-mono">62%</span>
            </div>
            <div className="h-2 bg-surface-200 rounded-full overflow-hidden">
              <div className="h-full w-[62%] bg-gradient-to-r from-accent-green via-accent-yellow to-accent-green rounded-full" />
            </div>
          </div>

          {/* Bullish/Bearish */}
          <div className="grid grid-cols-2 gap-2 pt-2">
            <button
              onClick={() => navigate('/a-stock')}
              className="bg-accent-green/10 rounded-xl p-3 border border-accent-green/20 hover:bg-accent-green/20 transition-colors btn-press text-left"
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-accent-green">✓</span>
                <span className="text-xs font-medium text-accent-green">利好因素</span>
              </div>
              <ul className="text-[10px] text-gray-400 space-y-0.5">
                <li>• 美股反弹动能持续</li>
                <li>• 北向资金净买入</li>
                <li>• AI政策持续加码</li>
              </ul>
            </button>
            <button
              onClick={() => navigate('/macro')}
              className="bg-accent-red/10 rounded-xl p-3 border border-accent-red/20 hover:bg-accent-red/20 transition-colors btn-press text-left"
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-accent-red">!</span>
                <span className="text-xs font-medium text-accent-red">风险提示</span>
              </div>
              <ul className="text-[10px] text-gray-400 space-y-0.5">
                <li>• 成交量有所萎缩</li>
                <li>• 人民币汇率承压</li>
                <li>• 外部地缘风险</li>
              </ul>
            </button>
          </div>

          {/* Position Suggestion */}
          <button
            onClick={() => setSelectedMetric('position')}
            className="w-full bg-surface-200/50 rounded-xl p-3 border border-white/5 hover:bg-surface-200 transition-colors btn-press text-left"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">仓位建议</span>
              <Badge text="40-60%" variant="yellow" />
            </div>
            <div className="text-sm text-white mt-1">
              轻仓试错，不追涨杀跌
            </div>
            <div className="text-[10px] text-gray-600 mt-1">点击查看详细计算方法 →</div>
          </button>
        </div>
      </Card>
    </div>
  );
}
