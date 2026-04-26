import { useState, useEffect } from 'react';
import { Card } from '../Card';
import { apiService, ApiLeader, ApiConvergencePreset, ApiRiskPreference } from '../../services/api/apiService';

// 分析模式类型
export type AnalysisMode = 'tradingagents' | 'aihedgefund' | 'fusion';

interface AnalysisParamsProps {
  // 当前选中的参数
  mode: AnalysisMode;
  leaderId: string | null;
  convergencePreset: string;
  riskLevel: string;
  
  // 回调函数
  onModeChange: (mode: AnalysisMode) => void;
  onLeaderChange: (leaderId: string) => void;
  onConvergenceChange: (preset: string) => void;
  onRiskChange: (riskLevel: string) => void;
}

// 模式配置
const MODE_CONFIG: Record<AnalysisMode, { name: string; icon: string; description: string }> = {
  tradingagents: {
    name: 'TradingAgents',
    icon: '🤖',
    description: '多智能体辩论分析',
  },
  aihedgefund: {
    name: 'AI Hedge Fund',
    icon: '🎯',
    description: '投资大师决策模式',
  },
  fusion: {
    name: 'Fusion',
    icon: '⚡',
    description: '融合模式',
  },
};

// 模式标签
const MODE_LABELS: Record<AnalysisMode, string> = {
  tradingagents: 'TradingAgents',
  aihedgefund: 'AI Hedge Fund',
  fusion: 'Fusion',
};

export function AnalysisParams({
  mode,
  leaderId,
  convergencePreset,
  riskLevel,
  onModeChange,
  onLeaderChange,
  onConvergenceChange,
  onRiskChange,
}: AnalysisParamsProps) {
  // 状态
  const [leaders, setLeaders] = useState<ApiLeader[]>([]);
  const [convergencePresets, setConvergencePresets] = useState<ApiConvergencePreset[]>([]);
  const [riskPreferences, setRiskPreferences] = useState<ApiRiskPreference[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载配置数据
  useEffect(() => {
    const loadConfig = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const [leadersData, convergenceData, riskData] = await Promise.all([
          apiService.getLeaders(),
          apiService.getConvergencePresets(),
          apiService.getRiskLevels(),
        ]);
        
        setLeaders(leadersData);
        setConvergencePresets(convergenceData);
        setRiskPreferences(riskData);
        
        // 设置默认值
        if (!leaderId && leadersData.length > 0 && (mode === 'aihedgefund' || mode === 'fusion')) {
          onLeaderChange(leadersData[0].id);
        }
      } catch (err) {
        console.error('加载配置失败:', err);
        setError('加载配置失败，请检查后端服务');
        
        // 使用默认配置
        setConvergencePresets([
          { id: 'quick', name: 'Quick Mode', description: '快速分析', max_iterations: 1, convergence_gap: 20, early_stop_gap: 15 },
          { id: 'standard', name: 'Standard Mode', description: '标准分析', max_iterations: 3, convergence_gap: 15, early_stop_gap: 10 },
          { id: 'deep', name: 'Deep Mode', description: '深度分析', max_iterations: 5, convergence_gap: 10, early_stop_gap: 5 },
        ]);
        setRiskPreferences([
          { id: 'conservative', name: 'Conservative', description: '保守型', max_position: 20, stop_loss: 3, volatility_alert: 5 },
          { id: 'moderate', name: 'Moderate', description: '平衡型', max_position: 30, stop_loss: 5, volatility_alert: 8 },
          { id: 'aggressive', name: 'Aggressive', description: '进取型', max_position: 50, stop_loss: 8, volatility_alert: 12 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadConfig();
  }, []);

  // 判断是否显示领袖选择器
  const showLeaderSelector = mode === 'aihedgefund' || mode === 'fusion';

  // 获取当前选中的领袖
  const selectedLeader = leaders.find(l => l.id === leaderId);

  return (
    <Card className="p-4">
      {/* 标题 */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-lg">⚙️</span>
        <h3 className="text-sm font-semibold text-white uppercase tracking-wide">
          分析参数
        </h3>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-accent-red/10 border border-accent-red/20 rounded-lg text-xs text-accent-red">
          {error}
        </div>
      )}

      {/* 模式选择 */}
      <div className="mb-5">
        <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
          分析模式
        </div>
        <div className="grid grid-cols-3 gap-2">
          {(Object.keys(MODE_CONFIG) as AnalysisMode[]).map((modeKey) => {
            const config = MODE_CONFIG[modeKey];
            const isSelected = mode === modeKey;
            
            return (
              <button
                key={modeKey}
                onClick={() => onModeChange(modeKey)}
                className={`
                  p-3 rounded-xl border transition-all duration-200 text-center
                  ${isSelected
                    ? 'bg-accent-blue/20 border-accent-blue text-accent-blue'
                    : 'bg-surface-200/50 border-white/10 text-gray-300 hover:border-white/20'
                  }
                `}
              >
                <div className="text-xl mb-1">{config.icon}</div>
                <div className="text-xs font-medium">{MODE_LABELS[modeKey]}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 领袖选择器 - 仅在 ai-hedge-fund 和 Fusion 模式下显示 */}
      {showLeaderSelector && (
        <div className="mb-5">
          <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
            投资大师
          </div>
          {loading ? (
            <div className="p-3 bg-surface-200/30 rounded-xl text-xs text-gray-400">
              加载中...
            </div>
          ) : (
            <select
              value={leaderId || ''}
              onChange={(e) => onLeaderChange(e.target.value)}
              className="w-full p-3 bg-surface-200/50 border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-accent-blue/50 appearance-none cursor-pointer"
            >
              {leaders.map((leader) => (
                <option key={leader.id} value={leader.id}>
                  {leader.name} - {leader.style}
                </option>
              ))}
            </select>
          )}
          
          {/* 选中领袖信息 */}
          {selectedLeader && (
            <div className="mt-2 p-2 bg-surface-200/30 rounded-lg">
              <div className="text-xs text-gray-400 line-clamp-2">
                {selectedLeader.description}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 收敛预设选择 */}
      <div className="mb-5">
        <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
          收敛预设
        </div>
        <div className="grid grid-cols-3 gap-2">
          {convergencePresets.map((preset) => {
            const isSelected = convergencePreset === preset.id;
            
            return (
              <button
                key={preset.id}
                onClick={() => onConvergenceChange(preset.id)}
                className={`
                  p-2 rounded-lg border transition-all duration-200 text-center
                  ${isSelected
                    ? 'bg-accent-purple/20 border-accent-purple text-accent-purple'
                    : 'bg-surface-200/50 border-white/10 text-gray-300 hover:border-white/20'
                  }
                `}
              >
                <div className="text-xs font-medium">{preset.name}</div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {preset.max_iterations}轮迭代
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 风险等级选择 */}
      <div className="mb-4">
        <div className="text-xs text-gray-400 mb-2 uppercase tracking-wider">
          风险等级
        </div>
        <div className="space-y-2">
          {riskPreferences.map((risk) => {
            const isSelected = riskLevel === risk.id;
            const riskColors = {
              conservative: { border: 'border-accent-green', text: 'text-accent-green', bg: 'bg-accent-green/10' },
              moderate: { border: 'border-accent-yellow', text: 'text-accent-yellow', bg: 'bg-accent-yellow/10' },
              aggressive: { border: 'border-accent-red', text: 'text-accent-red', bg: 'bg-accent-red/10' },
            };
            const colors = riskColors[risk.id as keyof typeof riskColors] || riskColors.moderate;
            
            return (
              <button
                key={risk.id}
                onClick={() => onRiskChange(risk.id)}
                className={`
                  w-full p-3 rounded-lg border transition-all duration-200 text-left
                  ${isSelected
                    ? `${colors.bg} border-${risk.id === 'conservative' ? 'accent-green' : risk.id === 'aggressive' ? 'accent-red' : 'accent-yellow'}`
                    : 'bg-surface-200/50 border-white/10 hover:border-white/20'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium ${isSelected ? colors.text : 'text-gray-300'}`}>
                    {risk.name}
                  </span>
                  <span className={`text-xs ${isSelected ? colors.text : 'text-gray-500'}`}>
                    {risk.max_position}% 仓位
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  止损 {risk.stop_loss}% | 波动率警报 {risk.volatility_alert}%
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </Card>
  );
}

export default AnalysisParams;
