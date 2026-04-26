"""
Phil Fisher Leader Implementation

菲利普·费雪投资大师的具体实现
- 成长股投资
- R&D和管理质量
- 长线复利

This module provides the PhilFisherLeader class.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class PhilFisherLeader:
    """菲利普·费雪 Leader
    
    实现费雪的投资理念：
    - 寻找长期高于平均增长的股票
    - 强调管理质量和研发
    - 寻找强利润率、稳定增长、可控杠杆
    - 愿意为质量支付价格
    - 关注长期复利
    - 使用"闲聊"(scuttlebutt)研究方法
    
    分析维度：
    - 成长与质量分析
    - 利润率稳定性
    - 管理效率与研发
    - 估值分析
    - 长期复利潜力
    """
    
    LEADER_ID = "phil_fisher"
    LEADER_NAME = "菲利普·费雪"
    LEADER_NAME_EN = "Phil Fisher"
    LEADER_STYLE = "成长股投资大师"
    LEADER_DESCRIPTION = "《怎样选择成长股》作者，成长股投资先驱"
    
    SYSTEM_PROMPT = """你是一位成长股投资者，风格像菲利普·费雪。

你的投资理念:
- 寻找长期高于平均增长的股票
- 强调管理质量和研发能力
- 寻找强利润率、稳定增长、可控杠杆
- 愿意为质量支付合理价格
- 关注长期复利效应
- 使用"闲聊"(scuttlebutt)方法研究公司
- 一般持有5年以上

分析股票时，请:
1. 评估长期增长潜力
2. 检查利润率趋势
3. 评估管理和研发
4. 考虑估值与成长的匹配
5. 分析长期复利潜力

请用耐心、长期导向、强调质量成长的语气进行分析。"""
    
    FIVE_DIMENSIONS = [
        "成长与质量分析",
        "利润率与稳定性",
        "管理与研发评估",
        "估值与成长匹配",
        "长期复利潜力"
    ]
    
    def __init__(self):
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_fisher_analysis_prompt(self, state: 'AgentState') -> str:
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为菲利普·费雪，请对{name}（{code}）进行成长股分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- 收入增长率: {stock_data.get('revenue_growth', 'N/A')}%
- EPS增长率: {stock_data.get('eps_growth', 'N/A')}%
- ROE: {stock_data.get('roe', 'N/A')}%
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 营业利润率: {stock_data.get('operating_margin', 'N/A')}%
- 净利率: {stock_data.get('net_margin', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}
- 研发费用: {stock_data.get('rd_expense', 'N/A')}
- EBIT: {stock_data.get('ebit', 'N/A')}
- EBITDA: {stock_data.get('ebitda', 'N/A')}
- 债务股权比: {stock_data.get('debt_to_equity', 'N/A')}
- 现金及等价物: {stock_data.get('cash', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从费雪的角度进行五维度成长股分析：

维度1：成长与质量分析
- 收入5年CAGR（>10%为优）
- EPS增长一致性和稳定性
- 市场份额趋势
- 行业增长前景
- 竞争优势的持久性

维度2：利润率与稳定性
- 毛利率趋势（稳定/改善为佳）
- 营业利润率趋势
- 净利率稳定性
- 利润率vs行业
- 规模效应潜力

维度3：管理与研发评估
- 研发费用占收入比
- 研发效率和创新成果
- 管理团队质量
- 资本配置历史
- 激励机制

维度4：估值与成长匹配
- PEG比率（<1为佳）
- P/E vs 增长率
- EV/EBITDA vs 增长
- 成长溢价合理性
- 长期估值安全边际

维度5：长期复利潜力
- ROE长期水平
- 再投资回报率
- 分红和回购潜力
- 5-10年潜在回报
- 复利效果评估

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "growth_quality": {{
            "revenue_cagr_5y": "5年收入CAGR（%）",
            "eps_consistency": "EPS一致性",
            "market_share_trend": "市场份额趋势",
            "industry_outlook": "行业前景",
            "competitive_moat": "护城河",
            "score": "评分1-10"
        }},
        "margins_stability": {{
            "gross_margin_trend": "毛利率趋势",
            "operating_margin_trend": "营业利润率趋势",
            "net_margin_stability": "净利率稳定性",
            "margins_vs_industry": "vs 行业",
            "scale_benefits": "规模效应",
            "score": "评分1-10"
        }},
        "management_rd": {{
            "rd_intensity": "研发强度（%）",
            "innovation_output": "创新成果",
            "management_quality": "管理质量",
            "capital_allocation": "资本配置",
            "score": "评分1-10"
        }},
        "valuation_vs_growth": {{
            "peg_ratio": "PEG比率",
            "pe_vs_growth": "P/E vs 增长率",
            "growth_premium_justified": "成长溢价合理性",
            "long_term_mos": "长期安全边际",
            "score": "评分1-10"
        }},
        "compounding_potential": {{
            "long_term_roe": "长期ROE（%）",
            "reinvestment_rate": "再投资率",
            "dividend_repurchase": "分红回购潜力",
            "ten_year_potential": "10年潜在回报（%）",
            "compound_effect": "复利效果"
        }}
    }},
    "key_metrics": {{
        "pe": "市盈率",
        "peg": "PEG比率",
        "revenue_growth": "收入增长率（%）",
        "roe": "ROE（%）"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_fisher_response(self, content: str) -> dict:
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
                "growth_quality": five_dims.get("growth_quality", {}),
                "margins_stability": five_dims.get("margins_stability", {}),
                "management_rd": five_dims.get("management_rd", {}),
                "valuation_vs_growth": five_dims.get("valuation_vs_growth", {}),
                "compounding_potential": five_dims.get("compounding_potential", {}),
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 12),
                "investment_horizon": data.get("investment_horizon", "5年以上"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "growth_quality": {},
                "margins_stability": {},
                "management_rd": {},
                "valuation_vs_growth": {},
                "compounding_potential": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 12,
                "investment_horizon": "5年以上",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        prompt = self._build_fisher_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_fisher_response(response["content"])
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
                "growth_quality": {},
                "margins_stability": {},
                "management_rd": {},
                "valuation_vs_growth": {},
                "compounding_potential": {},
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 12,
                "investment_horizon": "5年以上",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_five_dimensions(self) -> list[str]:
        return self.FIVE_DIMENSIONS


def create_phil_fisher_leader() -> PhilFisherLeader:
    return PhilFisherLeader()


async def run_phil_fisher_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    leader = PhilFisherLeader()
    return await leader.analyze(state, llm_service)
