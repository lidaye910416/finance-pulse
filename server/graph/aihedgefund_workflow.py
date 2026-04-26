"""
AI Hedge Fund Workflow

PRD Section 6.2 - AI Hedge Fund mode with 4-layer architecture

Architecture:
    Layer 1: Data Collection
    Layer 2: Dynamic Analyst Selection (based on leader style)
    Layer 3: Risk Agent Evaluation (full version)
    Layer 4: Leader Decision with Full Intervention

The workflow routes to the appropriate analyst types based on the leader's investment style,
uses a comprehensive risk evaluation, and gives the leader full decision-making authority.
"""

from typing import Literal

from langgraph.graph import StateGraph, END

from .state import AgentState
from config.leaders import LEADERS_BY_ID, STYLE_ANALYST_MAP
from services.llm import LLMService


# Analyst types available for selection
ANALYST_TYPES = {
    "fundamental": {
        "name": "基本面分析师",
        "name_en": "Fundamental Analyst",
        "system_prompt": """你是一位资深基本面分析师，擅长分析公司的财务状况、盈利能力和内在价值。
你关注：财务报表、盈利能力、现金流、估值指标（PE、PB）、行业地位、竞争优势。"""
    },
    "technical": {
        "name": "技术分析师",
        "name_en": "Technical Analyst",
        "system_prompt": """你是一位专业技术分析师，擅长通过价格走势和成交量判断股票趋势。
你关注：均线系统、MACD、KDJ、布林带、支撑阻力位、趋势线、形态分析。"""
    },
    "sentiment": {
        "name": "情绪分析师",
        "name_en": "Sentiment Analyst",
        "system_prompt": """你是一位市场情绪分析专家，擅长判断市场情绪和资金流向。
你关注：北向资金、融资融券、主力净流入、市场情绪指标、资金流向分析。"""
    },
    "financial": {
        "name": "财务分析师",
        "name_en": "Financial Analyst",
        "system_prompt": """你是一位专业财务分析师，擅长深度财务分析。
你关注：资产负债表、利润表、现金流量表、财务比率、资产质量、债务结构。"""
    },
    "bullish": {
        "name": "多头分析师",
        "name_en": "Bullish Analyst",
        "system_prompt": """你是一位专业的多头分析师，擅长发掘股票的上涨理由和投资价值。
你关注：正面因素、增长潜力、催化剂事件、估值修复空间。"""
    },
    "bearish": {
        "name": "空头分析师",
        "name_en": "Bearish Analyst",
        "system_prompt": """你是一位专业的空头分析师，擅长发掘股票的风险和下跌因素。
你关注：负面因素、风险点、经营问题、行业下行压力。"""
    },
}


RISK_AGENT_SYSTEM = """你是一位专业的风险评估专家，擅长全面评估投资风险。
你关注市场风险、信用风险、流动性风险、操作风险等各个方面。
你的评估应该客观全面，帮助投资者做出理性的决策。"""


def _get_analysts_for_style(leader_style: str) -> list[dict]:
    """Get analyst types for a given leader style"""
    analyst_type_ids = STYLE_ANALYST_MAP.get(leader_style, ["fundamental", "technical"])
    return [
        {**ANALYST_TYPES[analyst_id], "id": analyst_id}
        for analyst_id in analyst_type_ids
    ]


def _build_analysis_prompt(analyst: dict, stock_data: dict, leader_name: str, leader_style: str) -> str:
    """Build analyst prompt with leader context"""
    return f"""作为{analyst['name_en']}，请分析以下股票：

股票：{stock_data.get('name', '未知')}（{stock_data.get('code', '')}）

当前行情：
- 价格: ¥{stock_data.get('price', 0):.2f}
- 涨跌幅: {stock_data.get('change_percent', 0):+.2f}%
- 今开: ¥{stock_data.get('open', 0):.2f}
- 最高: ¥{stock_data.get('high', 0):.2f}
- 最低: ¥{stock_data.get('low', 0):.2f}
- 成交量: {stock_data.get('volume', 0)/10000:.2f}万手
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}

【重要背景】
你正在为{leader_name}提供分析支持。{leader_name}的投资风格是{leader_style}。

请用JSON格式返回分析结果：
{{
    "signal": "bullish" | "bearish" | "neutral",
    "confidence": 0-100,
    "reasoning": "分析理由（100字以内）",
    "key_points": ["要点1", "要点2", "要点3"]
}}"""


def _build_risk_prompt(state: AgentState, leader_style: str) -> str:
    """Build risk evaluation prompt"""
    signals = state.get("analyst_signals", [])
    stock_data = state.get("stock_data", {})
    risk_config = state.get("risk_config", {})

    bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
    bearish_count = len([s for s in signals if s.get("signal") == "bearish"])

    return f"""作为风险评估专家，请对以下分析进行全面风险评估：

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{stock_data.get('price', 0):.2f}

【分析师共识】
- 看多: {bullish_count}位
- 看空: {bearish_count}位

【分析师详情】
{chr(10).join([f"- {s['agent']}: {s['signal']} ({s['confidence']}%) - {s.get('reasoning', '')[:60]}" for s in signals])}

【风险偏好设置】
- 风险等级: {state.get('risk_level', 'moderate')}
- 最大仓位: {risk_config.get('max_position', 30)}%
- 止损线: {risk_config.get('stop_loss', 5)}%
- 波动率警报: {risk_config.get('volatility_alert', 8)}%

请评估以下风险维度：
1. 市场风险（系统性风险、市场波动）
2. 行业风险（行业景气度、竞争格局）
3. 公司风险（经营风险、财务风险）
4. 流动性风险
5. 尾部风险（黑天鹅事件）

请用JSON格式返回：
{{
    "overall_risk_score": 0-100,
    "risk_level": "low" | "medium" | "high",
    "key_risks": ["风险1", "风险2", "风险3"],
    "risk_mitigation": ["缓解措施1", "缓解措施2"],
    "position_adjustment": -20 到 +20 (建议的仓位调整)
}}"""


def _build_leader_decision_prompt(state: AgentState, leader: dict) -> str:
    """Build leader decision prompt with full intervention authority"""
    signals = state.get("analyst_signals", [])
    risk_evaluation = state.get("risk_evaluation", {})
    stock_data = state.get("stock_data", {})

    bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
    bearish_count = len([s for s in signals if s.get("signal") == "bearish"])
    avg_confidence = sum(s.get("confidence", 0) for s in signals) / max(len(signals), 1)

    return f"""作为{leader.name}（{leader.description}），请做出最终投资决策。

【你的投资风格】
- 风格: {leader.style}
- 核心理念: {leader.description}

股票：{state.get('name', '')}（{state.get('code', '')}）
当前价格：¥{stock_data.get('price', 0):.2f}

【分析师共识】
- 看多: {bullish_count}位
- 看空: {bearish_count}位
- 平均置信度: {avg_confidence:.1f}%

【分析师详情】
{chr(10).join([f"- {s['agent']}: {s['signal']} ({s['confidence']}%) - {s.get('reasoning', '')[:60]}" for s in signals])}

【风险评估】
- 风险评分: {risk_evaluation.get('overall_risk_score', 50)}/100
- 风险等级: {risk_evaluation.get('risk_level', 'medium')}
- 主要风险: {', '.join(risk_evaluation.get('key_risks', [])[:3])}
- 建议仓位调整: {risk_evaluation.get('position_adjustment', 0)}%

【你的权限】
作为投资大师，你有完全的决策权。你可以根据自己的投资风格和判断：
1. 接受或否决分析师的建议
2. 调整目标价和止损价
3. 修改建议仓位
4. 添加你自己的投资逻辑

请用JSON格式返回最终决策：
{{
    "action": "buy" | "hold" | "sell" | "watch",
    "confidence": 0-100,
    "entry_price": 建议买入价或null,
    "exit_price": 目标价,
    "stop_loss": 止损价,
    "position_size": 建议仓位0-100,
    "timeframe": "投资周期",
    "reasoning": "你的决策理由（结合你的投资风格）",
    "risks": ["风险1", "风险2"],
    "overrides": {"分析师建议": "你的调整理由"}
}}"""


async def _run_layer1_collect(state: AgentState, llm_service: LLMService = None) -> AgentState:
    """Layer 1: Data Collection"""
    from services.data import DataService

    print(f"[aihedgefund] Layer 1: 收集 {state['code']} 数据...")

    data_service = DataService()
    code = state["code"]

    try:
        stock_data = data_service.get_stock_data_sync(code)
        state["stock_data"] = stock_data
        print(f"[aihedgefund] Layer 1: 数据收集完成")
    except Exception as e:
        state["error"] = f"数据获取失败: {str(e)}"
        print(f"[aihedgefund] Layer 1 错误: {e}")

    return state


async def _run_layer2_analysts(state: AgentState, llm_service: LLMService = None) -> AgentState:
    """Layer 2: Dynamic Analyst Selection based on leader style"""
    import asyncio

    leader_id = state.get("leader_id")
    leader = LEADERS_BY_ID.get(leader_id)

    if not leader:
        state["error"] = f"Leader not found: {leader_id}"
        return state

    # Get analysts based on leader style
    analysts = _get_analysts_for_style(leader.style)

    print(f"[aihedgefund] Layer 2: 动态选择分析师 for {leader.name} (风格: {leader.style})")
    print(f"[aihedgefund] Layer 2: 选择分析师类型: {[a['id'] for a in analysts]}")

    stock_data = state.get("stock_data", {})

    # Run analysts in parallel
    tasks = []
    for analyst in analysts:
        prompt = _build_analysis_prompt(analyst, stock_data, leader.name, leader.style)
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
        analyst = analysts[i]
        if isinstance(result, Exception):
            print(f"[aihedgefund] Layer 2: {analyst['name']} 错误: {result}")
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

    print(f"[aihedgefund] Layer 2: 分析师分析完成，收集到 {len(signals)} 个信号")

    return state


async def _run_layer3_risk(state: AgentState, llm_service: LLMService = None) -> AgentState:
    """Layer 3: Risk Agent Evaluation (full version)"""
    leader_id = state.get("leader_id")
    leader = LEADERS_BY_ID.get(leader_id, {})

    print(f"[aihedgefund] Layer 3: 风险评估...")

    prompt = _build_risk_prompt(state, leader.get("style", ""))

    try:
        response = await llm_service.complete([
            {"role": "system", "content": RISK_AGENT_SYSTEM},
            {"role": "user", "content": prompt},
        ])

        import json
        try:
            data = json.loads(response["content"])
            state["risk_evaluation"] = {
                "overall_risk_score": data.get("overall_risk_score", 50),
                "risk_level": data.get("risk_level", "medium"),
                "key_risks": data.get("key_risks", []),
                "risk_mitigation": data.get("risk_mitigation", []),
                "position_adjustment": data.get("position_adjustment", 0),
            }
        except json.JSONDecodeError:
            state["risk_evaluation"] = {
                "overall_risk_score": 50,
                "risk_level": "medium",
                "key_risks": ["风险评估解析失败"],
                "risk_mitigation": [],
                "position_adjustment": 0,
            }

        state["total_tokens"] += response.get("tokens", 0)

    except Exception as e:
        print(f"[aihedgefund] Layer 3 风险评估错误: {e}")
        state["risk_evaluation"] = {
            "overall_risk_score": 50,
            "risk_level": "medium",
            "key_risks": [f"风险评估错误: {str(e)}"],
            "risk_mitigation": [],
            "position_adjustment": 0,
        }

    print(f"[aihedgefund] Layer 3: 风险评估完成")

    return state


async def _run_layer4_decision(state: AgentState, llm_service: LLMService = None) -> AgentState:
    """Layer 4: Leader Decision with Full Intervention"""
    leader_id = state.get("leader_id")
    leader = LEADERS_BY_ID.get(leader_id, {})

    print(f"[aihedgefund] Layer 4: {leader.get('name', 'Unknown')} 做出最终决策...")

    prompt = _build_leader_decision_prompt(state, leader)

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
                "overrides": data.get("overrides", {}),
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
                "overrides": {},
            }

        state["total_tokens"] += response.get("tokens", 0)

        # Generate summary
        signals = state.get("analyst_signals", [])
        bullish_count = len([s for s in signals if s.get("signal") == "bullish"])
        bearish_count = len([s for s in signals if s.get("signal") == "bearish"])

        state["final_summary"] = f"基于{leader.get('name')}的投资风格分析：{bullish_count}位分析师看多，{bearish_count}位分析师看空。{leader.get('name')}最终决策：{state['recommendation']['action']}，置信度{state['recommendation']['confidence']}%。"

    except Exception as e:
        print(f"[aihedgefund] Layer 4 决策错误: {e}")
        state["error"] = f"决策失败: {str(e)}"
        state["recommendation"] = {
            "action": "watch",
            "confidence": 50,
            "risks": [f"决策错误: {str(e)}"],
        }

    print(f"[aihedgefund] Layer 4: 决策完成: {state['recommendation']['action']}")

    return state


def create_aihedgefund_workflow(llm_service: LLMService) -> StateGraph:
    """
    创建 AI Hedge Fund 工作流

    4层架构:
    1. collect_data: 数据收集
    2. run_analysts: 动态分析师选择（基于领袖风格）
    3. evaluate_risk: 风险评估（完整版）
    4. leader_decision: 领袖决策（完全干预权）

    Args:
        llm_service: LLM 服务实例

    Returns:
        StateGraph: 编译后的工作流图
    """
    workflow = StateGraph(AgentState)

    # 添加节点 - 使用闭包捕获 llm_service
    def make_node(fn):
        async def wrapper(state):
            return await fn(state, llm_service)
        return wrapper

    workflow.add_node("collect_data", make_node(_run_layer1_collect))
    workflow.add_node("run_analysts", make_node(_run_layer2_analysts))
    workflow.add_node("evaluate_risk", make_node(_run_layer3_risk))
    workflow.add_node("leader_decision", make_node(_run_layer4_decision))

    # 设置入口和边
    workflow.set_entry_point("collect_data")
    workflow.add_edge("collect_data", "run_analysts")
    workflow.add_edge("run_analysts", "evaluate_risk")
    workflow.add_edge("evaluate_risk", "leader_decision")
    workflow.add_edge("leader_decision", END)

    return workflow
