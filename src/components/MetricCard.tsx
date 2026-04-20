interface MetricCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: string;
  animationDelay?: number;
  onClick?: () => void;
}

export function MetricCard({
  label,
  value,
  subValue,
  trend = 'neutral',
  icon,
  animationDelay = 0,
  onClick
}: MetricCardProps) {
  const trendConfig = {
    up: {
      border: 'border-l-accent-green',
      text: 'text-accent-green',
      glow: 'shadow-glow-green',
    },
    down: {
      border: 'border-l-accent-red',
      text: 'text-accent-red',
      glow: 'shadow-glow-red',
    },
    neutral: {
      border: 'border-l-accent-blue',
      text: 'text-white',
      glow: '',
    },
  };

  const config = trendConfig[trend];

  return (
    <div
      className={`
        relative bg-surface-100/80
        border-l-2 ${config.border}
        rounded-2xl p-4
        border border-white/5
        hover:bg-surface-200
        hover:border-white/10
        transition-all duration-200
        animate-fade-in-up
        ${config.glow}
        ${onClick ? 'cursor-pointer' : ''}
      `}
      style={{ animationDelay: `${animationDelay}ms` }}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-display font-medium text-gray-500 uppercase tracking-wider">
          {label}
        </span>
        {icon && (
          <span className="text-lg opacity-80">{icon}</span>
        )}
      </div>

      {/* Value */}
      <div className={`text-2xl font-display font-bold ${config.text} font-mono`}>
        {value}
      </div>

      {/* Sub Value */}
      {subValue && (
        <div className="text-xs text-gray-500 mt-1 font-mono">
          {subValue}
        </div>
      )}

      {/* Trend Indicator */}
      {trend !== 'neutral' && (
        <div className={`absolute top-3 right-3 ${config.text}`}>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {trend === 'up' ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            )}
          </svg>
        </div>
      )}
    </div>
  );
}
