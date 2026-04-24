"""
辩论 Agent

多空双方进行辩论，通过循环迭代直到收敛或达到最大迭代次数
"""

import json

from graph.state import AgentState
from services.llm import LLMService


BULLISH_SYSTEM = """你是一位专业的多头研究员，擅长从正面角度分析股票。
你会发掘股票的上涨理由、投资价值和积极因素。
你的分析应该客观但偏向乐观，给出有说服力的看多理由。"""

BEARISH_SYSTEM = """你是一位专业的空头研究员，擅长从负面角度分析股票。
你会发掘股票的风险、下跌因素和问题点。
你的分析应该客观但偏向悲观，给出有说服力的看空理由。"""


def _build_bullish_prompt(state: AgentState) -> str:
    """构建多头研究员的 prompt"""
    signals = state.get("analyst_signals", [])
    bullish_signals = [s for s in signals if s.get("signal") == "bullish"]
    
    return f"""作为多头研究员，请基于以下信息给出你的看多观点：

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{state.get('stock_data', {}).get('price', 0):.2f}

现有看多分析师（{len(bullish_signals)}位）：
{chr(10).join([f"- {s['agent']}: {s['reasoning'][:50]}..." for s in bullish_signals[:3]]) or '暂无'}

现有看空分析师：
{bullish_signals}  # 复用变量名，但这是给多头看的反面观点

请给出：
1. 你的看多核心理由（最多3点）
2. 最看好的买入理由
3. 目标价位的判断

请用JSON格式返回：
{{
    "signal": "bullish",
    "confidence": 0-100,
    "reasoning": "看多理由（100字以内）",
    "key_points": ["理由1", "理由2", "理由3"]
}}"""


def _build_bearish_prompt(state: AgentState) -> str:
    """构建空头研究员的 prompt"""
    signals = state.get("analyst_signals", [])
    bearish_signals = [s for s in signals if s.get("signal") == "bearish"]
    bullish_signals = [s for s in signals if s.get("signal") == "bullish"]
    
    return f"""作为空头研究员，请基于以下信息给出你的看空观点：

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{state.get('stock_data', {}).get('price', 0):.2f}

现有看空分析师（{len(bearish_signals)}位）：
{chr(10).join([f"- {s['agent']}: {s['reasoning'][:50]}..." for s in bearish_signals[:3]]) or '暂无'}

现有看多分析师：
{chr(10).join([f"- {s['agent']}: {s['reasoning'][:50]}..." for s in bullish_signals[:3]]) or '暂无'}

请给出：
1. 你的看空核心理由（最多3点）
2. 主要风险点
3. 止损价位的判断

请用JSON格式返回：
{{
    "signal": "bearish", 
    "confidence": 0-100,
    "reasoning": "看空理由（100字以内）",
    "key_points": ["风险1", "风险2", "风险3"]
}}"""


def _parse_debate_response(content: str, signal_type: str, agent_name: str, agent_id: str) -> dict:
    """解析辩论响应"""
    try:
        json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(content)
        
        return {
            "agent": agent_name,
            "agent_id": agent_id,
            "signal": data.get("signal", signal_type),
            "confidence": min(100, max(0, int(data.get("confidence", 50)))),
            "reasoning": data.get("reasoning", "")[:200],
            "key_points": data.get("key_points", []),
        }
    except json.JSONDecodeError:
        return {
            "agent": agent_name,
            "agent_id": agent_id,
            "signal": signal_type,
            "confidence": 50,
            "reasoning": content[:200] if content else "辩论完成",
            "key_points": [],
        }


async def run_debate_round(state: AgentState, llm_service: LLMService) -> AgentState:
    """
    运行一轮辩论
    
    这是 LangGraph 的循环节点，会根据条件判断是否继续
    """
    import asyncio
    
    iteration = state.get("iteration", 0) + 1
    state["iteration"] = iteration
    
    print(f"[debate] 第 {iteration} 轮辩论开始...")
    
    # 获取历史辩论
    debate_history = state.get("debate_history", [])
    
    try:
        # 并行运行多空双方
        bullish_prompt = _build_bullish_prompt(state)
        bearish_prompt = _build_bearish_prompt(state)
        
        bullish_response, bearish_response = await asyncio.gather(
            llm_service.complete([
                {"role": "system", "content": BULLISH_SYSTEM},
                {"role": "user", "content": bullish_prompt},
            ]),
            llm_service.complete([
                {"role": "system", "content": BEARISH_SYSTEM},
                {"role": "user", "content": bearish_prompt},
            ]),
        )
        
        # 解析响应
        bullish_signal = _parse_debate_response(
            bullish_response["content"],
            "bullish",
            "多头研究员",
            "bullish_researcher"
        )
        bullish_signal["tokens"] = bullish_response.get("tokens", 0)
        
        bearish_signal = _parse_debate_response(
            bearish_response["content"],
            "bearish",
            "空头研究员", 
            "bearish_researcher"
        )
        bearish_signal["tokens"] = bearish_response.get("tokens", 0)
        
        # 更新状态
        state["bullish_signal"] = bullish_signal
        state["bearish_signal"] = bearish_signal
        state["total_tokens"] = state.get("total_tokens", 0) + bullish_signal["tokens"] + bearish_signal["tokens"]
        
        # 检查是否收敛
        confidence_diff = abs(bullish_signal["confidence"] - bearish_signal["confidence"])
        consensus_reached = confidence_diff < 15
        
        # 记录辩论历史
        debate_round = {
            "round": iteration,
            "bullish": bullish_signal,
            "bearish": bearish_signal,
            "consensus_reached": consensus_reached,
            "confidence_diff": confidence_diff,
        }
        debate_history.append(debate_round)
        state["debate_history"] = debate_history
        
        print(f"[debate] 第 {iteration} 轮完成: 多头{bullish_signal['confidence']}% vs 空头{bearish_signal['confidence']}%")
        print(f"[debate] 收敛状态: {consensus_reached} (差距{confidence_diff}%)")
        
    except Exception as e:
        print(f"[debate] 辩论出错: {e}")
        state["error"] = f"辩论失败: {str(e)}"
        
        # 使用默认信号
        if not state.get("bullish_signal"):
            state["bullish_signal"] = {
                "agent": "多头研究员",
                "agent_id": "bullish_researcher",
                "signal": "bullish",
                "confidence": 55,
                "reasoning": "基于现有分析综合判断",
            }
        if not state.get("bearish_signal"):
            state["bearish_signal"] = {
                "agent": "空头研究员",
                "agent_id": "bearish_researcher", 
                "signal": "bearish",
                "confidence": 50,
                "reasoning": "需要关注回调风险",
            }
    
    return state
