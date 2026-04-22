import { useState, useRef, useEffect } from 'react';
import { Card } from '../Card';
import { ALL_AGENTS } from '../../services/analysis/agentConfig';
import { executeAnalysis } from '../../services/analysis/orchestrator';
import { WorkflowState } from '../../services/analysis/types';

// 转换 AgentConfig 为 analysts 数组格式
interface Analyst {
  id: string;
  name: string;
  nameCn: string;
  avatar: string;
  style: string;
  description: string;
}

const analysts: Analyst[] = ALL_AGENTS.slice(0, 6).map(agent => ({
  id: agent.id,
  name: agent.nameCn,
  nameCn: agent.nameCn,
  avatar: agent.avatar,
  style: agent.style,
  description: agent.description,
}));

interface Message {
  id: string;
  role: 'user' | 'analyst' | 'system';
  content: string;
  analyst?: Analyst;
  timestamp: Date;
  signals?: Array<{
    agent: string;
    agentId: string;
    signal: string;
    confidence: number;
    reasoning: string;
  }>;
  recommendation?: {
    action: string;
    confidence: number;
    positionSize?: number;
    stopLoss?: number;
    risks: string[];
  };
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
      content: '👋 欢迎使用AI分析师！\n\n请选择分析师并输入股票代码进行分析。\n\n💡 提示：可选择多个分析师进行综合分析',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState<WorkflowState | null>(null);
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
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsAnalyzing(true);
    setProgress({ status: 'running', progress: 0, currentStep: '准备分析...', agentsCompleted: [] });

    try {
      // 调用编排器执行分析
      const response = await executeAnalysis(
        {
          code: input.trim(),
          analystIds: [selectedAnalyst.id],
          includeHistory: true,
        },
        (state) => setProgress(state)
      );

      const analystResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'analyst',
        content: response.summary.text,
        analyst: selectedAnalyst,
        timestamp: new Date(),
        signals: response.signals.map(s => ({
          agent: s.agent,
          agentId: s.agentId,
          signal: s.signal,
          confidence: s.confidence,
          reasoning: s.reasoning,
        })),
        recommendation: response.recommendation,
      };

      setMessages((prev) => [...prev, analystResponse]);
    } catch (error) {
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: `分析失败: ${error}`,
        timestamp: new Date(),
      }]);
    } finally {
      setIsAnalyzing(false);
      setProgress(null);
    }
  };

  // 信号颜色
  const getSignalColor = (signal: string) => {
    if (signal === 'bullish') return 'text-accent-green';
    if (signal === 'bearish') return 'text-accent-red';
    return 'text-gray-400';
  };

  const getSignalIcon = (signal: string) => {
    if (signal === 'bullish') return '↗';
    if (signal === 'bearish') return '↘';
    return '→';
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

                {/* 多维度分析信号 */}
                {message.signals && message.signals.length > 0 && (
                  <div className="mb-3 p-3 bg-surface-200/30 rounded-xl">
                    <div className="text-xs text-gray-400 mb-2">多维度分析</div>
                    <div className="grid grid-cols-2 gap-2">
                      {message.signals.map((signal, idx) => (
                        <div key={idx} className="text-xs flex items-center gap-1">
                          <span className="text-gray-500 truncate">{signal.agent}:</span>
                          <span className={`font-medium ${getSignalColor(signal.signal)}`}>
                            {getSignalIcon(signal.signal)}{signal.confidence.toFixed(0)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 投资建议 */}
                {message.recommendation && (
                  <div className="mb-3 p-3 bg-accent-blue/10 rounded-xl border border-accent-blue/20">
                    <div className="text-xs text-accent-blue mb-2">📋 投资建议</div>
                    <div className="flex items-center gap-4">
                      <div className={`text-lg font-bold ${
                        message.recommendation.action === 'buy' ? 'text-accent-green' :
                        message.recommendation.action === 'sell' ? 'text-accent-red' : 'text-accent-yellow'
                      }`}>
                        {message.recommendation.action === 'buy' ? '买入' :
                         message.recommendation.action === 'sell' ? '卖出' :
                         message.recommendation.action === 'hold' ? '持有' : '观望'}
                      </div>
                      <div className="text-xs text-gray-400">
                        置信度: {message.recommendation.confidence}%
                        {message.recommendation.positionSize && ` | 建议仓位: ${message.recommendation.positionSize}%`}
                      </div>
                    </div>
                    {message.recommendation.risks.length > 0 && (
                      <div className="mt-2 text-xs text-gray-500">
                        风险: {message.recommendation.risks.slice(0, 2).join(', ')}
                      </div>
                    )}
                  </div>
                )}

                <div className="text-sm text-gray-300 whitespace-pre-line leading-relaxed">
                  {message.content}
                </div>
              </Card>
            )}
          </div>
        ))}

        {/* 分析进度 */}
        {isAnalyzing && progress && (
          <div className="animate-fade-in-up">
            <Card className="border-accent-yellow/20">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-accent-yellow/20 flex items-center justify-center animate-pulse">
                  {selectedAnalyst?.avatar || '🤔'}
                </div>
                <div className="flex-1">
                  <div className="text-sm text-accent-yellow font-medium mb-1">
                    {selectedAnalyst?.name} 正在分析... {progress.currentStep}
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div 
                      className="h-full bg-accent-yellow rounded-full transition-all duration-300"
                      style={{ width: `${progress.progress}%` }}
                    />
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
            placeholder={selectedAnalyst ? `输入股票代码，如 600519...` : '请先选择分析师'}
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
