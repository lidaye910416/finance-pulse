import { useEffect, useState } from 'react';
import { Card, Badge } from '../components';
import { fetchPolymarketEvents, fetchArbitrageOpportunities, PolymarketEvent, ArbitrageOpportunity } from '../services/api/predictionMarket';

export function PredictionMarket() {
  const [polymarketEvents, setPolymarketEvents] = useState<PolymarketEvent[]>([]);
  const [arbitrageOpportunities, setArbitrageOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const [events, arbitrage] = await Promise.all([
          fetchPolymarketEvents(10),
          fetchArbitrageOpportunities(),
        ]);
        setPolymarketEvents(events);
        setArbitrageOpportunities(arbitrage);
      } catch (error) {
        console.error('加载预测市场数据失败:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    Promise.all([
      fetchPolymarketEvents(10),
      fetchArbitrageOpportunities(),
    ]).then(([events, arbitrage]) => {
      setPolymarketEvents(events);
      setArbitrageOpportunities(arbitrage);
    }).catch((error) => {
      console.error('刷新数据失败:', error);
    }).finally(() => {
      setLoading(false);
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">🔮 预测市场</h2>
        <button
          className="text-finance-blue text-sm hover:underline disabled:opacity-50"
          onClick={handleRefresh}
          disabled={loading}
        >
          {loading ? '加载中...' : '[刷新]'}
        </button>
      </div>

      {/* Polymarket Hot Events */}
      <Card title="Polymarket 热门事件">
        <div className="space-y-4">
          {polymarketEvents.map((event) => (
            <div
              key={event.id}
              className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors cursor-pointer"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="text-white text-sm font-medium flex-1 pr-2">
                  {event.question}
                </h3>
                <div className="flex items-center gap-2">
                  {event.trend && (
                    <span className={`text-sm ${event.trend === 'up' ? 'text-finance-green' : 'text-finance-red'}`}>
                      {event.trend === 'up' ? '↑' : '↓'}
                    </span>
                  )}
                  <button className="text-finance-blue text-xs hover:underline">
                    查看详情 ›
                  </button>
                </div>
              </div>

              {/* Probability Bar */}
              <div className="mb-2">
                <div className="flex justify-between text-sm mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-400">Yes</span>
                    <div className="w-48 h-2 bg-gray-600 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-finance-blue rounded-full"
                        style={{ width: `${event.probability}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="text-white font-medium">{event.probability}%</span>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>No</span>
                  <span>{100 - event.probability}%</span>
                </div>
              </div>

              {/* Volume */}
              <div className="text-xs text-gray-400">
                <span className="text-gray-500">交易量:</span> {event.volume}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Cross-platform Arbitrage */}
      <Card title="跨平台套利机会">
        <div className="space-y-4">
          {arbitrageOpportunities.map((opp, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-white font-medium">{opp.event}</h3>
                <Badge
                  text={`差异 ${opp.difference}%`}
                  variant={opp.difference > 5 ? 'green' : 'yellow'}
                />
              </div>

              {/* Platform Comparison */}
              <div className="grid grid-cols-4 gap-2 mb-3">
                <div className="text-center">
                  <div className="text-gray-400 text-xs mb-1">Polymarket</div>
                  <div className="text-white font-bold">{opp.platforms[0].probability}%</div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-xs mb-1">Metaculus</div>
                  <div className="text-white font-bold">{opp.platforms[1].probability}%</div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-xs mb-1">Kalshi</div>
                  <div className="text-white font-bold">{opp.platforms[2].probability}%</div>
                </div>
                <div className="text-center">
                  <div className="text-gray-400 text-xs mb-1">差异</div>
                  <div className="text-finance-yellow font-bold">{opp.difference}%</div>
                </div>
              </div>

              {/* Suggestion */}
              <div className="bg-finance-yellow/10 rounded-lg p-3 border border-finance-yellow/30">
                <div className="flex items-start gap-2">
                  <span className="text-finance-yellow">⚠️</span>
                  <p className="text-sm text-gray-300">{opp.suggestion}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* How Prediction Markets Work */}
      <Card title="💡 预测市场入门">
        <div className="space-y-3 text-sm">
          <div>
            <h4 className="text-white font-medium mb-1">什么是预测市场?</h4>
            <p className="text-gray-400">
              预测市场允许用户对未来的事件进行交易，其价格反映了市场对该事件发生概率的共识。
            </p>
          </div>
          <div>
            <h4 className="text-white font-medium mb-1">如何解读概率?</h4>
            <p className="text-gray-400">
              概率以百分比表示。例如，70%意味着市场认为该事件有70%的可能性发生。
            </p>
          </div>
          <div>
            <h4 className="text-white font-medium mb-1">套利机会?</h4>
            <p className="text-gray-400">
              当不同平台对同一事件的概率预测存在差异时，可能存在套利机会。但需注意执行风险和手续费。
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
