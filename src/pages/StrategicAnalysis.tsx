import { useState } from 'react';
import { Card, Badge } from '../components';

interface IndustryAnalysis {
  industry: string;
  marketSize: string;
  growth: string;
  concentration: string;
  lifecycle: string;
  portersForces: {
    supplierPower: string;
    buyerPower: string;
    newEntrants: string;
    substitutes: string;
    rivalry: string;
  };
  industryChain: {
    upstream: string;
    midstream: string;
    downstream: string;
    profitDistribution: string;
  };
  pest: {
    political: string;
    economic: string;
    social: string;
    technological: string;
  };
  opportunities: string;
  risks: string;
}

const sampleAnalysis: IndustryAnalysis = {
  industry: '智能驾驶',
  marketSize: '5,200亿（2025年）',
  growth: '+38% YoY',
  concentration: 'CR3 = 45%',
  lifecycle: '高速增长期',
  portersForces: {
    supplierPower: '中等（芯片略有紧缺）',
    buyerPower: '低（消费者价格敏感）',
    newEntrants: '小米/华为入局，威胁增加 ⚠️',
    substitutes: '暂无',
    rivalry: '激烈（比亚迪、特斯拉、小鹏、华为）',
  },
  industryChain: {
    upstream: '芯片（英伟达/地平线）',
    midstream: '方案商',
    downstream: '整车厂',
    profitDistribution: '← 利润最强    利润次之 →',
  },
  pest: {
    political: '新能源补贴延续，智能驾驶准入法规加速落地',
    economic: '消费信心回升，30万以上车型销量增长',
    social: '自动驾驶接受度提升，年轻用户偏好明显',
    technological: '城市NOA落地，激光雷达成本下降50%',
  },
  opportunities: '能拿到英伟达Orin/Thor芯片的方案商',
  risks: '价格战压缩利润，传统车企转型慢',
};

const industries = ['智能驾驶', '新能源', '半导体', 'AI算力', '医药', '消费电子'];

export function StrategicAnalysis() {
  const [selectedIndustry, setSelectedIndustry] = useState<string>('智能驾驶');
  const [showAnalysis, setShowAnalysis] = useState(false);

  const handleSearch = () => {
    if (selectedIndustry) {
      setShowAnalysis(true);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">🧭 战略分析</h2>
        <button className="text-finance-blue text-sm hover:underline">[刷新]</button>
      </div>

      {/* Industry Search */}
      <Card>
        <div className="space-y-4">
          <div>
            <label className="text-gray-400 text-sm mb-2 block">输入行业/赛道</label>
            <div className="flex gap-2">
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-finance-blue"
              >
                {industries.map((industry) => (
                  <option key={industry} value={industry}>
                    {industry}
                  </option>
                ))}
              </select>
              <button
                onClick={handleSearch}
                className="px-6 py-2 bg-finance-blue text-white rounded-lg hover:bg-finance-blue/80 transition-colors"
              >
                分析
              </button>
            </div>
          </div>

          {/* Quick Select Tags */}
          <div className="flex flex-wrap gap-2">
            {industries.map((industry) => (
              <button
                key={industry}
                onClick={() => setSelectedIndustry(industry)}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  selectedIndustry === industry
                    ? 'bg-finance-blue text-white'
                    : 'bg-gray-700 text-gray-400 hover:text-white'
                }`}
              >
                {industry}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Analysis Results */}
      {showAnalysis && (
        <div className="space-y-4">
          {/* Market Overview */}
          <Card>
            <h3 className="text-lg font-semibold mb-3">行业概览：{sampleAnalysis.industry}</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-gray-400 text-xs">市场规模</div>
                <div className="text-white font-medium">{sampleAnalysis.marketSize}</div>
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-gray-400 text-xs">增速</div>
                <div className="text-finance-green font-medium">{sampleAnalysis.growth}</div>
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-gray-400 text-xs">市场集中度</div>
                <div className="text-white font-medium">{sampleAnalysis.concentration}</div>
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="text-gray-400 text-xs">生命周期</div>
                <Badge text={sampleAnalysis.lifecycle} variant="green" />
              </div>
            </div>
          </Card>

          {/* Porter's Five Forces */}
          <Card title="波特五力分析">
            <div className="space-y-3">
              <div className="flex justify-between items-center bg-gray-700 rounded-lg p-3">
                <span className="text-gray-400">供应商议价</span>
                <span className="text-white text-sm">{sampleAnalysis.portersForces.supplierPower}</span>
              </div>
              <div className="flex justify-between items-center bg-gray-700 rounded-lg p-3">
                <span className="text-gray-400">买方议价</span>
                <span className="text-white text-sm">{sampleAnalysis.portersForces.buyerPower}</span>
              </div>
              <div className="flex justify-between items-center bg-gray-700 rounded-lg p-3">
                <span className="text-gray-400">新进入者</span>
                <span className="text-finance-yellow text-sm">{sampleAnalysis.portersForces.newEntrants}</span>
              </div>
              <div className="flex justify-between items-center bg-gray-700 rounded-lg p-3">
                <span className="text-gray-400">替代品威胁</span>
                <span className="text-white text-sm">{sampleAnalysis.portersForces.substitutes}</span>
              </div>
              <div className="flex justify-between items-center bg-gray-700 rounded-lg p-3">
                <span className="text-gray-400">行业内竞争</span>
                <span className="text-finance-red text-sm">{sampleAnalysis.portersForces.rivalry}</span>
              </div>
            </div>
          </Card>

          {/* Industry Chain */}
          <Card title="产业链利润分布">
            <div className="bg-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-center mb-4">
                <div className="text-center">
                  <div className="text-gray-400 text-xs mb-1">上游</div>
                  <div className="text-white text-sm">{sampleAnalysis.industryChain.upstream}</div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-xs mb-1">中游</div>
                  <div className="text-white text-sm">{sampleAnalysis.industryChain.midstream}</div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-xs mb-1">下游</div>
                  <div className="text-white text-sm">{sampleAnalysis.industryChain.downstream}</div>
                </div>
              </div>
              <div className="text-center text-sm text-finance-green">
                {sampleAnalysis.industryChain.profitDistribution}
              </div>
            </div>
          </Card>

          {/* PEST Analysis */}
          <Card title="PEST 宏观分析">
            <div className="space-y-3">
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-finance-blue font-semibold">P</span>
                  <span className="text-gray-400">政策</span>
                </div>
                <p className="text-white text-sm">{sampleAnalysis.pest.political}</p>
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-finance-green font-semibold">E</span>
                  <span className="text-gray-400">经济</span>
                </div>
                <p className="text-white text-sm">{sampleAnalysis.pest.economic}</p>
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-finance-yellow font-semibold">S</span>
                  <span className="text-gray-400">社会</span>
                </div>
                <p className="text-white text-sm">{sampleAnalysis.pest.social}</p>
              </div>
              <div className="bg-gray-700 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-finance-purple font-semibold">T</span>
                  <span className="text-gray-400">技术</span>
                </div>
                <p className="text-white text-sm">{sampleAnalysis.pest.technological}</p>
              </div>
            </div>
          </Card>

          {/* Summary */}
          <Card title="总结">
            <div className="space-y-3">
              <div className="bg-finance-green/10 rounded-lg p-3 border border-finance-green/30">
                <div className="text-finance-green font-medium mb-1">核心机会</div>
                <p className="text-gray-300 text-sm">{sampleAnalysis.opportunities}</p>
              </div>
              <div className="bg-finance-red/10 rounded-lg p-3 border border-finance-red/30">
                <div className="text-finance-red font-medium mb-1">主要风险</div>
                <p className="text-gray-300 text-sm">{sampleAnalysis.risks}</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {!showAnalysis && (
        <Card>
          <div className="text-center text-gray-400 py-8">
            <p className="mb-2">选择一个行业开始分析</p>
            <p className="text-sm">输入行业/赛道，例如：智能驾驶、新能源、半导体</p>
          </div>
        </Card>
      )}
    </div>
  );
}
