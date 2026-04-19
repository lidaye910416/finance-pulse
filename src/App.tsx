import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { listen } from '@tauri-apps/api/event';
import {
  DashboardHome,
  AStockSentiment,
  MacroData,
  PositionManagement,
  News,
  PredictionMarket,
  Tools,
  StrategicAnalysis,
} from './pages';

const tabs = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/a-stock', label: '行情', icon: '📊' },
  { path: '/macro', label: '宏观', icon: '📈' },
  { path: '/position', label: '仓位', icon: '🎯' },
  { path: '/news', label: '资讯', icon: '📰' },
  { path: '/prediction', label: '预测', icon: '🔮' },
  { path: '/tools', label: '工具', icon: '⚙️' },
];

interface HeaderProps {
  lastUpdate: Date | null;
  onRefresh: () => void;
  isRefreshing: boolean;
}

function Header({ lastUpdate, onRefresh, isRefreshing }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5">
      <div className="max-w-lg mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-blue to-accent-green flex items-center justify-center shadow-glow-blue">
                <span className="text-lg">📊</span>
              </div>
            </div>
            <div>
              <h1 className="text-lg font-display font-bold bg-gradient-to-r from-white via-white to-gray-400 bg-clip-text text-transparent">
                FinancePulse
              </h1>
              <p className="text-[10px] text-gray-500 font-mono tracking-wider">FINANCIAL DASHBOARD</p>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider">Last Update</div>
              <div className="text-sm font-mono text-gray-300">
                {lastUpdate
                  ? lastUpdate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
                  : '--:--'}
              </div>
            </div>

            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className={`
                w-10 h-10 rounded-xl
                flex items-center justify-center
                border border-white/10
                transition-all duration-200
                btn-press
                ${isRefreshing
                  ? 'text-gray-500 cursor-not-allowed'
                  : 'text-accent-blue hover:bg-accent-blue/10 hover:border-accent-blue/30 hover:shadow-glow-blue'
                }
              `}
              title="Refresh"
            >
              <svg
                className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

function BottomNav() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 glass border-t border-white/5 safe-bottom">
      <div className="max-w-lg mx-auto px-2 py-2">
        <div className="flex justify-around items-center">
          {tabs.map((tab, index) => {
            const isActive = location.pathname === tab.path;
            return (
              <Link
                key={tab.path}
                to={tab.path}
                className={`
                  relative flex flex-col items-center
                  py-1.5 px-3
                  rounded-xl
                  transition-all duration-200
                  btn-press animate-slide-in
                  ${isActive
                    ? 'text-accent-blue'
                    : 'text-gray-500 hover:text-gray-300'
                  }
                `}
                style={{ animationDelay: `${index * 30}ms` }}
              >
                {isActive && (
                  <div className="absolute inset-0 bg-accent-blue/10 rounded-xl border border-accent-blue/20" />
                )}
                <span className={`text-xl relative z-10 ${isActive ? 'filter drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]' : ''}`}>
                  {tab.icon}
                </span>
                <span className={`text-[10px] mt-0.5 font-medium relative z-10 ${isActive ? 'text-accent-blue' : ''}`}>
                  {tab.label}
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

function App() {
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true);
    setTimeout(() => {
      setLastUpdate(new Date());
      setIsRefreshing(false);
    }, 800);
  }, []);

  useEffect(() => {
    const unlisten = listen('refresh-data', () => {
      handleRefresh();
    });

    return () => {
      unlisten.then((fn) => fn());
    };
  }, [handleRefresh]);

  useEffect(() => {
    setLastUpdate(new Date());
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-void text-white pb-24">
        <Header lastUpdate={lastUpdate} onRefresh={handleRefresh} isRefreshing={isRefreshing} />

        <main className="max-w-lg mx-auto px-4 pt-20">
          <Routes>
            <Route path="/" element={<DashboardHome />} />
            <Route path="/a-stock" element={<AStockSentiment />} />
            <Route path="/macro" element={<MacroData />} />
            <Route path="/position" element={<PositionManagement />} />
            <Route path="/news" element={<News />} />
            <Route path="/prediction" element={<PredictionMarket />} />
            <Route path="/tools" element={<Tools />} />
            <Route path="/strategic" element={<StrategicAnalysis />} />
          </Routes>
        </main>

        <BottomNav />
      </div>
    </BrowserRouter>
  );
}

export default App;
