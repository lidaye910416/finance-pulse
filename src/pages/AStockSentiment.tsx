import { useState } from 'react';
import { Card, Badge } from '../components';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { metricExplanations, MetricExplanationKeys } from './DashboardHome';

const fearGreedValue = 26;

const quantSignals = [
  { label: '涨停数量', value: 47, status: '偏冰点', variant: 'yellow' as const },
  { label: '跌停数量', value: 8, status: '正常', variant: 'green' as const },
  { label: '成交额', value: '7,821亿', status: '萎缩', variant: 'yellow' as const },
  { label: '北向资金', value: '+23亿', status: '净买入', variant: 'green' as const },
];

const northboundTrend = [
  { day: '周一', value: 35 },
  { day: '周二', value: 42 },
  { day: '周三', value: 38 },
  { day: '周四', value: 55 },
  { day: '周五', value: 67 },
  { day: '周六', value: 72 },
  { day: '周日', value: 80 },
];

const sectorFlow = [
  { name: 'AI算力', flow: '+28亿', trend: 'up' as const },
  { name: '半导体设备', flow: '+15亿', trend: 'up' as const },
  { name: '房地产', flow: '-8亿', trend: 'down' as const },
  { name: '银行', flow: '-3亿', trend: 'down' as const },
];

const premarketNews = [
  '国家发布AI芯片补贴政策，规模百亿级（中长期利好）',
  '宁德时代辟谣：暂未与特斯拉合作建厂',
  '东方财富：北向资金连续3日净买入',
];

export function AStockSentiment() {
  const [showModal, setShowModal] = useState(false);
  const [activeMetric, setActiveMetric] = useState<MetricExplanationKeys | ''>('');

  const openMetricModal = (metricKey: MetricExplanationKeys) => {
    setActiveMetric(metricKey);
    setShowModal(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">📊 A股市场情绪</h2>
        <button className="text-finance-blue text-sm hover:underline">[刷新]</button>
      </div>

      {/* Sentiment Gauge - Clickable */}
      <Card
        className="cursor-pointer hover:border-finance-blue/50 transition-colors"
        onClick={() => openMetricModal('fearGreed')}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">恐惧贪婪指数</span>
          <span className="text-xs text-finance-blue">点击查看计算方法 →</span>
        </div>
        <div className="relative py-4">
          {/* Phase bar */}
          <div className="h-3 bg-gradient-to-r from-blue-500 via-green-500 via-yellow-500 to-red-500 rounded-full relative">
            {/* Phase markers */}
            <div className="absolute top-6 left-0 text-xs text-gray-400">冰点</div>
            <div className="absolute top-6 left-1/4 text-xs text-gray-400 -translate-x-1/2">修复</div>
            <div className="absolute top-6 left-1/2 text-xs text-gray-400 -translate-x-1/2">分歧</div>
            <div className="absolute top-6 right-0 text-xs text-gray-400">亢奋</div>

            {/* Current position indicator */}
            <div
              className="absolute -top-1 w-4 h-5 bg-white rounded-full shadow-lg transform -translate-x-1/2"
              style={{ left: `${Math.min(fearGreedValue / 100 * 100, 95)}%` }}
            >
              <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-center">
                <span className="text-2xl">😰</span>
                <div className="text-white text-sm font-bold">{fearGreedValue}</div>
              </div>
            </div>
          </div>
        </div>
        <div className="text-center mt-8 text-gray-400 text-sm">
          当前: <span className="text-white font-semibold">极度恐惧</span> ({fearGreedValue})
        </div>
      </Card>

      {/* Quant Signals */}
      <Card title="量化信号面板">
        <div className="grid grid-cols-2 gap-3">
          {quantSignals.map((signal) => (
            <div key={signal.label} className="bg-gray-700 rounded-lg p-3">
              <div className="text-gray-400 text-xs mb-1">{signal.label}</div>
              <div className="text-white font-semibold text-lg">{signal.value}</div>
              <Badge text={signal.status} variant={signal.variant} />
            </div>
          ))}
        </div>
      </Card>

      {/* Northbound Capital Trend */}
      <Card title="北向资金趋势（近7日）">
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={northboundTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="day" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#10B981"
                strokeWidth={2}
                dot={{ fill: '#10B981' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-2">
          <div className="bg-gray-700 rounded-full h-3 overflow-hidden">
            <div className="bg-finance-green h-full rounded-full" style={{ width: '60%' }}></div>
          </div>
          <div className="text-sm text-gray-400 mt-1">7日累计净买入 ¥127亿</div>
        </div>
      </Card>

      {/* Margin Balance */}
      <Card>
        <div className="text-gray-400 text-sm">融资融券余额</div>
        <div className="text-2xl font-bold text-white">1.58万亿</div>
        <div className="text-sm text-gray-400">较昨日 -12亿</div>
      </Card>

      {/* Sector Fund Flow */}
      <Card title="板块资金流向">
        <div className="grid grid-cols-2 gap-3">
          {sectorFlow.map((sector) => (
            <div key={sector.name} className="flex justify-between items-center bg-gray-700 rounded-lg p-3">
              <span className="text-white">{sector.name}</span>
              <span className={sector.trend === 'up' ? 'text-finance-green' : 'text-finance-red'}>
                {sector.flow}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Premarket News */}
      <Card title="盘前新闻摘要">
        <ul className="space-y-2">
          {premarketNews.map((news, index) => (
            <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
              <span className="text-finance-green">•</span>
              {news}
            </li>
          ))}
        </ul>
      </Card>

      {/* Metric Explanation Modal */}
      {showModal && !!activeMetric && metricExplanations[activeMetric] && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-end justify-center z-50" onClick={() => setShowModal(false)}>
          <div
            className="bg-gray-800 rounded-t-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-gray-800 border-b border-gray-700 p-4 flex justify-between items-center">
              <h3 className="text-lg font-bold text-white">{metricExplanations[activeMetric as MetricExplanationKeys].title}</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white">✕</button>
            </div>
            <div className="p-4 space-y-4">
              <div className="text-center p-4 bg-gray-700/50 rounded-xl">
                <div className="text-3xl font-bold text-white font-mono">
                  {metricExplanations[activeMetric as MetricExplanationKeys].currentValue}
                </div>
                <Badge text={metricExplanations[activeMetric as MetricExplanationKeys].phase} variant={activeMetric === 'fearGreed' ? 'yellow' : 'green'} />
              </div>

              <div>
                <h4 className="text-finance-blue font-semibold mb-2 flex items-center gap-2">
                  <span>📐</span> 计算方法
                </h4>
                <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300 whitespace-pre-line">
                  {metricExplanations[activeMetric as MetricExplanationKeys].calculation}
                </div>
              </div>

              <div>
                <h4 className="text-finance-green font-semibold mb-2 flex items-center gap-2">
                  <span>📖</span> 解读指南
                </h4>
                <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300 whitespace-pre-line">
                  {metricExplanations[activeMetric as MetricExplanationKeys].interpretation}
                </div>
              </div>

              <div className="bg-finance-yellow/10 border border-finance-yellow/30 rounded-xl p-4">
                <h4 className="text-finance-yellow font-semibold mb-2 flex items-center gap-2">
                  <span>💡</span> 投资建议
                </h4>
                <p className="text-sm text-gray-300">{metricExplanations[activeMetric as MetricExplanationKeys].suggestion}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
