"""
Mohnish Pabrai Leader Implementation

莫尼什·帕伯莱投资大师的具体实现
- 克拉曼式雪茄烟蒂投资
- 下行保护分析
- 双重潜力评估

This module provides the MohnishPabraiLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class MohnishPabraiLeader:
    """莫尼什·帕伯莱 Leader
    
    实现帕伯莱的投资理念：
    - " Heads I win, tails I don't lose much"（正面我赢，反面我不会输太多）
    - 寻找简单的业务
    - 重视下行保护和清算价值
    - 关注FCF收益率与替代品比较
    - 寻求2-3年内翻倍的潜力
    - 低风险、高潜在回报
    
    分析维度：
    - 下行保护分析
    - 现金流收益率评估
    - 翻倍潜力分析
    - 业务简单性
    - 估值安全边际
    """
    
    LEADER_ID = "mohnish_pabrai"
    LEADER_NAME = "莫尼什·帕伯莱"
    LEADER_NAME_EN = "Mohnish Pabrai"
    LEADER_STYLE = "雪茄烟蒂投资者"
    LEADER_DESCRIPTION = "Pabrai Funds创始人，价值投资实践者"
    
    SYSTEM_PROMPT = """你是一位雪茄烟蒂投资者，风格像莫尼什·帕伯莱。

你的投资理念:
- "Heads I win, tails I don't lose much" - 正面我赢，反面我不会输太多
- 寻找简单的业务
- 重视下行保护和清算价值
- 关注FCF收益率与替代品比较
- 寻求2-3年内翻倍的潜力
- 低风险、高潜在回报
- 集中投资少数机会

分析股票时，请:
1. 评估下行保护和清算价值
2. 检查净现金状况
3. 计算FCF收益率
4. 评估翻倍潜力
5. 考虑风险收益不对称

请用谨慎、保守、强调保本的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "下行保护分析",
        "现金流收益率评估",
        "翻倍潜力分析",
        "业务简单性",
        "估值安全边际"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_pabrai_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为莫尼什·帕伯莱，请对{name}（{code}）进行雪茄烟蒂投资分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 股息率: {stock_data.get('dividend_yield', 'N/A')}%
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- 流动比率: {stock_data.get('current_ratio', 'N/A')}
- 速动比率: {stock_data.get('quick_ratio', 'N/A')}
- 现金及现金等价物: {stock_data.get('cash', 'N/A')}
- 总债务: {stock_data.get('total_debt', 'N/A')}
- 净现金: {stock_data.get('net_cash', 'N/A')}
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 营业利润率: {stock_data.get('operating_margin', 'N/A')}%
- ROE: {stock_data.get('roe', 'N/A')}%
- 资产负债率: {stock_data.get('debt_ratio', 'N/A')}%
- 流动资产: {stock_data.get('current_assets', 'N/A')}
- 流动负债: {stock_data.get('current_liabilities', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从帕伯莱的角度进行五维度分析：

维度1：下行保护分析
- 净现金状况 = 现金 - 债务（正值=强保护）
- 流动比率（>1.5为佳）
- 清算价值 vs 市值
- NCAV（净流动资产）分析
- 下行空间估算

维度2：现金流收益率评估
- FCF收益率 = FCF / 市值（> 10%为佳）
- FCF vs 替代投资机会
- FCF稳定性
- 现金生成能力

维度3：翻倍潜力分析
- 当前估值 vs 内在价值
- 2-3年内翻倍的概率
- 催化剂（市场重新定价、业务改善）
- 潜在回报 vs 风险

维度4：业务简单性
- 业务模式是否简单易懂
- 主营业务是否清晰
- 避免复杂业务
- 审计报告是否干净

维度5：估值安全边际
- PE vs 历史平均/行业
- PB vs 清算价值
- EV/EBIT vs 竞争对手
- 安全边际百分比

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "downside_protection": {{
            "net_cash": "净现金",
            "current_ratio": "流动比率",
            "liquidation_value_vs_market": "清算价值vs市值",
            "ncav": "NCAV（净流动资产）",
            "downside_risk": "下行风险（%）",
            "score": "评分1-10"
        }},
        "cash_flow_yield": {{
            "fcf_yield": "FCF收益率（%）",
            "vs_alternatives": "vs 替代投资",
            "fcf_stability": "FCF稳定性",
            "cash_generation": "现金生成能力",
            "score": "评分1-10"
        }},
        "double_potential": {{
            "upside_to_intrinsic": "内在价值上涨空间（%）",
            "time_to_double": "翻倍时间（年）",
            "probability_of_doubling": "翻倍概率（%）",
            "catalysts": "催化剂",
            "score": "评分1-10"
        }},
        "business_simplicity": {{
            "understandable": "业务易懂程度",
            "main_business_clear": "主营业务清晰",
            "avoid_complex": "避免复杂业务",
            "audit_clean": "审计干净",
            "score": "评分1-10"
        }},
        "valuation_margin": {{
            "pe_vs_history": "P/E vs 历史",
            "pb_vs_liquidation": "P/B vs 清算",
            "margin_of_safety_pct": "安全边际（%）",
            "valuation_grade": "估值等级"
        }}
    }},
    "key_metrics": {{
        "pe": "市盈率",
        "pb": "市净率",
        "fcf_yield": "FCF收益率（%）",
        "net_cash": "净现金"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_pabrai_response(self, content: str) -> dict:
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
                "downside_protection": five_dims.get("downside_protection", {}),
                "cash_flow_yield": five_dims.get("cash_flow_yield", {}),
                "double_potential": five_dims.get("double_potential", {}),
                "business_simplicity": five_dims.get("business_simplicity", {}),
                "valuation_margin": five_dims.get("valuation_margin", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 15),
                "investment_horizon": data.get("investment_horizon", "2-3年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "downside_protection": {},
                "cash_flow_yield": {},
                "double_potential": {},
                "business_simplicity": {},
                "valuation_margin": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
                "investment_horizon": "2-3年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_pabrai_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_pabrai_response(response["content"])
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
                "downside_protection": {},
                "cash_flow_yield": {},
                "double_potential": {},
                "business_simplicity": {},
                "valuation_margin": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 15,
                "investment_horizon": "2-3年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_mohnish_pabrai_leader() -> MohnishPabraiLeader:
    return MohnishPabraiLeader()


async def run_mohnish_pabrai_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = MohnishPabraiLeader()
    return await leader.analyze(state, llm_service)
