import { useState } from 'react';
import { Card, Badge } from '../components';
import { metricExplanations, MetricExplanationKeys } from './DashboardHome';

const positionRules = [
  { rule: '① 不轻易满仓，保留20-30%现金应对极端情况', completed: true },
  { rule: '② 单票不超过总仓位30%', completed: true },
  { rule: '③ 分批建仓，首次不超过30%，加仓不超过20%', completed: true },
  { rule: '④ 动态调整，根据情绪变化每周评估一次', completed: true },
  { rule: '⑤ 单票亏损超过8%必须止损', completed: true },
];

const judgmentBasis = [
  { indicator: '恐惧贪婪指数', value: '26 (Fear)', conclusion: '冰点/修复区间' },
  { indicator: '涨停数量', value: '47（<60）', conclusion: '冰点特征' },
  { indicator: '北向资金', value: '连续3日净买入', conclusion: '修复特征' },
];

const currentPosition = 48;

export function PositionManagement() {
  const [showModal, setShowModal] = useState(false);
  const [activeMetric, setActiveMetric] = useState<MetricExplanationKeys | ''>('');

  const openMetricModal = (metricKey: MetricExplanationKeys) => {
    setActiveMetric(metricKey);
    setShowModal(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">🎯 仓位管理</h2>
        <button className="text-finance-blue text-sm hover:underline">[刷新]</button>
      </div>

      {/* Current Position Recommendation - Clickable */}
      <Card
        className="cursor-pointer hover:border-finance-blue/50 transition-colors"
        onClick={() => openMetricModal('position')}
      >
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">仓位建议</span>
          <span className="text-xs text-finance-blue">点击查看计算方法 →</span>
        </div>
        <div className="text-center mb-4">
          <div className="text-gray-400 text-sm mb-1">当前建议仓位</div>
          <div className="text-3xl font-bold text-finance-yellow font-mono">40-60%</div>
          <div className="text-gray-400 text-sm">冰点/修复阶段</div>
        </div>

        {/* Position Slider Visualization */}
        <div className="relative pt-8 pb-4">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>0%</span>
            <span>20%</span>
            <span>40%</span>
            <span>60%</span>
            <span>80%</span>
            <span>100%</span>
          </div>
          <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-finance-green via-finance-yellow to-finance-red rounded-full relative">
              {/* 40-60% zone indicator */}
              <div className="absolute top-0 bottom-0 left-1/3 w-1/3 bg-white/20 border-l border-r border-white/30"></div>
              {/* Current position marker */}
              <div
                className="absolute top-1/2 -translate-y-1/2 w-3 h-6 bg-white rounded shadow-lg"
                style={{ left: `${currentPosition}%`, transform: 'translate(-50%, -50%)' }}
              >
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 text-xs text-white whitespace-nowrap">
                  ▲ {currentPosition}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="text-center text-sm text-gray-400">
          建议区间: <span className="text-finance-yellow font-mono">40-60%</span>
        </div>
      </Card>

      {/* Five Position Rules */}
      <Card title="五条仓位铁律">
        <div className="space-y-3">
          {positionRules.map((item, index) => (
            <div key={index} className="flex items-start gap-3 bg-gray-700 rounded-lg p-3">
              <div className="w-6 h-6 rounded-full bg-finance-green/20 flex items-center justify-center flex-shrink-0">
                <span className="text-finance-green text-sm">✓</span>
              </div>
              <span className="text-gray-300">{item.rule}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Market Phase Judgment */}
      <Card title="市场阶段判断依据">
        <div className="space-y-3">
          {judgmentBasis.map((item, index) => (
            <div key={index} className="flex justify-between items-center bg-gray-700 rounded-lg p-3">
              <div>
                <div className="text-gray-400 text-sm">{item.indicator}</div>
                <div className="text-white font-medium">{item.value}</div>
              </div>
              <div className="text-right">
                <Badge text="→" variant="gray" />
                <div className="text-finance-green text-sm mt-1">{item.conclusion}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-finance-green/10 rounded-lg border border-finance-green/30">
          <div className="flex justify-between items-center">
            <span className="text-white font-medium">综合判断</span>
            <Badge text="冰点/修复阶段" variant="green" />
          </div>
          <div className="text-gray-400 text-sm mt-2">
            → 建议仓位 <span className="text-finance-yellow font-bold">40-60%</span>
          </div>
        </div>
      </Card>

      {/* Position Management Tips */}
      <Card title="💡 操作建议">
        <div className="space-y-2 text-sm">
          <p className="text-gray-300">
            <span className="text-finance-yellow">冰点/修复阶段</span>是布局的好时机，但需控制仓位。
          </p>
          <p className="text-gray-400">
            • 分批建仓，避免一次性投入<br />
            • 保留足够的现金应对可能的极端情况<br />
            • 设定止损线，严格执行
          </p>
        </div>
      </Card>

      {/* Market Judgment Cards - Clickable */}
      <Card title="市场阶段判断依据">
        <div className="space-y-3">
          {judgmentBasis.map((item, index) => (
            <div
              key={index}
              className="flex justify-between items-center bg-gray-700 rounded-lg p-3 cursor-pointer hover:bg-gray-600 transition-colors"
              onClick={() => openMetricModal(item.indicator === '恐惧贪婪指数' ? 'fearGreed' : item.indicator === '北向资金' ? 'northbound' : 'sentiment')}
            >
              <div>
                <div className="text-gray-400 text-sm">{item.indicator}</div>
                <div className="text-white font-medium font-mono">{item.value}</div>
              </div>
              <div className="text-right flex items-center gap-2">
                <Badge text="→" variant="gray" />
                <div className="text-finance-green text-sm mt-1">{item.conclusion}</div>
                <span className="text-xs text-finance-blue">点击 →</span>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-finance-green/10 rounded-lg border border-finance-green/30">
          <div className="flex justify-between items-center">
            <span className="text-white font-medium">综合判断</span>
            <Badge text="冰点/修复阶段" variant="green" />
          </div>
          <div className="text-gray-400 text-sm mt-2">
            → 建议仓位 <span className="text-finance-yellow font-bold font-mono">40-60%</span>
          </div>
        </div>
      </Card>

      {/* Metric Explanation Modal */}
      {showModal && !!activeMetric && metricExplanations[activeMetric as MetricExplanationKeys] && (
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
                <Badge text={metricExplanations[activeMetric as MetricExplanationKeys].phase} variant="yellow" />
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
