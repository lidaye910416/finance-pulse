"""
分析师 Agent

并行运行多个专业分析师对股票进行分析
"""

import json
from typing import Any

from graph.state import AgentState
from services.llm import LLMService


# ========== 分析师配置 ==========

ANALYSTS = [
    {
        "id": "warren_buffett",
        "name": "沃伦·巴菲特",
        "name_en": "Warren Buffett",
        "style": "价值投资大师",
        "system_prompt": """你是一位价值投资大师，风格像沃伦·巴菲特。
你专注于公司的内在价值，寻找被低估的优质企业。
你关注：护城河、盈利能力、现金流、长期竞争力。
分析时注重基本面，避免投机取巧。""",
    },
    {
        "id": "ben_graham",
        "name": "本杰明·格雷厄姆",
        "name_en": "Benjamin Graham", 
        "style": "安全边际专家",
        "system_prompt": """你是一位安全边际专家，风格像本杰明·格雷厄姆。
你专注于风险控制，寻找足够安全边际的投资机会。
你关注：市盈率、市净率、股息率、债务水平。
分析时注重估值的安全边际。""",
    },
    {
        "id": "peter_lynch",
        "name": "彼得·林奇",
        "name_en": "Peter Lynch",
        "style": "成长投资专家",
        "system_prompt": """你是一位成长投资专家，风格像彼得·林奇。
你擅长发掘高成长性的公司，追求业绩增长带来的收益。
你关注：营收增长、利润率、市场份额、扩张潜力。
分析时注重公司的成长性和行业前景。""",
    },
    {
        "id": "technicals_agent",
        "name": "技术分析专家",
        "name_en": "Technical Analyst",
        "style": "技术分析专家",
        "system_prompt": """你是一位技术分析专家，擅长通过价格走势和成交量判断股票趋势。
你关注：均线系统、MACD、KDJ、布林带、支撑阻力位。
分析时注重量价配合和趋势确认。""",
    },
    {
        "id": "sentiment_agent",
        "name": "情绪分析专家",
        "name_en": "Sentiment Analyst",
        "style": "市场情绪专家",
        "system_prompt": """你是一位市场情绪分析专家，擅长判断市场情绪和资金流向。
你关注：北向资金、融资融券、主力净流入、恐慌贪婪指数。
分析时注重资金面和市场情绪的变化。""",
    },
]


def _build_analysis_prompt(analyst: dict, stock_data: dict) -> str:
    """构建分析师的 prompt"""
    return f"""分析股票：{stock_data.get('name', '未知')}（{stock_data.get('code', '')}）

当前行情数据：
- 当前价格: ¥{stock_data.get('price', 0):.2f}
- 涨跌幅: {stock_data.get('change_percent', 0):+.2f}%
- 今开: ¥{stock_data.get('open', 0):.2f}
- 最高: ¥{stock_data.get('high', 0):.2f}
- 最低: ¥{stock_data.get('low', 0):.2f}
- 成交量: {stock_data.get('volume', 0)/10000:.2f}万手
- 成交额: ¥{stock_data.get('amount', 0)/100000000:.2f}亿
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

请以{analyst['name']}（{analyst['style']}）的风格，分析这只股票的投资价值。

请用JSON格式返回分析结果：
{{
    "signal": "bullish" | "bearish" | "neutral",
    "confidence": 0-100,
    "reasoning": "分析理由（100字以内）",
    "key_points": ["要点1", "要点2", "要点3"]
}}"""


def _parse_signal_response(content: str, analyst: dict) -> dict:
    """解析 LLM 响应"""
    try:
        json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = json.loads(content)
        
        return {
            "agent": analyst["name"],
            "agent_id": analyst["id"],
            "signal": data.get("signal", "neutral"),
            "confidence": min(100, max(0, int(data.get("confidence", 50)))),
            "reasoning": data.get("reasoning", "")[:200],
        }
    except json.JSONDecodeError:
        return {
            "agent": analyst["name"],
            "agent_id": analyst["id"],
            "signal": "neutral",
            "confidence": 50,
            "reasoning": content[:200] if content else "分析完成",
        }


async def run_analyst(analyst: dict, stock_data: dict, llm_service: LLMService) -> dict:
    """运行单个分析师"""
    print(f"[analyst] {analyst['name']} 正在分析...")
    
    prompt = _build_analysis_prompt(analyst, stock_data)
    
    try:
        response = await llm_service.complete([
            {"role": "system", "content": analyst["system_prompt"]},
            {"role": "user", "content": prompt},
        ])
        
        signal = _parse_signal_response(response["content"], analyst)
        signal["tokens"] = response.get("tokens", 0)
        
        print(f"[analyst] {analyst['name']} 完成: {signal['signal']} ({signal['confidence']}%)")
        return signal
        
    except Exception as e:
        print(f"[analyst] {analyst['name']} 错误: {e}")
        return {
            "agent": analyst["name"],
            "agent_id": analyst["id"],
            "signal": "neutral",
            "confidence": 30,
            "reasoning": f"分析服务暂时不可用: {str(e)}",
        }


async def run_analysts_parallel(state: AgentState, llm_service: LLMService) -> AgentState:
    """
    并行运行所有分析师
    
    使用 asyncio.gather 实现并行调用
    """
    import asyncio
    
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    
    print(f"[run_analysts] 开始并行分析 {code}...")
    
    # 并行运行所有分析师
    tasks = [
        run_analyst(analyst, stock_data, llm_service)
        for analyst in ANALYSTS
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 收集有效结果
    signals = []
    total_tokens = state.get("total_tokens", 0)
    
    for result in results:
        if isinstance(result, dict):
            signals.append(result)
            total_tokens += result.get("tokens", 0)
        elif isinstance(result, Exception):
            print(f"[run_analysts] 分析师异常: {result}")
    
    state["analyst_signals"] = signals
    state["total_tokens"] = total_tokens
    
    print(f"[run_analysts] 完成，收集到 {len(signals)} 个信号")
    
    return state
