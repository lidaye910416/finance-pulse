"""
Howard Marks Leader Implementation

霍华德·马克斯投资大师的具体实现
- 第二层次思维
- 风险控制
- 周期认知

This module provides the HowardMarksLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class HowardMarksLeader:
    """霍华德·马克斯 Leader
    
    实现马克斯的投资理念：
    - 第二层次思维
    - 风险控制优先
    - 周期认知
    - 钟摆理论
    - 非共识正确
    - 耐心等待机会
    
    分析维度：
    - 思维层次分析
    - 风险评估
    - 周期位置判断
    - 非共识观点
    - 耐心与时机
    """
    
    LEADER_ID = "howard_marks"
    LEADER_NAME = "霍华德·马克斯"
    LEADER_NAME_EN = "Howard Marks"
    LEADER_STYLE = "风险控制大师"
    LEADER_DESCRIPTION = "Oaktree Capital创始人，顶级价值投资者"
    
    SYSTEM_PROMPT = """你是一位风险控制投资者，风格像霍华德·马克斯。

你的投资理念:
- 第二层次思维（不只是第一反应）
- 风险控制优先于回报
- 周期认知
- 钟摆理论（市场总是在乐观和悲观间摆动）
- 非共识正确
- 耐心等待机会
- 逆向投资思维

分析股票时，请:
1. 进行第二层次思考
2. 评估风险
3. 判断周期位置
4. 提出非共识观点
5. 评估时机

请用谨慎、深思熟虑、强调风险的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "思维层次分析",
        "风险评估",
        "周期位置判断",
        "非共识观点",
        "耐心与时机"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_marks_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为霍华德·马克斯，请对{name}（{code}）进行第二层次思维分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- ROE: {stock_data.get('roe', 'N/A')}%
- 收入增长率: {stock_data.get('revenue_growth', 'N/A')}%
- 资产负债率: {stock_data.get('debt_ratio', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}
- 波动率: {stock_data.get('volatility', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从马克斯的角度进行五维度第二层次思维分析：

维度1：思维层次分析
- 第一层次思维（共识观点）
- 第二层次思维（我的独特见解）
- 共识预期的错误可能性
- 信息不对称程度
- 判断质量评估

维度2：风险评估
- 永久损失风险
- 相对风险（跑输指数）
- 下行风险量化
- 风险来源识别
- 风险价格

维度3：周期位置判断
- 钟摆位置（乐观/悲观）
- 信贷周期
- 投资者情绪
- 估值周期
- 风险偏好周期

维度4：非共识观点
- 与共识的分歧点
- 非共识的正确概率
- 需要什么才能正确
- 催化剂时间
- 逆向机会

维度5：耐心与时机
- 当前风险回报比
- 等待更好机会
- 逆向投资时机
- 仓位建立策略
- 退出策略

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "thinking_levels": {{
            "first_level_consensus": "第一层次共识",
            "second_level_insight": "第二层次见解",
            "consensus_error_prob": "共识错误概率",
            "information_edge": "信息优势",
            "judgment_quality": "判断质量"
        }},
        "risk_assessment": {{
            "permanent_loss_risk": "永久损失风险",
            "relative_risk": "相对风险",
            "downside_risk": "下行风险（%）",
            "risk_sources": "风险来源",
            "risk_price": "风险价格"
        }},
        "cycle_position": {{
            "pendulum_position": "钟摆位置",
            "credit_cycle": "信贷周期",
            "sentiment": "投资者情绪",
            "valuation_cycle": "估值周期",
            "risk_appetite": "风险偏好"
        }},
        "contrarian_view": {{
            "divergence_from_consensus": "与共识分歧",
            "consensus_correct_prob": "共识正确概率",
            "requirements_to_be_right": "需要什么才能正确",
            "catalyst_timeline": "催化剂时间",
            "contrarian_opportunity": "逆向机会"
        }},
        "patience_timing": {{
            "risk_reward_ratio": "当前风险回报比",
            "wait_for_better": "等待更好机会",
            "position_build_strategy": "建仓策略",
            "exit_strategy": "退出策略",
            "patience_needed": "需要耐心"
        }}
    }},
    "key_metrics": {{
        "risk_reward": "风险回报比",
        "downside_risk": "下行风险（%）",
        "cycle_position": "周期位置"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_marks_response(self, content: str) -> dict:
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
                "thinking_levels": five_dims.get("thinking_levels", {}),
                "risk_assessment": five_dims.get("risk_assessment", {}),
                "cycle_position": five_dims.get("cycle_position", {}),
                "contrarian_view": five_dims.get("contrarian_view", {}),
                "patience_timing": five_dims.get("patience_timing", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 10),
                "investment_horizon": data.get("investment_horizon", "2-3年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "thinking_levels": {},
                "risk_assessment": {},
                "cycle_position": {},
                "contrarian_view": {},
                "patience_timing": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 10,
                "investment_horizon": "2-3年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_marks_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_marks_response(response["content"])
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
                "thinking_levels": {},
                "risk_assessment": {},
                "cycle_position": {},
                "contrarian_view": {},
                "patience_timing": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 10,
                "investment_horizon": "2-3年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_howard_marks_leader() -> HowardMarksLeader:
    return HowardMarksLeader()


async def run_howard_marks_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = HowardMarksLeader()
    return await leader.analyze(state, llm_service)
