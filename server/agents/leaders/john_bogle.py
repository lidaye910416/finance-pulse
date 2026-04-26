"""
John Bogle Leader Implementation

约翰·博格投资大师的具体实现
- 指数投资
- 低成本理念
- 长期持有

This module provides the JohnBogleLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class JohnBogleLeader:
    """约翰·博格 Leader
    
    实现博格的投资理念：
    - 指数投资优于主动管理
    - 低成本理念
    - 长期持有
    - 被动投资策略
    - 复利的力量
    - 避免投机
    
    分析维度：
    - 指数化可行性
    - 成本效益分析
    - 被动vs主动评估
    - 长期复利潜力
    - 成本影响分析
    """
    
    LEADER_ID = "john_bogle"
    LEADER_NAME = "约翰·博格"
    LEADER_NAME_EN = "John Bogle"
    LEADER_STYLE = "指数投资之父"
    LEADER_DESCRIPTION = " Vanguard创始人，指数投资先驱"
    
    SYSTEM_PROMPT = """你是一位指数投资者，风格像约翰·博格。

你的投资理念:
- 指数投资优于大多数主动管理
- 低成本理念（费用率至关重要）
- 长期持有
- 被动投资策略
- 复利的力量
- 避免投机和交易
- 简单即有效

分析股票时，请:
1. 评估指数化可行性
2. 分析成本效益
3. 比较被动vs主动
4. 计算长期复利
5. 评估成本影响

请用简单、务实、长期导向的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "指数化可行性",
        "成本效益分析",
        "被动vs主动评估",
        "长期复利潜力",
        "成本影响分析"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_bogle_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为约翰·博格，请对{name}（{code}）进行指数化分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}
- 换手率: {stock_data.get('turnover_rate', 'N/A')}

财务指标：
- ROE: {stock_data.get('roe', 'N/A')}%
- 收入增长率: {stock_data.get('revenue_growth', 'N/A')}%
- 分红率: {stock_data.get('dividend_yield', 'N/A')}%
- 波动率: {stock_data.get('volatility', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从博格的角度进行五维度指数化分析：

维度1：指数化可行性
- 行业代表性
- 市值覆盖度
- 可投资性
- 流动性
- 指数跟踪成本

维度2：成本效益分析
- 管理费用率
- 交易成本
- 税负效率
- 跟踪误差
- 总持有成本

维度3：被动vs主动评估
- 主动Alpha潜力
- 主动管理难度
- 信息比率
- 胜率vs指数
- 主动风险

维度4：长期复利潜力
- 历史年化回报
- 分红再投资
- 复利效果
- 通胀调整后回报
- 20年潜在价值

维度5：成本影响分析
- 费用对回报影响
- 交易成本累积
- 税收影响
- 通胀侵蚀
- 净回报估算

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "index_feasibility": {{
            "sector_representation": "行业代表性",
            "market_cap_coverage": "市值覆盖度",
            "investability": "可投资性",
            "liquidity": "流动性",
            "tracking_cost": "跟踪成本"
        }},
        "cost_effectiveness": {{
            "expense_ratio": "费用率（%）",
            "trading_cost": "交易成本",
            "tax_efficiency": "税负效率",
            "tracking_error": "跟踪误差",
            "total_cost": "总持有成本"
        }},
        "passive_vs_active": {{
            "alpha_potential": "Alpha潜力",
            "active_difficulty": "主动难度",
            "information_ratio": "信息比率",
            "win_rate_vs_index": "胜率vs指数",
            "active_risk": "主动风险"
        }},
        "compounding_potential": {{
            "historical_return": "历史年化回报（%）",
            "dividend_reinvestment": "分红再投资",
            "compound_effect": "复利效果",
            "real_return": "实际回报（%）",
            "twenty_year_value": "20年潜在价值"
        }},
        "cost_impact": {{
            "fee_impact": "费用影响",
            "trading_cost_accumulation": "交易成本累积",
            "tax_impact": "税收影响",
            "inflation_erosion": "通胀侵蚀",
            "net_return": "净回报估算"
        }}
    }},
    "key_metrics": {{
        "expense_ratio": "费用率",
        "expected_return": "期望回报（%）",
        "cost_impact": "成本影响"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_bogle_response(self, content: str) -> dict:
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
                "index_feasibility": five_dims.get("index_feasibility", {}),
                "cost_effectiveness": five_dims.get("cost_effectiveness", {}),
                "passive_vs_active": five_dims.get("passive_vs_active", {}),
                "compounding_potential": five_dims.get("compounding_potential", {}),
                "cost_impact": five_dims.get("cost_impact", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 5),
                "investment_horizon": data.get("investment_horizon", "10年以上"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "index_feasibility": {},
                "cost_effectiveness": {},
                "passive_vs_active": {},
                "compounding_potential": {},
                "cost_impact": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 5,
                "investment_horizon": "10年以上",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_bogle_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_bogle_response(response["content"])
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
                "index_feasibility": {},
                "cost_effectiveness": {},
                "passive_vs_active": {},
                "compounding_potential": {},
                "cost_impact": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 5,
                "investment_horizon": "10年以上",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_john_bogle_leader() -> JohnBogleLeader:
    return JohnBogleLeader()


async def run_john_bogle_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = JohnBogleLeader()
    return await leader.analyze(state, llm_service)
