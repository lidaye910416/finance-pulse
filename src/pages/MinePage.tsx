import { useState } from 'react';
import { Card, Badge } from '../components';
import { LLMSettings } from '../components/settings/LLMSettings';

// 自选股数据
const watchlist = [
  { code: '600519', name: '贵州茅台', price: 1688.0, change: -1.2, position: 10, cost: 1750.0 },
  { code: '000858', name: '五粮液', price: 145.6, change: -0.9, position: 100, cost: 150.0 },
  { code: '300750', name: '宁德时代', price: 186.5, change: 2.3, position: 50, cost: 180.0 },
];

// 仓位数据
const positionData = {
  totalValue: 56890,
  totalCost: 57500,
  position: 48,
  recommendedPosition: '40-60%',
  rules: [
    '不轻易满仓，保留20-30%现金',
    '单票不超过总仓位30%',
    '分批建仓，首次不超过30%',
    '动态调整，每周评估一次',
    '单票亏损超过8%必须止损',
  ],
};

// 设置项
const settings = [
  { id: 'notifications', label: '消息通知', icon: '🔔', type: 'toggle' as const, value: true },
  { id: 'sound', label: '声音提醒', icon: '🔊', type: 'toggle' as const, value: false },
  { id: 'autoRefresh', label: '自动刷新', icon: '🔄', type: 'toggle' as const, value: true },
  { id: 'refreshInterval', label: '刷新间隔', icon: '⏱️', type: 'select' as const, value: '1min' },
  { id: 'theme', label: '深色模式', icon: '🌙', type: 'toggle' as const, value: true },
];

const tabs = [
  { id: 'watchlist', label: '自选股', icon: '⭐' },
  { id: 'position', label: '仓位', icon: '🎯' },
  { id: 'tools', label: '工具箱', icon: '🧰' },
  { id: 'settings', label: '设置', icon: '⚙️' },
];

export function MinePage() {
  const [activeTab, setActiveTab] = useState('watchlist');
  const [showLLMSettings, setShowLLMSettings] = useState(false);

  const totalProfit = positionData.totalValue - positionData.totalCost;
  const profitPercent = (totalProfit / positionData.totalCost * 100).toFixed(2);

  return (
    <div className="space-y-4 animate-fade-in-up pt-4">
      {/* 标题 */}
      <div className="text-center">
        <h1 className="text-2xl font-display font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
          我的
        </h1>
      </div>

      {/* 标签切换 */}
      <div className="flex gap-2 p-1 bg-surface-200/30 rounded-xl">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg
              transition-all duration-200 btn-press
              ${activeTab === tab.id
                ? 'bg-accent-blue/20 text-accent-blue border border-accent-blue/30'
                : 'text-gray-400 hover:text-white'
              }
            `}
          >
            <span>{tab.icon}</span>
            <span className="text-sm font-medium">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* 自选股 */}
      {activeTab === 'watchlist' && (
        <div className="space-y-4">
          <Card title="我的自选">
            <div className="space-y-3">
              {watchlist.map((stock) => {
                const profit = (stock.price - stock.cost) * stock.position;
                const profitPercent = ((stock.price - stock.cost) / stock.cost * 100).toFixed(2);
                const isProfit = stock.price >= stock.cost;
                return (
                  <div
                    key={stock.code}
                    className="flex justify-between items-center py-2 border-b border-white/5 last:border-0"
                  >
                    <div>
                      <div className="text-white font-medium">{stock.name}</div>
                      <div className="text-xs text-gray-500">
                        {stock.code} · 持仓 {stock.position}股 · 成本 ¥{stock.cost}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-white font-mono">¥{stock.price.toFixed(2)}</div>
                      <Badge
                        text={`${isProfit ? '+' : ''}${profit.toFixed(0)} (${isProfit ? '+' : ''}${profitPercent}%)`}
                        variant={isProfit ? 'green' : 'red'}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card title="添加自选">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="输入股票代码"
                className="flex-1 bg-surface-200/50 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-blue/50"
              />
              <button className="px-6 py-3 bg-accent-blue rounded-xl text-white font-medium hover:bg-accent-blue/80 transition-colors btn-press">
                添加
              </button>
            </div>
          </Card>
        </div>
      )}

      {/* 仓位管理 */}
      {activeTab === 'position' && (
        <div className="space-y-4">
          <Card>
            <div className="text-center mb-4">
              <div className="text-gray-400 text-sm mb-1">当前建议仓位</div>
              <div className="text-3xl font-bold text-accent-yellow">{positionData.recommendedPosition}</div>
              <Badge text="冰点/修复阶段" variant="green" />
            </div>

            <div className="relative pt-6 pb-4">
              <div className="flex justify-between text-xs text-gray-500 mb-2">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
              </div>
              <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-accent-green via-accent-yellow to-accent-red rounded-full relative">
                  <div className="absolute top-0 bottom-0 left-1/3 w-1/3 bg-white/20 border-l border-r border-white/30" />
                  <div
                    className="absolute top-1/2 -translate-y-1/2 w-3 h-6 bg-white rounded shadow-lg"
                    style={{ left: `${positionData.position}%`, transform: 'translate(-50%, -50%)' }}
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-white/5">
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-1">总市值</div>
                <div className="text-lg font-bold text-white font-mono">
                  ¥{positionData.totalValue.toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-1">盈亏</div>
                <div className={`text-lg font-bold font-mono ${totalProfit >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {totalProfit >= 0 ? '+' : ''}¥{totalProfit.toLocaleString()}
                </div>
              </div>
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-1">收益率</div>
                <div className={`text-lg font-bold font-mono ${parseFloat(profitPercent) >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {parseFloat(profitPercent) >= 0 ? '+' : ''}{profitPercent}%
                </div>
              </div>
            </div>
          </Card>

          <Card title="五条仓位铁律">
            <div className="space-y-3">
              {positionData.rules.map((rule, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-accent-green/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-accent-green text-sm">✓</span>
                  </div>
                  <span className="text-sm text-gray-300">{rule}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* 工具箱 */}
      {activeTab === 'tools' && (
        <div className="space-y-4">
          <Card title="汇率工具">
            <div className="space-y-4">
              <div className="flex gap-2 items-center">
                <input
                  type="number"
                  placeholder="金额"
                  defaultValue={100}
                  className="flex-1 bg-surface-200/50 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-blue/50"
                />
                <select className="bg-surface-200/50 rounded-xl px-4 py-3 text-white focus:outline-none">
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="JPY">JPY</option>
                  <option value="HKD">HKD</option>
                </select>
                <span className="text-gray-400">→</span>
                <div className="flex-1 bg-accent-blue/20 rounded-xl px-4 py-3 text-accent-blue font-mono">
                  ¥724.00 CNY
                </div>
              </div>
            </div>
          </Card>

          <Card title="换汇渠道对比">
            <div className="space-y-2">
              <div className="flex justify-between items-center p-3 bg-accent-green/10 rounded-xl">
                <div className="flex items-center gap-2">
                  <span className="text-lg">🏦</span>
                  <span className="text-white">银行</span>
                </div>
                <div className="text-right">
                  <span className="text-accent-green font-bold">7.24</span>
                  <span className="text-xs text-accent-green ml-2">⭐推荐</span>
                </div>
              </div>
              <div className="flex justify-between items-center p-3 bg-surface-200/30 rounded-xl">
                <div className="flex items-center gap-2">
                  <span className="text-lg">📱</span>
                  <span className="text-white">支付宝</span>
                </div>
                <span className="text-white font-bold">7.23</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-surface-200/30 rounded-xl">
                <div className="flex items-center gap-2">
                  <span className="text-lg">💬</span>
                  <span className="text-white">微信</span>
                </div>
                <span className="text-white font-bold">7.22</span>
              </div>
            </div>
          </Card>

          <Card title="金融产品推荐">
            <div className="space-y-3">
              <div className="p-3 bg-surface-200/50 rounded-xl cursor-pointer hover:bg-surface-200 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">📈</span>
                    <span className="text-white font-medium">华泰证券</span>
                  </div>
                  <Badge text="热门" variant="green" />
                </div>
                <div className="text-sm text-gray-400">开户即送Level2行情 + 佣金万一</div>
              </div>
              <div className="p-3 bg-surface-200/50 rounded-xl cursor-pointer hover:bg-surface-200 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">💳</span>
                    <span className="text-white font-medium">招商银行</span>
                  </div>
                  <Badge text="新客" variant="blue" />
                </div>
                <div className="text-sm text-gray-400">新客理财年化3.5%</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* 设置 */}
      {activeTab === 'settings' && (
        <div className="space-y-4">
          {/* LLM 设置入口 */}
          <Card
            className="cursor-pointer hover:border-accent-blue/30 transition-all"
            onClick={() => setShowLLMSettings(true)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">🤖</span>
                <div>
                  <div className="text-white font-medium">AI 模型设置</div>
                  <div className="text-xs text-gray-400">配置 LLM 提供商和 API Key</div>
                </div>
              </div>
              <span className="text-accent-blue">→</span>
            </div>
          </Card>

          <Card title="通知设置">
            <div className="space-y-3">
              {settings.slice(0, 3).map((setting) => (
                <div key={setting.id} className="flex justify-between items-center py-2">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{setting.icon}</span>
                    <span className="text-white">{setting.label}</span>
                  </div>
                  <button
                    className={`
                      w-12 h-6 rounded-full transition-colors relative
                      ${setting.value ? 'bg-accent-blue' : 'bg-gray-600'}
                    `}
                  >
                    <div
                      className={`
                        absolute top-1 w-4 h-4 bg-white rounded-full transition-transform
                        ${setting.value ? 'translate-x-7' : 'translate-x-1'}
                      `}
                    />
                  </button>
                </div>
              ))}
            </div>
          </Card>

          <Card title="显示设置">
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2">
                <div className="flex items-center gap-3">
                  <span className="text-xl">🌙</span>
                  <span className="text-white">深色模式</span>
                </div>
                <span className="text-accent-blue text-sm">已启用</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <div className="flex items-center gap-3">
                  <span className="text-xl">📊</span>
                  <span className="text-white">数据精度</span>
                </div>
                <span className="text-gray-400 text-sm">2位小数</span>
              </div>
            </div>
          </Card>

          <Card title="关于">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">版本</span>
                <span className="text-white">v0.1.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">构建时间</span>
                <span className="text-white">2026-04-22</span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* LLM 设置弹窗 */}
      {showLLMSettings && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-surface-100 rounded-2xl border border-white/10 shadow-xl overflow-hidden">
            <div className="p-4 border-b border-white/10">
              <LLMSettings onClose={() => setShowLLMSettings(false)} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
