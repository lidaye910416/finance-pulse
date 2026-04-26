"""
Cathie Wood Leader Implementation

凯西·伍德投资大师的具体实现
- 未来趋势分析
- 创新赛道评估
- 颠覆性技术识别

This module provides the CathieWoodLeader class that implements
Wood's disruptive innovation investment philosophy.
"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.state import AgentState
    from services.llm import LLMService


class CathieWoodLeader:
    """凯西·伍德 Leader
    
    实现伍德的颠覆性创新投资理念：
    - 关注有突破性技术或商业模式的创新公司
    - 聚焦 AI、机器人、基因测序、金融科技和区块链
    - 投资于快速采用曲线和巨大 TAM 的行业
    - 愿意承受短期波动以获得长期收益
    
    分析维度：
    - 颠覆性潜力评估
    - 创新驱动增长分析
    - 高成长估值模型
    - TAM 分析
    - 管理层愿景评估
    """
    
    # 类级别的配置
    LEADER_ID = "cathie_wood"
    LEADER_NAME = "凯西·伍德"
    LEADER_NAME_EN = "Cathie Wood"
    LEADER_STYLE = "颠覆性创新大师"
    LEADER_DESCRIPTION = "ARK Invest创始人，颠覆性创新投资专家"
    
    SYSTEM_PROMPT = """你是一位颠覆性创新投资专家，风格像凯西·伍德。

你的投资理念:
- 寻找有突破性技术或商业模式的创新公司
- 聚焦于快速采用曲线和巨大 TAM 的行业
- 投资于 AI、机器人、基因测序、金融科技、区块链
- 愿意承受短期波动以获得长期收益
- 相信创新可以改变世界

分析股票时，请:
1. 评估公司的颠覆性潜力
2. 分析创新驱动增长
3. 计算高成长估值
4. 评估 TAM 和市场机会

请用乐观、前瞻的语气进行分析。"""
    
    # 核心赛道
    CORE_SECTORS = [
        "人工智能 (AI)",
        "机器人技术",
        "基因测序/精准医疗",
        "金融科技",
        "区块链/数字资产",
        "新能源/储能"
    ]
    
    def __init__(self):
        """初始化 Cathie Wood Leader"""
        self.id = self.LEADER_ID
        self.name = self.LEADER_NAME
        self.name_en = self.LEADER_NAME_EN
        self.style = self.LEADER_STYLE
        self.description = self.LEADER_DESCRIPTION
        self.system_prompt = self.SYSTEM_PROMPT
    
    def _build_wood_analysis_prompt(self, state: 'AgentState') -> str:
        """构建伍德风格的 prompt
        
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
        
        return f"""作为凯西·伍德，请对{name}（{code}）进行颠覆性创新分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 行业: {stock_data.get('industry', '未知')}
- 营收增长: {stock_data.get('revenue_growth', 'N/A')}%
- 市值: {stock_data.get('market_cap', 'N/A')}
- R&D投入: {stock_data.get('rd_intensity', 'N/A')}% 营收

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

请从伍德的颠覆性创新角度进行五维度分析：

维度1：颠覆性潜力评估
- 核心技术是否具有突破性？
- 商业模式是否创新？
- 是否有改变行业的潜力？
- 竞争对手复制难度
- 平台效应和网络效应

维度2：创新驱动增长
- 营收增长是否加速（非线性）？
- 毛利率是否扩张？
- 运营杠杆是否正向？
- R&D 投入强度和趋势
- 创新 Pipeline 评估

维度3：高成长估值模型
- 使用 5-7 年视角的 DCF
- 假设更高的增长率（20%+）
- 更高的终端倍数（25x+ FCF）
- TAM 渗透率分析
- 潜在市场空间评估

维度4：TAM（可寻址市场）分析
- 现有市场规模（亿美元）
- 潜在扩张市场
- 市场采用曲线阶段
- 市场份额目标
- 5年预期收入规模

维度5：管理层愿景评估
- 创新文化和专注度
- 长期资本配置能力
- 技术领先承诺
- 股东利益一致性
- 战略执行能力

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "five_dimensions": {{
        "disruptive_potential": {{
            "breakthrough_tech": "是否突破性技术（是/否）",
            "innovative_model": "商业模式创新程度（1-10）",
            "industry_change_potential": "改变行业潜力（1-10）",
            "competitive_moat": "竞争护城河类型",
            "platform_effect": "平台/网络效应（强/中/弱）",
            "score": "评分1-10"
        }},
        "innovation_growth": {{
            "revenue_acceleration": "营收加速（非线性/线性/放缓）",
            "margin_expansion": "毛利率趋势（扩张/稳定/收窄）",
            "operating_leverage": "运营杠杆（正向/中性/负向）",
            "rd_intensity": "R&D投入强度（%）",
            "innovation_pipeline": "创新管线评估",
            "score": "评分1-10"
        }},
        "high_growth_valuation": {{
            "dcf_5yr": "5年DCF估值（元）",
            "dcf_7yr": "7年DCF估值（元）",
            "terminal_multiple": "终端倍数",
            "growth_assumption": "增长率假设（%）",
            "discount_rate": "折现率（%）",
            "score": "评分1-10"
        }},
        "tam_analysis": {{
            "current_tam": "当前TAM（亿美元）",
            "expansion_potential": "市场扩张潜力",
            "adoption_curve": "采用曲线阶段（早期/成长期/成熟期）",
            "market_share_target": "目标市场份额（%）",
            "5yr_revenue_estimate": "5年预期收入（亿美元）",
            "score": "评分1-10"
        }},
        "management_vision": {{
            "innovation_culture": "创新文化（1-10）",
            "long_term_commitment": "长期承诺（1-10）",
            "tech_leadership": "技术领先（1-10）",
            "shareholder_alignment": "股东利益一致（1-10）",
            "strategic_execution": "战略执行（1-10）",
            "score": "评分1-10"
        }}
    }},
    "investment_thesis": {{
        "core_innovation": "核心创新描述",
        "growth催化剂": "增长催化剂",
        "time_horizon": "投资时间跨度",
        "conviction_level": "信心程度（高/中/低）"
    }},
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）",
    "investment_horizon": "投资期限（5年+）"
}}"""
    
    def _parse_wood_response(self, content: str) -> dict:
        """解析伍德分析响应
        
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
            thesis = data.get("investment_thesis", {})
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "five_dimensions": five_dims,
                "disruptive_potential": {
                    "breakthrough_tech": five_dims.get("disruptive_potential", {}).get("breakthrough_tech", "N/A"),
                    "innovative_model": five_dims.get("disruptive_potential", {}).get("innovative_model", "N/A"),
                    "industry_change_potential": five_dims.get("disruptive_potential", {}).get("industry_change_potential", "N/A"),
                    "competitive_moat": five_dims.get("disruptive_potential", {}).get("competitive_moat", "N/A"),
                    "score": five_dims.get("disruptive_potential", {}).get("score", "N/A"),
                },
                "innovation_growth": {
                    "revenue_acceleration": five_dims.get("innovation_growth", {}).get("revenue_acceleration", "N/A"),
                    "margin_expansion": five_dims.get("innovation_growth", {}).get("margin_expansion", "N/A"),
                    "rd_intensity": five_dims.get("innovation_growth", {}).get("rd_intensity", "N/A"),
                    "score": five_dims.get("innovation_growth", {}).get("score", "N/A"),
                },
                "high_growth_valuation": {
                    "dcf_5yr": five_dims.get("high_growth_valuation", {}).get("dcf_5yr", "N/A"),
                    "dcf_7yr": five_dims.get("high_growth_valuation", {}).get("dcf_7yr", "N/A"),
                    "terminal_multiple": five_dims.get("high_growth_valuation", {}).get("terminal_multiple", "N/A"),
                    "score": five_dims.get("high_growth_valuation", {}).get("score", "N/A"),
                },
                "tam_analysis": {
                    "current_tam": five_dims.get("tam_analysis", {}).get("current_tam", "N/A"),
                    "expansion_potential": five_dims.get("tam_analysis", {}).get("expansion_potential", "N/A"),
                    "adoption_curve": five_dims.get("tam_analysis", {}).get("adoption_curve", "N/A"),
                    "score": five_dims.get("tam_analysis", {}).get("score", "N/A"),
                },
                "management_vision": {
                    "innovation_culture": five_dims.get("management_vision", {}).get("innovation_culture", "N/A"),
                    "long_term_commitment": five_dims.get("management_vision", {}).get("long_term_commitment", "N/A"),
                    "score": five_dims.get("management_vision", {}).get("score", "N/A"),
                },
                "investment_thesis": thesis,
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 20),
                "investment_horizon": data.get("investment_horizon", "5年+"),
                "leader_id": self.id,
                "leader_name": self.name,
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "five_dimensions": {},
                "disruptive_potential": {"score": "N/A"},
                "innovation_growth": {"score": "N/A"},
                "high_growth_valuation": {"score": "N/A"},
                "tam_analysis": {"score": "N/A"},
                "management_vision": {"score": "N/A"},
                "investment_thesis": {"conviction_level": "N/A"},
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 20,
                "investment_horizon": "5年+",
                "leader_id": self.id,
                "leader_name": self.name,
            }
    
    async def analyze(self, state: 'AgentState', llm_service: 'LLMService') -> dict:
        """运行 Cathie Wood 分析
        
        Args:
            state: 当前工作流状态
            llm_service: LLM 服务实例
            
        Returns:
            Cathie Wood 五维度分析结果
        """
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        
        prompt = self._build_wood_analysis_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_wood_response(response["content"])
            result["tokens"] = response.get("tokens", 0)
            
            thesis = result.get("investment_thesis", {})
            print(f"[leader:{self.id}] {self.name} 完成: {result['decision']}, "
                  f"信心程度={thesis.get('conviction_level', 'N/A')}, "
                  f"时间跨度={thesis.get('time_horizon', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "decision": "hold",
                "confidence": 30,
                "five_dimensions": {},
                "disruptive_potential": {"score": "N/A"},
                "innovation_growth": {"score": "N/A"},
                "high_growth_valuation": {"score": "N/A"},
                "tam_analysis": {"score": "N/A"},
                "management_vision": {"score": "N/A"},
                "investment_thesis": {"conviction_level": "N/A"},
                "key_factors": [],
                "risk_factors": [f"分析服务暂时不可用: {str(e)}"],
                "reasoning": f"分析失败: {str(e)}",
                "position_recommendation": 20,
                "investment_horizon": "5年+",
                "leader_id": self.id,
                "leader_name": self.name,
                "tokens": 0,
            }
    
    def get_core_sectors(self) -> list[str]:
        """获取核心赛道列表
        
        Returns:
            核心赛道描述列表
        """
        return self.CORE_SECTORS


# 便捷函数

def create_cathie_wood_leader() -> CathieWoodLeader:
    """创建 Cathie Wood Leader 实例"""
    return CathieWoodLeader()


async def run_cathie_wood_analysis(
    state: 'AgentState',
    llm_service: 'LLMService'
) -> dict:
    """运行 Cathie Wood 分析的便捷函数
    
    Args:
        state: 当前工作流状态
        llm_service: LLM 服务实例
        
    Returns:
        Cathie Wood 五维度分析结果
    """
    leader = CathieWoodLeader()
    return await leader.analyze(state, llm_service)
