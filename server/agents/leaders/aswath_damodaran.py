"""
Aswath Damodaran Leader Implementation

阿斯瓦特·达摩达兰投资大师的具体实现
- DCF内在价值分析
- 风险调整回报
- 相对估值

This module provides the AswathDamodaranLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class AswathDamodaranLeader:
    """阿斯瓦特·达摩达兰 Leader
    
    实现达摩达兰的投资理念：
    - 使用DCF进行内在价值分析
    - 风险调整后的回报评估
    - 相对估值与行业比较
    - 关注增长与再投资
    - 强调估值的不确定性
    
    分析维度：
    - 增长与再投资分析
    - 风险概况评估
    - DCF内在价值
    - 相对估值分析
    - 安全边际
    """
    
    LEADER_ID = "aswath_damodaran"
    LEADER_NAME = "阿斯瓦特·达摩达兰"
    LEADER_NAME_EN = "Aswath Damodaran"
    LEADER_STYLE = "估值大师"
    LEADER_DESCRIPTION = "纽约大学金融学教授，知名估值专家"
    
    SYSTEM_PROMPT = """你是一位估值专家，风格像阿斯瓦特·达摩达兰。

你的投资理念:
- 使用DCF模型进行精确的内在价值计算
- 评估风险概况和股权成本
- 关注增长质量和再投资效率
- 进行相对估值与行业比较
- 强调估值的不确定性范围
- 使用风险调整后的回报评估

分析股票时，请:
1. 计算增长率和再投资率
2. 评估风险概况和Beta
3. 进行DCF估值
4. 进行相对估值比较
5. 计算安全边际

请用严谨、分析性强、数字驱动的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "增长与再投资分析",
        "风险概况评估",
        "DCF内在价值计算",
        "相对估值分析",
        "安全边际评估"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_damodaran_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为阿斯瓦特·达摩达兰，请对{name}（{code}）进行估值分析：

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
- EBIT: {stock_data.get('ebit', 'N/A')}
- 折旧摊销: {stock_data.get('dna', 'N/A')}
- 资本支出: {stock_data.get('capex', 'N/A')}
- 净债务: {stock_data.get('net_debt', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从达摩达兰的角度进行五维度估值分析：

维度1：增长与再投资分析
- 收入增长率（5年CAGR > 8%为强）
- 自由现金流增长率
- 再投资率 = 资本支出/FCF
- ROIC vs WACC（> WACC为创造价值）
- 增长效率评估

维度2：风险概况评估
- Beta系数估计
- 股权成本（CAMP = 无风险 + Beta * ERP）
- 债务成本和结构
- 加权平均资本成本（WACC）
- 财务杠杆风险

维度3：DCF内在价值计算
- 5年FCF预测
- 终端价值计算（TV Multiple或Gordon Growth）
- 折现率（WACC）
- 每股内在价值
- 估值区间（乐观/基准/悲观）

维度4：相对估值分析
- P/E vs 行业（中位数/均值）
- EV/EBIT vs 行业
- P/S vs 行业
- PEG vs 行业
- 相对估值结论

维度5：安全边际评估
- 当前价格 vs DCF内在价值
- 安全边际 = (内在价值 - 当前价格) / 内在价值
- 安全边际是否 > 20-25%
- 风险调整后回报

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "growth_reinvestment": {{
            "revenue_cagr": "收入CAGR（%）",
            "fcf_growth": "FCF增长率（%）",
            "reinvestment_rate": "再投资率",
            "roic_vs_wacc": "ROIC vs WACC比较",
            "growth_efficiency": "增长效率评价",
            "score": "评分1-10"
        }},
        "risk_profile": {{
            "beta": "Beta系数",
            "cost_of_equity": "股权成本（%）",
            "wacc": "WACC（%）",
            "financial_leverage": "财务杠杆",
            "risk_rating": "风险评级"
        }},
        "dcf_valuation": {{
            "intrinsic_value": "DCF内在价值",
            "valuation_range_low": "估值区间下限",
            "valuation_range_high": "估值区间上限",
            "terminal_value_method": "终端价值方法",
            "key_assumptions": "关键假设"
        }},
        "relative_valuation": {{
            "pe_vs_industry": "P/E vs 行业",
            "ev_ebit_vs_industry": "EV/EBIT vs 行业",
            "relative_cheap_expense": "相对估值结论",
            "score": "评分1-10"
        }},
        "margin_of_safety": {{
            "mos_pct": "安全边际（%）",
            "risk_adjusted_return": "风险调整后回报（%）",
            "mos_adequate": "安全边际是否充分",
            "grade": "A/B/C/D 等级"
        }}
    }},
    "key_metrics": {{
        "pe": "市盈率",
        "dcf_intrinsic_value": "DCF内在价值",
        "margin_of_safety": "安全边际（%）",
        "wacc": "WACC（%）"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_damodaran_response(self, content: str) -> dict:
        try:
            json_match = content.search(r'\{[\s\S]*\}') if hasattr(content, 'search') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            five_dims = data.get("five_dimensions", {})
            mos = five_dims.get("margin_of_safety", {})
            mos_pct = mos.get("mos_pct", 0)
            if isinstance(mos_pct, str) and '%' in mos_pct:
                mos_pct = float(mos_pct.replace('%', ''))
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "five_dimensions": five_dims,
                "growth_reinvestment": five_dims.get("growth_reinvestment", {}),
                "risk_profile": five_dims.get("risk_profile", {}),
                "dcf_valuation": five_dims.get("dcf_valuation", {}),
                "relative_valuation": five_dims.get("relative_valuation", {}),
                "margin_of_safety": {"mos_pct": mos_pct, "grade": mos.get("grade", "C")},
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 12),
                "investment_horizon": data.get("investment_horizon", "2-3年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "growth_reinvestment": {},
                "risk_profile": {},
                "dcf_valuation": {},
                "relative_valuation": {},
                "margin_of_safety": {"mos_pct": 0, "grade": "N/A"},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 12,
                "investment_horizon": "2-3年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_damodaran_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_damodaran_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"DCF内在价值={result.get('dcf_valuation', {}).get('intrinsic_value', 'N/A')}, "
                  f"安全边际={result['margin_of_safety']['mos_pct']}%")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "five_dimensions": {},
                "growth_reinvestment": {},
                "risk_profile": {},
                "dcf_valuation": {},
                "relative_valuation": {},
                "margin_of_safety": {"mos_pct": 0, "grade": "error"},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 12,
                "investment_horizon": "2-3年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_aswath_damodaran_leader() -> AswathDamodaranLeader:
    return AswathDamodaranLeader()


async def run_aswath_damodaran_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = AswathDamodaranLeader()
    return await leader.analyze(state, llm_service)
