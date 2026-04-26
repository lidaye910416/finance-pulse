"""
Ed Thorp Leader Implementation

爱德华·索普投资大师的具体实现
- 套利思维
- 数学优势
- 风险管理

This module provides the EdThorpLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class EdThorpLeader:
    """爱德华·索普 Leader
    
    实现索普的投资理念：
    - 寻找数学优势
    - 可转换套利
    - 事件驱动策略
    - 严格风险管理
    - 凯利公式应用
    - 长期正期望值
    
    分析维度：
    - 数学优势评估
    - 套利机会识别
    - 事件驱动分析
    - 凯利公式应用
    - 风险回报率
    """
    
    LEADER_ID = "ed_thorp"
    LEADER_NAME = "爱德华·索普"
    LEADER_NAME_EN = "Ed Thorp"
    LEADER_STYLE = "数学套利大师"
    LEADER_DESCRIPTION = "数学天才，期权定价先驱，量化投资先驱"
    
    SYSTEM_PROMPT = """你是一位数学套利投资者，风格像爱德华·索普。

你的投资理念:
- 寻找数学优势
- 可转换套利策略
- 事件驱动策略
- 严格风险管理
- 凯利公式应用
- 长期正期望值
- 避免不对称风险

分析股票时，请:
1. 评估数学优势
2. 识别套利机会
3. 分析事件驱动
4. 应用凯利公式
5. 计算风险回报

请用数学化、精确、强调概率优势的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "数学优势评估",
        "套利机会识别",
        "事件驱动分析",
        "凯利公式应用",
        "风险回报率"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_thorp_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为爱德华·索普，请对{name}（{code}）进行数学套利分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}
- 波动率: {stock_data.get('volatility', 'N/A')}

财务指标：
- ROE: {stock_data.get('roe', 'N/A')}%
- 资产负债率: {stock_data.get('debt_ratio', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}
- 净债务: {stock_data.get('net_debt', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从索普的角度进行五维度数学套利分析：

维度1：数学优势评估
- 期望值计算
- 概率优势
- 风险调整后优势
- 统计显著性
- 边缘稳定性

维度2：套利机会识别
- 可转换套利机会
- 事件驱动机会
- 相对价值机会
- 统计套利机会
- 市场效率低下

维度3：事件驱动分析
- 并购套利机会
- 重组套利机会
- 分拆套利机会
- 股权激励事件
- 诉讼结果预期

维度4：凯利公式应用
- 胜率估算
- 盈亏比
- 凯利 fraction 推荐
- 头寸规模
- 资金管理

维度5：风险回报率
- 不对称回报结构
- 下行保护
- 上行潜力
- 期望值评估
- 风险预算

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "mathematical_edge": {{
            "expected_value": "期望值",
            "probability_edge": "概率优势",
            "risk_adjusted_edge": "风险调整优势",
            "statistical_significance": "统计显著性",
            "edge_stability": "边缘稳定性",
            "score": "评分1-10"
        }},
        "arbitrage_opportunities": {{
            "convertible_arbitrage": "可转债套利",
            "event_driven": "事件驱动",
            "relative_value": "相对价值",
            "statistical_arbitrage": "统计套利",
            "market_inefficiency": "市场效率低下"
        }},
        "event_analysis": {{
            "ma_arbitrage": "并购套利",
            "restructuring": "重组套利",
            "spinoff": "分拆套利",
            "litigation_outcome": "诉讼结果",
            "event_probability": "事件概率"
        }},
        "kelly_formula": {{
            "win_probability": "胜率",
            "win_loss_ratio": "盈亏比",
            "kelly_fraction": "凯利比例",
            "position_size": "建议头寸",
            "bankroll_management": "资金管理"
        }},
        "risk_return": {{
            "asymmetric_return": "不对称回报",
            "downside_protection": "下行保护",
            "upside_potential": "上行潜力",
            "expected_return": "期望回报",
            "risk_budget": "风险预算"
        }}
    }},
    "key_metrics": {{
        "expected_value": "期望值",
        "kelly_fraction": "凯利比例",
        "edge": "优势"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_thorp_response(self, content: str) -> dict:
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
                "mathematical_edge": five_dims.get("mathematical_edge", {}),
                "arbitrage_opportunities": five_dims.get("arbitrage_opportunities", {}),
                "event_analysis": five_dims.get("event_analysis", {}),
                "kelly_formula": five_dims.get("kelly_formula", {}),
                "risk_return": five_dims.get("risk_return", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 10),
                "investment_horizon": data.get("investment_horizon", "3-12个月"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "mathematical_edge": {},
                "arbitrage_opportunities": {},
                "event_analysis": {},
                "kelly_formula": {},
                "risk_return": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 10,
                "investment_horizon": "3-12个月",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_thorp_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_thorp_response(response["content"])
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
                "mathematical_edge": {},
                "arbitrage_opportunities": {},
                "event_analysis": {},
                "kelly_formula": {},
                "risk_return": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 10,
                "investment_horizon": "3-12个月",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_ed_thorp_leader() -> EdThorpLeader:
    return EdThorpLeader()


async def run_ed_thorp_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = EdThorpLeader()
    return await leader.analyze(state, llm_service)
