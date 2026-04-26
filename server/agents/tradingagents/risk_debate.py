"""
TradingAgents Risk Debate Node

Based on: TradingAgents/tradingagents/agents/risk/

Risk debate evaluates investment from three risk perspectives:
- conservative: Strict stop-loss, minimum position, downside protection first
- moderate: Reasonable stop-loss, standard position, risk-reward balance
- aggressive: Loose stop-loss, larger position, upside potential first
"""

import json
from typing import Dict, Any
from services.llm import LLMService


RISK_DEBATE_SYSTEM = """你是一位专业风险辩论分析师，擅长从不同风险角度评估投资。
你会考虑保守、平衡、激进三种风险偏好，给出全面的风险评估。"""


def _build_risk_debate_prompt(state: Dict[str, Any]) -> str:
    """Build risk debate prompt for three risk perspectives"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    
    bull_signal = state.get("bullish_signal", {})
    bear_signal = state.get("bearish_signal", {})
    trader_plan = state.get("trader_plan", {})
    
    return f"""作为风险辩论分析师，请从三种风险偏好角度评估这笔投资：

股票：{name}（{code}）
当前价格：¥{price:.2f}

【交易员提案】
操作: {trader_plan.get('action', 'hold')}
入场价: {trader_plan.get('entry_price', price)}
目标价: {trader_plan.get('exit_price')}
止损价: {trader_plan.get('stop_loss')}
仓位: {trader_plan.get('position_size', 30)}%

【多空辩论结果】
多头观点: {bull_signal.get('confidence', 50)}% - {bull_signal.get('reasoning', '')[:80]}
空头观点: {bear_signal.get('confidence', 50)}% - {bear_signal.get('reasoning', '')[:80]}

请从三个角度评估：

1. 保守视角:
   - 严格止损要求
   - 最小仓位
   - 下行保护优先

2. 平衡视角:
   - 合理止损
   - 标准仓位
   - 风险收益平衡

3. 激进视角:
   - 宽松止损
   - 较大仓位
   - 上行潜力优先

请用JSON格式返回：
{{
    "conservative": {{"position": 0-100, "stop_loss_pct": 0-20, "risk_rating": "low/medium/high"}},
    "moderate": {{"position": 0-100, "stop_loss_pct": 0-20, "risk_rating": "low/medium/high"}},
    "aggressive": {{"position": 0-100, "stop_loss_pct": 0-20, "risk_rating": "low/medium/high"}},
    "final_recommendation": "综合建议",
    "key_risks": ["风险1", "风险2"]
}}"""


async def run_risk_debate(state: Dict[str, Any], llm_service: LLMService) -> Dict[str, Any]:
    """
    Run risk debate to evaluate investment from three risk perspectives
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Updated state with risk_debate, risk_recommendation, and risk_debate_history
    """
    print(f"[risk_debate] 评估风险 for {state.get('code', '')}...")
    
    risk_level = state.get("risk_level", "moderate")
    prompt = _build_risk_debate_prompt(state)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": RISK_DEBATE_SYSTEM},
            {"role": "user", "content": prompt}
        ])
        
        content = response.get("content", "{}")
        try:
            risk_analysis = json.loads(content)
        except json.JSONDecodeError:
            risk_analysis = {
                "conservative": {"position": 20, "stop_loss_pct": 3, "risk_rating": "low"},
                "moderate": {"position": 30, "stop_loss_pct": 5, "risk_rating": "medium"},
                "aggressive": {"position": 50, "stop_loss_pct": 8, "risk_rating": "high"},
                "final_recommendation": "持有观望",
                "key_risks": ["风险评估失败"]
            }
        
        # Select based on risk level
        selected_risk = risk_analysis.get(risk_level, risk_analysis.get("moderate", {}))
        
        state["risk_debate"] = risk_analysis
        state["risk_recommendation"] = selected_risk
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        # Store risk debate history
        risk_debate_history = state.get("risk_debate_history", [])
        risk_debate_history.append({
            "speaker": "Risk Analyst",
            "stance": risk_level,
            "content": json.dumps(risk_analysis, ensure_ascii=False),
        })
        state["risk_debate_history"] = risk_debate_history
        
        print(f"[risk_debate] 风险辩论完成: {risk_level}视角 - {selected_risk.get('risk_rating', 'medium')}风险")
        
    except Exception as e:
        print(f"[risk_debate] 错误: {e}")
        state["risk_debate"] = {"error": str(e)}
        state["risk_recommendation"] = {"position": 30, "stop_loss_pct": 5}
        state["error"] = f"风险辩论错误: {str(e)}"
    
    return state
