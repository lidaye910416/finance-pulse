import { useState } from 'react';
import { Card, Badge } from '../components';

const currencies = [
  { code: 'USD', name: '美元', flag: '🇺🇸' },
  { code: 'CNY', name: '人民币', flag: '🇨🇳' },
  { code: 'EUR', name: '欧元', flag: '🇪🇺' },
  { code: 'GBP', name: '英镑', flag: '🇬🇧' },
  { code: 'JPY', name: '日元', flag: '🇯🇵' },
  { code: 'HKD', name: '港币', flag: '🇭🇰' },
];

const exchangeRates: Record<string, number> = {
  USD: 1,
  CNY: 6.83,
  EUR: 0.848,
  GBP: 0.792,
  JPY: 158.62,
  HKD: 7.82,
};

const forexChannels = [
  { channel: '银行APP', rate: '实时牌价', fee: '无', suitable: '常规换汇首选', recommended: true },
  { channel: '支付宝', rate: '较好', fee: '低/免', suitable: '日常跨境消费', recommended: true },
  { channel: '微信支付', rate: '较好', fee: '低/免', suitable: '日常跨境消费', recommended: false },
  { channel: 'Wise', rate: '中间价', fee: '<1%', suitable: '国际汇款', recommended: false },
  { channel: '机场兑换', rate: '差-3~5%', fee: '高', suitable: '仅应急小额', recommended: false },
];

const brokers = [
  {
    name: '长桥(LongPort)',
    markets: '港美星三市场',
    feature: '低佣金',
    inviteCode: 'FINANCE',
  },
  {
    name: '老虎(Tiger)',
    markets: '港美股',
    feature: '送股票',
    inviteCode: 'PULSE',
  },
  {
    name: '富途(Futu)',
    markets: '港美股',
    feature: '开户福利',
    inviteCode: '888',
  },
];

export function Tools() {
  const [amount, setAmount] = useState<string>('100');
  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('CNY');

  const convertedAmount = (() => {
    const numAmount = parseFloat(amount) || 0;
    const inUSD = numAmount / exchangeRates[fromCurrency];
    return (inUSD * exchangeRates[toCurrency]).toFixed(2);
  })();

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const getCurrencyInfo = (code: string) => currencies.find(c => c.code === code);

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">🔧 金融工具</h2>
        <button className="text-finance-blue text-sm hover:underline">[刷新]</button>
      </div>

      {/* Currency Converter */}
      <Card title="💱 汇率换算器">
        <div className="space-y-4">
          {/* Amount Input */}
          <div>
            <label className="text-gray-400 text-sm mb-2 block">金额</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white text-lg focus:outline-none focus:border-finance-blue"
              placeholder="请输入金额"
            />
          </div>

          {/* Currency Selection */}
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="text-gray-400 text-sm mb-2 block">从</label>
              <select
                value={fromCurrency}
                onChange={(e) => setFromCurrency(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-finance-blue"
              >
                {currencies.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.flag} {c.code} - {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Swap Button */}
            <button
              onClick={swapCurrencies}
              className="mt-6 p-2 rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
              title="互换货币"
            >
              <span className="text-xl">⇄</span>
            </button>

            <div className="flex-1">
              <label className="text-gray-400 text-sm mb-2 block">兑换</label>
              <select
                value={toCurrency}
                onChange={(e) => setToCurrency(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-finance-blue"
              >
                {currencies.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.flag} {c.code} - {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Result */}
          <div className="bg-gray-700 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-2">兑换结果</div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{convertedAmount}</span>
              <span className="text-gray-400">{toCurrency}</span>
            </div>
            <div className="text-gray-500 text-xs mt-2">
              {amount} {getCurrencyInfo(fromCurrency)?.name} ≈ {convertedAmount} {getCurrencyInfo(toCurrency)?.name}
            </div>
          </div>
        </div>

        {/* Real-time Exchange Rates */}
        <div className="mt-4 pt-4 border-t border-gray-700">
          <div className="text-gray-400 text-sm mb-2">实时汇率（USD基准）</div>
          <div className="flex flex-wrap gap-3">
            {Object.entries(exchangeRates).filter(([code]) => code !== 'USD').map(([code, rate]) => (
              <div key={code} className="bg-gray-700 rounded px-3 py-1">
                <span className="text-gray-400 text-xs">USD/{code}</span>
                <span className="text-white ml-2">{rate}</span>
              </div>
            ))}
          </div>
          <div className="text-gray-500 text-xs mt-2">
            数据来源: exchangerate-api.com | 更新: {new Date().toLocaleDateString('zh-CN')}
          </div>
        </div>
      </Card>

      {/* Forex Channel Comparison */}
      <Card title="换汇渠道对比">
        <div className="space-y-2">
          <div className="grid grid-cols-4 gap-2 text-xs text-gray-400 mb-2">
            <div>渠道</div>
            <div>汇率质量</div>
            <div>手续费</div>
            <div>适合场景</div>
          </div>
          {forexChannels.map((channel, index) => (
            <div
              key={index}
              className={`grid grid-cols-4 gap-2 p-3 rounded-lg ${
                channel.recommended ? 'bg-finance-green/10 border border-finance-green/30' : 'bg-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="text-white">{channel.channel}</span>
                {channel.recommended && <Badge text="推荐" variant="green" />}
              </div>
              <div className="text-gray-300">{channel.rate}</div>
              <div className="text-gray-300">{channel.fee}</div>
              <div className="text-gray-400 text-sm">{channel.suitable}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* Broker Recommendations */}
      <Card title="券商推荐">
        <div className="grid grid-cols-1 gap-3">
          {brokers.map((broker, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h4 className="text-white font-medium">{broker.name}</h4>
                  <p className="text-gray-400 text-sm">{broker.markets}</p>
                </div>
                <Badge text={broker.feature} variant="blue" />
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-500 text-xs">
                  邀请码: <span className="text-finance-yellow">{broker.inviteCode}</span>
                </span>
                <button className="text-finance-blue text-sm hover:underline">
                  立即开户 →
                </button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
