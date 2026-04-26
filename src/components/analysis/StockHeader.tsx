import { useState } from 'react';

interface StockHeaderProps {
  code?: string;
  name?: string;
  price?: number;
  change?: number;
  changePercent?: number;
  onSearch?: (code: string) => void;
}

/**
 * StockHeader Component
 * PRD Section 12.1 - Stock search and basic quote display
 */
export function StockHeader({
  code,
  name = '未知',
  price = 0,
  change = 0,
  changePercent = 0,
  onSearch
}: StockHeaderProps) {
  const [searchCode, setSearchCode] = useState(code || '');

  const handleSearch = () => {
    if (searchCode.trim() && onSearch) {
      onSearch(searchCode.trim());
    }
  };

  const isPositive = change >= 0;

  return (
    <div className="space-y-3">
      {/* Search Bar */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={searchCode}
            onChange={(e) => setSearchCode(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="输入股票代码 (如 600519)"
            className="w-full bg-surface-200 border border-white/10 rounded-xl px-4 py-3 
                       text-white placeholder-gray-500
                       focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/20
                       transition-all"
          />
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">
            🔍
          </span>
        </div>
        <button
          onClick={handleSearch}
          className="px-6 py-3 bg-accent-blue rounded-xl text-white font-medium
                     hover:bg-accent-blue/90 transition-colors btn-press"
        >
          搜索
        </button>
      </div>

      {/* Stock Info */}
      {code && (
        <div className="bg-surface-100/50 rounded-xl p-4 border border-white/5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-blue/20 to-accent-green/20 
                              flex items-center justify-center text-xl font-bold text-white">
                {name.charAt(0)}
              </div>
              <div>
                <div className="text-lg font-bold text-white">{name}</div>
                <div className="text-sm text-gray-500">{code}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-white font-mono">
                ¥{price.toFixed(2)}
              </div>
              <div className={`text-sm font-medium ${isPositive ? 'text-accent-green' : 'text-accent-red'}`}>
                {isPositive ? '+' : ''}{change.toFixed(2)} ({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
