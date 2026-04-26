"""
Benjamin Graham Leader Implementation

本杰明·格雷厄姆投资大师的具体实现
- 安全边际计算
- 低估筛选逻辑
- 财务健康评估

This module provides the BenGrahamLeader class that implements
Graham's value investing philosophy with focus on margin of safety.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class BenGrahamLeader:
    """本杰明·格雷厄姆 Leader
    
    实现格雷厄姆的价值投资理念：
    - 强调"安全边际"是投资的核心
    - 寻找低估值、高防御性的股票
    - 主张采用"雪茄烟蒂"策略
    - 分散投资，降低风险
    - 接受市场短期无效，追求长期价值
    
    分析维度：
    - 清算价值评估
    - 内在价值估算
    - 安全边际计算
    - 财务健康状况
    - 风险收益比
    """
    
    # 类级别的配置
    LEADER_ID = "ben_graham"
    LEADER_NAME = "本杰明·格雷厄姆"
    LEADER_NAME_EN = "Benjamin Graham"
    LEADER_STYLE = "安全边际专家"
    LEADER_DESCRIPTION = "价值投资之父，\"安全边际\"理念的创始人"
    
    SYSTEM_PROMPT = """你是一位安全边际专家，风格像本杰明·格雷厄姆。

你的投资理念:
- 强调"安全边际"是投资的核心
- 寻找低估值、高防御性的股票
- 主张采用"雪茄烟蒂"策略
- 分散投资，降低风险
- 接受市场短期无效，追求长期价值

分析股票时，请:
1. 计算清算价值和内在价值
2. 评估安全边际
3. 检查财务健康状况
4. 判断是否被低估

请用谨慎、理性的语气进行分析。"""
    
    # 分析维度
    FIVE_DIMENSIONS = [
        "清算价值评估",
        "内在价值估算",
        "安全边际计算",
        "财务健康状况",
        "风险收益比"
    ]
    
    def __init__(self):
        """初始化 Ben Graham Leader"""
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_graham_analysis_prompt(self, state: 'AgentState') -> str:
        """构建格雷厄姆风格分析的 prompt
        
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
        
        return f"""作为本杰明·格雷厄姆，请对{name}（{code}）进行安全边际分析：

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
- 速动比率: {stock_data.get('quick_ratio', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从格雷厄姆的安全边际角度进行五维度分析：

维度1：清算价值评估
- 流动资产 vs 总负债
- NCAV（净流动资产）= 流动资产 - 全部负债
- 如果 NCAV > 市值，则是典型的格雷厄姆买入信号
- 计算每股清算价值

维度2：内在价值估算
- 使用格雷厄姆公式：sqrt(22.5 × EPS × BVPS)
- 格雷厄姆Number = sqrt(22.5 × 每股收益 × 每股净资产)
- 考虑长期债券利率影响

维度3：安全边际计算
- 当前价格 vs 格雷厄姆Number
- 安全边际 = (格雷厄姆Number - 当前价格) / 格雷厄姆Number
- 经典格雷厄姆：安全边际应 > 33%

维度4：财务健康状况
- 当前比率（> 2.0 为佳）
- 债务权益比（< 0.5 为佳）
- 盈利稳定性（多年正收益）
- 分红历史

维度5：风险收益比
- 潜在下跌空间 vs 上涨空间
- 预期收益率 vs 无风险收益率
- 不对称收益机会

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "liquidation_value": {{
            "ncav": "净流动资产（亿元）",
            "ncav_per_share": "每股清算价值（元）",
            "ncav_vs_market_cap": "NCAV与市值比较",
            "score": "评分1-10"
        }},
        "intrinsic_value": {{
            "graham_number": "格雷厄姆Number（元）",
            "formula_used": "计算公式说明",
            "confidence_in_estimate": "估算置信度"
        }},
        "margin_of_safety": {{
            "current_price": "当前价格（元）",
            "graham_number": "格雷厄姆Number（元）",
            "safety_margin_pct": "安全边际（%）",
            "grade": "A/B/C/D 等级"
        }},
        "financial_health": {{
            "current_ratio": "流动比率",
            "debt_ratio": "资产负债率（%）",
            "earnings_stability": "盈利稳定性评分",
            "dividend_record": "分红记录",
            "score": "评分1-10"
        }},
        "risk_reward": {{
            "downside_risk": "下行风险（%）",
            "upside_potential": "上行潜力（%）",
            "asymmetric_ratio": "不对称比率",
            "recommendation": "风险收益评价"
        }}
    }},
    "key_metrics": {{
        "pe": "市盈率",
        "pb": "市净率",
        "dividend_yield": "股息率（%）"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_graham_response(self, content: str) -> dict:
        """解析格雷厄姆分析响应
        
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
            
            # 提取五维度数据
            five_dims = data.get("five_dimensions", {})
            margin_of_safety = five_dims.get("margin_of_safety", {})
            liquidation_value = five_dims.get("liquidation_value", {})
            intrinsic_value = five_dims.get("intrinsic_value", {})
            financial_health = five_dims.get("financial_health", {})
            risk_reward = five_dims.get("risk_reward", {})
            
            # 解析安全边际百分比
            safety_pct = margin_of_safety.get("safety_margin_pct", 0)
            if isinstance(safety_pct, str) and '%' in safety_pct:
                safety_pct = float(safety_pct.replace('%', ''))
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "five_dimensions": five_dims,
                "liquidation_value": {
                    "ncav": liquidation_value.get("ncav", "N/A"),
                    "ncav_per_share": liquidation_value.get("ncav_per_share", "N/A"),
                    "ncav_vs_market_cap": liquidation_value.get("ncav_vs_market_cap", "N/A"),
                    "score": liquidation_value.get("score", "N/A"),
                },
                "intrinsic_value": {
                    "graham_number": intrinsic_value.get("graham_number", "N/A"),
                    "formula_used": intrinsic_value.get("formula_used", "sqrt(22.5 × EPS × BVPS)"),
                    "confidence": intrinsic_value.get("confidence_in_estimate", "medium"),
                },
                "margin_of_safety": {
                    "current_price": margin_of_safety.get("current_price", "N/A"),
                    "graham_number": margin_of_safety.get("graham_number", "N/A"),
                    "safety_margin_pct": safety_pct,
                    "grade": margin_of_safety.get("grade", "C"),
                },
                "financial_health": {
                    "current_ratio": financial_health.get("current_ratio", "N/A"),
                    "debt_ratio": financial_health.get("debt_ratio", "N/A"),
                    "earnings_stability": financial_health.get("earnings_stability", "N/A"),
                    "dividend_record": financial_health.get("dividend_record", "N/A"),
                    "score": financial_health.get("score", "N/A"),
                },
                "risk_reward": {
                    "downside_risk": risk_reward.get("downside_risk", "N/A"),
                    "upside_potential": risk_reward.get("upside_potential", "N/A"),
                    "asymmetric_ratio": risk_reward.get("asymmetric_ratio", "N/A"),
                    "recommendation": risk_reward.get("recommendation", "N/A"),
                },
                "key_metrics": data.get("key_metrics", {}),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 15),
                "investment_horizon": data.get("investment_horizon", "2-3年"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "liquidation_value": {
                    "ncav": "N/A",
                    "ncav_per_share": "N/A",
                    "ncav_vs_market_cap": "N/A",
                    "score": "N/A",
                },
                "intrinsic_value": {
                    "graham_number": "N/A",
                    "formula_used": "sqrt(22.5 × EPS × BVPS)",
                    "confidence": "error",
                },
                "margin_of_safety": {
                    "current_price": "N/A",
                    "graham_number": "N/A",
                    "safety_margin_pct": 0,
                    "grade": "N/A",
                },
                "financial_health": {
                    "current_ratio": "N/A",
                    "debt_ratio": "N/A",
                    "earnings_stability": "N/A",
                    "dividend_record": "N/A",
                    "score": "N/A",
                },
                "risk_reward": {
                    "downside_risk": "N/A",
                    "upside_potential": "N/A",
                    "asymmetric_ratio": "N/A",
                    "recommendation": "N/A",
                },
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
                "investment_horizon": "2-3年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        """运行 Ben Graham 分析
        
        Args:
            state: 当前工作流状态
            llm_service: LLM 服务实例
            
        Returns:
            Ben Graham 五维度分析结果
        """
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        
        prompt = self._build_graham_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_graham_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"格雷厄姆Number={result['intrinsic_value']['graham_number']}, "
                  f"安全边际={result['margin_of_safety']['safety_margin_pct']}%")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "five_dimensions": {},
                "liquidation_value": {
                    "ncav": "N/A",
                    "ncav_per_share": "N/A",
                    "ncav_vs_market_cap": "N/A",
                    "score": "N/A",
                },
                "intrinsic_value": {
                    "graham_number": "N/A",
                    "formula_used": "sqrt(22.5 × EPS × BVPS)",
                    "confidence": "error",
                },
                "margin_of_safety": {
                    "current_price": "N/A",
                    "graham_number": "N/A",
                    "safety_margin_pct": 0,
                    "grade": "N/A",
                },
                "financial_health": {
                    "current_ratio": "N/A",
                    "debt_ratio": "N/A",
                    "earnings_stability": "N/A",
                    "dividend_record": "N/A",
                    "score": "N/A",
                },
                "risk_reward": {
                    "downside_risk": "N/A",
                    "upside_potential": "N/A",
                    "asymmetric_ratio": "N/A",
                    "recommendation": "N/A",
                },
                "key_metrics": {},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 15,
                "investment_horizon": "2-3年",
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

def create_ben_graham_leader() -> BenGrahamLeader:
    """创建 Ben Graham Leader 实例"""
    return BenGrahamLeader()


async def run_ben_graham_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    """运行 Ben Graham 分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例
        
    Returns:
        Ben Graham 五维度分析结果
    """
    leader = BenGrahamLeader()
    return await leader.analyze(state, llm_service)
