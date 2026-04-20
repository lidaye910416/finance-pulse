import { useState, useRef, useEffect } from 'react';
import { analysts, Analyst } from '../../services/analysts';
import { Card } from '../Card';

interface Message {
  id: string;
  role: 'user' | 'analyst' | 'system';
  content: string;
  analyst?: Analyst;
  timestamp: Date;
}

interface ChatInterfaceProps {
  selectedAnalyst: Analyst | null;
  onAnalystChange: (analyst: Analyst) => void;
}

export function ChatInterface({ selectedAnalyst, onAnalystChange }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'system',
      content: '👋 欢迎使用AI分析师！\n\n请选择一位分析师，然后输入股票代码或基金代码进行分析。\n\n例如：600519（贵州茅台）\n      000001（平安银行）\n      510300（沪深300ETF）',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !selectedAnalyst) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsAnalyzing(true);

    // 模拟AI分析过程
    setTimeout(() => {
      const analystResponse = generateAnalysisResponse(input, selectedAnalyst);
      setMessages((prev) => [...prev, analystResponse]);
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)]">
      {/* 分析师选择器 */}
      <div className="mb-4">
        <div className="text-sm text-gray-400 mb-2">选择分析师：</div>
        <div className="flex flex-wrap gap-2">
          {analysts.map((analyst) => (
            <button
              key={analyst.id}
              onClick={() => onAnalystChange(analyst)}
              className={`
                px-3 py-2 rounded-lg border transition-all duration-200
                ${selectedAnalyst?.id === analyst.id
                  ? 'bg-accent-blue/20 border-accent-blue text-accent-blue'
                  : 'bg-surface-200/50 border-white/10 text-gray-300 hover:border-white/20'
                }
              `}
            >
              <span className="text-lg mr-1">{analyst.avatar}</span>
              <span className="text-sm font-medium">{analyst.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* 聊天消息区域 */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`animate-fade-in-up ${
              message.role === 'user' ? 'ml-auto max-w-[90%]' : 'max-w-full'
            }`}
          >
            {message.role === 'system' && (
              <div className="bg-surface-200/50 rounded-2xl rounded-tl-sm p-4 text-sm text-gray-300 whitespace-pre-line">
                {message.content}
              </div>
            )}
            {message.role === 'user' && (
              <div className="bg-accent-blue/20 border border-accent-blue/30 rounded-2xl rounded-tr-sm p-3">
                <div className="text-sm text-accent-blue mb-1">我</div>
                <div className="text-white">{message.content}</div>
              </div>
            )}
            {message.role === 'analyst' && message.analyst && (
              <Card className="border-accent-green/20">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">{message.analyst.avatar}</span>
                  <div>
                    <div className="text-sm font-semibold text-accent-green">
                      {message.analyst.name}
                    </div>
                    <div className="text-xs text-gray-400">{message.analyst.style}</div>
                  </div>
                </div>
                <div className="text-sm text-gray-300 whitespace-pre-line leading-relaxed">
                  {message.content}
                </div>
              </Card>
            )}
          </div>
        ))}
        {isAnalyzing && (
          <div className="animate-fade-in-up">
            <Card className="border-accent-yellow/20">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-accent-yellow/20 flex items-center justify-center animate-pulse">
                  {selectedAnalyst?.avatar || '🤔'}
                </div>
                <div className="flex-1">
                  <div className="text-sm text-accent-yellow font-medium mb-1">
                    {selectedAnalyst?.name} 正在分析...
                  </div>
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-accent-yellow rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-accent-yellow rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-accent-yellow rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="glass rounded-2xl p-3 border border-white/10">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={selectedAnalyst ? `输入股票代码或基金代码，如 600519...` : '请先选择分析师'}
            disabled={!selectedAnalyst || isAnalyzing}
            className="flex-1 bg-surface-200/50 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-blue/50 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || !selectedAnalyst || isAnalyzing}
            className="px-6 py-3 bg-accent-blue rounded-xl text-white font-medium hover:bg-accent-blue/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed btn-press"
          >
            发送
          </button>
        </div>
        {!selectedAnalyst && (
          <div className="mt-2 text-xs text-gray-500 text-center">
            请从上方选择一位分析师开始分析
          </div>
        )}
      </div>
    </div>
  );
}

// 模拟分析响应生成
function generateAnalysisResponse(code: string, analyst: Analyst): Message {
  // 模拟数据
  const mockData: Record<string, { name: string; price: number; change: number; pe: number; marketCap: string }> = {
    '600519': { name: '贵州茅台', price: 1688.0, change: -1.2, pe: 28.5, marketCap: '2.1万亿' },
    '000001': { name: '平安银行', price: 12.35, change: 0.8, pe: 5.2, marketCap: '2400亿' },
    '510300': { name: '沪深300ETF', price: 3.85, change: 0.5, pe: 12.3, marketCap: '1150亿' },
    '000858': { name: '五粮液', price: 145.6, change: -0.9, pe: 18.2, marketCap: '5600亿' },
  };

  const data = mockData[code] || {
    name: `股票 ${code}`,
    price: Math.random() * 100 + 10,
    change: (Math.random() - 0.5) * 10,
    pe: Math.random() * 30 + 5,
    marketCap: `${(Math.random() * 10000 + 100).toFixed(0)}亿`,
  };

  const responses: Record<string, string> = {
    buffett: `🔍 **${data.name}(${code}) 价值分析**

**基础数据：**
- 现价: ¥${data.price.toFixed(2)}
- 涨跌幅: ${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}%
- 市盈率(PE): ${data.pe.toFixed(1)}
- 总市值: ${data.marketCap}

**内在价值评估：**
基于DCF模型估算，当前股价 ${data.change > 0 ? '略高于' : '接近'} 内在价值。

**护城河分析：**
- 品牌护城河: ★★★★☆
- 定价权: ★★★★☆
- 规模经济: ★★★☆☆

**投资建议：**
${data.change < 0 ? '近期下跌提供了更好的安全边际，可以关注。' : '当前价格已反映了一定成长预期，建议耐心等待更好的买入机会。'}

*本分析仅供参考，不构成投资建议*`,
    lynch: `🚀 **${data.name}(${code}) 成长性分析**

**基础数据：**
- 现价: ¥${data.price.toFixed(2)}
- 涨跌幅: ${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}%
- 市盈率(PE): ${data.pe.toFixed(1)}
- 总市值: ${data.marketCap}

**成长性评估：**
- 营收增长率: 预计15-20%/年
- 利润增长率: 预计12-18%/年
- 行业地位: 具备成长空间

**PEG分析：**
当前PEG = ${(data.pe / 15).toFixed(2)} (基于15%增长假设)

**投资亮点：**
${data.pe < 20 ? '✓ PE处于合理区间，成长性未被过度定价' : '⚠ PE偏高，需要更高的增长率支撑'}

*本分析仅供参考，不构成投资建议*`,
    dalio: `🌍 **${data.name}(${code}) 宏观视角分析**

**基础数据：**
- 现价: ¥${data.price.toFixed(2)}
- 涨跌幅: ${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}%
- 市盈率(PE): ${data.pe.toFixed(1)}
- 总市值: ${data.marketCap}

**宏观环境：**
- 货币政策: 稳健略宽松
- 汇率影响: 人民币贬值压力
- 行业周期: 处于成熟期

**风险评估：**
- 宏观风险: 中等
- 政策风险: 低
- 市场风险: 高

**配置建议：**
建议占总仓位 5-10%，作为核心持仓的补充。

*本分析仅供参考，不构成投资建议*`,
    technical: `📈 **${data.name}(${code}) 技术分析**

**基础数据：**
- 现价: ¥${data.price.toFixed(2)}
- 涨跌幅: ${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}%

**技术指标：**
- MA5: ${(data.price * 0.99).toFixed(2)} (偏多)
- MA10: ${(data.price * 0.98).toFixed(2)} (偏多)
- MA20: ${(data.price * 1.01).toFixed(2)} (偏空)
- RSI(14): ${(45 + Math.random() * 20).toFixed(1)}
- MACD: ${data.change > 0 ? '金叉' : '死叉'}

**趋势判断：**
${data.change > 0 ? '价格站上均线，短期趋势向好' : '价格跌破均线，短期趋势偏弱'}

**操作建议：**
- 止损位: ¥${(data.price * 0.95).toFixed(2)}
- 止盈位: ¥${(data.price * 1.08).toFixed(2)}
- 建议: ${data.change > 0 ? '逢低买入' : '观望等待'}

*本分析仅供参考，不构成投资建议*`,
    burry: `🦔 **${data.name}(${code}) 逆向分析**

**基础数据：**
- 现价: ¥${data.price.toFixed(2)}
- 涨跌幅: ${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}%
- 市盈率(PE): ${data.pe.toFixed(1)}
- 总市值: ${data.marketCap}

**逆向思考：**
${data.change < 0 ? '✓ 市场恐慌下跌，可能存在错误定价机会' : '⚠ 市场乐观，需警惕过度泡沫'}

**风险因素：**
- 市场共识是否过于乐观？
- 是否有被忽视的风险？
- 安全边际是否足够？

**逆向建议：**
${data.change < 0 ? '在控制仓位的前提下，可以考虑分批建仓' : '保持谨慎，等待更好的逆向机会'}

*本分析仅供参考，不构成投资建议*`,
    quant: `🤖 **${data.name}(${code}) 量化分析**

**基础数据：**
- 现价: ¥${data.price.toFixed(2)}
- 涨跌幅: ${data.change > 0 ? '+' : ''}${data.change.toFixed(2)}%
- 市盈率(PE): ${data.pe.toFixed(1)}
- 总市值: ${data.marketCap}

**量化指标：**
- 历史分位: ${(Math.random() * 50 + 25).toFixed(1)}%
- 波动率: ${(Math.random() * 10 + 5).toFixed(1)}%
- Beta: ${(Math.random() * 0.5 + 0.8).toFixed(2)}
- 夏普比率: ${(Math.random() * 1 + 0.5).toFixed(2)}

**统计信号：**
${data.change > 0 ? '短期动能指标偏多' : '短期动能指标偏空'}

**量化结论：**
建议关注均值回归机会，当前 ${data.pe < 15 ? '估值偏低' : '估值合理偏高'}

*本分析仅供参考，不构成投资建议*`,
  };

  return {
    id: (Date.now() + 1).toString(),
    role: 'analyst',
    content: responses[analyst.id] || responses['buffett'],
    analyst,
    timestamp: new Date(),
  };
}
