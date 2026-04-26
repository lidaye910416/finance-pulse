import { useState } from 'react';
import { Card } from '../Card';

type Period = 'daily' | 'weekly' | 'monthly';

interface KlineChartProps {
  data?: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

/**
 * KlineChart Component
 * PRD Section 12.1 - K-line chart with daily/weekly/monthly period switching
 */
export function KlineChart({ data }: KlineChartProps) {
  const [period, setPeriod] = useState<Period>('daily');

  // Mock data if no data provided
  const chartData = data || [
    { date: '05-01', open: 3200, high: 3250, low: 3180, close: 3230, volume: 2500000 },
    { date: '05-02', open: 3230, high: 3280, low: 3220, close: 3265, volume: 2800000 },
    { date: '05-03', open: 3265, high: 3300, low: 3250, close: 3280, volume: 3100000 },
    { date: '05-04', open: 3280, high: 3320, low: 3265, close: 3305, volume: 2900000 },
    { date: '05-05', open: 3305, high: 3340, low: 3290, close: 3320, volume: 3200000 },
    { date: '05-06', open: 3320, high: 3350, low: 3305, close: 3310, volume: 2700000 },
    { date: '05-07', open: 3310, high: 3330, low: 3280, close: 3295, volume: 2400000 },
  ];

  const periods: { id: Period; label: string }[] = [
    { id: 'daily', label: '日K' },
    { id: 'weekly', label: '周K' },
    { id: 'monthly', label: '月K' },
  ];

  // Simple bar chart representation
  const maxHigh = Math.max(...chartData.map(d => d.high));
  const minLow = Math.min(...chartData.map(d => d.low));
  const range = maxHigh - minLow || 1;

  return (
    <Card className="h-[300px]">
      {/* Header with period selector */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider">
          📈 K线走势
        </h3>
        <div className="flex gap-1 bg-surface-200 rounded-lg p-1">
          {periods.map((p) => (
            <button
              key={p.id}
              onClick={() => setPeriod(p.id)}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors
                ${period === p.id 
                  ? 'bg-accent-blue text-white' 
                  : 'text-gray-400 hover:text-white'}`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart area */}
      <div className="relative h-[200px]">
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-xs text-gray-500 font-mono">
          <span>{maxHigh.toFixed(0)}</span>
          <span>{((maxHigh + minLow) / 2).toFixed(0)}</span>
          <span>{minLow.toFixed(0)}</span>
        </div>

        {/* Chart bars */}
        <div className="absolute left-8 right-0 top-0 bottom-4 flex items-end justify-between gap-1">
          {chartData.map((item, index) => {
            const height = ((item.high - item.low) / range) * 100;
            const isUp = item.close >= item.open;
            
            return (
              <div
                key={index}
                className="flex-1 flex flex-col items-center"
                style={{ height: '100%', justifyContent: 'flex-end' }}
              >
                {/* High-Low line with body */}
                <div
                  className="w-full relative"
                  style={{ height: `${height}%` }}
                >
                  {/* Candle body */}
                  <div
                    className={`absolute left-1/2 -translate-x-1/2 w-3/4 rounded-sm
                      ${isUp ? 'bg-accent-green' : 'bg-accent-red'}`}
                    style={{
                      top: `${((item.high - Math.max(item.open, item.close)) / (item.high - item.low)) * 100}%`,
                      height: `${(Math.abs(item.close - item.open) / (item.high - item.low)) * 100}%`,
                      minHeight: '4px',
                    }}
                  />
                  {/* Wick */}
                  <div
                    className={`absolute left-1/2 -translate-x-1/2 w-px
                      ${isUp ? 'bg-accent-green' : 'bg-accent-red'}`}
                    style={{
                      top: '0',
                      height: '100%',
                    }}
                  />
                </div>
                {/* Date label */}
                <span className="text-xs text-gray-500 mt-1">{item.date}</span>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
