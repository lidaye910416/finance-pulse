import { Card } from '../Card';

type Action = 'buy' | 'hold' | 'sell' | 'watch';
type RiskLevel = 'conservative' | 'moderate' | 'aggressive';

interface Recommendation {
  action: Action;
  confidence: number;
  timeframe: string;
  position_size?: number;
  stop_loss?: number;
  exit_price?: number;
  entry_price?: number;
  risks?: string[];
}

interface RecommendationCardProps {
  recommendation?: Recommendation;
  riskLevel?: RiskLevel;
  leaderName?: string;
}

/**
 * RecommendationCard Component
 * PRD Section 12.2 - Display investment recommendation
 */
export function RecommendationCard({
  recommendation,
  riskLevel = 'moderate',
  leaderName
}: RecommendationCardProps) {
  const defaultRec: Recommendation = recommendation || {
    action: 'hold',
    confidence: 60,
    timeframe: '1-3个月',
    position_size: 30,
    stop_loss: 5,
    exit_price: 3280,
    entry_price: 3200,
    risks: ['市场波动风险', '行业下行风险'],
  };

  const actionConfig = {
    buy: { emoji: '✅', text: '买入', color: 'text-accent-green', bg: 'bg-accent-green' },
    hold: { emoji: '⏸️', text: '持有', color: 'text-accent-blue', bg: 'bg-accent-blue' },
    sell: { emoji: '❌', text: '卖出', color: 'text-accent-red', bg: 'bg-accent-red' },
    watch: { emoji: '👀', text: '观望', color: 'text-yellow-500', bg: 'bg-yellow-500' },
  };

  const riskColors = {
    conservative: 'border-l-yellow-500',
    moderate: 'border-l-accent-blue',
    aggressive: 'border-l-accent-red',
  };

  const config = actionConfig[defaultRec.action];

  return (
    <Card className={`border-l-4 ${riskColors[riskLevel]}`}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider">
            {leaderName ? `📌 ${leaderName} 决策` : '📌 投资建议'}
          </h3>
        </div>
        {/* Action Badge */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl ${config.bg}/10`}>
          <span className="text-lg">{config.emoji}</span>
          <span className={`text-lg font-bold ${config.color}`}>{config.text}</span>
        </div>
      </div>

      {/* Confidence */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm text-gray-400">置信度</span>
          <span className="text-lg font-bold text-white">{defaultRec.confidence}%</span>
        </div>
        <div className="h-2 bg-surface-200 rounded-full overflow-hidden">
          <div
            className={`h-full ${config.bg} transition-all rounded-full`}
            style={{ width: `${defaultRec.confidence}%` }}
          />
        </div>
      </div>

      {/* Price Info Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {defaultRec.entry_price && (
          <div className="bg-surface-200/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">买入价</div>
            <div className="text-sm font-mono text-accent-green">
              ¥{defaultRec.entry_price.toFixed(2)}
            </div>
          </div>
        )}
        {defaultRec.exit_price && (
          <div className="bg-surface-200/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">目标价</div>
            <div className="text-sm font-mono text-white">
              ¥{defaultRec.exit_price.toFixed(2)}
            </div>
          </div>
        )}
        {defaultRec.stop_loss && (
          <div className="bg-surface-200/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">止损价</div>
            <div className="text-sm font-mono text-accent-red">
              ¥{defaultRec.stop_loss.toFixed(2)}
            </div>
          </div>
        )}
        {defaultRec.position_size !== undefined && (
          <div className="bg-surface-200/50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">建议仓位</div>
            <div className="text-sm font-mono text-accent-blue">
              {defaultRec.position_size}%
            </div>
          </div>
        )}
      </div>

      {/* Timeframe */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-gray-400">投资周期</span>
        <span className="text-sm text-white">{defaultRec.timeframe}</span>
      </div>

      {/* Risks */}
      {defaultRec.risks && defaultRec.risks.length > 0 && (
        <div className="pt-3 border-t border-white/5">
          <div className="text-xs text-gray-500 mb-2">⚠️ 风险提示</div>
          <div className="flex flex-wrap gap-1">
            {defaultRec.risks.map((risk, index) => (
              <span
                key={index}
                className="text-xs px-2 py-1 rounded bg-accent-red/10 text-accent-red"
              >
                {risk}
              </span>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
