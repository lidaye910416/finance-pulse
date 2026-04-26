import { useState, useEffect } from 'react';
import { Card, Badge } from '../components';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { metricExplanations, MetricExplanationKeys } from './DashboardHome';
import { fetchFearGreedIndex, fetchLimitUpDown, fetchNorthboundData } from '../services/api/marketData';

function useSentimentData() {
  const [fearGreed, setFearGreed] = useState({ value: 26, phase: '极度恐惧' });
  const [limitUpDown, setLimitUpDown] = useState({ limitUp: 47, limitDown: 8 });
  const [northboundData, setNorthboundData] = useState<{date: string; total: number}[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [fg, lud, nb] = await Promise.all([
        fetchFearGreedIndex(),
        fetchLimitUpDown(),
        fetchNorthboundData(7),
      ]);
      if (fg) setFearGreed(fg);
      if (lud) setLimitUpDown(lud);
      if (nb.length > 0) setNorthboundData(nb);
    } catch (e) {
      console.error('加载数据失败:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  return { fearGreed, limitUpDown, northboundData, loading, refetch: loadData };
}

// 获取涨跌状态描述
function getLimitStatus(limitUp: number): string {
  if (limitUp < 30) return '偏冰点';
  if (limitUp < 60) return '正常';
  if (limitUp < 100) return '偏活跃';
  return '偏亢奋';
}

export function AStockSentiment() {
  const [showModal, setShowModal] = useState(false);
  const [activeMetric, setActiveMetric] = useState<MetricExplanationKeys | ''>('');
  const { fearGreed, limitUpDown, northboundData, loading, refetch } = useSentimentData();

  const openMetricModal = (metricKey: MetricExplanationKeys) => {
    setActiveMetric(metricKey);
    setShowModal(true);
  };

  // 准备图表数据 - 使用实际日期
  const chartData = northboundData.slice(-7).map((item) => ({
    date: item.date ? new Date(item.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) : '',
    value: item.total,
  }));

  // 计算7日累计
  const totalNorthbound = northboundData.slice(-7).reduce((sum, item) => sum + (item.total || 0), 0);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">📊 A股市场情绪</h2>
        <button 
          onClick={() => refetch()}
          className="text-accent-blue text-sm hover:underline"
        >
          {loading ? '加载中...' : '[刷新]'}
        </button>
      </div>

      {/* Sentiment Gauge - Clickable */}
      <Card
        className="cursor-pointer hover:border-accent-blue/50 transition-colors"
        onClick={() => openMetricModal('fearGreed')}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">恐惧贪婪指数</span>
          <span className="text-xs text-accent-blue">点击查看计算方法 →</span>
        </div>
        <div className="relative py-4">
          <div className="h-3 bg-gradient-to-r from-blue-500 via-green-500 via-yellow-500 to-red-500 rounded-full relative">
            <div className="absolute top-6 left-0 text-xs text-gray-400">冰点</div>
            <div className="absolute top-6 left-1/4 text-xs text-gray-400 -translate-x-1/2">修复</div>
            <div className="absolute top-6 left-1/2 text-xs text-gray-400 -translate-x-1/2">分歧</div>
            <div className="absolute top-6 right-0 text-xs text-gray-400">亢奋</div>
            <div
              className="absolute -top-1 w-4 h-5 bg-white rounded-full shadow-lg transform -translate-x-1/2"
              style={{ left: `${Math.min(fearGreed.value, 95)}%` }}
            >
              <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-center">
                <span className="text-2xl">😰</span>
                <div className="text-white text-sm font-bold">{fearGreed.value}</div>
              </div>
            </div>
          </div>
        </div>
        <div className="text-center mt-8 text-gray-400 text-sm">
          当前: <span className="text-white font-semibold">{fearGreed.phase}</span> ({fearGreed.value})
        </div>
      </Card>

      {/* Quant Signals */}
      <Card title="量化信号面板">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">涨停数量</div>
            <div className="text-white font-semibold text-lg">{loading ? '...' : limitUpDown.limitUp}</div>
            <Badge text={loading ? '加载中' : getLimitStatus(limitUpDown.limitUp)} variant="yellow" />
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">跌停数量</div>
            <div className="text-white font-semibold text-lg">{loading ? '...' : limitUpDown.limitDown}</div>
            <Badge text="正常" variant="green" />
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">成交额</div>
            <div className="text-white font-semibold text-lg">{loading ? '...' : '加载中'}</div>
            <Badge text="正常" variant="blue" />
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">北向资金</div>
            <div className="text-white font-semibold text-lg">
              {loading ? '...' : (northboundData[0]?.total >= 0 ? '+' : '') + (northboundData[0]?.total?.toFixed(0) || '0')}亿
            </div>
            <Badge 
              text={loading ? '加载中' : (northboundData[0]?.total >= 0 ? '净买入' : '净卖出')} 
              variant={northboundData[0]?.total >= 0 ? 'green' : 'red'} 
            />
          </div>
        </div>
      </Card>

      {/* Northbound Capital Trend */}
      <Card title="北向资金趋势（近7日）">
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData.length > 0 ? chartData : [{date: '-', value: 0}]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" fontSize={12} />
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
            <div 
              className="bg-accent-green h-full rounded-full" 
              style={{ width: `${Math.min(Math.abs(totalNorthbound) / 200 * 100, 100)}%` }}
            ></div>
          </div>
          <div className="text-sm text-gray-400 mt-1">
            7日累计净买入 ¥{totalNorthbound >= 0 ? '+' : ''}{totalNorthbound.toFixed(0)}亿
          </div>
        </div>
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
                <h4 className="text-accent-blue font-semibold mb-2 flex items-center gap-2">
                  <span>📐</span> 计算方法
                </h4>
                <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300 whitespace-pre-line">
                  {metricExplanations[activeMetric as MetricExplanationKeys].calculation}
                </div>
              </div>

              <div>
                <h4 className="text-accent-green font-semibold mb-2 flex items-center gap-2">
                  <span>📖</span> 解读指南
                </h4>
                <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300 whitespace-pre-line">
                  {metricExplanations[activeMetric as MetricExplanationKeys].interpretation}
                </div>
              </div>

              <div className="bg-accent-yellow/10 border border-accent-yellow/30 rounded-xl p-4">
                <h4 className="text-accent-yellow font-semibold mb-2 flex items-center gap-2">
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
