"""
决策 Agent

基于综合分析结果，生成最终的投资建议
"""

from graph.state import AgentState
from services.llm import LLMService


DECISION_SYSTEM = """你是一位专业的投资顾问，擅长给出明确、可执行的投资建议。
你的建议应该：1）明确买入/持有/卖出/观望；2）给出具体的价位建议；3）提示风险。"""


def _calculate_default_recommendation(state: AgentState) -> dict:
    """计算默认的投资建议（当 LLM 调用失败时）"""
    signals = state.get("analyst_signals", [])
    bullish_signal = state.get("bullish_signal", {})
    bearish_signal = state.get("bearish_signal", {})
    stock_data = state.get("stock_data", {})
    
    price = stock_data.get("price", 0)
    change_pct = stock_data.get("change_percent", 0)
    
    # 统计信号
    bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
    bearish_count = len([s for s in signals if s.get("signal") == "bearish"])
    
    # 计算平均置信度
    avg_confidence = sum(s.get("confidence", 0) for s in signals) / max(len(signals), 1)
    
    # 综合辩论结果
    bullish_conf = bullish_signal.get("confidence", 50)
    bearish_conf = bearish_signal.get("confidence", 50)
    
    # 决策逻辑
    if bullish_count > bearish_count * 1.5 and bullish_conf > 60:
        action = "buy"
        confidence = min(95, int(avg_confidence + 10))
    elif bearish_count > bullish_count * 1.5:
        action = "sell"
        confidence = min(90, int(avg_confidence))
    elif bullish_count > bearish_count:
        action = "hold"
        confidence = int(avg_confidence)
    else:
        action = "watch"
        confidence = max(40, int(avg_confidence - 15))
    
    # 计算建议价位
    if action == "buy":
        entry_price = round(price * 0.98, 2)
        exit_price = round(price * 1.15, 2)
        stop_loss = round(price * 0.95, 2)
        position_size = max(20, 60 - (bearish_count * 10))
    elif action == "sell":
        entry_price = None
        exit_price = round(price * 0.85, 2)
        stop_loss = round(price * 1.02, 2)
        position_size = 0
    else:
        entry_price = None
        exit_price = round(price * 1.08, 2) if action == "hold" else None
        stop_loss = round(price * 0.97, 2) if action in ["buy", "hold"] else None
        position_size = 30 if action == "hold" else 20
    
    # 风险评估
    risks = []
    if abs(change_pct) > 5:
        risks.append("价格波动较大")
    if bearish_count > bullish_count:
        risks.append("市场分歧较大")
    if stock_data.get("pe") and stock_data["pe"] > 40:
        risks.append("估值偏高")
    
    return {
        "action": action,
        "confidence": confidence,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "stop_loss": stop_loss,
        "position_size": position_size,
        "timeframe": "1-3个月",
        "risks": risks,
    }


async def make_decision(state: AgentState, llm_service: LLMService) -> AgentState:
    """
    决策节点
    
    最终的投资建议输出
    """
    print("[decision] 生成投资建议...")
    
    stock_data = state.get("stock_data", {})
    price = stock_data.get("price", 0)
    
    prompt = f"""基于以下分析，给出最终的投资建议：

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{price:.2f}

综合分析报告：
{state.get('final_summary', '')}

分析师信号统计：
- 多头信号: {len([s for s in state.get('analyst_signals', []) if s.get('signal') == 'bullish'])}个
- 空头信号: {len([s for s in state.get('analyst_signals', []) if s.get('signal') == 'bearish'])}个

多头研究员: {state.get('bullish_signal', {}).get('confidence', 0)}% - {state.get('bullish_signal', {}).get('reasoning', '')}
空头研究员: {state.get('bearish_signal', {}).get('confidence', 0)}% - {state.get('bearish_signal', {}).get('reasoning', '')}

请给出明确的投资建议，包括：
1. 操作建议（buy/hold/sell/watch）
2. 置信度（0-100）
3. 建议买入价（如适用）
4. 目标价
5. 止损价
6. 建议仓位
7. 投资周期
8. 主要风险

请用JSON格式返回：
{{
    "action": "buy" | "hold" | "sell" | "watch",
    "confidence": 0-100,
    "entry_price": 建议买入价或null,
    "exit_price": 目标价,
    "stop_loss": 止损价,
    "position_size": 建议仓位0-100,
    "timeframe": "投资周期",
    "risks": ["风险1", "风险2"]
}}"""
    
    try:
        # 尝试调用 LLM
        if llm_service.is_configured():
            response = await llm_service.complete([
                {"role": "system", "content": DECISION_SYSTEM},
                {"role": "user", "content": prompt},
            ])
            
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', response["content"])
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response["content"])
            
            recommendation = {
                "action": data.get("action", "watch"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "entry_price": data.get("entry_price"),
                "exit_price": data.get("exit_price"),
                "stop_loss": data.get("stop_loss"),
                "position_size": data.get("position_size", 30),
                "timeframe": data.get("timeframe", "1-3个月"),
                "risks": data.get("risks", []),
            }
            
            state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        else:
            # LLM 未配置，使用默认逻辑
            recommendation = _calculate_default_recommendation(state)
            
    except Exception as e:
        print(f"[decision] LLM 决策失败，使用默认逻辑: {e}")
        recommendation = _calculate_default_recommendation(state)
    
    state["recommendation"] = recommendation
    
    print(f"[decision] 决策完成: {recommendation['action']} (置信度{recommendation['confidence']}%)")
    
    return state
