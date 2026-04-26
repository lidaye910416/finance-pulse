import { useState, useEffect } from 'react';
import { MetricCard, Card, Badge } from '../components';
import { useNavigate } from 'react-router-dom';
import { fetchFearGreedIndex, fetchLimitUpDown } from '../services/api/marketData';

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
        <div className="absolute top-3 left-1/2 -translate-x-1/2 w-10 h-1 bg-gray-600 rounded-full" />
        <div className="flex items-center justify-between mb-4 mt-2">
          <h2 className="text-lg font-display font-bold text-white">{data.title}</h2>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:text-white"
          >
            ✕
          </button>
        </div>
        <div className="bg-gradient-to-r from-accent-blue/20 to-accent-green/20 rounded-xl p-4 mb-4 border border-accent-blue/20">
          <div className="text-xs text-gray-400 mb-1">当前值</div>
          <div className="text-2xl font-display font-bold text-white">{data.currentValue}</div>
          <div className="text-sm text-accent-green mt-1">{data.phase}</div>
        </div>
        <div className="mb-4">
          <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            <span className="w-5 h-5 rounded bg-accent-blue/20 text-accent-blue text-xs flex items-center justify-center">📐</span>
            计算方法
          </h3>
          <div className="bg-surface-200/50 rounded-xl p-4 text-sm text-gray-300 whitespace-pre-line font-mono leading-relaxed">
            {data.calculation}
          </div>
        </div>
        <div className="mb-4">
          <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
            <span className="w-5 h-5 rounded bg-accent-green/20 text-accent-green text-xs flex items-center justify-center">📊</span>
            解读指南
          </h3>
          <div className="bg-surface-200/50 rounded-xl p-4 text-sm text-gray-300 whitespace-pre-line leading-relaxed">
            {data.interpretation}
          </div>
        </div>
        <div className="bg-accent-yellow/10 rounded-xl p-4 border border-accent-yellow/20">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-accent-yellow">💡</span>
            <span className="text-sm font-display font-semibold text-accent-yellow">投资建议</span>
          </div>
          <p className="text-sm text-gray-300">{data.suggestion}</p>
        </div>
        <div className="mt-4 pt-4 border-t border-white/10">
          <p className="text-xs text-gray-500 text-center">
            点击查看更多详细分析 → A股情绪 / 仓位管理 页面
          </p>
        </div>
      </div>
    </div>
  );
}

// 动态获取的市场数据
function useMarketData() {
  const [fearGreed, setFearGreed] = useState({ value: 26, phase: '极度恐惧' });
  const [limitUpDown, setLimitUpDown] = useState({ limitUp: 47, limitDown: 8 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [fg, lud] = await Promise.all([
          fetchFearGreedIndex(),
          fetchLimitUpDown(),
        ]);
        setFearGreed(fg);
        setLimitUpDown(lud);
      } catch (e) {
        console.error('加载市场数据失败:', e);
      } finally {
        setLoading(false);
      }
    };
    loadData();
    // 每30秒刷新一次
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  return { fearGreed, limitUpDown, loading };
}

// 根据恐惧贪婪获取颜色
function getFearGreedColor(value: number): string {
  if (value <= 25) return 'red';
  if (value <= 45) return 'orange';
  if (value <= 55) return 'yellow';
  if (value <= 75) return 'blue';
  return 'green';
}

export function DashboardHome() {
  const navigate = useNavigate();
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);
  const { fearGreed, limitUpDown, loading } = useMarketData();

  // 动态计算仓位建议
  const getPositionAdvice = () => {
    if (fearGreed.value <= 30) return { value: '20-40%', phase: '冰点期', subValue: '极低仓位' };
    if (fearGreed.value <= 45) return { value: '30-50%', phase: '恐惧', subValue: '轻仓试错' };
    if (fearGreed.value <= 55) return { value: '40-60%', phase: '中性', subValue: '适中仓位' };
    if (fearGreed.value <= 75) return { value: '60-80%', phase: '贪婪', subValue: '较高仓位' };
    return { value: '80-100%', phase: '极度贪婪', subValue: '满仓' };
  };

  const positionAdvice = getPositionAdvice();

  // 动态情绪数据
  const sentimentPhase = fearGreed.value <= 30 ? '冰点' : 
                         fearGreed.value <= 45 ? '修复' : 
                         fearGreed.value <= 55 ? '分歧' : '亢奋';

  // 动态涨跌停状态
  const limitStatus = limitUpDown.limitUp < 30 ? '偏冰点' : 
                      limitUpDown.limitUp > 100 ? '偏亢奋' : '正常';

  return (
    <div className="space-y-4">
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
            <span className="text-xs font-display text-gray-500 uppercase tracking-wider">
              {loading ? '加载中...' : '实时数据'}
            </span>
          </div>
          <div className="text-2xl font-display font-bold text-white mb-1">
            早上好
          </div>
          <div className="text-sm text-gray-400">
            A股市场处于 <span className={`font-semibold ${
              sentimentPhase === '冰点' ? 'text-accent-blue' :
              sentimentPhase === '修复' ? 'text-accent-green' :
              sentimentPhase === '分歧' ? 'text-accent-yellow' : 'text-accent-red'
            }`}>{sentimentPhase}</span>
            {limitUpDown.limitUp < 50 && <span className="text-gray-500 ml-2">（涨停偏少，情绪低迷）</span>}
          </div>
        </div>
      </div>

      {/* Quick Navigation */}
      <div className="grid grid-cols-4 gap-2 stagger-children">
        {[
          { icon: '📊', title: 'A股行情', desc: '情绪仪表盘', path: '/a-stock' },
          { icon: '📈', title: '宏观数据', desc: 'GDP/CPI/PMI', path: '/macro' },
          { icon: '🎯', title: '仓位管理', desc: '风险控制', path: '/position' },
          { icon: '🔮', title: '预测市场', desc: 'Polymarket', path: '/prediction' },
        ].map((item) => (
          <button
            key={item.path}
            onClick={() => navigate(item.path)}
            className="bg-surface-100/50 rounded-xl p-3 border border-white/5 hover:bg-surface-200 hover:border-white/10 transition-all duration-200 btn-press flex flex-col items-center text-center"
          >
            <span className="text-xl mb-1">{item.icon}</span>
            <span className="text-xs font-display font-medium text-white">{item.title}</span>
            <span className="text-[10px] text-gray-500 mt-0.5">{item.desc}</span>
          </button>
        ))}
      </div>

      {/* Key Metrics - 动态数据 */}
      <div className="grid grid-cols-2 gap-3 stagger-children">
        <button onClick={() => setSelectedMetric('fearGreed')} className="text-left">
          <MetricCard 
            icon="😰" 
            label="恐惧贪婪" 
            value={loading ? '...' : fearGreed.value.toString()}
            subValue={loading ? '加载中' : fearGreed.phase}
            trend="neutral"
            animationDelay={0}
          />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
        <button onClick={() => setSelectedMetric('position')} className="text-left">
          <MetricCard 
            icon="📊" 
            label="仓位建议" 
            value={loading ? '...' : positionAdvice.value}
            subValue={loading ? '加载中' : positionAdvice.phase}
            trend={fearGreed.value <= 45 ? 'up' : 'down'}
            animationDelay={50}
          />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
        <button onClick={() => setSelectedMetric('northbound')} className="text-left">
          <MetricCard 
            icon="🌊" 
            label="涨停数量" 
            value={loading ? '...' : limitUpDown.limitUp.toString()}
            subValue={loading ? '加载中' : limitStatus}
            trend={limitUpDown.limitUp >= 60 ? 'up' : 'down'}
            animationDelay={100}
          />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
        <button onClick={() => setSelectedMetric('sentiment')} className="text-left">
          <MetricCard 
            icon="📈" 
            label="市场情绪" 
            value={loading ? '...' : sentimentPhase}
            subValue={loading ? '加载中' : `涨跌停 ${limitUpDown.limitUp}/${limitUpDown.limitDown}`}
            trend={sentimentPhase === '修复' || sentimentPhase === '分歧' ? 'up' : 'down'}
            animationDelay={150}
          />
          <div className="text-[10px] text-gray-600 mt-1 text-center">点击了解计算方法 →</div>
        </button>
      </div>

      {/* Market Status Info */}
      <Card title="市场状态" animationDelay={200}>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-accent-blue/10 rounded-xl">
            <div className="text-2xl font-bold text-white font-mono">{loading ? '...' : fearGreed.value}</div>
            <div className="text-xs text-gray-400">恐惧贪婪</div>
            <Badge text={loading ? '加载中' : fearGreed.phase} variant={getFearGreedColor(fearGreed.value) as any} />
          </div>
          <div className="text-center p-3 bg-accent-green/10 rounded-xl">
            <div className="text-2xl font-bold text-accent-green font-mono">{loading ? '...' : limitUpDown.limitUp}</div>
            <div className="text-xs text-gray-400">涨停家数</div>
            <Badge text={loading ? '加载中' : limitStatus} variant="yellow" />
          </div>
          <div className="text-center p-3 bg-accent-red/10 rounded-xl">
            <div className="text-2xl font-bold text-accent-red font-mono">{loading ? '...' : limitUpDown.limitDown}</div>
            <div className="text-xs text-gray-400">跌停家数</div>
            <Badge text="正常" variant="green" />
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card title="快捷功能" animationDelay={300}>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => navigate('/a-stock')}
            className="bg-surface-200/50 rounded-xl p-4 border border-white/5 hover:bg-surface-300 transition-all btn-press text-left"
          >
            <div className="text-lg mb-1">📊</div>
            <div className="text-sm font-medium text-white">A股情绪分析</div>
            <div className="text-xs text-gray-500">查看详细市场情绪数据</div>
          </button>
          <button
            onClick={() => navigate('/data')}
            className="bg-surface-200/50 rounded-xl p-4 border border-white/5 hover:bg-surface-300 transition-all btn-press text-left"
          >
            <div className="text-lg mb-1">📈</div>
            <div className="text-sm font-medium text-white">数据中心</div>
            <div className="text-xs text-gray-500">查看更多市场数据</div>
          </button>
        </div>
      </Card>

      {/* Last Update Time */}
      <div className="text-center text-xs text-gray-600">
        {loading ? '数据加载中...' : `数据更新时间: ${new Date().toLocaleTimeString('zh-CN')}`}
        <button onClick={() => window.location.reload()} className="ml-2 text-accent-blue hover:underline">
          刷新
        </button>
      </div>
    </div>
  );
}
