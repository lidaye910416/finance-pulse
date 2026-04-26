"""
TradingAgents 8-Stage Workflow

Based on: TradingAgents/tradingagents/graph/trading_graph.py

This is the complete 8-stage workflow for TradingAgents mode:

Stage 1: Market Analyst - Market overview and trend analysis
Stage 2: Social Analyst - Social media sentiment
Stage 3: News Analyst - News event analysis
Stage 4: Fundamentals Analyst - Financial data analysis
Stage 5: Bull/Bear Debate - Multi-round debate with convergence (loop)
Stage 6: Trader Proposal - Trading proposal generation
Stage 7: Risk Debate - Three risk preference debate
Stage 8: Portfolio Manager - Final investment decision

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │  1. market_analyst     - 市场概览和趋势分析                  │
    │  2. social_analyst     - 社交媒体情绪                       │
    │  3. news_analyst      - 新闻事件分析                        │
    │  4. fundamentals      - 财务数据分析                        │
    │  5. bull_bear_debate  - 多空辩论 (可循环)                   │
    │  6. trader_proposal   - 交易员提案                         │
    │  7. risk_debate      - 风险辩论 (激进/中性/保守)            │
    │  8. portfolio_manager  - 投资组合经理最终决策              │
    └─────────────────────────────────────────────────────────────┘
"""

import asyncio
import json
from typing import Dict, Any, List

from langgraph.graph import StateGraph, END

from .state import AgentState, should_continue
from services.llm import LLMService

# Import TradingAgents agents
from agents.tradingagents.researchers.market import run_market_analyst
from agents.tradingagents.researchers.social import run_social_analyst
from agents.tradingagents.researchers.news import run_news_analyst
from agents.tradingagents.managers.trader import run_trader
from agents.tradingagents.managers.portfolio_manager import run_portfolio_manager

# Bull/Bear debate configuration
BULL_SYSTEM = """你是一位专业的多头研究员，擅长从正面角度分析股票。
你会发掘股票的上涨理由、投资价值和积极因素。
你的分析应该客观但偏向乐观，给出有说服力的看多理由。"""

BEAR_SYSTEM = """你是一位专业的空头研究员，擅长从负面角度分析股票。
你会发掘股票的风险、下跌因素和问题点。
你的分析应该客观但偏向悲观，给出有说服力的看空理由。"""

# Risk debate configuration
RISK_DEBATE_SYSTEM = """你是一位专业风险辩论分析师，擅长从不同风险角度评估投资。
你会考虑保守、平衡、激进三种风险偏好，给出全面的风险评估。"""


# ==================== Stage 1: Market Analyst ====================

async def stage1_market_analyst(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 1: Market Analyst - Market overview and trend analysis"""
    print(f"[TA-Stage1] 市场分析师: 分析 {state.get('code', '')} 的市场背景...")
    
    state = await run_market_analyst(state, llm_service)
    
    print(f"[TA-Stage1] 市场分析完成: {state.get('market_signal', {}).get('sector_trend', 'unknown')}")
    return state


# ==================== Stage 2: Social Analyst ====================

async def stage2_social_analyst(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 2: Social Analyst - Social media sentiment"""
    print(f"[TA-Stage2] 社交分析师: 分析 {state.get('code', '')} 的市场情绪...")
    
    state = await run_social_analyst(state, llm_service)
    
    print(f"[TA-Stage2] 社交分析完成: {state.get('social_signal', {}).get('sentiment', 'unknown')}")
    return state


# ==================== Stage 3: News Analyst ====================

async def stage3_news_analyst(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 3: News Analyst - News event analysis"""
    print(f"[TA-Stage3] 新闻分析师: 分析 {state.get('code', '')} 的新闻事件...")

    state = await run_news_analyst(state, llm_service)

    print(f"[TA-Stage3] 新闻分析完成: {state.get('news_signal', {}).get('news_sentiment', 'unknown')}")
    return state


# ==================== Stage 4: Fundamentals Analyst ====================

async def stage4_fundamentals(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 4: Fundamentals Analyst - Financial data analysis"""
    print(f"[TA-Stage4] 基本面分析师: 分析 {state.get('code', '')} 的财务数据...")
    
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    pe = stock_data.get("pe", "N/A")
    pb = stock_data.get("pb", "N/A")
    market_cap = stock_data.get("market_cap", 0)
    
    FUNDAMENTALS_SYSTEM = """你是一位资深基本面分析师，擅长分析公司的财务状况和内在价值。
你的分析关注：
1. 财务报表关键指标（营收、利润、现金流）
2. 估值指标（PE、PB、PS、PCF）
3. 盈利能力分析（毛利率、净利率、ROE）
4. 成长性分析（营收增速、利润增速）
5. 行业地位和竞争优势

输出格式（JSON）：
{
    "financial_summary": "财务摘要（100字以内）",
    "valuation": {"pe": number, "pb": number, "rating": "低估/合理/高估"},
    "profitability": {"gross_margin": number, "net_margin": number, "roe": number},
    "growth": {"revenue_growth": number, "profit_growth": number},
    "overall_rating": "strong_buy" | "buy" | "hold" | "sell" | "strong_sell",
    "key_strengths": ["优势1", "优势2"],
    "key_weaknesses": ["劣势1", "劣势2"]
}"""

    prompt = f"""作为基本面分析师，请分析{name}（{code}）的财务数据：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {pe}
- 市净率(PB): {pb}
- 总市值: ¥{market_cap/1e8:.2f}亿

请分析：
1. 估值水平（是否低估/合理/高估）
2. 盈利能力（毛利率、净利率、ROE）
3. 成长性（营收增速、利润增速）
4. 综合评级

请用JSON格式返回分析结果。"""

    try:
        response = await llm_service.complete([
            {"role": "system", "content": FUNDAMENTALS_SYSTEM},
            {"role": "user", "content": prompt}
        ])
        
        content = response.get("content", "{}")
        try:
            report = json.loads(content)
        except json.JSONDecodeError:
            report = {"financial_summary": content[:200], "overall_rating": "hold"}
        
        state["fundamentals_report"] = json.dumps(report, ensure_ascii=False)
        state["fundamentals_signal"] = report
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        print(f"[TA-Stage4] 基本面分析完成: {report.get('overall_rating', 'hold')}")
        
    except Exception as e:
        print(f"[TA-Stage4] 错误: {e}")
        state["fundamentals_report"] = f"基本面分析失败: {str(e)}"
        state["error"] = f"基本面分析师错误: {str(e)}"
    
    return state


# ==================== Stage 5: Bull/Bear Debate ====================

def _build_bull_prompt(state: AgentState, iteration: int, bull_history: str, bear_point: str = "") -> str:
    """Build bull researcher prompt for debate"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    
    return f"""作为多头研究员，请基于以下信息给出你的看多观点：

股票：{name}（{code}）
当前价格：¥{price:.2f}
辩论轮次: 第 {iteration} 轮

已有看空观点：
{bear_point}

请给出：
1. 你的看多核心理由（最多3点）
2. 对空头观点的反驳
3. 目标价位的判断

请用JSON格式返回：
{{
    "signal": "bullish",
    "confidence": 0-100,
    "reasoning": "看多理由（100字以内）",
    "key_points": ["理由1", "理由2", "理由3"],
    "target_price": 目标价
}}"""


def _build_bear_prompt(state: AgentState, iteration: int, bear_history: str, bull_point: str = "") -> str:
    """Build bear researcher prompt for debate"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    
    return f"""作为空头研究员，请基于以下信息给出你的看空观点：

股票：{name}（{code}）
当前价格：¥{price:.2f}
辩论轮次: 第 {iteration} 轮

已有看多观点：
{bull_point}

请给出：
1. 你的看空核心理由（最多3点）
2. 对多头观点的反驳
3. 止损价位的判断

请用JSON格式返回：
{{
    "signal": "bearish",
    "confidence": 0-100,
    "reasoning": "看空理由（100字以内）",
    "key_points": ["风险1", "风险2", "风险3"],
    "stop_loss": 止损价
}}"""


async def stage5_bull_bear_debate(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 5: Bull/Bear Debate - Multi-round debate with convergence"""
    print(f"[TA-Stage5] 多空辩论: 开始辩论 for {state.get('code', '')}...")
    
    max_iterations = state.get("max_iterations", 3)
    convergence_gap = state.get("convergence_gap", 15)
    early_stop_gap = state.get("early_stop_gap", 10)
    
    bull_history = state.get("bull_history", "")
    bear_history = state.get("bear_history", "")
    debate_history = state.get("debate_history", [])
    
    bull_signal = None
    bear_signal = None
    
    for iteration in range(1, max_iterations + 1):
        state["iteration"] = iteration
        print(f"[TA-Stage5] 第 {iteration} 轮辩论...")
        
        # Build prompts
        bear_point = bear_signal.get("reasoning", "")[:100] if bear_signal else ""
        bull_point = bull_signal.get("reasoning", "")[:100] if bull_signal else ""
        
        bull_prompt = _build_bull_prompt(state, iteration, bull_history, bear_point)
        bear_prompt = _build_bear_prompt(state, iteration, bear_history, bull_point)
        
        # Run bull/bear debate in parallel
        bull_result, bear_result = await asyncio.gather(
            llm_service.complete([
                {"role": "system", "content": BULL_SYSTEM},
                {"role": "user", "content": bull_prompt}
            ]),
            llm_service.complete([
                {"role": "system", "content": BEAR_SYSTEM},
                {"role": "user", "content": bear_prompt}
            ])
        )
        
        # Parse responses
        try:
            bull_data = json.loads(bull_result["content"])
            bull_signal = {
                "agent": "多头研究员",
                "agent_id": "bull_researcher",
                "signal": "bullish",
                "confidence": min(100, max(0, int(bull_data.get("confidence", 50)))),
                "reasoning": bull_data.get("reasoning", "")[:200],
                "target_price": bull_data.get("target_price"),
            }
        except json.JSONDecodeError:
            bull_signal = {
                "agent": "多头研究员",
                "agent_id": "bull_researcher",
                "signal": "bullish",
                "confidence": 50,
                "reasoning": bull_result.get("content", "")[:200],
            }
        
        try:
            bear_data = json.loads(bear_result["content"])
            bear_signal = {
                "agent": "空头研究员",
                "agent_id": "bear_researcher",
                "signal": "bearish",
                "confidence": min(100, max(0, int(bear_data.get("confidence", 50)))),
                "reasoning": bear_data.get("reasoning", "")[:200],
                "stop_loss": bear_data.get("stop_loss"),
            }
        except json.JSONDecodeError:
            bear_signal = {
                "agent": "空头研究员",
                "agent_id": "bear_researcher",
                "signal": "bearish",
                "confidence": 50,
                "reasoning": bear_result.get("content", "")[:200],
            }
        
        # Update history
        bull_history += f"\n[第{iteration}轮] {bull_signal['reasoning']}"
        bear_history += f"\n[第{iteration}轮] {bear_signal['reasoning']}"
        
        # Check convergence
        confidence_diff = abs(bull_signal["confidence"] - bear_signal["confidence"])
        
        debate_round = {
            "round": iteration,
            "bullish": bull_signal,
            "bearish": bear_signal,
            "confidence_diff": confidence_diff,
        }
        debate_history.append(debate_round)
        
        print(f"[TA-Stage5] 第 {iteration} 轮完成 - 多头{bull_signal['confidence']}% vs 空头{bear_signal['confidence']}% (差距{confidence_diff}%)")
        
        # Check early stop condition
        if confidence_diff <= early_stop_gap:
            print(f"[TA-Stage5] 提前停止：差距{confidence_diff}% <= 提前停止阈值{early_stop_gap}%")
            break
        
        # Check convergence
        if confidence_diff < convergence_gap:
            print(f"[TA-Stage5] 收敛达成：差距{confidence_diff}% < 收敛阈值{convergence_gap}%")
            break
    
    state["bullish_signal"] = bull_signal
    state["bearish_signal"] = bear_signal
    state["bull_history"] = bull_history
    state["bear_history"] = bear_history
    state["debate_history"] = debate_history
    state["total_tokens"] = state.get("total_tokens", 0) + bull_result.get("tokens", 0) + bear_result.get("tokens", 0)
    
    # Update analyst signals
    if "analyst_signals" not in state:
        state["analyst_signals"] = []
    state["analyst_signals"] = state.get("analyst_signals", []) + [bull_signal, bear_signal]
    
    print(f"[TA-Stage5] 多空辩论完成，共 {len(debate_history)} 轮")
    return state


# ==================== Stage 6: Trader Proposal ====================

async def stage6_trader_proposal(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 6: Trader Proposal - Trading proposal generation"""
    print(f"[TA-Stage6] 交易员提案: 生成交易计划 for {state.get('code', '')}...")
    
    state = await run_trader(state, llm_service)
    
    print(f"[TA-Stage6] 交易提案完成: {state.get('trader_plan', {}).get('action', 'hold')}")
    return state


# ==================== Stage 7: Risk Debate ====================

def _build_risk_debate_prompt(state: AgentState) -> str:
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


async def stage7_risk_debate(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 7: Risk Debate - Three risk preference debate"""
    print(f"[TA-Stage7] 风险辩论: 评估风险 for {state.get('code', '')}...")
    
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
        
        print(f"[TA-Stage7] 风险辩论完成: {risk_level}视角 - {selected_risk.get('risk_rating', 'medium')}风险")
        
    except Exception as e:
        print(f"[TA-Stage7] 错误: {e}")
        state["risk_debate"] = {"error": str(e)}
        state["risk_recommendation"] = {"position": 30, "stop_loss_pct": 5}
        state["error"] = f"风险辩论错误: {str(e)}"
    
    return state


# ==================== Stage 8: Portfolio Manager ====================

async def stage8_portfolio_manager(state: AgentState, llm_service: LLMService) -> AgentState:
    """Stage 8: Portfolio Manager - Final investment decision"""
    print(f"[TA-Stage8] 投资组合经理: 最终决策 for {state.get('code', '')}...")
    
    state = await run_portfolio_manager(state, llm_service)
    
    print(f"[TA-Stage8] 最终决策: {state.get('rating', 'Hold')}")
    return state


# ==================== Workflow Creation ====================

def create_tradingagents_workflow(llm_service: LLMService) -> StateGraph:
    """
    创建 TradingAgents 8阶段工作流
    
    Args:
        llm_service: LLM 服务实例
        
    Returns:
        StateGraph: 编译后的工作流图
    """
    workflow = StateGraph(AgentState)
    
    # 添加8个阶段节点
    workflow.add_node("stage1_market", lambda state: stage1_market_analyst(state, llm_service))
    workflow.add_node("stage2_social", lambda state: stage2_social_analyst(state, llm_service))
    workflow.add_node("stage3_news", lambda state: stage3_news_analyst(state, llm_service))
    workflow.add_node("stage4_fundamentals", lambda state: stage4_fundamentals(state, llm_service))
    workflow.add_node("stage5_debate", lambda state: stage5_bull_bear_debate(state, llm_service))
    workflow.add_node("stage6_trader", lambda state: stage6_trader_proposal(state, llm_service))
    workflow.add_node("stage7_risk", lambda state: stage7_risk_debate(state, llm_service))
    workflow.add_node("stage8_portfolio", lambda state: stage8_portfolio_manager(state, llm_service))
    
    # 设置入口点
    workflow.set_entry_point("stage1_market")
    
    # 添加边 - 线性流程
    workflow.add_edge("stage1_market", "stage2_social")
    workflow.add_edge("stage2_social", "stage3_news")
    workflow.add_edge("stage3_news", "stage4_fundamentals")
    workflow.add_edge("stage4_fundamentals", "stage5_debate")
    
    # 辩论后可选择继续辩论或进入交易员提案
    workflow.add_conditional_edges(
        "stage5_debate",
        should_continue,
        {
            "debate": "stage5_debate",      # 继续辩论
            "synthesize": "stage6_trader",  # 进入交易员提案
        }
    )
    
    workflow.add_edge("stage6_trader", "stage7_risk")
    workflow.add_edge("stage7_risk", "stage8_portfolio")
    workflow.add_edge("stage8_portfolio", END)
    
    return workflow


# Alias for backwards compatibility
create_workflow = create_tradingagents_workflow
