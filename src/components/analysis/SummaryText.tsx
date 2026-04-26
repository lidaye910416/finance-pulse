import { Card } from '../Card';

interface SummaryTextProps {
  summary?: string;
  mode?: string;
  leaderName?: string;
}

/**
 * SummaryText Component
 * PRD Section 12.2 - Display analysis summary
 */
export function SummaryText({
  summary,
  mode = 'tradingagents',
  leaderName
}: SummaryTextProps) {
  const defaultSummary = summary || 
    `基于多智能体深度分析，该股票当前处于震荡整理阶段。从技术面来看，短期均线金叉形成， MACD 指标显示多方力量占优。从基本面来看，公司估值处于历史中位水平，具备一定安全边际。综合建议保持谨慎乐观，控制仓位在30%左右，止损位设置在5%。`;

  const modeLabels: Record<string, string> = {
    tradingagents: '多智能体辩论',
    aihedgefund: 'AI投资大师',
    fusion: '融合模式',
  };

  return (
    <Card>
      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider">
          📝 综合分析报告
        </h3>
        {leaderName && (
          <span className="text-xs px-2 py-0.5 rounded bg-accent-blue/10 text-accent-blue">
            {leaderName}
          </span>
        )}
        <span className="text-xs px-2 py-0.5 rounded bg-surface-200 text-gray-500">
          {modeLabels[mode] || mode}
        </span>
      </div>
      
      <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
        {defaultSummary}
      </div>
    </Card>
  );
}
