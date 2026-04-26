"""
Bill Ackman Leader Implementation

比尔·阿克曼投资大师的具体实现
- 品牌护城河分析
- 积极主义潜力评估
- DCF估值与安全边际

This module provides the BillAckmanLeader class that implements
Ackman's activist investing philosophy with focus on brand quality.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class BillAckmanLeader:
    """比尔·阿克曼 Leader
    
    实现比尔·阿克曼的积极主义投资理念：
    - 寻找具有持久竞争优势的品牌
    - 强调一致的现金流和增长潜力
    - 主张强财务纪律
    - 关注内在价值与安全边际
    - 在有利条件下敢于激进
    
    分析维度：
    - 业务质量分析
    - 财务纪律评估
    - 积极主义潜力
    - 估值分析
    - 催化剂识别
    """
    
    # 类级别的配置
    LEADER_ID = "bill_ackman"
    LEADER_NAME = "比尔·阿克曼"
    LEADER_NAME_EN = "Bill Ackman"
    LEADER_STYLE = "积极主义投资者"
    LEADER_DESCRIPTION = "Pershing Square创始人，知名积极主义投资者"
    
    SYSTEM_PROMPT = """你是一位积极主义投资者，风格像比尔·阿克曼。

你的投资理念:
- 寻找具有持久竞争优势的品牌和公司
- 强调一致的自由现金流和长期增长潜力
- 主张强财务纪律（合理杠杆、高效资本配置）
- 估值很重要：以内在价值为目标，强调安全边际
- 在管理层或运营改善能释放重大价值时考虑积极主义
- 集中于少数高确信度的投资

分析股票时，请:
1. 评估业务质量和护城河
2. 检查财务纪律和资本配置
3. 识别积极主义机会
4. 计算内在价值和催化剂

请用自信、分析性强、有时带有对抗性的语气进行分析。"""
    
    # 分析维度
    FIVE_DIMENSIONS = [
        "业务质量与护城河",
        "财务纪律与资本配置",
        "积极主义潜力",
        "估值与安全边际",
        "催化剂识别"
    ]
    
    def __init__(self):
        """初始化 Bill Ackman Leader"""
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_ackman_analysis_prompt(self, state: 'AgentState') -> str:
        """构建阿克曼风格分析的 prompt"""
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为比尔·阿克曼，请对{name}（{code}）进行积极主义投资分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 股息率: {stock_data.get('dividend_yield', 'N/A')}%
- 总市值: {stock_data.get('market_cap', 'N/A')}

财务指标：
- ROE: {stock_data.get('roe', 'N/A')}%
- 资产负债率: {stock_data.get('debt_ratio', 'N/A')}%
- 流动比率: {stock_data.get('current_ratio', 'N/A')}
- 毛利率: {stock_data.get('gross_margin', 'N/A')}%
- 营业利润率: {stock_data.get('operating_margin', 'N/A')}%
- 自由现金流: {stock_data.get('free_cash_flow', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从阿克曼的积极主义投资角度进行五维度分析：

维度1：业务质量与护城河
- 品牌实力和市场地位
- 竞争优势的持久性
- 收入和FCF增长趋势
- ROE是否超过15%（竞争优势标志）

维度2：财务纪律与资本配置
- 债务股权比（<1.0为佳）
- 分红和回购历史
- 流通股变化（减少=回购=好）
- 资本配置效率

维度3：积极主义潜力
- 收入增长但利润率低（改善空间）
- 运营改进潜力
- 资产剥离或重组可能性
- 管理层变更催化剂

维度4：估值与安全边际
- DCF内在价值计算
- 当前市值vs内在价值
- 安全边际百分比
- 风险调整后回报

维度5：催化剂识别
- 近期可能的催化剂
- 积极行动的时间窗口
- 潜在价值释放路径
- 退出策略和目标价

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "business_quality": {{
            "brand_strength": "品牌实力评估",
            "competitive_advantage": "竞争优势描述",
            "revenue_growth": "收入增长率（%）",
            "fcf_generation": "自由现金流生成能力",
            "score": "评分1-10"
        }},
        "financial_discipline": {{
            "debt_to_equity": "债务股权比",
            "capital_allocation": "资本配置评价",
            "dividend_history": "分红历史",
            "buyback_activity": "回购活动",
            "score": "评分1-10"
        }},
        "activism_potential": {{
            "margin_improvement": "利润率改善潜力（%）",
            "operational_leverage": "运营杠杆",
            "management_change": "管理层变化催化剂",
            "restructuring_possible": "重组可能性",
            "score": "评分1-10"
        }},
        "valuation": {{
            "dcf_intrinsic_value": "DCF内在价值",
            "current_market_cap": "当前市值",
            "margin_of_safety_pct": "安全边际（%）",
            "upside_potential": "上涨潜力（%）",
            "score": "评分1-10"
        }},
        "catalysts": {{
            "near_term_catalysts": ["催化剂1", "催化剂2"],
            "timeline": "时间线",
            "target_price": "目标价",
            "exit_strategy": "退出策略"
        }}
    }},
    "key_metrics": {{
        "pe": "市盈率",
        "pb": "市净率",
        "roe": "ROE（%）",
        "fcf_yield": "自由现金流收益率（%）"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_ackman_response(self, content: str) -> dict:
        """解析阿克曼分析响应"""
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
                "business_quality": five_dims.get("business_quality", {}),
                "financial_discipline": five_dims.get("financial_discipline", {}),
                "activism_potential": five_dims.get("activism_potential", {}),
                "valuation": five_dims.get("valuation", {}),
                "catalysts": five_dims.get("catalysts", {}),
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
                "business_quality": {},
                "financial_discipline": {},
                "activism_potential": {},
                "valuation": {},
                "catalysts": {},
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
        """运行 Bill Ackman 分析"""
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        
        prompt = self._build_ackman_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_ackman_response(response["content"])
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
                "business_quality": {},
                "financial_discipline": {},
                "activism_potential": {},
                "valuation": {},
                "catalysts": {},
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
        """获取五维度框架列表"""
        return self.FIVE_DIMENSIONS


# 便捷函数

def create_bill_ackman_leader() -> BillAckmanLeader:
    """创建 Bill Ackman Leader 实例"""
    return BillAckmanLeader()


async def run_bill_ackman_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    """运行 Bill Ackman 分析的便捷函数"""
    leader = BillAckmanLeader()
    return await leader.analyze(state, llm_service)
