"""
TradingAgents News Analyst

Based on: TradingAgents/tradingagents/agents/analysts/

News analyst analyzes news events and their impact on stock price.
"""

import json
from typing import Dict, Any
from services.llm import LLMService


NEWS_ANALYST_SYSTEM_PROMPT = """你是一位专业的新闻分析师，擅长分析股票相关的新闻事件和市场影响。
你的分析关注：
1. 重大新闻事件对股价的影响
2. 政策变化对行业的影响
3. 公司公告和业绩报告
4. 行业热点和催化剂事件

输出格式（JSON）：
{
    "news_summary": "新闻摘要（100字以内）",
    "news_sentiment": "positive" | "negative" | "neutral",
    "key_events": ["事件1", "事件2", "事件3"],
    "impact_assessment": "影响评估（50字以内）",
    "risk_alerts": ["风险提示1", "风险提示2"]
}"""


def _build_news_prompt(state: dict) -> str:
    """Build news analyst prompt from state"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    change_pct = stock_data.get("change_percent", 0)
    
    return f"""作为新闻分析师，请分析{name}（{code}）相关的新闻事件：

当前行情：
- 价格: ¥{price:.2f}
- 涨跌幅: {change_pct:+.2f}%

请分析：
1. 近期重要新闻事件
2. 新闻对股价的影响方向
3. 需要关注的风险提示

请用JSON格式返回分析结果。"""


async def run_news_analyst(state: dict, llm_service: LLMService) -> dict:
    """
    Run news analyst to generate news event analysis report
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Updated state with news_report and news_signal
    """
    print(f"[news_analyst] 分析新闻事件 for {state.get('code', '')}...")
    
    prompt = _build_news_prompt(state)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": NEWS_ANALYST_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        content = response.get("content", "{}")
        try:
            report = json.loads(content)
        except json.JSONDecodeError:
            report = {"news_summary": content[:200], "news_sentiment": "neutral"}
        
        state["news_report"] = json.dumps(report, ensure_ascii=False)
        state["news_signal"] = report
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        print(f"[news_analyst] 新闻分析完成: {report.get('news_sentiment', 'neutral')}")
        
    except Exception as e:
        print(f"[news_analyst] 错误: {e}")
        state["news_report"] = f"新闻分析失败: {str(e)}"
        state["error"] = f"新闻分析师错误: {str(e)}"
    
    return state
