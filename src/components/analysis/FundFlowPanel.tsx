import { Card } from '../Card';

interface FundFlowPanelProps {
  northbound?: number;
  sentiment?: 'fear' | 'greed' | 'neutral';
}

/**
 * FundFlowPanel Component
 * PRD Section 12.1 - Fund flow display panel
 * Note: Full implementation may require additional API endpoints
 */
export function FundFlowPanel({
  northbound = 0,
  sentiment = 'neutral'
}: FundFlowPanelProps) {
  const sentimentEmoji = {
    fear: '😰',
    greed: '🤑',
    neutral: '😐'
  };

  const sentimentText = {
    fear: '恐惧',
    greed: '贪婪',
    neutral: '中性'
  };

  return (
    <Card>
      <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider mb-4">
        💰 资金流向
      </h3>
      
      <div className="space-y-4">
        {/* Northbound */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">北向资金</span>
          <span className={`text-sm font-medium ${
            northbound > 0 ? 'text-accent-green' : northbound < 0 ? 'text-accent-red' : 'text-gray-400'
          }`}>
            {northbound > 0 ? '+' : ''}{northbound.toFixed(1)}亿
          </span>
        </div>

        {/* Sentiment */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">市场情绪</span>
          <span className="text-sm font-medium text-white">
            {sentimentEmoji[sentiment]} {sentimentText[sentiment]}
          </span>
        </div>

        {/* Placeholder for future fund flow data */}
        <div className="pt-2 border-t border-white/5">
          <div className="text-xs text-gray-500">
            更多资金流向数据待接入...
          </div>
        </div>
      </div>
    </Card>
  );
}
