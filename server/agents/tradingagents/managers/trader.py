"""
TradingAgents Trader Agent

Based on: TradingAgents/tradingagents/agents/trader/trader.py

The trader node receives the investment plan from research manager,
evaluates it, and creates a validated trading proposal with A-share rule checking.
"""

import json
from typing import Dict, Any
from services.llm import LLMService

# A-share trading rules configuration
A_SHARE_RULES = {
    "t_plus_1": True,      # T+1 settlement (can't sell same day)
    "涨跌停限制": True,      # Price limit (10% for normal stocks, 20% for创业板/科创板)
    "涨跌停幅度": {
        "normal": 0.10,     # 10% for normal stocks
        "chi_next": 0.20,   # 20% for 创业板
        "star_market": 0.20  # 20% for 科创板
    }
}

# Check if stock is in special market (创业板/科创板)
SPECIAL_MARKET_CODES = {
    "300": "chi_next",  # 创业板
    "301": "chi_next",  # 创业板
    "688": "star_market"  # 科创板
}

def get_market_type(code: str) -> str:
    """Get market type from stock code"""
    if len(code) >= 3:
        prefix = code[:3]
        return SPECIAL_MARKET_CODES.get(prefix, "normal")
    return "normal"

def validate_trading_plan(code: str, plan: Dict[str, Any], prev_close: float = None) -> Dict[str, Any]:
    """
    Validate and rewrite trading plan according to A-share rules
    
    Args:
        code: Stock code
        plan: Proposed trading plan
        prev_close: Previous close price for price limit validation
        
    Returns:
        Validated trading plan
    """
    market_type = get_market_type(code)
    limit_pct = A_SHARE_RULES["涨跌停幅度"].get(market_type, 0.10)
    
    validated = plan.copy()
    
    if prev_close and prev_close > 0:
        upper_limit = prev_close * (1 + limit_pct)
        lower_limit = prev_close * (1 - limit_pct)
        
        # Validate entry price
        if "entry_price" in plan and plan["entry_price"]:
            entry = plan["entry_price"]
            if entry > upper_limit:
                validated["entry_price"] = upper_limit
                validated["warnings"] = validated.get("warnings", []) + [f"买入价超出涨停限制，已调整至{upper_limit:.2f}"]
            elif entry < lower_limit:
                validated["entry_price"] = lower_limit
                validated["warnings"] = validated.get("warnings", []) + [f"买入价超出跌停限制，已调整至{lower_limit:.2f}"]
        
        # Validate exit price
        if "exit_price" in plan and plan["exit_price"]:
            exit_price = plan["exit_price"]
            if exit_price > upper_limit:
                validated["exit_price"] = upper_limit
            elif exit_price < lower_limit:
                validated["exit_price"] = lower_limit
    
    # Add T+1 warning
    if market_type != "normal" or code.startswith("6") or code.startswith("0"):
        validated["warnings"] = validated.get("warnings", []) + ["注意：A股实行T+1交收制度，当日买入的股票不能当日卖出"]
    
    return validated


TRADER_SYSTEM_PROMPT = """你是一位专业的A股交易员，擅长根据分析师的报告制定具体的交易计划。

你的职责：
1. 接收分析师团队的研究报告和投资计划
2. 结合市场情况和风险评估，制定具体的交易策略
3. 考虑A股特有的交易规则（T+1、涨跌停板等）
4. 输出结构化的交易计划，包括：买入/卖出价格区间、仓位、止损、止盈

交易计划格式（JSON）：
{
    "action": "buy" | "sell" | "hold",
    "entry_price": 建议买入价或null,
    "exit_price": 目标卖出价,
    "stop_loss": 止损价,
    "position_size": 0-100,
    "entry_range": "价格区间描述",
    "time_horizon": "持仓周期",
    "key_metrics": ["关键指标1", "关键指标2"],
    "rationale": "交易逻辑说明"
}"""

def _build_trader_prompt(state: dict, investment_plan: str = None) -> str:
    """Build trader prompt from state"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    change_pct = stock_data.get("change_percent", 0)
    
    # Get analysis reports from state
    market_report = state.get("market_report", "")
    sentiment_report = state.get("sentiment_report", "")
    news_report = state.get("news_report", "")
    fundamentals_report = state.get("fundamentals_report", "")
    bull_bear_debate = state.get("bull_bear_debate", "")
    
    prompt = f"""作为专业交易员，请为以下股票制定交易计划：

股票：{name}（{code}）
当前价格：¥{price:.2f}
涨跌幅：{change_pct:+.2f}%

【市场分析报告】
{market_report or '暂无市场分析数据'}

【情绪分析报告】
{sentiment_report or '暂无情绪分析数据'}

【新闻分析报告】
{news_report or '暂无新闻分析数据'}

【基本面分析报告】
{fundamentals_report or '暂无基本面分析数据'}

【多空辩论结果】
{bull_bear_debate or '暂无辩论结果'}

【已有的投资计划】
{investment_plan or '暂无预设投资计划，请根据以上分析自行制定'}

请用JSON格式返回交易计划："""
    
    return prompt


async def run_trader(state: dict, llm_service: LLMService) -> dict:
    """
    Run trader agent to generate trading proposal
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Updated state with trader_plan
    """
    print(f"[trader] 生成交易计划 for {state.get('code', '')}...")
    
    # Get previous close price for A-share rule validation
    prev_close = state.get("stock_data", {}).get("prev_close")
    
    # Build prompt
    investment_plan = state.get("investment_plan")
    prompt = _build_trader_prompt(state, investment_plan)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": TRADER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        # Parse response
        content = response.get("content", "{}")
        try:
            plan = json.loads(content)
        except json.JSONDecodeError:
            plan = {
                "action": "hold",
                "entry_price": None,
                "exit_price": None,
                "stop_loss": None,
                "position_size": 0,
                "rationale": content[:200]
            }
        
        # Validate against A-share rules
        code = state.get("code", "")
        validated_plan = validate_trading_plan(code, plan, prev_close)
        
        state["trader_plan"] = validated_plan
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        print(f"[trader] 交易计划生成完成: {validated_plan.get('action', 'hold')}")
        
    except Exception as e:
        print(f"[trader] 错误: {e}")
        state["trader_plan"] = {
            "action": "hold",
            "error": str(e)
        }
        state["error"] = f"交易计划生成失败: {str(e)}"
    
    return state
