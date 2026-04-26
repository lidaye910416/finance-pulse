"""
Jim Simons Leader Implementation

吉姆·西蒙斯投资大师的具体实现
- 量化投资先驱
- 统计套利
- 算法驱动决策

This module provides the JimSimonsLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class JimSimonsLeader:
    """吉姆·西蒙斯 Leader
    
    实现西蒙斯的量化投资理念：
    - 量化投资先驱
    - 统计套利策略
    - 算法驱动决策
    - 数据驱动的分析方法
    - 寻找市场无效性
    
    分析维度：
    - 数据质量评估
    - 技术分析
    - 均值回归分析
    - 动量分析
    - 统计异常检测
    """
    
    LEADER_ID = "jim_simons"
    LEADER_NAME = "吉姆·西蒙斯"
    LEADER_NAME_EN = "Jim Simons"
    LEADER_STYLE = "量化投资大师"
    LEADER_DESCRIPTION = "大奖章基金创始人，量化投资传奇"
    
    SYSTEM_PROMPT = """你是一位量化投资大师，风格像吉姆·西蒙斯。

你的投资理念:
- 量化投资先驱，使用数学模型和算法
- 统计套利策略，寻找市场无效性
- 算法驱动决策，减少人为情绪
- 数据驱动的分析方法
- 短期/中期持有，快速迭代
- 追求稳定的超额收益

分析股票时，请:
1. 评估数据质量和信号
2. 分析技术指标和价格模式
3. 寻找均值回归机会
4. 检测动量信号
5. 评估统计异常

请用数据驱动、模型化、强调概率的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "数据质量评估",
        "技术分析",
        "均值回归分析",
        "动量信号",
        "统计异常检测"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_simons_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        
        return f"""作为吉姆·西蒙斯，请对{name}（{code}）进行量化分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- 收入增长率: {stock_data.get('revenue_growth', 'N/A')}%
- ROE: {stock_data.get('roe', 'N/A')}%
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 营业利润率: {stock_data.get('operating_margin', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

请从西蒙斯的量化角度进行五维度分析：

维度1：数据质量评估
- 历史数据的完整性和可靠性
- 财务数据的质量
- 数据的时间跨度
- 异常值的处理

维度2：技术分析
- 价格趋势和波动率
- 技术指标信号（MA, MACD, RSI等）
- 支撑/阻力位
- 价格模式识别

维度3：均值回归分析
- 当前估值的历史分位数
- P/E, P/B的均值回归概率
- 历史波动性vs当前
- 回归时间估计

维度4：动量信号
- 短期/中期/长期动量
- 动量加速/减速
- 相对强弱指数
- 板块动量

维度5：统计异常检测
- 偏离正常范围的价格
- 异常成交量
- 基本面vs技术面背离
- 可利用的异常机会

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "data_quality": {{
            "historical_coverage": "历史覆盖",
            "data_reliability": "数据可靠性",
            "data_score": "评分1-10"
        }},
        "technical": {{
            "trend": "趋势方向",
            "volatility": "波动率",
            "signals": ["信号列表"],
            "score": "评分1-10"
        }},
        "mean_reversion": {{
            "historical_percentile": "历史分位数",
            "reversion_probability": "回归概率（%）",
            "reversion_timeframe": "回归时间",
            "score": "评分1-10"
        }},
        "momentum": {{
            "short_term": "短期动量",
            "medium_term": "中期动量",
            "long_term": "长期动量",
            "score": "评分1-10"
        }},
        "anomaly_detection": {{
            "price_anomaly": "价格异常",
            "volume_anomaly": "成交量异常",
            "opportunity": "异常机会描述",
            "score": "评分1-10"
        }}
    }},
    "quantitative_signals": {{
        "signal_strength": "信号强度",
        "expected_return": "预期收益（%）",
        "holding_period": "持有期"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_simons_response(self, content: str) -> dict:
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
                "data_quality": five_dims.get("data_quality", {}),
                "technical": five_dims.get("technical", {}),
                "mean_reversion": five_dims.get("mean_reversion", {}),
                "momentum": five_dims.get("momentum", {}),
                "anomaly_detection": five_dims.get("anomaly_detection", {}),
                "quantitative_signals": data.get("quantitative_signals", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 10),
                "investment_horizon": data.get("investment_horizon", "1-3个月"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "data_quality": {},
                "technical": {},
                "mean_reversion": {},
                "momentum": {},
                "anomaly_detection": {},
                "quantitative_signals": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 10,
                "investment_horizon": "1-3个月",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_simons_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_simons_response(response["content"])
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
                "data_quality": {},
                "technical": {},
                "mean_reversion": {},
                "momentum": {},
                "anomaly_detection": {},
                "quantitative_signals": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 10,
                "investment_horizon": "1-3个月",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_jim_simons_leader() -> JimSimonsLeader:
    return JimSimonsLeader()


async def run_jim_simons_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = JimSimonsLeader()
    return await leader.analyze(state, llm_service)
