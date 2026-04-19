import { useState } from 'react';
import { Card, Badge } from '../components';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

type MacroMetricKeys = 'gdp' | 'cpi' | 'pmi' | 'lpr';

const macroExplanations: Record<MacroMetricKeys, {
  title: string;
  calculation: string;
  interpretation: string;
  currentValue: string;
  phase: string;
  suggestion: string;
}> = {
  gdp: {
    title: 'GDP增速',
    calculation: '国内生产总值(GDP)增速计算方法：\n\nGDP增速 = (本期GDP - 上期GDP) / 上期GDP × 100%\n\n数据来源：国家统计局每季度发布\n计算周期：同比（与去年同期相比）\n\n• 5%以上：经济运行在合理区间\n• 4-5%：面临一定下行压力\n• 4%以下：经济衰退风险',
    interpretation: '• >5.5%：经济过热，政策可能收紧\n• 5-5.5%：稳健增长区间\n• 4-5%：温和放缓\n• <4%：经济偏冷',
    currentValue: '5.0%',
    phase: '稳定',
    suggestion: 'GDP增速稳定在5%左右，表明经济运行总体平稳，是布局权益资产的好时机',
  },
  cpi: {
    title: 'CPI消费者物价指数',
    calculation: '消费者物价指数(CPI)计算方法：\n\nCPI = (一组固定商品按当期价格计算的价值 / 同一组商品按基期价格计算的价值) × 100\n\n权重构成：\n• 食品烟酒：约30%\n• 居住：约20%\n• 交通通信：约15%\n• 教育文化：约15%\n• 医疗保健：约10%\n• 其他：约10%',
    interpretation: '• 0-1%：通缩风险\n• 1-2%：温和通胀（理想区间）\n• 2-3%：温和通胀上行\n• >3%：通胀压力较大\n• >5%：严重通胀',
    currentValue: '+1.2%',
    phase: '温和',
    suggestion: 'CPI温和上涨，通胀压力可控，货币政策有操作空间',
  },
  pmi: {
    title: 'PMI采购经理指数',
    calculation: '采购经理指数(PMI)计算方法：\n\nPMI = 新订单×30% + 产出×25% + 就业×20% + 供应商配送×15% + 库存×10%\n\n• 50% = 荣枯线\n• >50%：制造业扩张\n• <50%：制造业收缩\n• 连续低于50%：经济衰退信号',
    interpretation: '• >55%：经济过热\n• 50-55%：稳健扩张\n• 47-50%：温和收缩\n• <47%：严重收缩',
    currentValue: '49.2',
    phase: '荣枯线下',
    suggestion: 'PMI略低于荣枯线，制造业仍有压力，但政策支持力度在加大',
  },
  lpr: {
    title: 'LPR贷款市场报价利率',
    calculation: '贷款市场报价利率(LPR)计算方法：\n\n由18家报价行根据MLF利率+加点形成\n每月20日公布（节假日顺延）\n\nLPR = MLF利率 + 加点（18家银行算术平均值）\n\n• 1年期LPR：短期贷款利率基准\n• 5年期LPR：长期贷款利率基准（影响房贷）',
    interpretation: '• LPR下调：货币政策宽松，利好股市\n• LPR不变：政策中性\n• LPR上调：货币政策收紧',
    currentValue: '3.45%',
    phase: '维持不变',
    suggestion: 'LPR连续多月维持不变，货币政策保持稳健',
  },
};

const gdpData = [
  { year: '2023', value: 5.2 },
  { year: '2024', value: 5.0 },
  { year: '2025-Q1', value: 5.4 },
  { year: '2025-Q2', value: 5.3 },
  { year: '2025-Q3', value: 5.2 },
  { year: '2025-Q4', value: 5.1 },
];

const cpiData = [
  { month: '5月', value: 0.3 },
  { month: '6月', value: 0.2 },
  { month: '7月', value: 0.5 },
  { month: '8月', value: 0.6 },
  { month: '9月', value: 0.4 },
  { month: '10月', value: 0.3 },
  { month: '11月', value: 0.2 },
  { month: '12月', value: 0.1 },
  { month: '1月', value: 0.5 },
  { month: '2月', value: 0.7 },
  { month: '3月', value: 1.2 },
  { month: '4月', value: 1.1 },
];

const pmiData = [
  { month: '1月', value: 49.1 },
  { month: '2月', value: 49.9 },
  { month: '3月', value: 50.5 },
  { month: '4月', value: 49.2 },
];

const lprData = [
  { period: '2024-01', value: 3.45 },
  { period: '2024-04', value: 3.45 },
  { period: '2024-07', value: 3.45 },
  { period: '2024-10', value: 3.45 },
  { period: '2025-01', value: 3.45 },
  { period: '2025-04', value: 3.45 },
];

const exchangeRates = [
  { pair: 'USD/CNY', rate: 6.83 },
  { pair: 'EUR/CNY', rate: 7.58 },
  { pair: 'GBP/CNY', rate: 8.62 },
  { pair: 'JPY/CNY', rate: 0.043 },
];

const moneySupply = {
  m2: { value: '313.52万亿', yoy: '+7.0%' },
  m1: { value: '67.47万亿', yoy: '+1.2%' },
  m0: { value: '12.18万亿', yoy: '+5.8%' },
};

export function MacroData() {
  const [showModal, setShowModal] = useState(false);
  const [activeMetric, setActiveMetric] = useState<MacroMetricKeys | ''>('');

  const openMetricModal = (metricKey: MacroMetricKeys) => {
    setActiveMetric(metricKey);
    setShowModal(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">📈 宏观数据</h2>
        <button className="text-finance-blue text-sm hover:underline">[刷新]</button>
      </div>

      {/* GDP - Clickable */}
      <Card
        className="cursor-pointer hover:border-finance-blue/50 transition-colors"
        onClick={() => openMetricModal('gdp')}
      >
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-gray-400 text-sm">GDP增速</div>
            <div className="text-2xl font-bold text-white font-mono">最新: 5.0%</div>
          </div>
          <div className="flex items-center gap-2">
            <Badge text="稳定" variant="green" />
            <span className="text-xs text-finance-blue">点击查看 →</span>
          </div>
        </div>
        <div className="h-32">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={gdpData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="year" stroke="#9CA3AF" fontSize={10} />
              <YAxis stroke="#9CA3AF" fontSize={10} domain={[4, 6]} />
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

      {/* CPI - Clickable */}
      <Card
        className="cursor-pointer hover:border-finance-blue/50 transition-colors"
        onClick={() => openMetricModal('cpi')}
      >
        <div className="flex justify-between items-start mb-3">
          <div>
            <div className="text-gray-400 text-sm">CPI</div>
            <div className="text-2xl font-bold text-white font-mono">最新: +1.2%</div>
          </div>
          <div className="flex items-center gap-2">
            <Badge text="温和" variant="blue" />
            <span className="text-xs text-finance-blue">点击查看 →</span>
          </div>
        </div>
        <div className="h-32">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cpiData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="month" stroke="#9CA3AF" fontSize={10} />
              <YAxis stroke="#9CA3AF" fontSize={10} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="text-gray-400 text-xs mt-2">近12个月趋势</div>
      </Card>

      {/* PMI and LPR */}
      <div className="grid grid-cols-1 gap-4">
        <Card
          className="cursor-pointer hover:border-finance-blue/50 transition-colors"
          onClick={() => openMetricModal('pmi')}
        >
          <div className="flex justify-between items-start mb-2">
            <div>
              <div className="text-gray-400 text-sm">PMI</div>
              <div className="text-2xl font-bold text-white font-mono">最新: 49.2</div>
            </div>
            <div className="flex items-center gap-2">
              <Badge text="荣枯线下" variant="yellow" />
              <span className="text-xs text-finance-blue">点击查看 →</span>
            </div>
          </div>
          <div className="h-24">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={pmiData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="month" stroke="#9CA3AF" fontSize={10} />
                <YAxis stroke="#9CA3AF" fontSize={10} domain={[48, 52]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
                  labelStyle={{ color: '#9CA3AF' }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#F59E0B"
                  strokeWidth={2}
                  dot={{ fill: '#F59E0B' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="text-gray-400 text-xs mt-2">荣枯线50下方，制造业收缩</div>
        </Card>

        <Card
          className="cursor-pointer hover:border-finance-blue/50 transition-colors"
          onClick={() => openMetricModal('lpr')}
        >
          <div className="flex justify-between items-start mb-2">
            <div>
              <div className="text-gray-400 text-sm">LPR(1年)</div>
              <div className="text-2xl font-bold text-white font-mono">最新: 3.45%</div>
            </div>
            <div className="flex items-center gap-2">
              <Badge text="维持不变" variant="gray" />
              <span className="text-xs text-finance-blue">点击查看 →</span>
            </div>
          </div>
          <div className="h-24">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lprData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="period" stroke="#9CA3AF" fontSize={10} />
                <YAxis stroke="#9CA3AF" fontSize={10} domain={[3.4, 3.5]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
                  labelStyle={{ color: '#9CA3AF' }}
                />
                <Line
                  type="stepAfter"
                  dataKey="value"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  dot={{ fill: '#8B5CF6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="text-gray-400 text-xs mt-2">连续多月维持不变</div>
        </Card>
      </div>

      {/* Exchange Rates */}
      <Card title="人民币汇率">
        <div className="grid grid-cols-2 gap-3">
          {exchangeRates.map((forex) => (
            <div key={forex.pair} className="bg-gray-700 rounded-lg p-3">
              <div className="text-gray-400 text-xs">{forex.pair}</div>
              <div className="text-white font-semibold">{forex.rate}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Money Supply */}
      <Card title="货币供应">
        <div className="space-y-3">
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-sm">M2货币供应</div>
            <div className="flex justify-between items-center">
              <span className="text-white font-semibold font-mono">{moneySupply.m2.value}</span>
              <Badge text={moneySupply.m2.yoy} variant="green" />
            </div>
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-sm">M1</div>
            <div className="flex justify-between items-center">
              <span className="text-white font-semibold font-mono">{moneySupply.m1.value}</span>
              <Badge text={moneySupply.m1.yoy} variant="yellow" />
            </div>
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-sm">M0</div>
            <div className="flex justify-between items-center">
              <span className="text-white font-semibold font-mono">{moneySupply.m0.value}</span>
              <Badge text={moneySupply.m0.yoy} variant="blue" />
            </div>
          </div>
        </div>
      </Card>

      {/* Metric Explanation Modal */}
      {showModal && !!activeMetric && macroExplanations[activeMetric as MacroMetricKeys] && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-end justify-center z-50" onClick={() => setShowModal(false)}>
          <div
            className="bg-gray-800 rounded-t-2xl w-full max-w-lg max-h-[80vh] overflow-y-auto animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-gray-800 border-b border-gray-700 p-4 flex justify-between items-center">
              <h3 className="text-lg font-bold text-white">{macroExplanations[activeMetric as MacroMetricKeys].title}</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white">✕</button>
            </div>
            <div className="p-4 space-y-4">
              <div className="text-center p-4 bg-gray-700/50 rounded-xl">
                <div className="text-3xl font-bold text-white font-mono">
                  {macroExplanations[activeMetric as MacroMetricKeys].currentValue}
                </div>
                <Badge text={macroExplanations[activeMetric as MacroMetricKeys].phase} variant={activeMetric === 'lpr' ? 'gray' : 'green'} />
              </div>

              <div>
                <h4 className="text-finance-blue font-semibold mb-2 flex items-center gap-2">
                  <span>📐</span> 计算方法
                </h4>
                <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300 whitespace-pre-line">
                  {macroExplanations[activeMetric as MacroMetricKeys].calculation}
                </div>
              </div>

              <div>
                <h4 className="text-finance-green font-semibold mb-2 flex items-center gap-2">
                  <span>📖</span> 解读指南
                </h4>
                <div className="bg-gray-700/50 rounded-lg p-3 text-sm text-gray-300 whitespace-pre-line">
                  {macroExplanations[activeMetric as MacroMetricKeys].interpretation}
                </div>
              </div>

              <div className="bg-finance-yellow/10 border border-finance-yellow/30 rounded-xl p-4">
                <h4 className="text-finance-yellow font-semibold mb-2 flex items-center gap-2">
                  <span>💡</span> 投资建议
                </h4>
                <p className="text-sm text-gray-300">{macroExplanations[activeMetric as MacroMetricKeys].suggestion}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
