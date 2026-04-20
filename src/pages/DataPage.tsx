import { useState } from 'react';
import { Card, Badge } from '../components';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

// 标签页数据
const tabs = [
  { id: 'market', label: '市场', icon: '📊' },
  { id: 'macro', label: '宏观', icon: '📈' },
  { id: 'sentiment', label: '情绪', icon: '😰' },
];

// 市场数据
const marketData = {
  indices: [
    { name: '上证指数', code: '000001', price: 3245.67, change: -0.82, changePercent: -0.03 },
    { name: '深证成指', code: '399001', price: 10245.23, change: 45.67, changePercent: 0.45 },
    { name: '创业板指', code: '399006', price: 2089.45, change: -12.34, changePercent: -0.59 },
    { name: '沪深300', code: '000300', price: 3856.78, change: 23.45, changePercent: 0.61 },
  ],
  northboundTrend: [
    { day: '周一', value: 35 },
    { day: '周二', value: 42 },
    { day: '周三', value: 38 },
    { day: '周四', value: 55 },
    { day: '周五', value: 67 },
  ],
};

// 宏观数据
const macroData = {
  gdp: [
    { year: '2023', value: 5.2 },
    { year: '2024', value: 5.0 },
    { year: '2025-Q1', value: 5.4 },
    { year: '2025-Q2', value: 5.3 },
  ],
  cpi: [
    { month: '1月', value: 0.5 },
    { month: '2月', value: 0.7 },
    { month: '3月', value: 1.2 },
    { month: '4月', value: 1.1 },
  ],
  indicators: [
    { name: 'GDP增速', value: '5.0%', status: '稳定', variant: 'green' as const },
    { name: 'CPI', value: '+1.1%', status: '温和', variant: 'blue' as const },
    { name: 'PMI', value: '49.2', status: '荣枯线下', variant: 'yellow' as const },
    { name: 'LPR(1年)', value: '3.45%', status: '不变', variant: 'gray' as const },
  ],
};

// 情绪数据
const sentimentData = {
  fearGreed: 26,
  signals: [
    { label: '涨停数量', value: 47, status: '偏冰点', variant: 'yellow' as const },
    { label: '跌停数量', value: 8, status: '正常', variant: 'green' as const },
    { label: '北向资金', value: '+23亿', status: '净买入', variant: 'green' as const },
    { label: '两融余额', value: '1.58万亿', status: '下降', variant: 'yellow' as const },
  ],
  phase: '极度恐惧',
};

export function DataPage() {
  const [activeTab, setActiveTab] = useState('market');

  return (
    <div className="space-y-4 animate-fade-in-up pt-4">
      {/* 标题 */}
      <div className="text-center">
        <h1 className="text-2xl font-display font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
          数据中心
        </h1>
      </div>

      {/* 标签切换 */}
      <div className="flex gap-2 p-1 bg-surface-200/30 rounded-xl">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg
              transition-all duration-200 btn-press
              ${activeTab === tab.id
                ? 'bg-accent-blue/20 text-accent-blue border border-accent-blue/30'
                : 'text-gray-400 hover:text-white'
              }
            `}
          >
            <span>{tab.icon}</span>
            <span className="text-sm font-medium">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* 市场数据 */}
      {activeTab === 'market' && (
        <div className="space-y-4">
          {/* 主要指数 */}
          <Card title="主要指数">
            <div className="space-y-2">
              {marketData.indices.map((index) => (
                <div
                  key={index.code}
                  className="flex justify-between items-center py-2 border-b border-white/5 last:border-0"
                >
                  <div>
                    <div className="text-white font-medium">{index.name}</div>
                    <div className="text-xs text-gray-500">{index.code}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-white font-mono">{index.price.toFixed(2)}</div>
                    <Badge
                      text={`${index.changePercent > 0 ? '+' : ''}${index.changePercent.toFixed(2)}%`}
                      variant={index.changePercent > 0 ? 'green' : 'red'}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* 北向资金趋势 */}
          <Card title="北向资金趋势（近5日）">
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={marketData.northboundTrend}>
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
          </Card>
        </div>
      )}

      {/* 宏观数据 */}
      {activeTab === 'macro' && (
        <div className="space-y-4">
          {/* 核心指标 */}
          <Card title="核心宏观指标">
            <div className="grid grid-cols-2 gap-3">
              {macroData.indicators.map((ind) => (
                <div key={ind.name} className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-gray-400 text-xs mb-1">{ind.name}</div>
                  <div className="text-xl font-bold text-white font-mono">{ind.value}</div>
                  <Badge text={ind.status} variant={ind.variant} />
                </div>
              ))}
            </div>
          </Card>

          {/* GDP趋势 */}
          <Card title="GDP增速趋势">
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={macroData.gdp}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="year" stroke="#9CA3AF" fontSize={12} />
                  <YAxis stroke="#9CA3AF" fontSize={12} domain={[4, 6]} />
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
          </Card>

          {/* CPI趋势 */}
          <Card title="CPI消费者物价指数">
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={macroData.cpi}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} />
                  <YAxis stroke="#9CA3AF" fontSize={12} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
                    labelStyle={{ color: '#9CA3AF' }}
                  />
                  <Bar dataKey="value" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      )}

      {/* 情绪数据 */}
      {activeTab === 'sentiment' && (
        <div className="space-y-4">
          {/* 恐惧贪婪指数 */}
          <Card>
            <div className="text-center mb-4">
              <div className="text-gray-400 text-sm mb-1">恐惧贪婪指数</div>
              <div className="text-4xl font-bold text-accent-yellow font-mono">
                {sentimentData.fearGreed}
              </div>
              <Badge text={sentimentData.phase} variant="yellow" />
            </div>
            <div className="relative py-4">
              <div className="h-3 bg-gradient-to-r from-blue-500 via-green-500 via-yellow-500 to-red-500 rounded-full relative">
                <div className="absolute top-6 left-0 text-xs text-gray-400">冰点</div>
                <div className="absolute top-6 left-1/4 text-xs text-gray-400 -translate-x-1/2">修复</div>
                <div className="absolute top-6 left-1/2 text-xs text-gray-400 -translate-x-1/2">分歧</div>
                <div className="absolute top-6 right-0 text-xs text-gray-400">亢奋</div>
                <div
                  className="absolute -top-1 w-4 h-5 bg-white rounded-full shadow-lg transform -translate-x-1/2"
                  style={{ left: `${sentimentData.fearGreed}%` }}
                />
              </div>
            </div>
          </Card>

          {/* 量化信号 */}
          <Card title="量化信号面板">
            <div className="grid grid-cols-2 gap-3">
              {sentimentData.signals.map((signal) => (
                <div key={signal.label} className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-gray-400 text-xs mb-1">{signal.label}</div>
                  <div className="text-xl font-bold text-white font-mono">{signal.value}</div>
                  <Badge text={signal.status} variant={signal.variant} />
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
