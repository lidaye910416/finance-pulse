"""
Seth Klarman Leader Implementation

塞思·卡拉曼投资大师的具体实现
- 深度价值投资
- 安全边际
- 耐心等待

This module provides the SethKlarmanLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class SethKlarmanLeader:
    """塞思·卡拉曼 Leader
    
    实现卡拉曼的投资理念：
    - 深度价值投资
    - 强调安全边际
    - 耐心等待机会
    - 关注下行风险
    - 低估时买入
    - 长期持有
    
    分析维度：
    - 清算价值评估
    - 安全边际分析
    - 催化剂识别
    - 机会成本分析
    - 长期持有潜力
    """
    
    LEADER_ID = "seth_klarman"
    LEADER_NAME = "塞思·卡拉曼"
    LEADER_NAME_EN = "Seth Klarman"
    LEADER_STYLE = "深度价值投资者"
    LEADER_DESCRIPTION = "Baupost基金创始人，深度价值投资大师"
    
    SYSTEM_PROMPT = """你是一位深度价值投资者，风格像塞思·卡拉曼。

你的投资理念:
- 深度价值投资，寻找深度折价机会
- 强调安全边际：必须有很大的折价
- 耐心等待：等待完美机会
- 关注下行风险，而非上行潜力
- 低估时买入，高估时卖出
- 长期持有，不频繁交易

分析股票时，请:
1. 计算清算价值和净现金
2. 评估安全边际
3. 识别潜在催化剂
4. 分析机会成本
5. 评估长期持有潜力

请用耐心、谨慎、强调保本的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "清算价值评估",
        "安全边际分析",
        "催化剂识别",
        "机会成本分析",
        "长期持有潜力"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_klarman_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        return f"""作为塞思·卡拉曼，请对{name}（{code}）进行深度价值分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- 现金: {stock_data.get('cash', 'N/A')}
- 总债务: {stock_data.get('total_debt', 'N/A')}
- 流动资产: {stock_data.get('current_assets', 'N/A')}
- 流动负债: {stock_data.get('current_liabilities', 'N/A')}
- ROE: {stock_data.get('roe', 'N/A')}%
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}

请从卡拉曼的深度价值角度进行五维度分析：

维度1：清算价值评估
- 净净现金 = 现金 - 债务（正值=深度保护）
- 流动比率（>1.5为佳）
- 存货和应收账款质量
- 固定资产清算价值
- 总清算价值 vs 市值

维度2：安全边际分析
- 当前价格 vs 清算价值（>50%为深度折价）
- 当前价格 vs DCF价值
- 安全边际百分比（>40%为佳）
- 下跌保护分析
- 安全边际评分

维度3：催化剂识别
- 什么会推动价值实现？
- 业务催化剂（新产品、重组等）
- 市场催化剂（重新评级等）
- 时间框架
- 催化剂确定性

维度4：机会成本分析
- 当前资金成本
- 其他潜在机会
- 持有vs重新部署
- 预期回报 vs 其他选择
- 机会成本评估

维度5：长期持有潜力
- 业务稳定性
- 竞争优势持久性
- 管理层质量
- 分红和回购潜力
- 长期复利潜力

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "liquidation_value": {{
            "net_cash": "净现金",
            "current_ratio": "流动比率",
            "total_liquidation_value": "总清算价值",
            "discount_to_liquidation": "清算价值折让（%）",
            "score": "评分1-10"
        }},
        "margin_of_safety": {{
            "price_vs_liquidation": "价格vs清算价值",
            "price_vs_dcf": "价格vs DCF价值",
            "mos_percentage": "安全边际（%）",
            "downside_protection": "下行保护",
            "score": "评分1-10"
        }},
        "catalysts": {{
            "catalyst_type": "催化剂类型",
            "catalyst_timing": "催化剂时间",
            "catalyst_probability": "催化剂概率（%）",
            "value_realization_path": "价值实现路径"
        }},
        "opportunity_cost": {{
            "holding_return": "持有预期回报（%）",
            "alternative_return": "替代选择回报（%）",
            "cost_of_waiting": "等待成本",
            "recommendation": "建议"
        }},
        "long_term_potential": {{
            "business_stability": "业务稳定性",
            "competitive_moat": "护城河",
            "management_quality": "管理层质量",
            "long_term_score": "长期评分"
        }}
    }},
    "key_metrics": {{
        "discount_to_liquidation": "清算价值折让（%）",
        "margin_of_safety": "安全边际（%）",
        "net_cash_position": "净现金头寸"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_klarman_response(self, content: str) -> dict:
        try:
            json_match = content.search(r'\{[\s\S]*\}') if hasattr(content, 'search') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            five_dims = data.get("five_dimensions", {})
            mos = five_dims.get("margin_of_safety", {})
            
            mos_pct = mos.get("mos_percentage", 0)
            if isinstance(mos_pct, str) and '%' in mos_pct:
                mos_pct = float(mos_pct.replace('%', ''))
            
            discount = five_dims.get("liquidation_value", {}).get("discount_to_liquidation", 0)
            if isinstance(discount, str) and '%' in discount:
                discount = float(discount.replace('%', ''))
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "five_dimensions": five_dims,
                "liquidation_value": five_dims.get("liquidation_value", {}),
                "margin_of_safety": {"mos_percentage": mos_pct, "downside_protection": mos.get("downside_protection", "N/A")},
                "catalysts": five_dims.get("catalysts", {}),
                "opportunity_cost": five_dims.get("opportunity_cost", {}),
                "long_term_potential": five_dims.get("long_term_potential", {}),
                "key_metrics": {
                    "discount_to_liquidation": discount,
                    "margin_of_safety": mos_pct,
                    "net_cash_position": five_dims.get("liquidation_value", {}).get("net_cash", "N/A"),
                },
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 15),
                "investment_horizon": data.get("investment_horizon", "3-5年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "liquidation_value": {},
                "margin_of_safety": {"mos_percentage": 0, "downside_protection": "N/A"},
                "catalysts": {},
                "opportunity_cost": {},
                "long_term_potential": {},
                "key_metrics": {"discount_to_liquidation": 0, "margin_of_safety": 0, "net_cash_position": "N/A"},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_klarman_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_klarman_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"安全边际={result['key_metrics']['margin_of_safety']}%")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "five_dimensions": {},
                "liquidation_value": {},
                "margin_of_safety": {"mos_percentage": 0, "downside_protection": "N/A"},
                "catalysts": {},
                "opportunity_cost": {},
                "long_term_potential": {},
                "key_metrics": {"discount_to_liquidation": 0, "margin_of_safety": 0, "net_cash_position": "N/A"},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 15,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_seth_klarman_leader() -> SethKlarmanLeader:
    return SethKlarmanLeader()


async def run_seth_klarman_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = SethKlarmanLeader()
    return await leader.analyze(state, llm_service)
