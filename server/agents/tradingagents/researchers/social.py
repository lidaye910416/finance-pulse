"""
TradingAgents Social Analyst

Based on: TradingAgents/tradingagents/agents/researchers/

Social analyst analyzes social media sentiment and investor behavior.
"""

import json
from typing import Dict, Any
from services.llm import LLMService


SOCIAL_ANALYST_SYSTEM_PROMPT = """你是一位专业的社交媒体分析师，擅长分析市场情绪和投资者行为。
你的分析关注：
1. 社交媒体讨论热度
2. 机构投资者动向
3. 散户情绪指标
4. 舆情热点追踪

输出格式（JSON）：
{
    "social_summary": "社交情绪摘要（80字以内）",
    "sentiment": "乐观/中性/悲观",
    "heat_level": "高/中/低",
    "key_topics": ["话题1", "话题2"],
    "investor_behavior": "投资者行为分析",
    "sentiment_indicators": ["指标1", "指标2"]
}"""


def _build_social_prompt(state: dict) -> str:
    """Build social analyst prompt from state"""
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = stock_data.get("name", code)
    price = stock_data.get("price", 0)
    
    return f"""作为社交媒体分析师，请分析{name}（{code}）的市场情绪：

当前行情：
- 价格: ¥{price:.2f}

请分析：
1. 社交媒体讨论热度
2. 投资者情绪方向
3. 主要讨论话题
4. 机构vs散户行为

请用JSON格式返回分析结果。"""


async def run_social_analyst(state: dict, llm_service: LLMService) -> dict:
    """
    Run social analyst to generate sentiment report
    
    Args:
        state: Current workflow state
        llm_service: LLM service instance
        
    Returns:
        Updated state with social_report and social_signal
    """
    print(f"[social_analyst] 分析市场情绪 for {state.get('code', '')}...")
    
    prompt = _build_social_prompt(state)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": SOCIAL_ANALYST_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        content = response.get("content", "{}")
        try:
            report = json.loads(content)
        except json.JSONDecodeError:
            report = {"social_summary": content[:200], "sentiment": "中性", "heat_level": "中"}
        
        state["social_report"] = json.dumps(report, ensure_ascii=False)
        state["social_signal"] = report
        state["total_tokens"] = state.get("total_tokens", 0) + response.get("tokens", 0)
        
        print(f"[social_analyst] 社交分析完成: {report.get('sentiment', 'unknown')}")
        
    except Exception as e:
        print(f"[social_analyst] 错误: {e}")
        state["social_report"] = f"社交分析失败: {str(e)}"
        state["error"] = f"社交分析师错误: {str(e)}"
    
    return state
