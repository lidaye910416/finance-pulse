import { Card } from '../Card';

interface Signal {
  analyst: string;
  avatar: string;
  signal: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
}

interface SignalPanelProps {
  signals?: Signal[];
  debateResult?: {
    bullishConfidence: number;
    bearishConfidence: number;
    gap: number;
    converged: boolean;
  };
}

/**
 * SignalPanel Component
 * PRD Section 12.2 - Display 5 analyst signals with confidence bars
 */
export function SignalPanel({ signals, debateResult }: SignalPanelProps) {
  const defaultSignals: Signal[] = signals || [
    { analyst: '多头研究员', avatar: '🐂', signal: 'bullish', confidence: 72 },
    { analyst: '空头研究员', avatar: '🐻', signal: 'bearish', confidence: 58 },
    { analyst: '技术分析师', avatar: '📊', signal: 'bullish', confidence: 65 },
    { analyst: '基本面分析师', avatar: '📈', signal: 'neutral', confidence: 55 },
    { analyst: '情绪分析师', avatar: '💭', signal: 'bullish', confidence: 68 },
  ];

  const debate = debateResult || {
    bullishConfidence: 70,
    bearishConfidence: 55,
    gap: 15,
    converged: true,
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish': return 'bg-accent-green';
      case 'bearish': return 'bg-accent-red';
      default: return 'bg-gray-500';
    }
  };

  const getSignalBadge = (signal: string) => {
    switch (signal) {
      case 'bullish': return { text: '看多', color: 'text-accent-green bg-accent-green/10' };
      case 'bearish': return { text: '看空', color: 'text-accent-red bg-accent-red/10' };
      default: return { text: '中性', color: 'text-gray-400 bg-gray-500/10' };
    }
  };

  return (
    <Card>
      <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider mb-4">
        📊 分析师信号
      </h3>

      {/* 5 Analyst Signals */}
      <div className="space-y-3">
        {defaultSignals.map((signal, index) => {
          const badge = getSignalBadge(signal.signal);
          return (
            <div key={index} className="flex items-center gap-3">
              {/* Avatar */}
              <div className="w-8 h-8 rounded-full bg-surface-200 flex items-center justify-center text-sm">
                {signal.avatar}
              </div>
              
              {/* Name and badge */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-white truncate">{signal.analyst}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${badge.color}`}>
                    {badge.text}
                  </span>
                </div>
                {/* Confidence bar */}
                <div className="mt-1 h-1.5 bg-surface-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${getSignalColor(signal.signal)}`}
                    style={{ width: `${signal.confidence}%` }}
                  />
                </div>
              </div>
              
              {/* Confidence value */}
              <span className="text-sm font-mono text-gray-400 w-10 text-right">
                {signal.confidence}%
              </span>
            </div>
          );
        })}
      </div>

      {/* Debate Result */}
      {debateResult && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="text-xs text-gray-500 mb-2">多空辩论结果</div>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <div className="text-xs text-accent-green mb-1">多头 {debate.bullishConfidence}%</div>
              <div className="h-1.5 bg-surface-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent-green rounded-full"
                  style={{ width: `${debate.bullishConfidence}%` }}
                />
              </div>
            </div>
            <div className="text-xs text-gray-500">
              差距 {debate.gap}%
            </div>
            <div className="flex-1">
              <div className="text-xs text-accent-red mb-1 text-right">空头 {debate.bearishConfidence}%</div>
              <div className="h-1.5 bg-surface-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent-red rounded-full"
                  style={{ width: `${debate.bearishConfidence}%` }}
                />
              </div>
            </div>
          </div>
          {debate.converged && (
            <div className="text-xs text-accent-blue mt-2 text-center">
              ✓ 辩论已收敛
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
