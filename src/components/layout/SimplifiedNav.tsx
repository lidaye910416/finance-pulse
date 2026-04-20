import { Link, useLocation } from 'react-router-dom';

const tabs = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/data', label: '数据', icon: '📊' },
  { path: '/analysis', label: '分析', icon: '🧠' },
  { path: '/mine', label: '我的', icon: '👤' },
];

export function SimplifiedNav() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 glass border-t border-white/5 safe-bottom">
      <div className="max-w-lg mx-auto px-4 py-2">
        <div className="flex justify-around items-center">
          {tabs.map((tab, index) => {
            const isActive = location.pathname === tab.path;
            return (
              <Link
                key={tab.path}
                to={tab.path}
                className={`
                  relative flex flex-col items-center
                  py-2 px-6
                  rounded-xl
                  transition-all duration-200
                  btn-press animate-fade-in-up
                  ${isActive
                    ? 'text-accent-blue'
                    : 'text-gray-500 hover:text-gray-300'
                  }
                `}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {isActive && (
                  <div className="absolute inset-0 bg-accent-blue/10 rounded-xl border border-accent-blue/20" />
                )}
                <span className={`text-2xl relative z-10 ${isActive ? 'filter drop-shadow-[0_0_8px_rgba(59,130,246,0.5)]' : ''}`}>
                  {tab.icon}
                </span>
                <span className={`text-xs mt-1 font-medium relative z-10 ${isActive ? 'text-accent-blue' : ''}`}>
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
