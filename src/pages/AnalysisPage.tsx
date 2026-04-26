import { useState } from 'react';
import {
  StockHeader,
  KlineChart,
  FundFlowPanel,
  AnalysisParams,
  SignalPanel,
  RecommendationCard,
  SummaryText,
  AnalysisMode,
} from '../components/analysis';
import { apiService, ApiQuoteResponse, ApiAnalysisResponse } from '../services/api/apiService';

// 分析状态
type AnalysisState = 'idle' | 'analyzing' | 'completed' | 'error';

// 分析参数状态
interface AnalysisConfig {
  mode: AnalysisMode;
  leaderId: string | null;
  convergencePreset: string;
  riskLevel: string;
}

export function AnalysisPage() {
  // 股票搜索状态
  const [stockCode, setStockCode] = useState('');
  const [stockQuote, setStockQuote] = useState<ApiQuoteResponse | null>(null);
  const [quoteError, setQuoteError] = useState<string | null>(null);

  // 分析参数状态
  const [config, setConfig] = useState<AnalysisConfig>({
    mode: 'tradingagents',
    leaderId: null,
    convergencePreset: 'standard',
    riskLevel: 'moderate',
  });

  // 分析状态
  const [analysisState, setAnalysisState] = useState<AnalysisState>('idle');
  const [analysisResult, setAnalysisResult] = useState<ApiAnalysisResponse | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  // 搜索股票
  const handleSearch = async (code: string) => {
    setStockCode(code);
    setQuoteError(null);
    setStockQuote(null);

    try {
      const quote = await apiService.getQuote(code);
      setStockQuote(quote);
    } catch (err) {
      setQuoteError(err instanceof Error ? err.message : '获取行情失败');
    }
  };

  // 开始分析
  const handleStartAnalysis = async () => {
    if (!stockCode) {
      setAnalysisError('请先搜索股票');
      return;
    }

    setAnalysisState('analyzing');
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      // 获取收敛预设参数
      const convergencePresets = await apiService.getConvergencePresets();
      const preset = convergencePresets.find(p => p.id === config.convergencePreset) || convergencePresets[1];

      // 调用分析API
      const result = await apiService.analyzeStock({
        code: stockCode,
        name: stockQuote?.name,
        mode: config.mode,
        leaderId: config.leaderId || undefined,
        maxIterations: preset.max_iterations,
        convergenceGap: preset.convergence_gap,
        earlyStopGap: preset.early_stop_gap,
        riskLevel: config.riskLevel as 'conservative' | 'moderate' | 'aggressive',
      });

      setAnalysisResult(result);
      setAnalysisState('completed');
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : '分析失败');
      setAnalysisState('error');
    }
  };

  // 参数更新回调
  const handleModeChange = (mode: AnalysisMode) => {
    setConfig(prev => ({ ...prev, mode }));
  };

  const handleLeaderChange = (leaderId: string) => {
    setConfig(prev => ({ ...prev, leaderId }));
  };

  const handleConvergenceChange = (preset: string) => {
    setConfig(prev => ({ ...prev, convergencePreset: preset }));
  };

  const handleRiskChange = (riskLevel: string) => {
    setConfig(prev => ({ ...prev, riskLevel }));
  };

  // 获取领袖名称
  const getLeaderName = () => {
    if (analysisResult && config.leaderId) {
      return config.leaderId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    return undefined;
  };

  // 获取辩论结果
  const getDebateResult = () => {
    if (analysisResult?.debate_result) {
      return {
        bullishConfidence: Math.round(analysisResult.debate_result.bullish.confidence * 100),
        bearishConfidence: Math.round(analysisResult.debate_result.bearish.confidence * 100),
        gap: Math.abs(
          Math.round(analysisResult.debate_result.bullish.confidence * 100) -
          Math.round(analysisResult.debate_result.bearish.confidence * 100)
        ),
        converged: analysisResult.debate_result.consensus_reached,
      };
    }
    return undefined;
  };

  // 获取推荐
  const getRecommendation = () => {
    if (analysisResult?.recommendation) {
      return {
        action: analysisResult.recommendation.action,
        confidence: Math.round(analysisResult.recommendation.confidence * 100),
        timeframe: analysisResult.recommendation.timeframe,
        position_size: analysisResult.recommendation.position_size ? Math.round(analysisResult.recommendation.position_size * 100) : undefined,
        stop_loss: analysisResult.recommendation.stop_loss ? Math.round(analysisResult.recommendation.stop_loss * 100) : undefined,
        exit_price: analysisResult.recommendation.exit_price,
        entry_price: analysisResult.recommendation.entry_price,
        risks: analysisResult.recommendation.risks,
      };
    }
    return undefined;
  };

  return (
    <div className="space-y-4 animate-fade-in-up pt-4">
      {/* 页面标题 */}
      <div className="text-center">
        <h1 className="text-2xl font-display font-bold bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent">
          AI 股票分析
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          多智能体协作，深度分析股票投资价值
        </p>
      </div>

      {/* 股票搜索头部 */}
      <StockHeader
        code={stockCode}
        name={stockQuote?.name}
        price={stockQuote?.price}
        change={stockQuote?.change}
        changePercent={stockQuote?.change_percent}
        onSearch={handleSearch}
      />

      {/* 行情错误提示 */}
      {quoteError && (
        <div className="p-3 bg-accent-red/10 border border-accent-red/20 rounded-xl text-sm text-accent-red">
          {quoteError}
        </div>
      )}

      {/* K线图和资金流向 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <KlineChart />
        </div>
        <div>
          <FundFlowPanel
            northbound={stockQuote ? Math.random() * 10 - 3 : 0}
            sentiment={stockQuote?.change_percent && stockQuote.change_percent > 0 ? 'greed' :
                        stockQuote?.change_percent && stockQuote.change_percent < 0 ? 'fear' : 'neutral'}
          />
        </div>
      </div>

      {/* 分析参数设置 */}
      <AnalysisParams
        mode={config.mode}
        leaderId={config.leaderId}
        convergencePreset={config.convergencePreset}
        riskLevel={config.riskLevel}
        onModeChange={handleModeChange}
        onLeaderChange={handleLeaderChange}
        onConvergenceChange={handleConvergenceChange}
        onRiskChange={handleRiskChange}
      />

      {/* 开始分析按钮 */}
      <button
        onClick={handleStartAnalysis}
        disabled={analysisState === 'analyzing' || !stockCode}
        className={`
          w-full py-4 rounded-xl font-semibold text-lg transition-all
          ${analysisState === 'analyzing'
            ? 'bg-surface-200 text-gray-500 cursor-wait'
            : stockCode
              ? 'bg-gradient-to-r from-accent-blue to-accent-purple text-white hover:opacity-90 btn-press'
              : 'bg-surface-200 text-gray-500 cursor-not-allowed'
          }
        `}
      >
        {analysisState === 'analyzing' ? (
          <span className="flex items-center justify-center gap-2">
            <span className="animate-spin">⏳</span>
            分析中...
          </span>
        ) : (
          '🚀 开始分析'
        )}
      </button>

      {/* 分析错误 */}
      {analysisError && (
        <div className="p-4 bg-accent-red/10 border border-accent-red/20 rounded-xl">
          <div className="flex items-start gap-3">
            <span className="text-xl">❌</span>
            <div>
              <div className="text-sm font-medium text-accent-red">分析失败</div>
              <div className="text-xs text-gray-400 mt-1">{analysisError}</div>
            </div>
          </div>
        </div>
      )}

      {/* 分析结果区域 */}
      {analysisState === 'completed' && analysisResult && (
        <>
          {/* 综合分析报告 */}
          <SummaryText
            summary={analysisResult.summary}
            mode={config.mode}
            leaderName={getLeaderName()}
          />

          {/* 信号面板和推荐卡片 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <SignalPanel
              signals={analysisResult.signals.map(s => ({
                analyst: s.agent,
                avatar: s.signal === 'bullish' ? '🐂' : s.signal === 'bearish' ? '🐻' : '➖',
                signal: s.signal,
                confidence: Math.round(s.confidence * 100),
              }))}
              debateResult={getDebateResult()}
            />
            <RecommendationCard
              recommendation={getRecommendation()}
              riskLevel={config.riskLevel as 'conservative' | 'moderate' | 'aggressive'}
              leaderName={getLeaderName()}
            />
          </div>

          {/* 分析统计 */}
          <div className="bg-surface-200/50 rounded-xl p-4 border border-white/5">
            <div className="text-xs text-gray-500 mb-2">分析统计</div>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-white">{analysisResult.iterations}</div>
                <div className="text-xs text-gray-500">迭代次数</div>
              </div>
              <div>
                <div className="text-lg font-bold text-white">{analysisResult.total_tokens.toLocaleString()}</div>
                <div className="text-xs text-gray-500">Token消耗</div>
              </div>
              <div>
                <div className="text-lg font-bold text-white">{analysisResult.model}</div>
                <div className="text-xs text-gray-500">使用模型</div>
              </div>
              <div>
                <div className="text-lg font-bold text-white">{(analysisResult.duration_ms / 1000).toFixed(1)}s</div>
                <div className="text-xs text-gray-500">耗时</div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
