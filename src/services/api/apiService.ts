/**
 * API 服务 - 调用后端 LangGraph 服务
 */

// ========== API 配置 ==========

export const API_BASE_URL = 'http://localhost:5000';

// ========== API 响应类型 ==========

export interface ApiSignal {
  agent: string;
  agent_id: string;
  signal: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  reasoning: string;
}

export interface ApiRecommendation {
  action: 'buy' | 'hold' | 'sell' | 'watch';
  confidence: number;
  entry_price?: number;
  exit_price?: number;
  stop_loss?: number;
  position_size?: number;
  timeframe: string;
  risks: string[];
}

// 分析模式类型
export type AnalysisMode = 'tradingagents' | 'aihedgefund' | 'fusion';

// 分析请求参数
export interface AnalyzeStockParams {
  code: string;
  name?: string;
  mode?: AnalysisMode;
  leaderId?: string;
  maxIterations?: number;
  convergenceGap?: number;
  earlyStopGap?: number;
  riskLevel?: 'conservative' | 'moderate' | 'aggressive';
}

export interface ApiAnalysisResponse {
  code: string;
  name: string;
  timestamp: number;
  duration_ms: number;
  iterations: number;
  signals: ApiSignal[];
  debate_result: {
    round: number;
    bullish: ApiSignal;
    bearish: ApiSignal;
    consensus_reached: boolean;
    final_confidence: number;
  } | null;
  summary: string;
  model: string;
  total_tokens: number;
  recommendation: ApiRecommendation;
  error: string | null;
}

export interface ApiQuoteResponse {
  code: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  prev_close: number;
  pe?: number;
  pb?: number;
  market_cap?: string;
}

// ========== API 服务 ==========

class APIService {
  private baseUrl = API_BASE_URL;
  private timeout = 120000; // 120秒超时

  /**
   * 检查后端服务是否可用
   */
  async checkHealth(): Promise<{ status: string; llm_configured: boolean; llm_provider: string } | null> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  }

  /**
   * 分析股票
   * @param params - 分析参数
   */
  async analyzeStock(params: AnalyzeStockParams): Promise<ApiAnalysisResponse> {
    const {
      code,
      name,
      mode = 'tradingagents',
      leaderId,
      maxIterations = 3,
      convergenceGap,
      earlyStopGap,
      riskLevel,
    } = params;

    // 构建请求体
    const requestBody: Record<string, unknown> = {
      code,
      name: name || `股票${code}`,
      include_history: false,
      mode,
      max_iterations: maxIterations,
    };

    // 可选参数：仅在非默认值时添加
    if (leaderId) {
      requestBody.leader_id = leaderId;
    }
    if (convergenceGap !== undefined) {
      requestBody.convergence_gap = convergenceGap;
    }
    if (earlyStopGap !== undefined) {
      requestBody.early_stop_gap = earlyStopGap;
    }
    if (riskLevel) {
      requestBody.risk_level = riskLevel;
    }

    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`分析失败: ${response.status} - ${error}`);
    }

    return await response.json();
  }

  /**
   * 获取股票行情
   */
  async getQuote(code: string): Promise<ApiQuoteResponse> {
    const response = await fetch(`${this.baseUrl}/quote/${code}`, {
      method: 'GET',
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      throw new Error(`获取行情失败: ${response.status}`);
    }

    return await response.json();
  }

  /**
   * 测试 LLM 连接
   */
  async testLLM(): Promise<{ success: boolean; content: string; model: string; tokens: number }> {
    const response = await fetch(`${this.baseUrl}/llm/test`, {
      method: 'GET',
      signal: AbortSignal.timeout(30000),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`LLM 测试失败: ${error}`);
    }

    return await response.json();
  }

  /**
   * 检查服务状态
   */
  
  /**
   * 获取投资大师列表
   */
  async getLeaders(): Promise<ApiLeader[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/leaders`, {
        method: 'GET',
        signal: AbortSignal.timeout(10000),
      });
      if (!response.ok) throw new Error(`获取大师列表失败: ${response.status}`);
      const data = await response.json();
      return data.leaders || [];
    } catch (err) {
      console.warn('获取大师列表失败，使用默认列表:', err);
      // 返回默认列表作为 fallback
      return [
        { id: 'warren_buffett', name: '沃伦·巴菲特', style: '价值投资大师', avatar: '🎯', description: '寻找伟大的公司，以合理的价格买入' },
        { id: 'ben_graham', name: '本杰明·格雷厄姆', style: '安全边际专家', avatar: '🛡️', description: '强调"安全边际"是投资的核心' },
        { id: 'peter_lynch', name: '彼得·林奇', style: '成长投资专家', avatar: '📈', description: '在日常生活中寻找10倍股' },
        { id: 'charlie_munger', name: '查理·芒格', style: '多元思维模型专家', avatar: '🧠', description: '跨学科分析，逆向思考' },
        { id: 'cathie_wood', name: '凯瑟琳·伍德', style: '颠覆性创新专家', avatar: '🚀', description: '专注未来趋势和颠覆性创新' },
        { id: 'bill_ackman', name: '比尔·阿克曼', style: '积极主义投资者', avatar: '🎯', description: 'Pershing Square创始人' },
        { id: 'stanley_druckenmiller', name: '斯坦利·德鲁肯米勒', style: '宏观对冲大师', avatar: '🌍', description: '量子基金前基金经理' },
        { id: 'aswath_damodaran', name: '阿斯瓦特·达摩达兰', style: '估值大师', avatar: '📊', description: '纽约大学金融学教授' },
        { id: 'mohnish_pabrai', name: '莫尼什·帕伯莱', style: '雪茄烟蒂投资者', avatar: '💰', description: 'Pabrai Funds创始人' },
        { id: 'phil_fisher', name: '菲利普·费雪', style: '成长股投资大师', avatar: '📈', description: '《怎样选择成长股》作者' },
        { id: 'george_soros', name: '乔治·索罗斯', style: '宏观对冲大师', avatar: '🌍', description: '量子基金创始人' },
        { id: 'rakesh_jhunjhunwala', name: '拉凯什·Jhunjhunwala', style: '印度巴菲特', avatar: '🇮🇳', description: '印度最成功的个人投资者' },
        { id: 'ray_dalio', name: '雷·达里奥', style: '风险平价大师', avatar: '⚖️', description: '桥水基金创始人' },
        { id: 'jim_simons', name: '吉姆·西蒙斯', style: '量化投资大师', avatar: '🔢', description: '大奖章基金创始人' },
        { id: 'paul_tudor_jones', name: '保罗·都铎·琼斯', style: '宏观交易大师', avatar: '📊', description: 'Tudor Investment创始人' },
        { id: 'ed_thorp', name: '爱德华·索普', style: '数学投资大师', avatar: '🧮', description: '数学教授，对冲基金经理' },
        { id: 'john_bogle', name: '约翰·博格', style: '指数投资先驱', avatar: '📉', description: 'Vanguard创始人，指数基金之父' },
        { id: 'howard_marks', name: '霍华德·马克斯', style: '价值投资大师', avatar: '💎', description: '橡树资本创始人' },
        { id: 'seth_klarman', name: '塞思·卡拉曼', style: '深度价值投资者', avatar: '💰', description: 'Baupost基金创始人' },
      ];
    }
  }

  /**
   * 获取收敛预设配置
   */
  async getConvergencePresets(): Promise<ApiConvergencePreset[]> {
    return [
      { id: 'quick', name: '快速决策', max_iterations: 1, convergence_gap: 20, early_stop_gap: 15 },
      { id: 'standard', name: '标准设置', max_iterations: 3, convergence_gap: 15, early_stop_gap: 10 },
      { id: 'deep', name: '深度分析', max_iterations: 5, convergence_gap: 10, early_stop_gap: 5 },
    ];
  }

  /**
   * 获取风险偏好设置
   */
  async getRiskLevels(): Promise<ApiRiskPreference[]> {
    return [
      { id: 'conservative', name: '保守型', description: '严格风控，适合风险厌恶型投资者' },
      { id: 'moderate', name: '平衡型', description: '平衡风险和收益，适合大多数投资者' },
      { id: 'aggressive', name: '激进型', description: '追求高收益，适合风险承受能力强投资者' },
    ];
  }

  isServiceAvailable(): boolean {
    // 可以添加检查逻辑
    return true;
  }
}

// ========== 单例导出 ==========

export const apiService = new APIService();
export default apiService;

// ========== Leaders 类型 ==========

export interface ApiLeader {
  id: string;
  name: string;
  style: string;
  avatar: string;
  description: string;
}

export interface ApiConvergencePreset {
  id: string;
  name: string;
  description?: string;
  max_iterations: number;
  convergence_gap: number;
  early_stop_gap: number;
}

export interface ApiRiskPreference {
  id: string;
  name: string;
  description: string;
  max_position?: number;
  stop_loss?: number;
  volatility_alert?: number;
}
