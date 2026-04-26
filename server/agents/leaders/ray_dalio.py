"""
Ray Dalio Leader Implementation

雷·达里奥投资大师的具体实现
- 全天候投资组合
- 风险平价
- 经济机器思维

This module provides the RayDalioLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class RayDalioLeader:
    """雷·达里奥 Leader
    
    实现达里奥的投资理念：
    - 全天候投资组合思维
    - 风险平价配置
    - 理解经济机器
    - 分散化降低风险
    - 理解债务周期
    - 基于原则的投资
    
    分析维度：
    - 经济增长敏感性
    - 通胀敏感性
    - 风险平价分析
    - 多元化效益
    - 周期位置评估
    """
    
    LEADER_ID = "ray_dalio"
    LEADER_NAME = "雷·达里奥"
    LEADER_NAME_EN = "Ray Dalio"
    LEADER_STYLE = "风险平价大师"
    LEADER_DESCRIPTION = "桥水基金创始人，全天候投资组合理念"
    
    SYSTEM_PROMPT = """你是一位风险平价投资者，风格像雷·达里奥。

你的投资理念:
- 全天候投资组合思维
- 风险平价配置
- 理解经济机器运转
- 分散化降低风险
- 理解债务周期
- 基于原则的投资
- 避免极端赌注

分析股票时，请:
1. 评估经济增长敏感性
2. 分析通胀敏感性
3. 考虑风险平价
4. 评估多元化效益
5. 确定周期位置

请用系统性、原则性、强调风险管理的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "经济增长敏感性",
        "通胀敏感性",
        "风险平价分析",
        "多元化效益",
        "周期位置评估"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_dalio_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为雷·达里奥，请对{name}（{code}）进行全天候风险分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- ROE: {stock_data.get('roe', 'N/A')}%
- 收入增长率: {stock_data.get('revenue_growth', 'N/A')}%
- 资产负债率: {stock_data.get('debt_ratio', 'N/A')}%
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}
- 净债务: {stock_data.get('net_debt', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从达里奥的角度进行五维度全天候分析：

维度1：经济增长敏感性
- 业务对GDP增长的敏感度
- 周期性 vs 防周期性
- 经济衰退时的表现
- 扩张期的表现
- 增长beta

维度2：通胀敏感性
- 定价权评估
- 成本传导能力
- 通胀上升时的表现
- 通胀保护能力
- 商品价格敏感度

维度3：风险平价分析
- 与债券的相关性
- 与大宗商品的相关性
- 与黄金的相关性
- 波动性特征
- 最大回撤风险

维度4：多元化效益
- 投资组合多元化贡献
- 与其他资产的相关性
- 非相关性收益
- 尾部风险对冲
- 分散化价值

维度5：周期位置评估
- 债务周期位置
- 经济周期位置
- 货币政策位置
- 财政政策位置
- 估值周期位置

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "growth_sensitivity": {{
            "gdp_beta": "GDP beta",
            "cyclicality": "周期性程度",
            "recession_performance": "衰退期表现",
            "expansion_performance": "扩张期表现",
            "score": "评分1-10"
        }},
        "inflation_sensitivity": {{
            "pricing_power": "定价权",
            "cost_pass_through": "成本传导",
            "inflation_hedge": "通胀对冲",
            "commodity_sensitivity": "商品敏感度",
            "score": "评分1-10"
        }},
        "risk_parity": {{
            "bond_correlation": "债券相关性",
            "commodity_correlation": "商品相关性",
            "gold_correlation": "黄金相关性",
            "volatility_profile": "波动性特征",
            "max_drawdown_risk": "最大回撤风险"
        }},
        "diversification": {{
            "portfolio_contribution": "组合贡献",
            "correlation_benefit": "相关性收益",
            "tail_hedge": "尾部对冲",
            "diversification_value": "分散化价值",
            "score": "评分1-10"
        }},
        "cycle_position": {{
            "debt_cycle": "债务周期位置",
            "economic_cycle": "经济周期位置",
            "monetary_cycle": "货币政策",
            "fiscal_cycle": "财政政策",
            "valuation_cycle": "估值周期"
        }}
    }},
    "key_metrics": {{
        "pe": "市盈率",
        "beta": "Beta",
        "volatility": "波动率"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_dalio_response(self, content: str) -> dict:
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
                "growth_sensitivity": five_dims.get("growth_sensitivity", {}),
                "inflation_sensitivity": five_dims.get("inflation_sensitivity", {}),
                "risk_parity": five_dims.get("risk_parity", {}),
                "diversification": five_dims.get("diversification", {}),
                "cycle_position": five_dims.get("cycle_position", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 10),
                "investment_horizon": data.get("investment_horizon", "3-5年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "growth_sensitivity": {},
                "inflation_sensitivity": {},
                "risk_parity": {},
                "diversification": {},
                "cycle_position": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 10,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_dalio_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_dalio_response(response["content"])
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
                "growth_sensitivity": {},
                "inflation_sensitivity": {},
                "risk_parity": {},
                "diversification": {},
                "cycle_position": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 10,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_ray_dalio_leader() -> RayDalioLeader:
    return RayDalioLeader()


async def run_ray_dalio_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = RayDalioLeader()
    return await leader.analyze(state, llm_service)
