"""
TradingAgents Risk Debate Node

实现风险辩论节点，从三种风险偏好角度评估投资：
- Conservative（保守型）：强调本金安全，严格止损
- Moderate（适度型）：平衡收益与风险
- Aggressive（激进型）：追求高收益，愿意承担更大风险

This node runs after bull/bear debate and before synthesis.
"""

import json
from typing import Dict, Any, Literal
from services.llm import LLMService


# ========== Risk Perspective System Prompts ==========

CONSERVATIVE_SYSTEM = """你是一位保守型风险分析师，风格谨慎，强调本金安全。

你的分析原则：
1. 本金安全是第一优先
2. 严格设置止损位（不超过5-8%）
3. 只在确定性高的机会上建仓
4. 仓位控制在20%以下
5. 偏好高股息、低估值的优质标的

你的分析输出必须包含：
- 最坏情况下的损失预估
- 止损价位建议
- 风险收益比评估
- 适合的仓位大小"""

MODERATE_SYSTEM = """你是一位适度型风险分析师，追求收益与风险的平衡。

你的分析原则：
1. 在控制风险的前提下追求合理收益
2. 止损设置在10-15%左右
3. 仓位控制在20-40%
4. 关注风险调整后收益
5. 适度分散投资

你的分析输出必须包含：
- 预期收益与风险的平衡分析
- 止损价位建议
- 风险收益比评估
- 建议仓位"""

AGGRESSIVE_SYSTEM = """你是一位激进型风险分析师，追求最大化收益。

你的分析原则：
1. 收益优先，接受更大波动
2. 止损设置较宽松（15-25%）
3. 仓位可达40-60%甚至更高
4. 愿意追涨杀跌
5. 关注趋势和动量

你的分析输出必须包含：
- 目标收益分析
- 止损价位建议（较宽松）
- 风险收益比评估
- 高仓位建议"""


def _build_risk_prompt(state: dict, risk_type: str) -> str:
    """Build risk analyst prompt based on perspective"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", "未知")
    price = stock_data.get("price", 0)
    
    # Get bull/bear signals from debate
    bullish_signal = state.get("bullish_signal", {})
    bearish_signal = state.get("bearish_signal", {})
    
    # Get analyst signals
    analyst_signals = state.get("analyst_signals", [])
    
    return f"""作为{risk_type}风险分析师，请评估{name}（{code}）的投资风险：

当前行情：
- 价格: ¥{price:.2f}

多头观点：{bullish_signal.get('reasoning', '暂无')[:100] if bullish_signal else '暂无'}
空头观点：{bearish_signal.get('reasoning', '暂无')[:100] if bearish_signal else '暂无'}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%置信度)" for s in analyst_signals[:5]]) or '暂无'}

请提供：
1. 关键风险因素（最多5个）
2. 建议止损价位（%）
3. 最大可承受损失
4. 建议仓位比例
5. 风险等级（低/中/高/极高）

请用JSON格式返回：
{{
    "risk_type": "{risk_type}",
    "risk_level": "low" | "medium" | "high" | "extreme",
    "stop_loss_pct": 0-30,
    "max_loss_pct": 0-30,
    "recommended_position_pct": 0-60,
    "risk_reward_ratio": "1:1" ~ "1:5",
    "key_risks": ["风险1", "风险2", "风险3"],
    "risk_mitigation": ["缓解措施1", "缓解措施2"],
    "reasoning": "风险分析理由（100字以内）"
}}"""


def _parse_risk_response(content: str, risk_type: str) -> dict:
    """Parse risk analysis response"""
    try:
        # Try to extract JSON from content
        json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(content)
        
        return {
            "risk_type": risk_type,
            "risk_level": data.get("risk_level", "medium"),
            "stop_loss_pct": min(30, max(0, float(data.get("stop_loss_pct", 10)))),
            "max_loss_pct": min(30, max(0, float(data.get("max_loss_pct", 10)))),
            "recommended_position_pct": min(60, max(0, float(data.get("recommended_position_pct", 20)))),
            "risk_reward_ratio": data.get("risk_reward_ratio", "1:2"),
            "key_risks": data.get("key_risks", []),
            "risk_mitigation": data.get("risk_mitigation", []),
            "reasoning": data.get("reasoning", "")[:200],
        }
    except json.JSONDecodeError:
        return {
            "risk_type": risk_type,
            "risk_level": "medium",
            "stop_loss_pct": 10,
            "max_loss_pct": 10,
            "recommended_position_pct": 20,
            "risk_reward_ratio": "1:2",
            "key_risks": ["风险分析失败"],
            "risk_mitigation": ["等待数据更新"],
            "reasoning": content[:200] if content else "风险分析完成",
        }


async def run_risk_debate(state: dict, llm_service: LLMService) -> dict:
    """
    Run risk debate from three perspectives
    
    This node evaluates investment from conservative, moderate, and aggressive viewpoints.
    Results are stored in state for later synthesis.
    """
    print(f"[risk_debate] 开始风险辩论 for {state.get('code', '')}...")
    
    risk_types = [
        ("conservative", CONSERVATIVE_SYSTEM),
        ("moderate", MODERATE_SYSTEM),
        ("aggressive", AGGRESSIVE_SYSTEM),
    ]
    
    risk_debate_results = []
    total_tokens = 0
    
    for risk_type, system_prompt in risk_types:
        prompt = _build_risk_prompt(state, risk_type)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            
            risk_analysis = _parse_risk_response(response.get("content", "{}"), risk_type)
            risk_analysis["tokens"] = response.get("tokens", 0)
            
            risk_debate_results.append(risk_analysis)
            total_tokens += risk_analysis["tokens"]
            
            print(f"[risk_debate] {risk_type}: {risk_analysis['risk_level']}, "
                  f"止损{risk_analysis['stop_loss_pct']}%, "
                  f"仓位{risk_analysis['recommended_position_pct']}%")
            
        except Exception as e:
            print(f"[risk_debate] {risk_type} 分析错误: {e}")
            risk_debate_results.append({
                "risk_type": risk_type,
                "risk_level": "medium",
                "stop_loss_pct": 10,
                "max_loss_pct": 10,
                "recommended_position_pct": 20,
                "risk_reward_ratio": "1:2",
                "key_risks": [f"分析错误: {str(e)}"],
                "risk_mitigation": ["等待重试"],
                "reasoning": "风险分析失败",
            })
    
    # Calculate aggregated risk recommendation
    risk_level_scores = {"low": 1, "medium": 2, "high": 3, "extreme": 4}
    
    # Get average stop loss and position from results
    avg_stop_loss = sum(r.get("stop_loss_pct", 10) for r in risk_debate_results) / len(risk_debate_results)
    avg_position = sum(r.get("recommended_position_pct", 20) for r in risk_debate_results) / len(risk_debate_results)
    
    # Determine consensus risk level (mode)
    risk_levels = [r.get("risk_level", "medium") for r in risk_debate_results]
    consensus_risk_level = max(set(risk_levels), key=risk_levels.count) if risk_levels else "medium"
    
    # Build final recommendation
    final_risk_recommendation = {
        "consensus_risk_level": consensus_risk_level,
        "recommended_stop_loss_pct": round(avg_stop_loss, 1),
        "recommended_position_pct": round(avg_position, 1),
        "all_risk_levels": risk_levels,
        "risk_debate_summary": _summarize_risk_debate(risk_debate_results),
    }
    
    # Store in state
    state["risk_debate_results"] = risk_debate_results
    state["risk_debate_history"] = [{
        "round": 1,
        "conservative": risk_debate_results[0] if len(risk_debate_results) > 0 else {},
        "moderate": risk_debate_results[1] if len(risk_debate_results) > 1 else {},
        "aggressive": risk_debate_results[2] if len(risk_debate_results) > 2 else {},
        "consensus_reached": True,
        "final_recommendation": final_risk_recommendation,
    }]
    state["risk_recommendation"] = final_risk_recommendation
    state["total_tokens"] = state.get("total_tokens", 0) + total_tokens
    
    print(f"[risk_debate] 风险辩论完成: 共识风险等级={consensus_risk_level}, "
          f"建议止损={avg_stop_loss:.1f}%, 建议仓位={avg_position:.1f}%")
    
    return state


def _summarize_risk_debate(results: list) -> str:
    """Summarize risk debate results"""
    if not results:
        return "风险辩论无结果"
    
    summaries = []
    for r in results:
        summaries.append(
            f"{r.get('risk_type', '未知')}型: "
            f"风险{r.get('risk_level', '中')}, "
            f"止损{r.get('stop_loss_pct', 0)}%, "
            f"仓位{r.get('recommended_position_pct', 0)}%"
        )
    
    return "; ".join(summaries)
