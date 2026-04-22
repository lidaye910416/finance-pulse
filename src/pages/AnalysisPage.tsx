import { useState } from 'react';
import { ChatInterface } from '../components/analysis/ChatInterface';
import { ALL_AGENTS } from '../services/analysis/agentConfig';
import { Card } from '../components';

// 简化分析师接口
interface Analyst {
  id: string;
  name: string;
  nameCn: string;
  avatar: string;
  style: string;
  description: string;
}

// 转换 AgentConfig 为简化格式
const analysts: Analyst[] = ALL_AGENTS.slice(0, 6).map(agent => ({
  id: agent.id,
  name: agent.nameCn,
  nameCn: agent.nameCn,
  avatar: agent.avatar,
  style: agent.style,
  description: agent.description,
}));

// 预设模板
const analysisTemplates = [
  { id: 'value', title: '价值投资', description: '巴菲特+格雷厄姆+达莫达兰', analysts: ['warren_buffett', 'ben_graham', 'aswath_damodaran'] },
  { id: 'growth', title: '成长投资', description: '彼得·林奇+凯西·伍德', analysts: ['peter_lynch', 'cathie_wood'] },
  { id: 'contrarian', title: '逆向投资', description: '伯里+塔勒布', analysts: ['michael_burry', 'nassim_taleb'] },
  { id: 'macro', title: '宏观策略', description: '德鲁肯米勒+宏观分析', analysts: ['stanley_druckenmiller'] },
];

export function AnalysisPage() {
  const [selectedAnalyst, setSelectedAnalyst] = useState<Analyst | null>(null);

  return (
    <div className="space-y-4 animate-fade-in-up pt-4">
      {/* 标题 */}
      <div className="text-center">
        <h1 className="text-2xl font-display font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
          AI 分析师
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          选择专业分析师，获取深度投资分析
        </p>
      </div>

      {/* 分析模板快捷入口 */}
      <div>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          快捷分析
        </h2>
        <div className="grid grid-cols-2 gap-2">
          {analysisTemplates.map((template) => (
            <button
              key={template.id}
              className="p-3 rounded-xl bg-surface-200/50 border border-white/10 hover:border-accent-blue/30 transition-all text-left btn-press"
              onClick={() => {
                // 选中第一个分析师作为默认
                const firstAnalyst = analysts.find(a => a.id === template.analysts[0]);
                if (firstAnalyst) setSelectedAnalyst(firstAnalyst);
              }}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">📊</span>
                <span className="text-sm font-medium text-white">{template.title}</span>
              </div>
              <div className="text-xs text-gray-500">{template.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 分析师选择提示 */}
      <Card className="border-accent-blue/20 bg-accent-blue/5">
        <div className="flex items-start gap-3">
          <span className="text-2xl">💡</span>
          <div>
            <div className="text-sm font-medium text-accent-blue mb-1">使用建议</div>
            <div className="text-xs text-gray-400 space-y-1">
              <p>• 输入股票代码（如 600519）获取个股分析</p>
              <p>• 输入基金代码（如 510300）获取基金分析</p>
              <p>• 可切换不同风格的分析师获取多元视角</p>
            </div>
          </div>
        </div>
      </Card>

      {/* 聊天界面 */}
      <ChatInterface
        selectedAnalyst={selectedAnalyst}
        onAnalystChange={setSelectedAnalyst}
      />
    </div>
  );
}
