"""
TradingAgents Fundamentals Analyst

Based on: TradingAgents/tradingagents/agents/analysts/

Fundamentals analyst analyzes financial data and valuation metrics.
"""

import json
from typing import Dict, Any
from services.llm import LLMService


FUNDAMENTALS_ANALYST_SYSTEM_PROMPT = """你是一位资深基本面分析师，擅长分析公司的财务状况和内在价值。
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


def _build_fundamentals_prompt(state: dict) -> str:
    """Build fundamentals analyst prompt from state"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    pe = stock_data.get("pe", "N/A")
    pb = stock_data.get("pb", "N/A")
    market_cap = stock_data.get("market_cap", 0)
    
    return f"""作为基本面分析师，请分析{name}（{code}）的财务数据：

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


async def run_fundamentals_analyst(state: dict, llm_service: LLMService) -> dict:
    """
    Run fundamentals analyst to generate financial analysis report
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Updated state with fundamentals_report and fundamentals_signal
    """
    print(f"[fundamentals_analyst] 分析财务数据 for {state.get('code', '')}...")
    
    prompt = _build_fundamentals_prompt(state)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": FUNDAMENTALS_ANALYST_SYSTEM_PROMPT},
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
        
        print(f"[fundamentals_analyst] 基本面分析完成: {report.get('overall_rating', 'hold')}")
        
    except Exception as e:
        print(f"[fundamentals_analyst] 错误: {e}")
        state["fundamentals_report"] = f"基本面分析失败: {str(e)}"
        state["error"] = f"基本面分析师错误: {str(e)}"
    
    return state
