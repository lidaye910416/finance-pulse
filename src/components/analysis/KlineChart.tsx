import { useState, useEffect } from 'react';
import { Card } from '../Card';

type Period = 'daily' | 'weekly' | 'monthly';

interface KlineChartProps {
  stockCode?: string;  // 默认贵州茅台 600519
}

interface KLineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// 获取K线数据的函数
async function fetchKLineData(code: string, period: Period = 'daily'): Promise<KLineData[]> {
  // 格式化股票代码
  const formatCode = (c: string) => {
    if (c.startsWith('6')) return `1.${c}`;
    if (c.startsWith('0') || c.startsWith('3')) return `0.${c}`;
    return c;
  };

  const periodMap: Record<Period, string> = {
    'daily': '101',
    'weekly': '102',
    'monthly': '103',
  };

  const url = `https://push2.eastmoney.com/api/qt/stock/kline/get`;
  const params = new URLSearchParams({
    secid: formatCode(code),
    fields1: 'f1,f2,f3,f4,f5,f6',
    fields2: 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
    klt: periodMap[period],
    fqt: '1',
    beg: '0',
    end: '20500101',
    lmt: '30',  // 最近30天
  });

  try {
    const response = await fetch(`${url}?${params.toString()}`);
    if (!response.ok) return [];

    const data = await response.json();
    const klines = data.data?.klines || [];

    return klines.map((k: string) => {
      const [date, open, close, high, low, volume] = k.split(',');
      return {
        date: date.substring(5),  // 截取 MM-DD 格式
        open: parseFloat(open),
        close: parseFloat(close),
        high: parseFloat(high),
        low: parseFloat(low),
        volume: parseFloat(volume),
      };
    });
  } catch (error) {
    console.error('获取K线数据失败:', error);
    return [];
  }
}

/**
 * KlineChart Component
 * PRD Section 12.1 - K-line chart with daily/weekly/monthly period switching
 * 默认显示贵州茅台 (600519)
 * API 失败时显示空状态，不使用模拟数据
 */
export function KlineChart({ stockCode = '600519' }: KlineChartProps) {
  const [period, setPeriod] = useState<Period>('daily');
  const [chartData, setChartData] = useState<KLineData[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      const data = await fetchKLineData(stockCode, period);
      setChartData(data);  // API 失败时返回空数组
      setLoading(false);
    };

    loadData();
  }, [stockCode, period]);

  const periods: { id: Period; label: string }[] = [
    { id: 'daily', label: '日K' },
    { id: 'weekly', label: '周K' },
    { id: 'monthly', label: '月K' },
  ];

  // 计算价格范围
  const maxHigh = Math.max(...chartData.map(d => d.high));
  const minLow = Math.min(...chartData.map(d => d.low));
  const range = maxHigh - minLow || 1;

  // 计算涨跌幅
  const firstClose = chartData[0]?.close || 0;
  const lastClose = chartData[chartData.length - 1]?.close || 0;
  const changePercent = firstClose > 0 ? ((lastClose - firstClose) / firstClose * 100).toFixed(2) : '0.00';
  const isUp = lastClose >= firstClose;

  return (
    <Card className="h-[300px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-display font-semibold text-gray-400 uppercase tracking-wider">
            📈 贵州茅台
          </h3>
          <span className={`text-xs font-mono ${isUp ? 'text-accent-green' : 'text-accent-red'}`}>
            {isUp ? '+' : ''}{changePercent}%
          </span>
        </div>
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

      {/* Stock code */}
      <div className="text-xs text-gray-500 mb-2">股票代码: {stockCode}</div>

      {/* Chart area */}
      <div className="relative h-[200px]">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface-100/50 z-10">
            <span className="text-gray-400">加载中...</span>
          </div>
        )}

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
            const isUpCandle = item.close >= item.open;

            return (
              <div
                key={index}
                className="flex-1 flex flex-col items-center"
                style={{ height: '100%', justifyContent: 'flex-end' }}
              >
                {/* High-Low line with body */}
                <div
                  className="w-full relative"
                  style={{ height: `${Math.max(height, 10)}%` }}
                >
                  {/* Candle body */}
                  <div
                    className={`absolute left-1/2 -translate-x-1/2 w-3/4 rounded-sm
                      ${isUpCandle ? 'bg-accent-green' : 'bg-accent-red'}`}
                    style={{
                      top: `${((item.high - Math.max(item.open, item.close)) / (item.high - item.low || 1)) * 100}%`,
                      height: `${(Math.abs(item.close - item.open) / (item.high - item.low || 1)) * 100}%`,
                      minHeight: '4px',
                    }}
                  />
                  {/* Wick */}
                  <div
                    className={`absolute left-1/2 -translate-x-1/2 w-px
                      ${isUpCandle ? 'bg-accent-green' : 'bg-accent-red'}`}
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
