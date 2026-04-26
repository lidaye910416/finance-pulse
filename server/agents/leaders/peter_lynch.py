"""
Peter Lynch Leader Implementation

彼得·林奇投资大师的具体实现
- 十倍股识别逻辑
- 成长股筛选标准
- GARP（合理价格成长股）策略

This module provides the PeterLynchLeader class that implements
Lynch's growth investing philosophy with focus on PEG ratio and ten-baggers.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class PeterLynchLeader:
    """彼得·林奇 Leader
    
    实现林奇的成长投资理念：
    - "投资你了解的领域"
    - 从日常生活中发现投资机会
    - 寻找具有增长潜力的中小市值公司
    - 相信普通人的选股能力
    - 成长股投资的关键是找到下一个"十倍股"
    - GARP（Growth At Reasonable Price）策略
    
    分析维度：
    - 公司类型判断
    - 成长潜力评估
    - 行业前景分析
    - PEG 估值
    - 管理层质量
    """
    
    # 类级别的配置
    LEADER_ID = "peter_lynch"
    LEADER_NAME = "彼得·林奇"
    LEADER_NAME_EN = "Peter Lynch"
    LEADER_STYLE = "成长投资专家"
    LEADER_DESCRIPTION = "富达基金传奇，\"十倍股\"猎手"
    
    SYSTEM_PROMPT = """你是一位成长投资专家，风格像彼得·林奇。

你的投资理念:
- "投资你了解的领域"
- 从日常生活中发现投资机会
- 寻找具有增长潜力的中小市值公司
- 相信普通人的选股能力
- 成长股投资的关键是找到下一个"十倍股"

分析股票时，请:
1. 评估公司的成长潜力和行业前景
2. 分析市场份额和竞争地位
3. 检查管理层质量
4. 估算成长空间和目标价

请用热情、乐观的语气进行分析。"""
    
    # 公司类型
    COMPANY_TYPES = [
        "快速增长型",
        "稳定增长型", 
        "缓慢增长型",
        "周期性公司",
        "资产型公司"
    ]
    
    def __init__(self):
        """初始化 Peter Lynch Leader"""
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_lynch_analysis_prompt(self, state: 'AgentState') -> str:
        """构建林奇风格的 prompt
        
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
        
        return f"""作为彼得·林奇，请对{name}（{code}）进行成长投资分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 营收增长: {stock_data.get('revenue_growth', 'N/A')}%
- 净利润增长: {stock_data.get('profit_growth', 'N/A')}%
- 行业: {stock_data.get('industry', '未知')}
- 市值: {stock_data.get('market_cap', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')}" for s in analyst_signals[:3]]) or '暂无'}

请从彼得·林奇的成长投资角度进行五维度分析：

维度1：公司类型判断
- 快速增长型（年增长20%+）
- 稳定增长型（年增长10-20%）
- 缓慢增长型（年增长<10%）
- 周期性公司
- 资产型公司（清算价值高于市值）

维度2：成长潜力评估
- 营收增速和持续性
- 净利润增速趋势
- 市场渗透率
- 新产品/新市场机会
- "十倍股"潜力评估

维度3：行业前景分析
- 行业增速 vs GDP增速
- 行业生命周期阶段
- 竞争格局变化
- 政策环境影响

维度4：GARP估值（合理价格成长股）
- PEG = P/E / 增长率
- PEG < 1: 价值型成长股（买入信号）
- PEG 1-2: 合理估值
- PEG > 2: 成长预期过高
- 目标价估算（基于PEG）

维度5：管理层质量
- 主营业务专注度
- 资本配置能力
- 股东回报意识
- 成长故事可信度

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "company_type": {{
            "type": "公司类型",
            "growth_rate": "预期增长率（%）",
            "ten_bagger_potential": "十倍股潜力（1-10）",
            "score": "评分1-10"
        }},
        "growth_potential": {{
            "revenue_cagr": "营收复合增速（%）",
            "profit_cagr": "利润复合增速（%）",
            "market_share": "市场份额变化",
            "new_opportunities": "新机会描述",
            "score": "评分1-10"
        }},
        "industry_outlook": {{
            "industry_growth": "行业增速（%）",
            "lifecycle_stage": "生命周期阶段",
            "competitive_landscape": "竞争格局",
            "policy_impact": "政策影响",
            "score": "评分1-10"
        }},
        "garp_valuation": {{
            "pe": "市盈率",
            "growth_rate": "预期增长率（%）",
            "peg": "PEG比率",
            "target_price": "目标价（元）",
            "upside_potential": "上涨空间（%）",
            "score": "评分1-10"
        }},
        "management_quality": {{
            "focus": "专注度（1-10）",
            "capital_allocation": "资本配置（1-10）",
            "shareholder_returns": "股东回报（1-10）",
            "story_credibility": "故事可信度（1-10）",
            "score": "评分1-10"
        }}
    }},
    "ten_bagger_analysis": {{
        "potential": "十倍股潜力评估",
        "time_horizon": "预期实现时间（年）",
        "key催化剂": "关键催化剂"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限"
}}"""
    
    def _parse_lynch_response(self, content: str) -> dict:
        """解析林奇分析响应
        
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
            ten_bagger = data.get("ten_bagger_analysis", {})
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "five_dimensions": five_dims,
                "company_type": {
                    "type": five_dims.get("company_type", {}).get("type", "N/A"),
                    "growth_rate": five_dims.get("company_type", {}).get("growth_rate", "N/A"),
                    "ten_bagger_potential": five_dims.get("company_type", {}).get("ten_bagger_potential", "N/A"),
                    "score": five_dims.get("company_type", {}).get("score", "N/A"),
                },
                "growth_potential": {
                    "revenue_cagr": five_dims.get("growth_potential", {}).get("revenue_cagr", "N/A"),
                    "profit_cagr": five_dims.get("growth_potential", {}).get("profit_cagr", "N/A"),
                    "market_share": five_dims.get("growth_potential", {}).get("market_share", "N/A"),
                    "score": five_dims.get("growth_potential", {}).get("score", "N/A"),
                },
                "industry_outlook": {
                    "industry_growth": five_dims.get("industry_outlook", {}).get("industry_growth", "N/A"),
                    "lifecycle_stage": five_dims.get("industry_outlook", {}).get("lifecycle_stage", "N/A"),
                    "score": five_dims.get("industry_outlook", {}).get("score", "N/A"),
                },
                "garp_valuation": {
                    "pe": five_dims.get("garp_valuation", {}).get("pe", "N/A"),
                    "peg": five_dims.get("garp_valuation", {}).get("peg", "N/A"),
                    "target_price": five_dims.get("garp_valuation", {}).get("target_price", "N/A"),
                    "upside_potential": five_dims.get("garp_valuation", {}).get("upside_potential", "N/A"),
                    "score": five_dims.get("garp_valuation", {}).get("score", "N/A"),
                },
                "management_quality": {
                    "focus": five_dims.get("management_quality", {}).get("focus", "N/A"),
                    "capital_allocation": five_dims.get("management_quality", {}).get("capital_allocation", "N/A"),
                    "score": five_dims.get("management_quality", {}).get("score", "N/A"),
                },
                "ten_bagger_analysis": ten_bagger,
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
                "five_dimensions": {},
                "company_type": {"type": "N/A", "score": "N/A"},
                "growth_potential": {"revenue_cagr": "N/A", "score": "N/A"},
                "industry_outlook": {"industry_growth": "N/A", "score": "N/A"},
                "garp_valuation": {"pe": "N/A", "peg": "N/A", "score": "N/A"},
                "management_quality": {"score": "N/A"},
                "ten_bagger_analysis": {"potential": "N/A"},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 20,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        """运行 Peter Lynch 分析
        
        Args:
            state: 当前工作流状态
            llm_service: LLM 服务实例
            
        Returns:
            Peter Lynch 五维度分析结果
        """
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        
        prompt = self._build_lynch_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_lynch_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            garp = result.get("garp_valuation", {})
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"PEG={garp.get('peg', 'N/A')}, "
                  f"十倍股潜力={result.get('company_type', {}).get('ten_bagger_potential', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "five_dimensions": {},
                "company_type": {"type": "N/A", "score": "N/A"},
                "growth_potential": {"revenue_cagr": "N/A", "score": "N/A"},
                "industry_outlook": {"industry_growth": "N/A", "score": "N/A"},
                "garp_valuation": {"pe": "N/A", "peg": "N/A", "score": "N/A"},
                "management_quality": {"score": "N/A"},
                "ten_bagger_analysis": {"potential": "N/A"},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 20,
                "investment_horizon": "3-5年",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_company_types(self) -> list[str]:
        """获取公司类型列表
        
        Returns:
            公司类型描述列表
        """
        return self.COMPANY_TYPES


# 便捷函数

def create_peter_lynch_leader() -> PeterLynchLeader:
    """创建 Peter Lynch Leader 实例"""
    return PeterLynchLeader()


async def run_peter_lynch_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    """运行 Peter Lynch 分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例
        
    Returns:
        Peter Lynch 五维度分析结果
    """
    leader = PeterLynchLeader()
    return await leader.analyze(state, llm_service)
