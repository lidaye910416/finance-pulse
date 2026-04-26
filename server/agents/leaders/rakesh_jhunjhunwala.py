"""
Rakesh Jhunjhunwala Leader Implementation

拉凯什·金君瓦拉投资大师的具体实现
- 长期价值投资
- 印度市场专家
- 成长性分析

This module provides the RakeshJhunjhunwalaLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class RakeshJhunjhunwalaLeader:
    """拉凯什·金君瓦拉 Leader
    
    实现金君瓦拉的投资理念：
    - 长期价值投资，耐心持有
    - 关注成长性和行业前景
    - 在合理价格买入优质公司
    - 相信印度的长期增长潜力
    
    分析维度：
    - 业务质量评估
    - 成长潜力分析
    - 管理层诚信度
    - 估值合理性
    """
    
    LEADER_ID = "rakesh_jhunjhunwala"
    LEADER_NAME = "拉凯什·金君瓦拉"
    LEADER_NAME_EN = "Rakesh Jhunjhunwala"
    LEADER_STYLE = "长期价值投资者"
    LEADER_DESCRIPTION = "印度巴菲特，知名长期投资者"
    
    SYSTEM_PROMPT = """你是一位长期价值投资者，风格像拉凯什·金君瓦拉。

你的投资理念:
- 长期投资，耐心持有优质公司
- 关注公司的成长潜力和行业前景
- 在合理价格买入，不追求极端便宜
- 相信优质公司会创造长期价值
- 分散投资，控制风险

分析股票时，请:
1. 评估公司的长期成长潜力
2. 分析行业结构和发展空间
3. 检查管理层的诚信和能力
4. 判断当前估值是否合理

请用乐观、长期导向的语气进行分析。"""
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_jhunjhunwala_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        return f"""作为拉凯什·金君瓦拉，请对{name}（{code}）进行长期价值分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 行业: {stock_data.get('industry', '未知')}
- 市值: {stock_data.get('market_cap', 'N/A')}
- ROE: {stock_data.get('roe', 'N/A')}%
- 营收增长: {stock_data.get('revenue_growth', 'N/A')}%

请从长期价值投资角度分析：

维度1：业务质量
- 公司的核心竞争力是什么？
- 业务模式是否可持续？
- 护城河的宽度如何？

维度2：成长潜力
- 行业增速预期（%）
- 公司市场份额变化趋势
- 新产品/新市场机会

维度3：管理层评估
- 管理层的诚信度（1-10）
- 资本配置能力（1-10）
- 股东回报意识

维度4：估值分析
- 当前PE是否合理？
- 与历史估值比较
- 目标价估算（3-5年）

维度5：风险因素
- 主要风险是什么？
- 竞争威胁程度
- 政策/宏观风险

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "business_quality": {{
        "core_competence": "核心竞争力",
        "sustainability": "可持续性评估",
        "moat_width": "护城河宽度（1-10）",
        "score": "评分1-10"
    }},
    "growth_potential": {{
        "industry_growth": "行业增速（%）",
        "market_share_trend": "市场份额趋势",
        "new_opportunities": "新机会"
    }},
    "management": {{
        "integrity": "诚信度（1-10）",
        "capital_allocation": "资本配置（1-10）",
        "score": "评分1-10"
    }},
    "valuation": {{
        "pe": "当前PE",
        "historical_pe": "历史PE区间",
        "target_price_3y": "3年目标价（元）",
        "upside_potential": "上涨空间（%）"
    }},
    "key_factors": ["因素1", "因素2"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（100字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_jhunjhunwala_response(self, content: str) -> dict:
        try:
            data = json.loads(content)
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "business_quality": data.get("business_quality", {}),
                "growth_potential": data.get("growth_potential", {}),
                "management": data.get("management", {}),
                "valuation": data.get("valuation", {}),
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
                "decision": "hold", "confidence": 50,
                "business_quality": {}, "growth_potential": {},
                "key_factors": [], "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
                "leader_id": self.id, "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_jhunjhunwala_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            result = self._parse_jhunjhunwala_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}")
            return result
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold", "confidence": 30,
                "key_factors": [], "risk_factors": [f"分析失败: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 15,
                "leader_id": self.id, "leader_name": self.name, "tokens": 0,
            }


def create_rakesh_jhunjhunwala_leader() -> RakeshJhunjhunwalaLeader:
    return RakeshJhunjhunwalaLeader()


async def run_rakesh_jhunjhunwala_analysis(state: 'AgentState', llm_service: 'LLMService') -> dict:
    leader = RakeshJhunjhunwalaLeader()
    return await leader.analyze(state, llm_service)
