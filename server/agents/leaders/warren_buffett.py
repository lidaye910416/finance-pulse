"""
Warren Buffett Leader Implementation

沃伦·巴菲特投资大师的具体实现
- 7维度分析框架
- 安全边际计算
- 内在价值评估

This module provides the WarrenBuffettLeader class that implements
Buffett's value investing philosophy.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class WarrenBuffettLeader:
    """沃伦·巴菲特 Leader
    
    实现巴菲特的价值投资理念：
    - 寻找伟大的公司，以合理的价格买入
    - 评估护城河（竞争优势）
    - 计算内在价值和安全边际
    - 7维度分析框架
    """
    
    # 类级别的配置
    LEADER_ID = "warren_buffett"
    LEADER_NAME = "沃伦·巴菲特"
    LEADER_NAME_EN = "Warren Buffett"
    LEADER_STYLE = "价值投资大师"
    LEADER_DESCRIPTION = "奥马哈先知，价值投资教父"
    
    SYSTEM_PROMPT = """你是一位价值投资大师，风格像沃伦·巴菲特。

你的投资理念:
- 只投资你理解的业务
- 寻找具有持久竞争优势（护城河）的公司
- 重视公司的内在价值，而非市场价格
- 长期持有，忽略短期波动
- 只买你觉得足够便宜的好公司

分析股票时，请:
1. 评估公司的商业模式和护城河
2. 计算合理的内在价值
3. 判断当前价格是否有安全边际
4. 给出明确的投资建议和持仓建议

请用专业、沉稳的语气进行分析。"""
    
    # 7维度分析框架
    SEVEN_DIMENSIONS = [
        "业务质量（护城河分析）",
        "盈利能力（ROE、ROA、毛利率）",
        "成长性（营收/利润增速）",
        "财务健康（负债率、现金流）",
        "内在价值估算",
        "安全边际评估",
        "管理层质量"
    ]
    
    def __init__(self):
        """初始化 Warren Buffett Leader"""
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_seven_dimension_prompt(self, state: 'AgentState') -> str:
        """构建7维度分析的 prompt
        
        Args:
            state: 当前工作流状态
            
        Returns:
            格式化后的 prompt 字符串
        """
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        # 获取分析师信号
        analyst_signals = state.get("analyst_signals", [])
        
        # 获取多空辩论结果
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        # 获取风险辩论结果
        risk_recommendation = state.get("risk_recommendation", {})
        
        return f"""作为沃伦·巴菲特，请对{name}（{code}）进行价值投资分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 总市值: {stock_data.get('market_cap', 'N/A')}
- 股息率: {stock_data.get('dividend_yield', 'N/A')}%

分析师信号汇总：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:5]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:100] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:100] if bearish_signal else '暂无'}

风险建议：{risk_recommendation.get('consensus_risk_level', 'medium')}风险

请从巴菲特的价值投资角度提供7维度分析：

维度1：业务质量（护城河分析）
- 公司拥有什么护城河？
- 竞争优势的持久性如何？
- 是否容易被竞争对手复制？

维度2：盈利能力
- ROE（净资产收益率）: {stock_data.get('roe', 'N/A')}%
- ROA（资产收益率）: {stock_data.get('roa', 'N/A')}%
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 净利率: {stock_data.get('net_margin', 'N/A')}%

维度3：成长性
- 营收增速: {stock_data.get('revenue_growth', 'N/A')}%
- 利润增速: {stock_data.get('profit_growth', 'N/A')}%
- 行业增速: {stock_data.get('industry_growth', 'N/A')}%
- 市场份额变化趋势

维度4：财务健康
- 资产负债率: {stock_data.get('debt_ratio', 'N/A')}%
- 现金流状况: {stock_data.get('cash_flow', 'N/A')}
- 财务灵活性

维度5：内在价值估算
- 使用DCF或DDM模型估算
- 考虑永续增长率
- 合理的折现率假设

维度6：安全边际
- 当前价格vs内在价值
- 安全边际比例 = (内在价值 - 当前价格) / 内在价值
- 是否提供足够的下跌保护

维度7：管理层质量
- 管理层是否诚实、有能力？
- 资本配置决策是否明智？
- 是否为股东利益服务？

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "seven_dimensions": {{
        "business_quality": {{
            "moat_type": "护城河类型",
            "moat_duration": "护城河持久性（年）",
            "score": "评分1-10"
        }},
        "profitability": {{
            "roe": "ROE值",
            "roa": "ROA值", 
            "gross_margin": "毛利率",
            "net_margin": "净利率",
            "score": "评分1-10"
        }},
        "growth": {{
            "revenue_growth": "营收增速",
            "profit_growth": "利润增速",
            "industry_position": "行业地位",
            "score": "评分1-10"
        }},
        "financial_health": {{
            "debt_ratio": "资产负债率",
            "cash_flow_status": "现金流状态",
            "flexibility": "财务灵活性",
            "score": "评分1-10"
        }},
        "intrinsic_value": {{
            "dcf_value": "DCF估值（元）",
            "ddm_value": "DDM估值（元）",
            "avg_value": "平均内在价值（元）",
            "confidence_in_estimate": "估算置信度"
        }},
        "margin_of_safety": {{
            "current_price": "当前价格（元）",
            "intrinsic_value": "内在价值（元）",
            "safety_margin_pct": "安全边际（%）",
            "adequate": "是否足够（true/false）"
        }},
        "management": {{
            "integrity": "诚信度（1-10）",
            "capability": "能力（1-10）",
            "capital_allocation": "资本配置（1-10）",
            "score": "评分1-10"
        }}
    }},
    "overall_score": "综合评分1-10",
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限（年）"
}}"""
    
    def _parse_seven_dimension_response(self, content: str) -> dict:
        """解析7维度分析响应
        
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
            
            # 提取7维度数据
            seven_dims = data.get("seven_dimensions", {})
            intrinsic_value = seven_dims.get("intrinsic_value", {})
            margin_of_safety = seven_dims.get("margin_of_safety", {})
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "seven_dimensions": seven_dims,
                "intrinsic_value": {
                    "dcf_value": intrinsic_value.get("dcf_value", "N/A"),
                    "ddm_value": intrinsic_value.get("ddm_value", "N/A"),
                    "avg_value": intrinsic_value.get("avg_value", "N/A"),
                    "confidence": intrinsic_value.get("confidence_in_estimate", "medium"),
                },
                "margin_of_safety": {
                    "current_price": margin_of_safety.get("current_price", "N/A"),
                    "intrinsic_value": margin_of_safety.get("intrinsic_value", "N/A"),
                    "safety_margin_pct": margin_of_safety.get("safety_margin_pct", 0),
                    "adequate": margin_of_safety.get("adequate", False),
                },
                "overall_score": data.get("overall_score", "N/A"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 20),
                "investment_horizon": data.get("investment_horizon", "3-5年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "seven_dimensions": {},
                "intrinsic_value": {
                    "dcf_value": "N/A",
                    "ddm_value": "N/A",
                    "avg_value": "N/A",
                    "confidence": "low",
                },
                "margin_of_safety": {
                    "current_price": "N/A",
                    "intrinsic_value": "N/A",
                    "safety_margin_pct": 0,
                    "adequate": False,
                },
                "overall_score": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 20,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        """运行 Warren Buffett 分析
        
        Args:
            state: 当前工作流状态
            llm_service: LLM 服务实例
            
        Returns:
            Warren Buffett 7维度分析结果
        """
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        
        prompt = self._build_seven_dimension_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_seven_dimension_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"内在价值={result['intrinsic_value']['avg_value']}, "
                  f"安全边际={result['margin_of_safety']['safety_margin_pct']}%")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "seven_dimensions": {},
                "intrinsic_value": {
                    "dcf_value": "N/A",
                    "ddm_value": "N/A",
                    "avg_value": "N/A",
                    "confidence": "error",
                },
                "margin_of_safety": {
                    "current_price": "N/A",
                    "intrinsic_value": "N/A",
                    "safety_margin_pct": 0,
                    "adequate": False,
                },
                "overall_score": "N/A",
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 20,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_seven_dimensions(self) -> list[str]:
        """获取7维度框架列表
        
        Returns:
            7个维度的描述列表
        """
        return self.SEVEN_DIMENSIONS


# 便捷函数

def create_warren_buffett_leader() -> WarrenBuffettLeader:
    """创建 Warren Buffett Leader 实例"""
    return WarrenBuffettLeader()


async def run_warren_buffett_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    """运行 Warren Buffett 分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例
        
    Returns:
        Warren Buffett 7维度分析结果
    """
    leader = WarrenBuffettLeader()
    return await leader.analyze(state, llm_service)
