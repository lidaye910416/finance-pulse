import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Card, MetricCard, Badge } from '../components';
import { fetchFearGreedIndex, fetchNorthboundData, fetchLimitUpDown } from '../services/api/marketData';
import { API_BASE_URL } from '../services/api/apiService';

// 仓位铁律
const positionRules = [
  { rule: '不轻易满仓，保留20-30%现金', status: 'ok' },
  { rule: '单票不超过总仓位30%', status: 'ok' },
  { rule: '分批建仓，首次不超过30%', status: 'ok' },
];

// 快捷操作
const quickActions = [
  { id: 'analysis', icon: '🧠', label: 'AI分析', path: '/analysis', color: 'blue' },
  { id: 'data', icon: '📊', label: '市场数据', path: '/data', color: 'green' },
  { id: 'macro', icon: '📈', label: '宏观数据', path: '/data', color: 'yellow' },
  { id: 'position', icon: '🎯', label: '仓位管理', path: '/mine', color: 'purple' },
];

// 类型定义
interface NewsItem {
  id: string;
  title: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  time: string;
}

interface HotStockItem {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

// 获取热门股票
async function fetchHotStocks(limit: number = 10): Promise<HotStockItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/hot-stocks?limit=${limit}`);
    if (response.ok) {
      const data = await response.json();
      return data.items || [];
    }
  } catch (error) {
    console.error('获取热门股票失败:', error);
  }
  return [];
}

// 获取两融余额（API失败返回 null）
async function fetchMarginBalance(): Promise<number | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/margin-balance`);
    if (response.ok) {
      const data = await response.json();
      return data.balance;
    }
  } catch (error) {
    console.error('获取两融余额失败:', error);
  }
  return null;  // API 失败返回 null
}

// 获取快讯（API失败返回空数组）
async function fetchFastNews(): Promise<NewsItem[]> {
  try {
    // 东方财富快讯API
    const url = `https://np-listapi.eastmoney.com/comm/web/getFastNewsList?cb=jQuery&client=web&page=1&pageSize=20&endTime=&keyword=&order=1`;
    const response = await fetch(url);
    if (!response.ok) return [];

    const data = await response.json();
    return data.list || [];
  } catch (error) {
    console.error('获取快讯失败:', error);
    return [];  // API 失败返回空数组
  }
}

export function HomePage() {
  const navigate = useNavigate();

  // 实时数据状态（初始化为 * / 空值）
  const [fearGreed, setFearGreed] = useState({ value: 0, phase: '-' });
  const [northbound, setNorthbound] = useState({ value: 0, trend: 'down' as 'up' | 'down' });
  const [marketMetrics, setMarketMetrics] = useState({
    limitUp: 0,
    limitDown: 0,
    marginBalance: null as number | null,
  });
  const [news, setNews] = useState<NewsItem[]>([]);
  const [hotStocks, setHotStocks] = useState<HotStockItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // 格式化更新时间
  const formatLastUpdate = () => {
    if (!lastUpdate) return '-';
    return lastUpdate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  // 加载实时数据（页面加载时 + 30秒定时刷新）
  useEffect(() => {
    const REFRESH_INTERVAL = 30000; // 30秒刷新一次

    const loadData = async () => {
      try {
        setIsLoading(true);
        const [fg, nb, ld, hs, mb, fn] = await Promise.all([
          fetchFearGreedIndex(),
          fetchNorthboundData(1),
          fetchLimitUpDown(),
          fetchHotStocks(5),
          fetchMarginBalance(),
          fetchFastNews(),
        ]);
        // API 成功时才更新，失败保持 * 显示
        if (fg) setFearGreed(fg);
        if (nb.length > 0) {
          setNorthbound({
            value: nb[0]?.total ?? 0,
            trend: (nb[0]?.total ?? 0) >= 0 ? 'up' : 'down',
          });
        }
        if (ld) {
          setMarketMetrics({
            limitUp: ld.limitUp,
            limitDown: ld.limitDown,
            marginBalance: mb,
          });
        }
        if (hs.length > 0) setHotStocks(hs);
        if (fn.length > 0) setNews(fn);
        setLastUpdate(new Date());
      } catch (error) {
        console.error('加载数据失败:', error);
      } finally {
        setIsLoading(false);
      }
    };

    // 首次加载
    loadData();

    // 每30秒定时刷新
    const intervalId = setInterval(loadData, REFRESH_INTERVAL);

    // 组件卸载时清除定时器
    return () => clearInterval(intervalId);
  }, []);

  // 仓位建议计算（数据无效时显示 *）
  const getPositionAdvice = () => {
    if (!fearGreed.value || fearGreed.value < 30) return { range: '*', phase: '-', color: 'gray' };
    if (fearGreed.value < 50) return { range: '30-50%', phase: '分歧', color: 'yellow' };
    if (fearGreed.value < 70) return { range: '20-40%', phase: '乐观', color: 'yellow' };
    return { range: '10-30%', phase: '亢奋', color: 'red' };
  };

  const positionAdvice = getPositionAdvice();

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* 标题 */}
      <div className="text-center pt-4">
        <h1 className="text-2xl font-display font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
          今日概览
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          {new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}
        </p>
      </div>

      {/* 数据更新状态栏 */}
      <Card className="border-accent-blue/20 bg-accent-blue/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-accent-yellow animate-pulse' : 'bg-accent-green animate-pulse'}`}></div>
            <span className="text-sm text-gray-300">{isLoading ? '数据加载中...' : '数据已更新'}</span>
          </div>
          <div className="text-xs text-gray-500">
            {lastUpdate ? `上次更新: ${formatLastUpdate()}` : '每30秒自动刷新'}
          </div>
        </div>
      </Card>

      {/* 🎯 仓位仪表盘 (position-management skill) */}
      <Card className="border-accent-yellow/20 bg-gradient-to-br from-surface-100/80 to-accent-yellow/5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">🎯</span>
            <span className="text-sm font-medium text-gray-300">仓位建议</span>
          </div>
          <button
            className="text-xs text-accent-blue hover:underline"
            onClick={() => navigate('/mine')}
          >
            详情 →
          </button>
        </div>

        <div className="text-center mb-3">
          <div className="text-3xl font-bold text-accent-yellow font-mono">{positionAdvice.range}</div>
          <Badge text={positionAdvice.phase} variant={positionAdvice.color as 'green' | 'yellow' | 'red'} />
        </div>

        {/* 仓位滑块 */}
        <div className="relative pt-6 pb-2">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>0%</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
          </div>
          <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-accent-green via-accent-yellow to-accent-red rounded-full relative">
              <div
                className="absolute top-0 bottom-0 bg-white/20 border-l border-r border-white/30"
                style={{
                  left: fearGreed.value < 30 ? '40%' : fearGreed.value < 50 ? '30%' : '20%',
                  width: '20%',
                }}
              />
              <div
                className="absolute top-1/2 -translate-y-1/2 w-2 h-5 bg-white rounded-full shadow-lg"
                style={{ left: `${Math.min(50 + fearGreed.value / 2, 95)}%` }}
              />
            </div>
          </div>
        </div>

        {/* 仓位铁律快速检查 */}
        <div className="mt-3 pt-3 border-t border-white/10">
          <div className="text-xs text-gray-500 mb-2">铁律检查</div>
          <div className="flex gap-2 flex-wrap">
            {positionRules.map((r, i) => (
              <span key={i} className="text-xs bg-accent-green/20 text-accent-green px-2 py-1 rounded-full">
                ✓ {r.rule.slice(0, 12)}...
              </span>
            ))}
          </div>
        </div>
      </Card>

      {/* 核心指标 (market-sentiment + a-stock-premarket-briefing skills) */}
      <div>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          核心指标
        </h2>
        <div className="grid grid-cols-2 gap-3">
          <MetricCard
            label="恐惧贪婪"
            value={fearGreed.value}
            trend={fearGreed.value < 30 ? 'down' : fearGreed.value > 70 ? 'up' : 'neutral'}
            icon="😰"
            onClick={() => navigate('/data')}
          />
          <MetricCard
            label="北向资金"
            value={`${northbound.value >= 0 ? '+' : ''}${northbound.value.toFixed(1)}亿`}
            trend={northbound.trend}
            icon="🌊"
            onClick={() => navigate('/data')}
          />
          <MetricCard
            label="涨停"
            value={`${marketMetrics.limitUp}家`}
            subValue={marketMetrics.limitUp < 30 ? '偏冰点' : marketMetrics.limitUp > 60 ? '偏亢奋' : '正常'}
            trend={marketMetrics.limitUp < 30 ? 'down' : marketMetrics.limitUp > 60 ? 'up' : 'neutral'}
            icon="📈"
            onClick={() => navigate('/data')}
          />
          <MetricCard
            label="两融余额"
            value={marketMetrics.marginBalance ? `${marketMetrics.marginBalance.toFixed(2)}万亿` : '*'}
            trend="down"
            icon="💰"
            onClick={() => navigate('/data')}
          />
        </div>
      </div>

      {/* 快捷操作 */}
      <div>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          快捷操作
        </h2>
        <div className="grid grid-cols-4 gap-2">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => navigate(action.path)}
              className={`
                flex flex-col items-center p-4 rounded-2xl
                bg-surface-200/50 border border-white/5
                hover:border-white/20 transition-all duration-200
                btn-press animate-fade-in-up
              `}
            >
              <span className="text-2xl mb-1">{action.icon}</span>
              <span className="text-xs text-gray-300">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 📰 快讯 (market-news skill) */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            市场快讯
          </h2>
          <button
            onClick={() => navigate('/news')}
            className="text-xs text-accent-blue hover:underline"
          >
            查看更多 →
          </button>
        </div>
        <Card>
          <div className="space-y-3">
            {news.map((newsItem) => (
              <div
                key={newsItem.id}
                className="flex items-start gap-3 py-2 border-b border-white/5 last:border-0 cursor-pointer hover:bg-surface-200/30 -mx-2 px-2 rounded-lg transition-colors"
                onClick={() => navigate('/news')}
              >
                <span className={`
                  text-lg
                  ${newsItem.sentiment === 'positive' ? 'text-accent-green' : ''}
                  ${newsItem.sentiment === 'negative' ? 'text-accent-red' : ''}
                  ${newsItem.sentiment === 'neutral' ? 'text-gray-400' : ''}
                `}>
                  {newsItem.sentiment === 'positive' ? '📈' : newsItem.sentiment === 'negative' ? '📉' : '📊'}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-200 line-clamp-2">{newsItem.title}</div>
                  <div className="text-xs text-gray-500 mt-1">{newsItem.time}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 热门股票 */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            热门股票
          </h2>
          <button
            onClick={() => navigate('/analysis')}
            className="text-xs text-accent-blue hover:underline"
          >
            AI分析 →
          </button>
        </div>
        <Card>
          <div className="space-y-3">
            {hotStocks.map((stock) => (
              <div
                key={stock.code}
                className="flex justify-between items-center cursor-pointer hover:bg-surface-200/30 rounded-lg p-2 -mx-2 transition-colors"
                onClick={() => navigate('/analysis')}
              >
                <div>
                  <div className="text-white font-medium">{stock.name}</div>
                  <div className="text-xs text-gray-500">{stock.code}</div>
                </div>
                <div className="text-right">
                  <div className="text-white font-mono">¥{stock.price.toFixed(2)}</div>
                  <Badge
                    text={`${stock.change > 0 ? '+' : ''}${stock.change.toFixed(2)}%`}
                    variant={stock.change > 0 ? 'green' : 'red'}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* 快捷操作 */}
      <div>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          快捷操作
        </h2>
        <div className="grid grid-cols-4 gap-2">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => navigate(action.path)}
              className="flex flex-col items-center p-4 rounded-2xl bg-surface-200/50 border border-white/5 hover:border-white/20 transition-all duration-200 btn-press animate-fade-in-up"
            >
              <span className="text-2xl mb-1">{action.icon}</span>
              <span className="text-xs text-gray-300">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* AI分析入口 */}
      <Card
        className="cursor-pointer hover:border-accent-blue/50 transition-all"
        onClick={() => navigate('/analysis')}
      >
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center shadow-glow-blue">
            <span className="text-3xl">🧠</span>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-white">AI 智能分析</h3>
            <p className="text-sm text-gray-400">选择专业分析师，获取个性化投资建议</p>
          </div>
          <span className="text-accent-blue">→</span>
        </div>
      </Card>
    </div>
  );
}
