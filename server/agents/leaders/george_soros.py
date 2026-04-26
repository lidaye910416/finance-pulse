"""
George Soros Leader Implementation

乔治·索罗斯投资大师的具体实现
- 反身性理论
- 宏观对冲
- 不对称风险管理

This module provides the GeorgeSorosLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class GeorgeSorosLeader:
    """乔治·索罗斯 Leader
    
    实现索罗斯的投资理念：
    - 反身性理论（市场偏见与自我强化）
    - 宏观对冲策略
    - 不对称风险管理
    - 等待高确定性机会
    
    分析维度：
    - 反身性分析（偏见识别）
    - 宏观环境评估
    - 趋势与拐点判断
    - 仓位不对称性
    """
    
    LEADER_ID = "george_soros"
    LEADER_NAME = "乔治·索罗斯"
    LEADER_NAME_EN = "George Soros"
    LEADER_STYLE = "宏观对冲大师"
    LEADER_DESCRIPTION = "量子基金创始人，宏观对冲传奇"
    
    SYSTEM_PROMPT = """你是一位宏观对冲大师，风格像乔治·索罗斯。

你的投资理念:
- 市场总是存在偏见，偏见会导致价格偏离基本面
- 偏见会在正反馈循环中自我强化
- 等待高确定性机会，用大仓位获取大利润
- 关注宏观趋势和结构性变化

分析股票时，请:
1. 评估市场偏见和自我强化趋势
2. 分析宏观环境对股价的影响
3. 判断趋势的可持续性
4. 评估不对称的风险收益比

请用深刻、批判性的语气进行分析。"""
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_soros_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        return f"""作为乔治·索罗斯，请对{name}（{code}）进行反身性分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 行业: {stock_data.get('industry', '未知')}
- 市值: {stock_data.get('market_cap', 'N/A')}

请从索罗斯的反身性理论角度分析：

维度1：偏见识别
- 市场当前对这只股票的主要偏见是什么？
- 这种偏见是正向还是负向？
- 偏见持续了多长时间？

维度2：自我强化机制
- 什么因素可能导致偏见自我强化？
- 正反馈循环是否存在？
- 趋势是否会延续或逆转？

维度3：宏观环境
- 当前宏观环境对该股的影响
- 政策/利率/汇率的潜在影响
- 系统性风险的评估

维度4：不对称性评估
- 潜在上涨空间 vs 下跌空间
- 成功概率 vs 失败损失
- 是否值得大仓位参与

维度5：拐点信号
- 什么情况下偏见会纠正？
- 逆转的触发因素是什么？
- 提前离场的信号是什么？

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "reflexivity_analysis": {{
        "market_bias": "市场偏见描述",
        "bias_direction": "正向/负向",
        "self_reinforcement": "自我强化程度",
        "score": "评分1-10"
    }},
    "macro_environment": {{
        "impact": "宏观影响（正面/负面/中性）",
        "policy_risk": "政策风险等级",
        "systemic_risk": "系统性风险"
    }},
    "asymmetry": {{
        "upside_pct": "潜在上涨（%）",
        "downside_pct": "潜在下跌（%）",
        "win_rate": "成功概率（%）",
        "recommendation": "仓位建议"
    }},
    "turning_point_signals": ["信号1", "信号2"],
    "key_factors": ["因素1", "因素2"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（100字以内）",
    "position_recommendation": "建议仓位（%）"
}}"""
    
    def _parse_soros_response(self, content: str) -> dict:
        try:
            data = json.loads(content)
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "reflexivity_analysis": data.get("reflexivity_analysis", {}),
                "macro_environment": data.get("macro_environment", {}),
                "asymmetry": data.get("asymmetry", {}),
                "turning_point_signals": data.get("turning_point_signals", []),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 15),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold", "confidence": 50,
                "key_factors": [], "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
                "leader_id": self.id, "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_soros_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            result = self._parse_soros_response(response["content"])
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


def create_george_soros_leader() -> GeorgeSorosLeader:
    return GeorgeSorosLeader()


async def run_george_soros_analysis(state: 'AgentState', llm_service: 'LLMService') -> dict:
    leader = GeorgeSorosLeader()
    return await leader.analyze(state, llm_service)
