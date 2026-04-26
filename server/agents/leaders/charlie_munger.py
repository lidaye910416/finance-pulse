"""
Charlie Munger Leader Implementation

查理·芒格投资大师的具体实现
- 心理模型分析
- 多元思维框架
- 逆向思考

This module provides the CharlieMungerLeader class that implements
Munger's mental models and multi-disciplinary thinking approach.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class CharlieMungerLeader:
    """查理·芒格 Leader
    
    实现芒格的多元思维模型理念：
    - 使用多元思维模型分析问题
    - 强调"逆向思维"的重要性
    - 追求"极好"的生意，而非"还好"
    - 耐心等待击球机会
    - 持续学习，提升认知
    
    分析维度：
    - 心理学视角（行为金融学角度）
    - 经济学视角（竞争优势）
    - 生物学视角（商业模式适应度）
    - 逆向分析（不做这件事的理由）
    - "极好"生意判断
    """
    
    # 类级别的配置
    LEADER_ID = "charlie_munger"
    LEADER_NAME = "查理·芒格"
    LEADER_NAME_EN = "Charlie Munger"
    LEADER_STYLE = "多元思维模型专家"
    LEADER_DESCRIPTION = "伯克希尔副主席，逆向思考大师"
    
    SYSTEM_PROMPT = """你是一位多元思维模型大师，风格像查理·芒格。

你的投资理念:
- 使用多元思维模型分析问题
- 强调"逆向思维"的重要性
- 追求"极好"的生意，而非"还好"
- 耐心等待击球机会
- 持续学习，提升认知

分析股票时，请:
1. 用多学科视角分析公司
2. 评估管理层的诚信和能力
3. 检查公司的竞争优势
4. 判断是否是"极好"的生意

请用深刻、睿智的语气进行分析。"""
    
    # 分析维度
    FIVE_DIMENSIONS = [
        "心理学视角（行为金融学）",
        "经济学视角（竞争优势）",
        "生物学视角（商业适应度）",
        "逆向分析",
        "极好生意判断"
    ]
    
    def __init__(self):
        """初始化 Charlie Munger Leader"""
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_munger_analysis_prompt(self, state: 'AgentState') -> str:
        """构建芒格风格的 prompt
        
        Args:
            state: 当前工作流状态
            
        Returns:
            格式化后的 prompt 字符串
        """
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为查理·芒格，请用多元思维模型对{name}（{code}）进行分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 行业: {stock_data.get('industry', '未知')}
- ROE: {stock_data.get('roe', 'N/A')}%
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 市值: {stock_data.get('market_cap', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从芒格的多元思维模型角度进行五维度分析：

维度1：心理学视角（行为金融学）
- 市场参与者的非理性行为
- 认知偏差（过度自信、锚定效应等）
- 情绪周期（贪婪/恐惧）
- 信息传播偏差

维度2：经济学视角（竞争优势）
- 护城河类型（品牌、转换成本、网络效应、成本优势）
- 护城河宽度和持久性
- 竞争对手复制的难度
- 定价权分析

维度3：生物学视角（商业适应度）
- 商业模式的进化能力
- 适应环境变化的能力
- 抗"黑天鹅"能力
- 熵减能力（有序性保持）

维度4：逆向分析
- 为什么这个投资可能失败？
- 不投资这只股票的理由是什么？
- 存在哪些"非显而易见"的风险？
- 历史上有类似的失败案例吗？

维度5："极好"生意判断
- 这是否是"极好"（wonderful）的生意，还是"还好"（okay）的生意？
- 管理层是否诚信、有能力？
- 长期竞争优势是否清晰？
- 资本配置是否合理？

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "psychology_insight": {{
            "market_biases": "市场偏差描述",
            "sentiment_indicator": "情绪指标（极度贪婪/贪婪/中性/恐惧/极度恐惧）",
            "cognitive_traps": ["认知陷阱1", "认知陷阱2"],
            "score": "评分1-10"
        }},
        "economic_advantage": {{
            "moat_type": "护城河类型",
            "moat_width": "护城河宽度（年）",
            "pricing_power": "定价权（强/中/弱）",
            "competitive_risk": "竞争风险",
            "score": "评分1-10"
        }},
        "biological_adaptation": {{
            "evolution_ability": "进化能力（1-10）",
            "environmental_fit": "环境适应性（1-10）",
            "black_swan_resistance": "抗黑天鹅能力（1-10）",
            "score": "评分1-10"
        }},
        "reverse_analysis": {{
            "failure_reasons": ["失败原因1", "失败原因2"],
            "non_obvious_risks": ["非显而易见风险1"],
            "historical_parallels": "历史类比",
            "confidence_in_investment": "投资信心"
        }},
        "wonderful_business": {{
            "is_wonderful": "极好/还好/较差",
            "management_integrity": "管理层诚信度（1-10）",
            "management_capability": "管理层能力（1-10）",
            "long_term_advantage": "长期竞争优势清晰度",
            "capital_allocation": "资本配置合理性",
            "score": "评分1-10"
        }}
    }},
    "overall_quality_score": "整体质量评分（1-10）",
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_munger_response(self, content: str) -> dict:
        """解析芒格分析响应
        
        Args:
            content: LLM 返回的原始内容
            
        Returns:
            结构化的分析结果字典
        """
        try:
            json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            five_dims = data.get("five_dimensions", {})
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "five_dimensions": five_dims,
                "psychology_insight": {
                    "market_biases": five_dims.get("psychology_insight", {}).get("market_biases", "N/A"),
                    "sentiment_indicator": five_dims.get("psychology_insight", {}).get("sentiment_indicator", "N/A"),
                    "cognitive_traps": five_dims.get("psychology_insight", {}).get("cognitive_traps", []),
                    "score": five_dims.get("psychology_insight", {}).get("score", "N/A"),
                },
                "economic_advantage": {
                    "moat_type": five_dims.get("economic_advantage", {}).get("moat_type", "N/A"),
                    "moat_width": five_dims.get("economic_advantage", {}).get("moat_width", "N/A"),
                    "pricing_power": five_dims.get("economic_advantage", {}).get("pricing_power", "N/A"),
                    "score": five_dims.get("economic_advantage", {}).get("score", "N/A"),
                },
                "biological_adaptation": {
                    "evolution_ability": five_dims.get("biological_adaptation", {}).get("evolution_ability", "N/A"),
                    "environmental_fit": five_dims.get("biological_adaptation", {}).get("environmental_fit", "N/A"),
                    "score": five_dims.get("biological_adaptation", {}).get("score", "N/A"),
                },
                "reverse_analysis": {
                    "failure_reasons": five_dims.get("reverse_analysis", {}).get("failure_reasons", []),
                    "non_obvious_risks": five_dims.get("reverse_analysis", {}).get("non_obvious_risks", []),
                    "historical_parallels": five_dims.get("reverse_analysis", {}).get("historical_parallels", "N/A"),
                },
                "wonderful_business": {
                    "is_wonderful": five_dims.get("wonderful_business", {}).get("is_wonderful", "N/A"),
                    "management_integrity": five_dims.get("wonderful_business", {}).get("management_integrity", "N/A"),
                    "management_capability": five_dims.get("wonderful_business", {}).get("management_capability", "N/A"),
                    "score": five_dims.get("wonderful_business", {}).get("score", "N/A"),
                },
                "overall_quality_score": data.get("overall_quality_score", "N/A"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 20),
                "investment_horizon": data.get("investment_horizon", "长期（5年+）"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "psychology_insight": {"score": "N/A"},
                "economic_advantage": {"score": "N/A"},
                "biological_adaptation": {"score": "N/A"},
                "reverse_analysis": {"failure_reasons": []},
                "wonderful_business": {"score": "N/A"},
                "overall_quality_score": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 20,
                "investment_horizon": "长期（5年+）",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        """运行 Charlie Munger 分析
        
        Args:
            state: 当前工作流状态
            llm_service: LLM 服务实例
            
        Returns:
            Charlie Munger 五维度分析结果
        """
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        
        prompt = self._build_munger_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_munger_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            wonderful = result.get("wonderful_business", {})
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"生意质量={result.get('overall_quality_score', 'N/A')}, "
                  f"是否极好={wonderful.get('is_wonderful', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "five_dimensions": {},
                "psychology_insight": {"score": "N/A"},
                "economic_advantage": {"score": "N/A"},
                "biological_adaptation": {"score": "N/A"},
                "reverse_analysis": {"failure_reasons": []},
                "wonderful_business": {"score": "N/A"},
                "overall_quality_score": "N/A",
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 20,
                "investment_horizon": "长期（5年+）",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        """获取五维度框架列表
        
        Returns:
            5个维度的描述列表
        """
        return self.FIVE_DIMENSIONS


# 便捷函数

def create_charlie_munger_leader() -> CharlieMungerLeader:
    """创建 Charlie Munger Leader 实例"""
    return CharlieMungerLeader()


async def run_charlie_munger_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    """运行 Charlie Munger 分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例
        
    Returns:
        Charlie Munger 五维度分析结果
    """
    leader = CharlieMungerLeader()
    return await leader.analyze(state, llm_service)
