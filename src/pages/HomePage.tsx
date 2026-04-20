import { useNavigate } from 'react-router-dom';
import { Card, MetricCard, Badge } from '../components';
import { DataType, UpdateFrequency, getUpdateConfig } from '../services/data';

// 首页数据
const todaySummary = {
  fearGreed: { value: 26, label: '恐惧贪婪', trend: 'down' as const, dataType: DataType.FEAR_GREED },
  northbound: { value: '+23.5亿', label: '北向资金', trend: 'up' as const, dataType: DataType.NORTHBOUND },
  limitUp: { value: '47家', label: '涨停', trend: 'down' as const, dataType: DataType.LIMIT_UP_DOWN },
  marginBalance: { value: '1.58万亿', label: '两融余额', trend: 'down' as const, dataType: DataType.MARGIN_BALANCE },
};

// 数据更新时间映射
const getUpdateFrequencyLabel = (type: DataType): string => {
  const config = getUpdateConfig(type);
  if (!config) return '未知';

  switch (config.updateFrequency) {
    case UpdateFrequency.REALTIME:
      return '实时';
    case UpdateFrequency.MINUTE:
      return '分钟更新';
    case UpdateFrequency.HOURLY:
      return '小时更新';
    case UpdateFrequency.DAILY:
      return '日更';
    case UpdateFrequency.WEEKLY:
      return '周更';
    case UpdateFrequency.MONTHLY:
      return '月更';
    default:
      return '未知';
  }
};

const quickActions = [
  { id: 'analysis', icon: '🧠', label: 'AI分析', path: '/analysis', color: 'blue' },
  { id: 'data', icon: '📊', label: '市场数据', path: '/data', color: 'green' },
  { id: 'macro', icon: '📈', label: '宏观数据', path: '/data', color: 'yellow' },
  { id: 'position', icon: '🎯', label: '仓位管理', path: '/mine', color: 'purple' },
];

const alerts = [
  { type: 'warning', icon: '⚠️', text: '恐惧贪婪指数处于极度恐惧区间，关注布局机会' },
  { type: 'info', icon: '💡', text: '北向资金连续3日净买入，外资信心增强' },
];

const hotStocks = [
  { code: '600519', name: '贵州茅台', price: 1688.0, change: -1.2 },
  { code: '000858', name: '五粮液', price: 145.6, change: -0.9 },
  { code: '300750', name: '宁德时代', price: 186.5, change: 2.3 },
];

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* 标题 */}
      <div className="text-center pt-4">
        <h1 className="text-2xl font-display font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
          今日概览
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          {new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}
        </p>
      </div>

      {/* 数据更新状态栏 */}
      <Card className="border-accent-blue/20 bg-accent-blue/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-accent-green rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-300">数据已更新</span>
          </div>
          <div className="text-xs text-gray-500">
            恐惧贪婪 {getUpdateFrequencyLabel(DataType.FEAR_GREED)} · 北向资金 {getUpdateFrequencyLabel(DataType.NORTHBOUND)}
          </div>
        </div>
      </Card>

      {/* 预警提示 */}
      <div className="space-y-2">
        {alerts.map((alert, index) => (
          <Card
            key={index}
            className={`
              ${alert.type === 'warning' ? 'border-accent-yellow/30 bg-accent-yellow/5' : 'border-accent-blue/30 bg-accent-blue/5'}
              cursor-pointer hover:scale-[1.01] transition-transform
            `}
            onClick={() => navigate('/analysis')}
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">{alert.icon}</span>
              <span className="text-sm text-gray-300">{alert.text}</span>
            </div>
          </Card>
        ))}
      </div>

      {/* 核心指标 */}
      <div>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          核心指标
        </h2>
        <div className="grid grid-cols-2 gap-3">
          {Object.entries(todaySummary).map(([key, data]) => (
            <MetricCard
              key={key}
              label={data.label}
              value={data.value}
              trend={data.trend}
              icon={key === 'fearGreed' ? '😰' : key === 'northbound' ? '🌊' : key === 'limitUp' ? '📈' : '💰'}
              onClick={() => navigate('/data')}
            />
          ))}
        </div>
      </div>

      {/* 快捷操作 */}
      <div>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          快捷操作
        </h2>
        <div className="grid grid-cols-4 gap-2">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => navigate(action.path)}
              className={`
                flex flex-col items-center p-4 rounded-2xl
                bg-surface-200/50 border border-white/5
                hover:border-white/20 transition-all duration-200
                btn-press animate-fade-in-up
              `}
            >
              <span className="text-2xl mb-1">{action.icon}</span>
              <span className="text-xs text-gray-300">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 热门股票 */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            热门股票
          </h2>
          <button
            onClick={() => navigate('/data')}
            className="text-xs text-accent-blue hover:underline"
          >
            查看更多 →
          </button>
        </div>
        <Card>
          <div className="space-y-3">
            {hotStocks.map((stock) => (
              <div
                key={stock.code}
                className="flex justify-between items-center cursor-pointer hover:bg-surface-200/30 rounded-lg p-2 -mx-2 transition-colors"
                onClick={() => navigate('/analysis')}
              >
                <div>
                  <div className="text-white font-medium">{stock.name}</div>
                  <div className="text-xs text-gray-500">{stock.code}</div>
                </div>
                <div className="text-right">
                  <div className="text-white font-mono">¥{stock.price.toFixed(2)}</div>
                  <Badge
                    text={`${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)}%`}
                    variant={stock.change > 0 ? 'green' : 'red'}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* AI分析入口 */}
      <Card
        className="cursor-pointer hover:border-accent-blue/50 transition-all"
        onClick={() => navigate('/analysis')}
      >
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center shadow-glow-blue">
            <span className="text-3xl">🧠</span>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white">AI 智能分析</h3>
            <p className="text-sm text-gray-400">选择专业分析师，获取个性化投资建议</p>
          </div>
          <span className="text-accent-blue">→</span>
        </div>
      </Card>
    </div>
  );
}
