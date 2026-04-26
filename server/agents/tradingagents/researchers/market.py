"""
TradingAgents Market Analyst

Based on: TradingAgents/tradingagents/agents/researchers/

Market analyst analyzes market overview and trend for a stock.
"""

import json
from typing import Dict, Any
from services.llm import LLMService


MARKET_ANALYST_SYSTEM_PROMPT = """你是一位专业的市场分析师，擅长分析股票的市场背景和行业趋势。
你的分析关注：
1. 行业板块走势和轮动
2. 市场情绪和资金流向
3. 宏观经济环境影响
4. 政策面对行业的影响

输出格式（JSON）：
{
    "market_overview": "市场概览（80字以内）",
    "sector_trend": "行业趋势：上涨/震荡/下跌",
    "market_sentiment": "市场情绪：乐观/中性/悲观",
    "key_drivers": ["驱动因素1", "驱动因素2"],
    "risk_factors": ["风险因素1", "风险因素2"],
    "sector_rotation": "板块轮动分析"
}"""


def _build_market_prompt(state: dict) -> str:
    """Build market analyst prompt from state"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    change_pct = stock_data.get("change_percent", 0)
    
    return f"""作为市场分析师，请分析{name}（{code}）的市场背景：

当前行情：
- 价格: ¥{price:.2f}
- 涨跌幅: {change_pct:+.2f}%

请分析：
1. 所在行业板块走势
2. 市场整体情绪
3. 可能的驱动因素
4. 需要关注的风险

请用JSON格式返回分析结果。"""


async def run_market_analyst(state: dict, llm_service: LLMService) -> dict:
    """
    Run market analyst to generate market overview report
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Updated state with market_report and market_signal
    """
    print(f"[market_analyst] 分析市场背景 for {state.get('code', '')}...")
    
    prompt = _build_market_prompt(state)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": MARKET_ANALYST_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        content = response.get("content", "{}")
        try:
            report = json.loads(content)
        except json.JSONDecodeError:
            report = {"market_overview": content[:200], "sector_trend": "震荡", "market_sentiment": "中性"}
        
        state["market_report"] = json.dumps(report, ensure_ascii=False)
        state["market_signal"] = report
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        print(f"[market_analyst] 市场分析完成: {report.get('sector_trend', 'unknown')}")
        
    except Exception as e:
        print(f"[market_analyst] 错误: {e}")
        state["market_report"] = f"市场分析失败: {str(e)}"
        state["error"] = f"市场分析师错误: {str(e)}"
    
    return state
