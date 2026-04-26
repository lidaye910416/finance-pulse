"""
LangGraph 状态定义

定义多智能体工作流中的共享状态
"""

from typing import TypedDict, Literal, Optional
from pydantic import BaseModel


class AnalystSignal(BaseModel):
    """分析师信号"""
    agent: str
    agent_id: str
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: int
    reasoning: str


class Recommendation(BaseModel):
    """投资建议"""
    action: Literal["buy", "hold", "sell", "watch"]
    confidence: int
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    timeframe: str
    risks: list[str]


class DebateResult(BaseModel):
    """辩论结果"""
    round: int
    bullish: AnalystSignal
    bearish: AnalystSignal
    consensus_reached: bool
    final_confidence: int


class AgentState(TypedDict):
    """
    LangGraph 工作流状态

    在各个节点间传递，包含完整的分析上下文
    """
    # 股票信息
    code: str
    name: str
    stock_data: dict

    # 迭代控制
    iteration: int
    max_iterations: int

    # 分析结果
    analyst_signals: list[dict]  # 各分析师的信号
    bullish_signal: Optional[dict]  # 多头研究员信号
    bearish_signal: Optional[dict]  # 空头研究员信号

    # 辩论历史
    debate_history: list[dict]

    # 最终输出
    final_summary: str
    recommendation: Optional[dict]
    total_tokens: int

    # 错误处理
    error: Optional[str]

    # 新增参数 (支持不同工作流模式)
    mode: str  # 'tradingagents' | 'aihedgefund' | 'fusion'
    leader_id: Optional[str]
    risk_level: Optional[str]  # 'conservative' | 'moderate' | 'aggressive'
    convergence_gap: Optional[float]
    early_stop_gap: Optional[float]


def should_continue(state: AgentState) -> Literal["debate", "synthesize"]:
    """
    条件路由函数：决定是否继续辩论
    
    如果达到最大迭代次数或置信度足够高，则结束辩论
    """
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)
    
    # 检查辩论是否收敛
    if state.get("bullish_signal") and state.get("bearish_signal"):
        bullish_conf = state["bullish_signal"].get("confidence", 0)
        bearish_conf = state["bearish_signal"].get("confidence", 0)
        
        # 两者置信度差距小于15%认为收敛
        if abs(bullish_conf - bearish_conf) < 15:
            return "synthesize"
    
    # 达到最大迭代
    if iteration >= max_iterations:
        return "synthesize"
    
    # 继续辩论
    return "debate"
