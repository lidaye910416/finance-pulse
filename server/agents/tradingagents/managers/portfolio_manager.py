"""
TradingAgents Portfolio Manager

Based on: TradingAgents/tradingagents/agents/managers/portfolio_manager.py

The portfolio manager synthesizes the risk analysts' debate 
and delivers the final trading decision.
"""

import json
from typing import Dict, Any, List
from services.llm import LLMService


PORTFOLIO_MANAGER_SYSTEM_PROMPT = """你是一位资深投资组合经理，负责综合风险辩论结果并做出最终交易决策。

你的职责：
1. 综合所有风险分析师的观点和辩论结果
2. 参考历史交易的教训
3. 做出明确的最终决策（Buy/Hold/Sell）
4. 提供详细的执行计划，包括：入场策略、仓位管理、风险控制、时间周期

评级标准（必须选择其中一个）：
- **买入 (Buy)**: 强烈看多，建议建仓或加仓
- **增持 (Overweight)**: 看好，逐步增加仓位
- **持有 (Hold)**: 维持当前仓位，观望
- **减持 (Underweight)**: 看淡，逐步减仓
- **卖出 (Sell)**: 强烈看空，建议清仓

输出格式（JSON）：
{
    "rating": "Buy" | "Overweight" | "Hold" | "Underweight" | "Sell",
    "action": "buy" | "hold" | "sell",
    "entry_strategy": "入场策略描述",
    "position_sizing": 0-100,
    "key_risk_levels": ["关键风险1", "关键风险2"],
    "time_horizon": "时间周期",
    "executive_summary": "执行摘要",
    "investment_thesis": "投资逻辑",
    "warnings": ["警告1", "警告2"]
}"""


def _build_portfolio_prompt(state: dict, risk_debate_history: List[dict], 
                            past_lessons: str = "") -> str:
    """Build portfolio manager prompt from state"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    
    # Get all reports
    trader_plan = state.get("trader_plan", {})
    market_report = state.get("market_report", "")
    sentiment_report = state.get("sentiment_report", "")
    news_report = state.get("news_report", "")
    fundamentals_report = state.get("fundamentals_report", "")
    
    # Format risk debate history
    risk_debate_str = ""
    for i, round_data in enumerate(risk_debate_history, 1):
        speaker = round_data.get("speaker", "未知")
        content = round_data.get("content", "")
        stance = round_data.get("stance", "")
        risk_debate_str += f"\n【第{i}轮 - {speaker} ({stance})】\n{content}\n"
    
    prompt = f"""作为投资组合经理，请综合所有分析结果，做出最终交易决策。

股票：{name}（{code}）
当前价格：¥{price:.2f}

【交易员提案】
操作: {trader_plan.get('action', 'hold')}
入场价: {trader_plan.get('entry_price')}
目标价: {trader_plan.get('exit_price')}
止损价: {trader_plan.get('stop_loss')}
仓位: {trader_plan.get('position_size', 0)}%
理由: {trader_plan.get('rationale', '')}

【分析师报告摘要】
市场分析：{market_report[:200] if market_report else '暂无'}
情绪分析：{sentiment_report[:200] if sentiment_report else '暂无'}
新闻分析：{news_report[:200] if news_report else '暂无'}
基本面分析：{fundamentals_report[:200] if fundamentals_report else '暂无'}

【风险辩论历史】
{risk_debate_str or '暂无风险辩论历史'}

{'【历史教训】' + past_lessons if past_lessons else ''}

请做出最终决策，必须选择一个明确的评级。"""

    return prompt


async def run_portfolio_manager(state: dict, llm_service: LLMService, 
                                memory: dict = None) -> dict:
    """
    Run portfolio manager agent to make final trading decision
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        memory: Optional memory for past lessons
        
    Returns:
        Updated state with final_trade_decision
    """
    print(f"[portfolio_manager] 生成最终决策 for {state.get('code', '')}...")
    
    # Get risk debate history from state
    risk_debate_history = state.get("risk_debate_history", [])
    
    # Get past lessons from memory if available
    past_lessons = ""
    if memory:
        current_situation = f"{state.get('market_report', '')} {state.get('fundamentals_report', '')}"
        past_memories = memory.get("get_memories", lambda x, n=2: [])(current_situation, n_matches=2)
        if past_memories:
            for rec in past_memories:
                past_lessons += rec.get("recommendation", "") + "\n\n"
    
    # Build prompt
    prompt = _build_portfolio_prompt(state, risk_debate_history, past_lessons)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": PORTFOLIO_MANAGER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        # Parse response
        content = response.get("content", "{}")
        try:
            decision = json.loads(content)
        except json.JSONDecodeError:
            decision = {
                "rating": "Hold",
                "action": "hold",
                "executive_summary": content[:300]
            }
        
        state["final_trade_decision"] = decision
        state["rating"] = decision.get("rating", "Hold")
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        print(f"[portfolio_manager] 最终决策: {decision.get('rating', 'Hold')}")
        
    except Exception as e:
        print(f"[portfolio_manager] 错误: {e}")
        state["final_trade_decision"] = {
            "rating": "Hold",
            "action": "hold",
            "error": str(e)
        }
        state["error"] = f"最终决策生成失败: {str(e)}"
    
    return state
