import { useState, useEffect } from 'react';
import { Card, Badge } from '../components';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { fetchFearGreedIndex, fetchNorthboundData, fetchLimitUpDown, fetchMultipleQuotes } from '../services/api/marketData';
import { fetchAllMacroData } from '../services/api/macroData';

// 标签页数据
const tabs = [
  { id: 'market', label: '市场', icon: '📊' },
  { id: 'macro', label: '宏观', icon: '📈' },
  { id: 'sentiment', label: '情绪', icon: '😰' },
];

// 模拟宏观数据（待接入国家统计局API）
const mockMacroIndicators = [
  { name: 'GDP增速', value: '5.0%', status: '稳定', variant: 'green' as const },
  { name: 'CPI', value: '+1.1%', status: '温和', variant: 'blue' as const },
  { name: 'PMI', value: '49.2', status: '荣枯线下', variant: 'yellow' as const },
  { name: 'LPR(1年)', value: '3.45%', status: '不变', variant: 'gray' as const },
];

// 模拟GDP趋势数据
const mockGdpTrend = [
  { year: '2023', value: 5.2 },
  { year: '2024', value: 5.0 },
  { year: '2025-Q1', value: 5.4 },
  { year: '2025-Q2', value: 5.3 },
];

// 模拟CPI趋势数据
const mockCpiTrend = [
  { month: '1月', value: 0.5 },
  { month: '2月', value: 0.7 },
  { month: '3月', value: 1.2 },
  { month: '4月', value: 1.1 },
];

export function DataPage() {
  const [activeTab, setActiveTab] = useState('market');

  // 市场数据状态
  const [marketData, setMarketData] = useState({
    indices: [
      { name: '上证指数', code: '000001', price: 3245.67, changePercent: -0.03 },
      { name: '深证成指', code: '399001', price: 10245.23, changePercent: 0.45 },
      { name: '创业板指', code: '399006', price: 2089.45, changePercent: -0.59 },
      { name: '沪深300', code: '000300', price: 3856.78, changePercent: 0.61 },
    ],
    northboundTrend: [
      { day: '周一', value: 35 },
      { day: '周二', value: 42 },
      { day: '周三', value: 38 },
      { day: '周四', value: 55 },
      { day: '周五', value: 67 },
    ],
  });

  // 情绪数据状态
  const [sentimentData, setSentimentData] = useState<{
    fearGreed: number;
    phase: string;
    signals: Array<{
      label: string;
      value: number | string;
      status: string;
      variant: 'yellow' | 'green' | 'red' | 'blue' | 'gray';
    }>;
  }>({
    fearGreed: 26,
    phase: '极度恐惧',
    signals: [
      { label: '涨停数量', value: 47, status: '偏冰点', variant: 'yellow' },
      { label: '跌停数量', value: 8, status: '正常', variant: 'green' },
      { label: '北向资金', value: '+23亿', status: '净买入', variant: 'green' },
      { label: '两融余额', value: '1.58万亿', status: '下降', variant: 'yellow' },
    ],
  });

  // 宏观数据状态
  const [macroData, setMacroData] = useState({
    indicators: mockMacroIndicators,
    gdp: mockGdpTrend,
    cpi: mockCpiTrend,
  });

  // 加载数据
  useEffect(() => {
    const loadData = async () => {
      try {
        // 并行加载市场、情绪、宏观数据
        const [quotes, fearGreed, northbound, limitUp, macro] = await Promise.all([
          fetchMultipleQuotes(['000001', '399001', '399006', '000300']),
          fetchFearGreedIndex(),
          fetchNorthboundData(5),
          fetchLimitUpDown(),
          fetchAllMacroData(),
        ]);

        // 更新市场指数
        if (quotes.length > 0) {
          setMarketData(prev => ({
            ...prev,
            indices: quotes.map(q => ({
              name: q.name,
              code: q.code,
              price: q.price,
              changePercent: q.changePercent,
            })),
          }));
        }

        // 更新恐惧贪婪
        setSentimentData(prev => ({
          ...prev,
          fearGreed: fearGreed.value,
          phase: fearGreed.phase,
        }));

        // 更新北向趋势
        if (northbound.length > 0) {
          setMarketData(prev => ({
            ...prev,
            northboundTrend: northbound.slice(0, 5).map((n, i) => ({
              day: ['周一', '周二', '周三', '周四', '周五'][i] || `Day${i + 1}`,
              value: n.total,
            })),
          }));
        }

        // 更新涨跌停
        setSentimentData(prev => ({
          ...prev,
          signals: [
            { label: '涨停数量', value: limitUp.limitUp, status: limitUp.limitUp < 30 ? '偏冰点' : limitUp.limitUp > 60 ? '偏亢奋' : '正常', variant: 'yellow' as const },
            { label: '跌停数量', value: limitUp.limitDown, status: '正常', variant: 'green' as const },
            { label: '北向资金', value: `${northbound[0]?.total >= 0 ? '+' : ''}${(northbound[0]?.total || 0).toFixed(0)}亿`, status: (northbound[0]?.total || 0) >= 0 ? '净买入' : '净卖出', variant: (northbound[0]?.total || 0) >= 0 ? 'green' : 'red' as 'green' | 'red' },
            { label: '两融余额', value: '1.58万亿', status: '下降', variant: 'yellow' as const },
          ],
        }));

        // 更新宏观指标
        setMacroData(prev => ({
          ...prev,
          indicators: [
            { name: 'GDP增速', value: `${macro.gdp.toFixed(1)}%`, status: macro.gdp >= 5 ? '稳定' : '放缓', variant: macro.gdp >= 5 ? 'green' as const : 'yellow' as const },
            { name: 'CPI', value: `${macro.cpi >= 0 ? '+' : ''}${macro.cpi.toFixed(1)}%`, status: macro.cpi < 2 ? '温和' : '偏高', variant: macro.cpi < 2 ? 'blue' as const : 'yellow' as const },
            { name: 'PMI', value: macro.pmi.toFixed(1), status: macro.pmi >= 50 ? '荣枯线上' : '荣枯线下', variant: macro.pmi >= 50 ? 'green' as const : 'yellow' as const },
            { name: 'LPR(1年)', value: `${macro.lpr1y.toFixed(2)}%`, status: '不变', variant: 'gray' as const },
          ],
        }));
      } catch (error) {
        console.error('加载数据失败:', error);
      }
    };

    loadData();
  }, []);

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

      {/* 市场数据 (zixun + a-stock-premarket-briefing skills) */}
      {activeTab === 'market' && (
        <div className="space-y-4">
          {/* 主要指数 */}
          <Card title="A股主要指数">
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

          {/* 北向资金趋势 (a-stock-premarket-briefing skill) */}
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

          {/* 涨跌停统计 */}
          <Card title="涨跌停统计 (a-stock-premarket-briefing)">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-accent-green/10 rounded-xl">
                <div className="text-3xl font-bold text-accent-green font-mono">
                  {sentimentData.signals[0]?.value || 47}
                </div>
                <div className="text-sm text-gray-400">涨停家数</div>
              </div>
              <div className="text-center p-4 bg-accent-red/10 rounded-xl">
                <div className="text-3xl font-bold text-accent-red font-mono">
                  {sentimentData.signals[1]?.value || 8}
                </div>
                <div className="text-sm text-gray-400">跌停家数</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* 宏观数据 (macro-analyst skill) */}
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

          {/* 汇率信息 (juhe-exchange-rate skill - 待接入) */}
          <Card title="人民币汇率 (juhe-exchange-rate)">
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center p-3 bg-gray-700/50 rounded-xl">
                <div className="text-xs text-gray-400 mb-1">USD/CNY</div>
                <div className="text-lg font-bold text-white font-mono">7.24</div>
              </div>
              <div className="text-center p-3 bg-gray-700/50 rounded-xl">
                <div className="text-xs text-gray-400 mb-1">EUR/CNY</div>
                <div className="text-lg font-bold text-white font-mono">7.85</div>
              </div>
              <div className="text-center p-3 bg-gray-700/50 rounded-xl">
                <div className="text-xs text-gray-400 mb-1">100JPY/CNY</div>
                <div className="text-lg font-bold text-white font-mono">4.82</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* 情绪数据 (market-sentiment + a-stock-market-sentiment skills) */}
      {activeTab === 'sentiment' && (
        <div className="space-y-4">
          {/* 恐惧贪婪指数 (market-sentiment skill) */}
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

          {/* A股情绪阶段 (a-stock-market-sentiment skill) */}
          <Card title="A股情绪阶段 (a-stock-market-sentiment)">
            <div className="text-center mb-4">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-accent-green/20 rounded-full">
                <span className="text-xl">❄️</span>
                <span className="text-lg font-bold text-accent-green">冰点/修复阶段</span>
              </div>
              <p className="text-sm text-gray-400 mt-2">
                市场情绪处于低位，可能是布局机会
              </p>
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
