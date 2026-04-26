"""
Fusion Workflow

PRD Section 6.3 - Fusion mode combining TradingAgents with leader decision

Architecture:
    Layer 1: Data Collection
    Layer 2: 5 Fixed Analysts (bull/bear/technical/fundamental/sentiment)
    Layer 3: Bull/Bear Debate with Convergence
    Layer 4: Risk Agent (simplified)
    Layer 5: Leader Decision (19 masters, decision only)

This workflow combines the standard TradingAgents debate mechanism with
investment master decision-making authority.
"""

from typing import Literal

from langgraph.graph import StateGraph, END

from .state import AgentState
from config.leaders import LEADERS_BY_ID
from services.llm import LLMService


# 5 Fixed Analysts for Fusion mode
FUSION_ANALYSTS = [
    {
        "id": "fusion_bull",
        "name": "多头研究员",
        "name_en": "Bull Researcher",
        "style": "bullish",
        "system_prompt": """你是一位专业的多头研究员，擅长发掘股票的上涨理由和投资价值。
你关注公司的正面因素、增长潜力、催化剂事件和估值修复空间。
你的分析应该客观但偏向乐观，给出有说服力的看多理由。""",
    },
    {
        "id": "fusion_bear",
        "name": "空头研究员",
        "name_en": "Bear Researcher",
        "style": "bearish",
        "system_prompt": """你是一位专业的空头研究员，擅长发掘股票的风险和下跌因素。
你关注公司的负面因素、风险点、经营问题、行业下行压力。
你的分析应该客观但偏向悲观，给出有说服力的看空理由。""",
    },
    {
        "id": "fusion_technical",
        "name": "技术分析师",
        "name_en": "Technical Analyst",
        "style": "technical",
        "system_prompt": """你是一位专业技术分析师，擅长通过价格走势和成交量判断股票趋势。
你关注均线系统、MACD、KDJ、布林带、支撑阻力位、趋势线和形态分析。
你的分析应该基于图表和技术指标。""",
    },
    {
        "id": "fusion_fundamental",
        "name": "基本面分析师",
        "name_en": "Fundamental Analyst",
        "style": "fundamental",
        "system_prompt": """你是一位资深基本面分析师，擅长分析公司的财务状况、盈利能力和内在价值。
你关注财务报表、盈利能力、现金流、估值指标（PE、PB）、行业地位和竞争优势。
你的分析应该基于公司财务数据。""",
    },
    {
        "id": "fusion_sentiment",
        "name": "情绪分析师",
        "name_en": "Sentiment Analyst",
        "style": "sentiment",
        "system_prompt": """你是一位市场情绪分析专家，擅长判断市场情绪和资金流向。
你关注北向资金、融资融券、主力净流入、市场情绪指标和资金流向分析。
你的分析应该基于市场情绪数据。""",
    },
]


RISK_AGENT_SIMPLIFIED_SYSTEM = """你是一位专业的风险评估专家，擅长简明扼要地评估投资风险。
你关注：市场风险、公司风险、流动性风险。
给出简洁的风险评估即可。"""


LEADER_DECISION_SYSTEM = """你是一位经验丰富的投资大师。
你的决策应该结合多方分析意见，给出明确、可执行的投资建议。
你有完全的决策权，可以接受或调整分析师的建议。"""


def _build_analyst_prompt(analyst: dict, stock_data: dict) -> str:
    """Build analyst prompt"""
    return f"""分析股票：{stock_data.get('name', '未知')}（{stock_data.get('code', '')}）

当前行情：
- 价格: ¥{stock_data.get('price', 0):.2f}
- 涨跌幅: {stock_data.get('change_percent', 0):+.2f}%
- 今开: ¥{stock_data.get('open', 0):.2f}
- 最高: ¥{stock_data.get('high', 0):.2f}
- 最低: ¥{stock_data.get('low', 0):.2f}
- 成交量: {stock_data.get('volume', 0)/10000:.2f}万手
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}

请用JSON格式返回分析结果：
{{
    "signal": "bullish" | "bearish" | "neutral",
    "confidence": 0-100,
    "reasoning": "分析理由（80字以内）",
    "key_points": ["要点1", "要点2"]
}}"""


def _build_bullish_debate_prompt(state: AgentState) -> str:
    """Build bullish side debate prompt"""
    signals = state.get("analyst_signals", [])
    bearish_signals = [s for s in signals if s.get("signal") == "bearish"]

    return f"""作为多头研究员，请基于以下信息给出你的看多观点：

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{state.get('stock_data', {}).get('price', 0):.2f}

现有看空分析师意见：
{chr(10).join([f"- {s['agent']}: {s['reasoning'][:50]}..." for s in bearish_signals[:2]]) or '暂无'}

请给出：
1. 你的看多核心理由（最多3点）
2. 反驳看空观点的论据
3. 目标价位的判断

请用JSON格式返回：
{{
    "signal": "bullish",
    "confidence": 0-100,
    "reasoning": "看多理由（100字以内）",
    "key_points": ["理由1", "理由2", "理由3"]
}}"""


def _build_bearish_debate_prompt(state: AgentState) -> str:
    """Build bearish side debate prompt"""
    signals = state.get("analyst_signals", [])
    bullish_signals = [s for s in signals if s.get("signal") == "bullish"]

    return f"""作为空头研究员，请基于以下信息给出你的看空观点：

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{state.get('stock_data', {}).get('price', 0):.2f}

现有看多分析师意见：
{chr(10).join([f"- {s['agent']}: {s['reasoning'][:50]}..." for s in bullish_signals[:2]]) or '暂无'}

请给出：
1. 你的看空核心理由（最多3点）
2. 反驳看多观点的论据
3. 止损价位的判断

请用JSON格式返回：
{{
    "signal": "bearish",
    "confidence": 0-100,
    "reasoning": "看空理由（100字以内）",
    "key_points": ["风险1", "风险2", "风险3"]
}}"""


def _build_risk_prompt(state: AgentState) -> str:
    """Build simplified risk evaluation prompt"""
    signals = state.get("analyst_signals", [])
    bullish_signal = state.get("bullish_signal", {})
    bearish_signal = state.get("bearish_signal", {})
    stock_data = state.get("stock_data", {})
    risk_config = state.get("risk_config", {})

    return f"""请对以下分析进行简化的风险评估：

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{stock_data.get('price', 0):.2f}

分析师共识：
- 看多: {len([s for s in signals if s.get('signal') == 'bullish'])}位
- 看空: {len([s for s in signals if s.get('signal') == 'bearish'])}位

多空辩论结果：
- 多头置信度: {bullish_signal.get('confidence', 0)}%
- 空头置信度: {bearish_signal.get('confidence', 0)}%

风险偏好设置：
- 风险等级: {state.get('risk_level', 'moderate')}
- 最大仓位: {risk_config.get('max_position', 30)}%
- 止损线: {risk_config.get('stop_loss', 5)}%

请用JSON格式返回简化评估：
{{
    "overall_risk_score": 0-100,
    "risk_level": "low" | "medium" | "high",
    "key_risks": ["风险1", "风险2"],
    "position_adjustment": -15 到 +15
}}"""


def _build_leader_prompt(state: AgentState, leader: dict) -> str:
    """Build leader decision prompt"""
    signals = state.get("analyst_signals", [])
    debate_history = state.get("debate_history", [])
    risk_evaluation = state.get("risk_evaluation", {})
    stock_data = state.get("stock_data", {})

    # Get latest debate results
    latest_debate = debate_history[-1] if debate_history else {}

    bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
    bearish_count = len([s for s in signals if s.get("signal") == "bearish"])

    return f"""作为{leader.name}，请做出最终投资决策。

【你的背景】
{leader.description}
投资风格: {leader.style}

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{stock_data.get('price', 0):.2f}

【分析师共识】
- 看多: {bullish_count}位
- 看空: {bearish_count}位

【分析师详情】
{chr(10).join([f"- {s['agent']}: {s['signal']} ({s['confidence']}%) - {s.get('reasoning', '')[:50]}" for s in signals])}

【辩论结果】
- 多头置信度: {latest_debate.get('bullish', {}).get('confidence', 0)}%
- 空头置信度: {latest_debate.get('bearish', {}).get('confidence', 0)}%
- 收敛状态: {"是" if latest_debate.get('consensus_reached') else "否"}

【风险评估】
- 风险评分: {risk_evaluation.get('overall_risk_score', 50)}/100
- 风险等级: {risk_evaluation.get('risk_level', 'medium')}
- 建议仓位调整: {risk_evaluation.get('position_adjustment', 0)}%

请用JSON格式返回最终决策：
{{
    "action": "buy" | "hold" | "sell" | "watch",
    "confidence": 0-100,
    "entry_price": 建议买入价或null,
    "exit_price": 目标价,
    "stop_loss": 止损价,
    "position_size": 建议仓位0-100,
    "timeframe": "投资周期",
    "reasoning": "决策理由",
    "risks": ["风险1", "风险2"]
}}"""


async def _run_layer1_collect(state: AgentState, llm_service: LLMService) -> AgentState:
    """Layer 1: Data Collection"""
    from services.data import DataService

    print(f"[fusion] Layer 1: 收集 {state['code']} 数据...")

    data_service = DataService()
    code = state["code"]

    try:
        stock_data = data_service.get_stock_data_sync(code)
        state["stock_data"] = stock_data
        print(f"[fusion] Layer 1: 数据收集完成")
    except Exception as e:
        state["error"] = f"数据获取失败: {str(e)}"
        print(f"[fusion] Layer 1 错误: {e}")

    return state


async def _run_layer2_analysts(state: AgentState, llm_service: LLMService) -> AgentState:
    """Layer 2: 5 Fixed Analysts"""
    import asyncio

    print(f"[fusion] Layer 2: 运行5位固定分析师...")

    stock_data = state.get("stock_data", {})

    tasks = []
    for analyst in FUSION_ANALYSTS:
        prompt = _build_analyst_prompt(analyst, stock_data)
        tasks.append(
            llm_service.complete([
                {"role": "system", "content": analyst["system_prompt"]},
                {"role": "user", "content": prompt},
            ])
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)

    signals = []
    total_tokens = state.get("total_tokens", 0)

    for i, result in enumerate(results):
        analyst = FUSION_ANALYSTS[i]
        if isinstance(result, Exception):
            print(f"[fusion] Layer 2: {analyst['name']} 错误: {result}")
            signals.append({
                "agent": analyst["name"],
                "agent_id": analyst["id"],
                "signal": "neutral",
                "confidence": 50,
                "reasoning": f"分析服务错误: {str(result)}",
            })
        else:
            import json
            try:
                data = json.loads(result["content"])
                signals.append({
                    "agent": analyst["name"],
                    "agent_id": analyst["id"],
                    "signal": data.get("signal", "neutral"),
                    "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                    "reasoning": data.get("reasoning", "")[:200],
                    "key_points": data.get("key_points", []),
                })
                total_tokens += result.get("tokens", 0)
            except json.JSONDecodeError:
                signals.append({
                    "agent": analyst["name"],
                    "agent_id": analyst["id"],
                    "signal": "neutral",
                    "confidence": 50,
                    "reasoning": result["content"][:200],
                })

    state["analyst_signals"] = signals
    state["total_tokens"] = total_tokens

    print(f"[fusion] Layer 2: 分析师分析完成，收集到 {len(signals)} 个信号")

    return state


async def _run_layer3_debate(state: AgentState, llm_service: LLMService) -> AgentState:
    """Layer 3: Bull/Bear Debate with Convergence"""
    import asyncio

    iteration = state.get("iteration", 0) + 1
    state["iteration"] = iteration
    max_iterations = state.get("max_iterations", 3)
    convergence_gap = state.get("convergence_gap", 15)

    print(f"[fusion] Layer 3: 第 {iteration} 轮辩论...")

    try:
        bullish_prompt = _build_bullish_debate_prompt(state)
        bearish_prompt = _build_bearish_debate_prompt(state)

        bullish_response, bearish_response = await asyncio.gather(
            llm_service.complete([
                {"role": "system", "content": FUSION_ANALYSTS[0]["system_prompt"]},
                {"role": "user", "content": bullish_prompt},
            ]),
            llm_service.complete([
                {"role": "system", "content": FUSION_ANALYSTS[1]["system_prompt"]},
                {"role": "user", "content": bearish_prompt},
            ]),
        )

        bullish_signal = {
            "agent": "多头研究员",
            "agent_id": "fusion_bull",
            "signal": "bullish",
            "confidence": 60,
            "reasoning": "辩论分析",
        }
        bearish_signal = {
            "agent": "空头研究员",
            "agent_id": "fusion_bear",
            "signal": "bearish",
            "confidence": 50,
            "reasoning": "辩论分析",
        }

        import json
        try:
            data = json.loads(bullish_response["content"])
            bullish_signal = {
                "agent": "多头研究员",
                "agent_id": "fusion_bull",
                "signal": data.get("signal", "bullish"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "reasoning": data.get("reasoning", "")[:200],
                "key_points": data.get("key_points", []),
            }
        except (json.JSONDecodeError, KeyError):
            pass

        try:
            data = json.loads(bearish_response["content"])
            bearish_signal = {
                "agent": "空头研究员",
                "agent_id": "fusion_bear",
                "signal": data.get("signal", "bearish"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "reasoning": data.get("reasoning", "")[:200],
                "key_points": data.get("key_points", []),
            }
        except (json.JSONDecodeError, KeyError):
            pass

        bullish_signal["tokens"] = bullish_response.get("tokens", 0)
        bearish_signal["tokens"] = bearish_response.get("tokens", 0)

        state["bullish_signal"] = bullish_signal
        state["bearish_signal"] = bearish_signal
        state["total_tokens"] += bullish_signal["tokens"] + bearish_signal["tokens"]

        # Check convergence
        confidence_diff = abs(bullish_signal["confidence"] - bearish_signal["confidence"])
        consensus_reached = confidence_diff < convergence_gap

        debate_round = {
            "round": iteration,
            "bullish": bullish_signal,
            "bearish": bearish_signal,
            "consensus_reached": consensus_reached,
            "confidence_diff": confidence_diff,
        }
        debate_history = state.get("debate_history", [])
        debate_history.append(debate_round)
        state["debate_history"] = debate_history

        print(f"[fusion] Layer 3: 辩论完成 - 多头{bullish_signal['confidence']}% vs 空头{bearish_signal['confidence']}%")
        print(f"[fusion] Layer 3: 收敛状态: {consensus_reached} (差距{confidence_diff}%, 阈值{convergence_gap}%)")

        # Check if should continue or converge
        if iteration >= max_iterations or consensus_reached:
            state["debate_converged"] = True
        else:
            state["debate_converged"] = False

    except Exception as e:
        print(f"[fusion] Layer 3 辩论错误: {e}")
        state["error"] = f"辩论失败: {str(e)}"
        state["debate_converged"] = True

    return state


def _should_continue_debate(state: AgentState) -> Literal["debate", "synthesize"]:
    """Check if debate should continue"""
    if state.get("debate_converged"):
        return "synthesize"
    return "debate"


async def _run_layer4_risk(state: AgentState, llm_service: LLMService) -> AgentState:
    """Layer 4: Simplified Risk Agent"""
    print(f"[fusion] Layer 4: 简化风险评估...")

    prompt = _build_risk_prompt(state)

    try:
        response = await llm_service.complete([
            {"role": "system", "content": RISK_AGENT_SIMPLIFIED_SYSTEM},
            {"role": "user", "content": prompt},
        ])

        import json
        try:
            data = json.loads(response["content"])
            state["risk_evaluation"] = {
                "overall_risk_score": data.get("overall_risk_score", 50),
                "risk_level": data.get("risk_level", "medium"),
                "key_risks": data.get("key_risks", []),
                "position_adjustment": data.get("position_adjustment", 0),
            }
        except json.JSONDecodeError:
            state["risk_evaluation"] = {
                "overall_risk_score": 50,
                "risk_level": "medium",
                "key_risks": ["风险评估解析失败"],
                "position_adjustment": 0,
            }

        state["total_tokens"] += response.get("tokens", 0)

    except Exception as e:
        print(f"[fusion] Layer 4 风险评估错误: {e}")
        state["risk_evaluation"] = {
            "overall_risk_score": 50,
            "risk_level": "medium",
            "key_risks": [f"风险评估错误: {str(e)}"],
            "position_adjustment": 0,
        }

    print(f"[fusion] Layer 4: 风险评估完成")

    return state


async def _run_layer5_decision(state: AgentState, llm_service: LLMService) -> AgentState:
    """Layer 5: Leader Decision (decision only)"""
    leader_id = state.get("leader_id")
    leader = LEADERS_BY_ID.get(leader_id, {})

    print(f"[fusion] Layer 5: {leader.get('name', 'Unknown')} 做出最终决策...")

    prompt = _build_leader_prompt(state, leader)

    try:
        response = await llm_service.complete([
            {"role": "system", "content": f"你是{leader.get('name')}，{leader.get('description', '')}"},
            {"role": "user", "content": prompt},
        ])

        import json
        try:
            data = json.loads(response["content"])
            state["recommendation"] = {
                "action": data.get("action", "watch"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "entry_price": data.get("entry_price"),
                "exit_price": data.get("exit_price"),
                "stop_loss": data.get("stop_loss"),
                "position_size": data.get("position_size", 30),
                "timeframe": data.get("timeframe", "1-3个月"),
                "risks": data.get("risks", []),
                "leader_reasoning": data.get("reasoning", ""),
            }
        except json.JSONDecodeError:
            state["recommendation"] = {
                "action": "watch",
                "confidence": 50,
                "entry_price": None,
                "exit_price": None,
                "stop_loss": None,
                "position_size": 30,
                "timeframe": "1-3个月",
                "risks": ["决策解析失败"],
                "leader_reasoning": response["content"][:200],
            }

        state["total_tokens"] += response.get("tokens", 0)

        # Generate summary
        signals = state.get("analyst_signals", [])
        bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
        bearish_count = len([s for s in signals if s.get("signal") == "bearish"])

        state["final_summary"] = f"融合模式分析：{bullish_count}位分析师看多，{bearish_count}位分析师看空。经过多轮辩论收敛后，{leader.get('name')}最终决策：{state['recommendation']['action']}，置信度{state['recommendation']['confidence']}%。"

    except Exception as e:
        print(f"[fusion] Layer 5 决策错误: {e}")
        state["error"] = f"决策失败: {str(e)}"
        state["recommendation"] = {
            "action": "watch",
            "confidence": 50,
            "risks": [f"决策错误: {str(e)}"],
        }

    print(f"[fusion] Layer 5: 决策完成: {state['recommendation']['action']}")

    return state


async def _synthesize(state: AgentState, llm_service: LLMService) -> AgentState:
    """Synthesize debate results"""
    signals = state.get("analyst_signals", [])
    bullish_signal = state.get("bullish_signal", {})
    bearish_signal = state.get("bearish_signal", {})

    bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
    bearish_count = len([s for s in signals if s.get("signal") == "bearish"])

    state["final_summary"] = f"融合分析完成：{bullish_count}位分析师看多，{bearish_count}位分析师看空。多空辩论置信度：多头{bullish_signal.get('confidence', 0)}%，空头{bearish_signal.get('confidence', 0)}%。"

    return state


def create_fusion_workflow(llm_service: LLMService) -> StateGraph:
    """
    创建 Fusion 工作流

    5层架构:
    1. collect_data: 数据收集
    2. run_analysts: 5位固定分析师
    3. debate: 多空辩论（带收敛判断）
    4. evaluate_risk: 简化风险评估
    5. leader_decision: 领袖决策

    Args:
        llm_service: LLM 服务实例

    Returns:
        StateGraph: 编译后的工作流图
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("collect_data", lambda state: _run_layer1_collect(state, llm_service))
    workflow.add_node("run_analysts", lambda state: _run_layer2_analysts(state, llm_service))
    workflow.add_node("debate", lambda state: _run_layer3_debate(state, llm_service))
    workflow.add_node("synthesize", lambda state: _synthesize(state, llm_service))
    workflow.add_node("evaluate_risk", lambda state: _run_layer4_risk(state, llm_service))
    workflow.add_node("leader_decision", lambda state: _run_layer5_decision(state, llm_service))

    # 设置入口和边
    workflow.set_entry_point("collect_data")
    workflow.add_edge("collect_data", "run_analysts")
    workflow.add_edge("run_analysts", "debate")

    # 辩论循环条件边
    workflow.add_conditional_edges(
        "debate",
        _should_continue_debate,
        {
            "debate": "debate",
            "synthesize": "evaluate_risk",
        }
    )

    workflow.add_edge("evaluate_risk", "leader_decision")
    workflow.add_edge("leader_decision", END)

    return workflow
