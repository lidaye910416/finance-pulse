"""
Paul Tudor Jones Leader Implementation

保罗·都铎·琼斯投资大师的具体实现
- 趋势跟踪
- 技术分析
- 风险管理

This module provides the PaulTudorJonesLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class PaulTudorJonesLeader:
    """保罗·都铎·琼斯 Leader
    
    实现琼斯的投资理念：
    - 趋势跟踪策略
    - 强调技术分析
    - 严格的风险管理
    - 损失最小化优先
    - 快速止损
    - 宏观视野
    
    分析维度：
    - 趋势分析
    - 技术指标评估
    - 风险管理
    - 动量评估
    - 宏观背景
    """
    
    LEADER_ID = "paul_tudor_jones"
    LEADER_NAME = "保罗·都铎·琼斯"
    LEADER_NAME_EN = "Paul Tudor Jones"
    LEADER_STYLE = "趋势交易大师"
    LEADER_DESCRIPTION = "Tudor Investment创始人，著名宏观交易员"
    
    SYSTEM_PROMPT = """你是一位趋势交易投资者，风格像保罗·都铎·琼斯。

你的投资理念:
- 趋势跟踪策略
- 强调技术分析
- 严格的风险管理
- 损失最小化优先
- 快速止损
- 宏观视野
- 关注价格行为

分析股票时，请:
1. 评估趋势方向和强度
2. 分析技术指标
3. 评估风险管理
4. 分析动量
5. 考虑宏观背景

请用交易员视角、强调止损、控制风险的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "趋势分析",
        "技术指标评估",
        "风险管理",
        "动量评估",
        "宏观背景"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_jones_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为保罗·都铎·琼斯，请对{name}（{code}）进行趋势交易分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- ROE: {stock_data.get('roe', 'N/A')}%
- 收入增长率: {stock_data.get('volume', 'N/A')}%
- 波动率: {stock_data.get('turnover_rate', 'N/A')}
- 52周高点: {stock_data.get('high_52w', 'N/A')}
- 52周低点: {stock_data.get('low_52w', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从琼斯的角度进行五维度趋势分析：

维度1：趋势分析
- 短期趋势（20日均线方向）
- 中期趋势（60日均线方向）
- 长期趋势（120日均线方向）
- 趋势强度（角度和一致性）
- 趋势持续性评估

维度2：技术指标评估
- RSI（超买/超卖）
- MACD（信号和交叉）
- 布林带位置
- 成交量趋势
- 支撑阻力位

维度3：风险管理
- 止损位置建议
- 风险收益比
- 头寸规模建议
- 最大回撤容忍
- 盈亏比评估

维度4：动量评估
- 价格动量强度
- 成交量动量
- 相对强弱
- 动量背离信号
- 动量持续性

维度5：宏观背景
- 市场整体趋势
- 行业趋势
- 利率环境影响
- 政策影响
- 风险偏好

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "trend_analysis": {{
            "short_term": "短期趋势",
            "medium_term": "中期趋势",
            "long_term": "长期趋势",
            "trend_strength": "趋势强度",
            "trend_sustainability": "趋势持续性",
            "score": "评分1-10"
        }},
        "technical_indicators": {{
            "rsi": "RSI值",
            "macd": "MACD信号",
            "bollinger_position": "布林带位置",
            "volume_trend": "成交量趋势",
            "support_resistance": "支撑阻力"
        }},
        "risk_management": {{
            "stop_loss": "止损位置",
            "risk_reward_ratio": "风险收益比",
            "position_size": "头寸规模（%）",
            "max_drawdown": "最大回撤容忍",
            "win_loss_ratio": "盈亏比"
        }},
        "momentum": {{
            "price_momentum": "价格动量",
            "volume_momentum": "成交量动量",
            "relative_strength": "相对强弱",
            "momentum_divergence": "动量背离",
            "score": "评分1-10"
        }},
        "macro_context": {{
            "market_trend": "市场趋势",
            "sector_trend": "行业趋势",
            "rate_impact": "利率影响",
            "policy_impact": "政策影响",
            "risk_appetite": "风险偏好"
        }}
    }},
    "key_metrics": {{
        "rsi": "RSI",
        "macd": "MACD",
        "trend": "趋势方向",
        "momentum": "动量强度"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_jones_response(self, content: str) -> dict:
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
                "trend_analysis": five_dims.get("trend_analysis", {}),
                "technical_indicators": five_dims.get("technical_indicators", {}),
                "risk_management": five_dims.get("risk_management", {}),
                "momentum": five_dims.get("momentum", {}),
                "macro_context": five_dims.get("macro_context", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 8),
                "investment_horizon": data.get("investment_horizon", "3-12个月"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "trend_analysis": {},
                "technical_indicators": {},
                "risk_management": {},
                "momentum": {},
                "macro_context": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 8,
                "investment_horizon": "3-12个月",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_jones_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_jones_response(response["content"])
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
                "trend_analysis": {},
                "technical_indicators": {},
                "risk_management": {},
                "momentum": {},
                "macro_context": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 8,
                "investment_horizon": "3-12个月",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_paul_tudor_jones_leader() -> PaulTudorJonesLeader:
    return PaulTudorJonesLeader()


async def run_paul_tudor_jones_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = PaulTudorJonesLeader()
    return await leader.analyze(state, llm_service)
