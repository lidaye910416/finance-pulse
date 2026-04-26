"""
Stanley Druckenmiller Leader Implementation

斯坦利·德鲁肯米勒投资大师的具体实现
- 非对称风险收益分析
- 增长与动量分析
- 市场情绪评估

This module provides the StanleyDruckenmillerLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class StanleyDruckenmillerLeader:
    """斯坦利·德鲁肯米勒 Leader
    
    实现德鲁肯米勒的投资理念：
    - 追求非对称风险收益机会
    - 强调增长、动量和市场情绪
    - 通过避免重大回撤来保护资本
    - 在有利条件下愿意激进
    - 信念强时敢于押注
    
    分析维度：
    - 增长与动量分析
    - 风险收益评估
    - 估值分析
    - 市场情绪
    - 内部人活动
    """
    
    LEADER_ID = "stanley_druckenmiller"
    LEADER_NAME = "斯坦利·德鲁肯米勒"
    LEADER_NAME_EN = "Stanley Druckenmiller"
    LEADER_STYLE = "宏观对冲大师"
    LEADER_DESCRIPTION = "量子基金前基金经理，著名宏观对冲投资者"
    
    SYSTEM_PROMPT = """你是一位宏观对冲投资者，风格像斯坦利·德鲁肯米勒。

你的投资理念:
- 追求非对称风险收益机会（大涨潜力、小跌风险）
- 强调增长、动量和市场情绪
- 通过避免重大回撤来保护资本
- 愿意为真正的成长领袖支付更高估值
- 信念强时敢于激进
- 如果论点改变，迅速止损

分析股票时，请:
1. 评估增长和动量指标
2. 分析风险收益比
3. 评估估值相对增长
4. 考虑市场情绪和催化剂

请用果断、动量驱动、高确信度的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "增长与动量分析",
        "风险收益评估",
        "估值与增长匹配",
        "市场情绪分析",
        "内部人活动评估"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_druckenmiller_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为斯坦利·德鲁肯米勒，请对{name}（{code}）进行宏观对冲分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- 收入增长率: {stock_data.get('revenue_growth', 'N/A')}%
- EPS增长率: {stock_data.get('eps_growth', 'N/A')}%
- ROE: {stock_data.get('roe', 'N/A')}%
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 营业利润率: {stock_data.get('operating_margin', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从德鲁肯米勒的角度进行五维度分析：

维度1：增长与动量分析
- 收入增长年化（CAGR > 8%为强）
- EPS增长年化
- 股价动量（近期表现）
- 增长加速度

维度2：风险收益评估
- 债务股权比（低杠杆为佳）
- 价格波动性
- 下行风险 vs 上行潜力
- 非对称收益比

维度3：估值与增长匹配
- P/E vs 增长率（PEG）
- P/FCF vs 增长
- EV/EBIT vs 增长
- 是否愿意为成长支付溢价

维度4：市场情绪分析
- 新闻情绪（正面/负面）
- 市场共识
- 情绪极端程度
- 反向投资机会

维度5：内部人活动评估
- 内部人买入vs卖出比例
- 内部人信心度
- 与股价表现的相关性

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "growth_momentum": {{
            "revenue_cagr": "收入CAGR（%）",
            "eps_cagr": "EPS CAGR（%）",
            "price_momentum": "价格动量（%）",
            "growth_acceleration": "增长加速度",
            "score": "评分1-10"
        }},
        "risk_reward": {{
            "debt_to_equity": "债务股权比",
            "volatility": "波动性",
            "downside_risk": "下行风险（%）",
            "upside_potential": "上行潜力（%）",
            "asymmetric_ratio": "非对称比率",
            "score": "评分1-10"
        }},
        "valuation_vs_growth": {{
            "peg_ratio": "PEG比率",
            "pfcf_ratio": "P/FCF",
            "willingness_to_pay": "支付意愿",
            "growth_premium_justified": "成长溢价合理",
            "score": "评分1-10"
        }},
        "market_sentiment": {{
            "news_sentiment": "新闻情绪",
            "market_consensus": "市场共识",
            "sentiment_extremes": "情绪极端程度",
            "contrarian_opportunity": "反向机会",
            "score": "评分1-10"
        }},
        "insider_activity": {{
            "buy_vs_sell_ratio": "买入vs卖出比率",
            "insider_confidence": "内部人信心",
            "score": "评分1-10"
        }}
    }},
    "key_metrics": {{
        "pe": "市盈率",
        "peg": "PEG比率",
        "revenue_growth": "收入增长率（%）",
        "momentum": "动量（%）"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_druckenmiller_response(self, content: str) -> dict:
        try:
            json_match = content.search(r'\{[\s\S]*\}') if hasattr(content, 'search') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            five_dims = data.get("five_dimensions", {})
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "five_dimensions": five_dims,
                "growth_momentum": five_dims.get("growth_momentum", {}),
                "risk_reward": five_dims.get("risk_reward", {}),
                "valuation_vs_growth": five_dims.get("valuation_vs_growth", {}),
                "market_sentiment": five_dims.get("market_sentiment", {}),
                "insider_activity": five_dims.get("insider_activity", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 15),
                "investment_horizon": data.get("investment_horizon", "1-2年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "growth_momentum": {},
                "risk_reward": {},
                "valuation_vs_growth": {},
                "market_sentiment": {},
                "insider_activity": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
                "investment_horizon": "1-2年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_druckenmiller_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_druckenmiller_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"置信度={result['confidence']}%")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "five_dimensions": {},
                "growth_momentum": {},
                "risk_reward": {},
                "valuation_vs_growth": {},
                "market_sentiment": {},
                "insider_activity": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 15,
                "investment_horizon": "1-2年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_stanley_druckenmiller_leader() -> StanleyDruckenmillerLeader:
    return StanleyDruckenmillerLeader()


async def run_stanley_druckenmiller_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = StanleyDruckenmillerLeader()
    return await leader.analyze(state, llm_service)
