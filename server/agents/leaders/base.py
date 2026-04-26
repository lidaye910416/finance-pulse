"""
Leader 基类和工厂函数

实现不同投资大师的分析风格，用于 Fusion 模式下的最终决策。

Pattern:
- Each leader has _build_*_prompt(state) and _parse_*_response(content)
- Each leader has run_leader(state, llm_service) async function
- Output format: JSON with decision, reasoning, key_factors, confidence
"""

import json
from abc import ABC, abstractmethod
from typing import Any

from graph.state import AgentState
from services.llm import LLMService


# ========== Leader 配置 ==========

LEADERS = [
    {
        "id": "warren_buffett",
        "name": "沃伦·巴菲特",
        "name_en": "Warren Buffett",
        "style": "价值投资大师",
        "description": "寻找伟大的公司，以合理的价格买入",
        "system_prompt": """你是一位价值投资大师，风格像沃伦·巴菲特。

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

请用专业、沉稳的语气进行分析。""",
    },
    {
        "id": "ben_graham",
        "name": "本杰明·格雷厄姆",
        "name_en": "Benjamin Graham",
        "style": "安全边际专家",
        "description": "强调安全边际是投资的核心",
        "system_prompt": """你是一位安全边际专家，风格像本杰明·格雷厄姆。

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

请用谨慎、理性的语气进行分析。""",
    },
    {
        "id": "peter_lynch",
        "name": "彼得·林奇",
        "name_en": "Peter Lynch",
        "style": "成长投资专家",
        "description": "在日常生活中寻找10倍股",
        "system_prompt": """你是一位成长投资专家，风格像彼得·林奇。

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

请用热情、乐观的语气进行分析。""",
    },
    {
        "id": "charlie_munger",
        "name": "查理·芒格",
        "name_en": "Charlie Munger",
        "style": "多元思维模型专家",
        "description": "跨学科分析，逆向思考",
        "system_prompt": """你是一位多元思维模型大师，风格像查理·芒格。

你的投资理念:
- 使用多元思维模型分析问题
- 强调"逆向思维"的重要性
- 追求"极好"的生意，而非"还好"
- 耐心等待击球机会
- 持续学习，提升认知

分析股票时，请:
1. 用多学科视角分析公司
2. 评估管理层的诚信和能力
3. 检查公司的竞争优势
4. 判断是否是"极好"的生意

请用深刻、睿智的语气进行分析。""",
    },
    {
        "id": "michael_burry",
        "name": "迈克尔·伯里",
        "name_en": "Michael Burry",
        "style": "逆向投资专家",
        "description": "独立思考，发现市场错误定价",
        "system_prompt": """你是一位逆向投资专家，风格像迈克尔·伯里。

你的投资理念:
- 独立思考，不随大流
- 深入研究，发现被忽视的风险
- 敢于做空被高估的资产
- 关注系统性风险和泡沫
- 逆向交易需要强大的信心和耐心

分析股票时，请:
1. 识别市场共识中的错误
2. 评估潜在的风险因素
3. 判断是否存在泡沫
4. 提供逆向投资建议

请用尖锐、直接的语气进行分析。""",
    },
    {
        "id": "nassim_taleb",
        "name": "纳西姆·塔勒布",
        "name_en": "Nassim Taleb",
        "style": "尾部风险管理专家",
        "description": "关注黑天鹅，追求不对称收益",
        "system_prompt": """你是一位尾部风险管理专家，风格像纳西姆·塔勒布。

你的投资理念:
- 关注"黑天鹅"事件的影响
- 构建"反脆弱"的投资组合
- 追求收益的不对称性
- 避免"脆弱"的资产和公司
- 杠铃策略：极度保守+适度冒险

分析股票时，请:
1. 评估公司的"反脆弱"性
2. 识别潜在的尾部风险
3. 分析收益风险比
4. 提供风险管理的建议

请用锐利、批判性的语气进行分析。""",
    },
]


def get_available_leaders() -> list[dict]:
    """获取所有可用的 Leader 配置"""
    return LEADERS


def get_leader_config(leader_id: str) -> dict | None:
    """根据 ID 获取 Leader 配置"""
    return next((l for l in LEADERS if l["id"] == leader_id), None)


# ========== Leader 基类 ==========

class LeaderBase(ABC):
    """Leader 抽象基类
    
    所有投资大师都应继承此类并实现核心方法。
    """
    
    def __init__(self, config: dict):
        """初始化 Leader
        
        Args:
            config: Leader 配置字典
        """
        self.id = config["id"]
        self.name = config["name"]
        self.name_en = config["name_en"]
        self.style = config["style"]
        self.description = config["description"]
        self.system_prompt = config["system_prompt"]
    
    @abstractmethod
    def _build_prompt(self, state: AgentState) -> str:
        """构建分析 prompt
        
        Args:
            state: 当前工作流状态
            
        Returns:
            格式化后的 prompt 字符串
        """
        pass
    
    @abstractmethod
    def _parse_response(self, content: str) -> dict:
        """解析 LLM 响应
        
        Args:
            content: LLM 返回的原始内容
            
        Returns:
            结构化的分析结果字典
        """
        pass
    
    async def analyze(self, state: AgentState, llm_service: LLMService) -> dict:
        """运行 Leader 分析
        
        Args:
            state: 当前工作流状态
            llm_service: LLM 服务实例
            
        Returns:
            Leader 分析结果
        """
        print(f"[leader:{self.id}] {self.name} 正在分析...")
        
        prompt = self._build_prompt(state)
        
        try:
            response = await llm_service.complete([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ])
            
            result = self._parse_response(response["content"])
            result["leader_id"] = self.id
            result["leader_name"] = self.name
            result["tokens"] = response.get("tokens", 0)
            
            print(f"[leader:{self.id}] {self.name} 完成: {result.get('decision', 'unknown')}")
            return result
            
        except Exception as e:
            print(f"[leader:{self.id}] {self.name} 错误: {e}")
            return {
                "leader_id": self.id,
                "leader_name": self.name,
                "decision": "hold",
                "confidence": 30,
                "reasoning": f"分析服务暂时不可用: {str(e)}",
                "key_factors": [],
                "risk_factors": [],
                "tokens": 0,
            }


# ========== 具体 Leader 实现 ==========

class WarrenBuffettLeader(LeaderBase):
    """沃伦·巴菲特 Leader
    
    价值投资风格，7维度分析，计算安全边际
    """
    
    def _build_prompt(self, state: AgentState) -> str:
        """构建巴菲特风格的 prompt"""
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

分析师信号汇总：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:5]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:100] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:100] if bearish_signal else '暂无'}

风险建议：{risk_recommendation.get('consensus_risk_level', 'medium')}风险

请从巴菲特的价值投资角度提供7维度分析：
1. 业务质量（护城河分析）
2. 盈利能力（ROE、ROA、毛利率）
3. 成长性（营收/利润增速）
4. 财务健康（负债率、现金流）
5. 内在价值估算
6. 安全边际评估
7. 最终投资决策

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "intrinsic_value": "内在价值估算（元）",
    "margin_of_safety": "安全边际（%）",
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（150字以内）",
    "position_recommendation": "建议仓位（%）"
}}"""
    
    def _parse_response(self, content: str) -> dict:
        """解析巴菲特分析响应"""
        try:
            json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "intrinsic_value": data.get("intrinsic_value", "待估算"),
                "margin_of_safety": data.get("margin_of_safety", "待计算"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 20),
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "intrinsic_value": "解析失败",
                "margin_of_safety": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 20,
            }


class BenGrahamLeader(LeaderBase):
    """本杰明·格雷厄姆 Leader
    
    安全边际风格，强调低估值的防御性投资
    """
    
    def _build_prompt(self, state: AgentState) -> str:
        """构建格雷厄姆风格的 prompt"""
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为本杰明·格雷厄姆，请对{name}（{code}）进行安全边际分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 市净率(PB): {stock_data.get('pb', 'N/A')}
- 股息率: {stock_data.get('dividend_yield', 'N/A')}%
- 总市值: {stock_data.get('market_cap', 'N/A')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')}" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从格雷厄姆的安全边际角度分析：
1. 清算价值评估
2. 内在价值估算
3. 安全边际计算
4. 财务健康状况
5. 风险收益比
6. 最终决策

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "liquidation_value": "清算价值（元）",
    "intrinsic_value": "内在价值（元）",
    "margin_of_safety": "安全边际（%）",
    "financial_health": "财务健康评估",
    "key_factors": ["因素1", "因素2"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（100字以内）",
    "position_recommendation": "建议仓位（%）"
}}"""
    
    def _parse_response(self, content: str) -> dict:
        """解析格雷厄姆分析响应"""
        try:
            json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "liquidation_value": data.get("liquidation_value", "N/A"),
                "intrinsic_value": data.get("intrinsic_value", "N/A"),
                "margin_of_safety": data.get("margin_of_safety", "N/A"),
                "financial_health": data.get("financial_health", "N/A"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 15),
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "liquidation_value": "N/A",
                "intrinsic_value": "N/A",
                "margin_of_safety": "N/A",
                "financial_health": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
            }


class PeterLynchLeader(LeaderBase):
    """彼得·林奇 Leader
    
    成长投资风格，关注公司成长性和行业前景
    """
    
    def _build_prompt(self, state: AgentState) -> str:
        """构建彼得·林奇风格的 prompt"""
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

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')}" for s in analyst_signals[:3]]) or '暂无'}

请从彼得·林奇的成长投资角度分析：
1. 公司类型判断（快速增长/稳定增长/缓慢增长）
2. 行业前景评估
3. 市场份额和竞争优势
4. 成长空间和目标价
5. 管理层质量评估
6. 最终投资决策

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "company_type": "公司类型",
    "growth_potential": "成长潜力",
    "target_price": "目标价（元）",
    "key_factors": ["因素1", "因素2", "因素3"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（100字以内）",
    "position_recommendation": "建议仓位（%）"
}}"""
    
    def _parse_response(self, content: str) -> dict:
        """解析彼得·林奇分析响应"""
        try:
            json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "company_type": data.get("company_type", "N/A"),
                "growth_potential": data.get("growth_potential", "N/A"),
                "target_price": data.get("target_price", "N/A"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 20),
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "company_type": "N/A",
                "growth_potential": "N/A",
                "target_price": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 20,
            }


class CharlieMungerLeader(LeaderBase):
    """查理·芒格 Leader
    
    多元思维模型风格，跨学科分析和逆向思考
    """
    
    def _build_prompt(self, state: AgentState) -> str:
        """构建芒格风格的 prompt"""
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        analyst_signals = state.get("analyst_signals", [])
        bullish_signal = state.get("bullish_signal", {})
        bearish_signal = state.get("bearish_signal", {})
        
        return f"""作为查理·芒格，请用多元思维模型对{name}（{code}）进行分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 行业: {stock_data.get('industry', '未知')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')}" for s in analyst_signals[:3]]) or '暂无'}

多空辩论：
- 多头: {bullish_signal.get('reasoning', '暂无')[:80] if bullish_signal else '暂无'}
- 空头: {bearish_signal.get('reasoning', '暂无')[:80] if bearish_signal else '暂无'}

请从芒格的多元思维模型角度分析：
1. 心理学视角（行为金融学角度）
2. 经济学视角（竞争优势）
3. 生物学视角（商业模式适应度）
4. 逆向分析（不做这件事的理由）
5. "极好"生意判断
6. 最终投资决策

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "psychology_insight": "心理学洞察",
    "economic_advantage": "经济竞争优势",
    "business_quality": "生意质量评估",
    "key_factors": ["因素1", "因素2"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（100字以内）",
    "position_recommendation": "建议仓位（%）"
}}"""
    
    def _parse_response(self, content: str) -> dict:
        """解析芒格分析响应"""
        try:
            json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "psychology_insight": data.get("psychology_insight", "N/A"),
                "economic_advantage": data.get("economic_advantage", "N/A"),
                "business_quality": data.get("business_quality", "N/A"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 20),
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "psychology_insight": "N/A",
                "economic_advantage": "N/A",
                "business_quality": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 20,
            }


class MichaelBurryLeader(LeaderBase):
    """迈克尔·伯里 Leader
    
    逆向投资风格，独立思考，发现市场错误定价
    """
    
    def _build_prompt(self, state: AgentState) -> str:
        """构建伯里风格的 prompt"""
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        analyst_signals = state.get("analyst_signals", [])
        
        return f"""作为迈克尔·伯里，请对{name}（{code}）进行逆向投资分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 行业: {stock_data.get('industry', '未知')}

市场共识（分析师）：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')} ({s.get('confidence', 0)}%)" for s in analyst_signals[:3]]) or '暂无'}

请从伯里的逆向投资角度分析：
1. 市场共识中的错误识别
2. 被忽视的风险因素
3. 潜在的价值陷阱
4. 泡沫评估
5. 不对称风险收益机会
6. 最终投资决策

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "market_error": "市场共识错误",
    "ignored_risks": ["风险1", "风险2"],
    "bubble_assessment": "泡沫评估",
    "asymmetric_opportunity": "不对称机会描述",
    "key_factors": ["因素1", "因素2"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（100字以内）",
    "position_recommendation": "建议仓位（%）"
}}"""
    
    def _parse_response(self, content: str) -> dict:
        """解析伯里分析响应"""
        try:
            json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "market_error": data.get("market_error", "N/A"),
                "ignored_risks": data.get("ignored_risks", []),
                "bubble_assessment": data.get("bubble_assessment", "N/A"),
                "asymmetric_opportunity": data.get("asymmetric_opportunity", "N/A"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 15),
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "market_error": "N/A",
                "ignored_risks": [],
                "bubble_assessment": "N/A",
                "asymmetric_opportunity": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 15,
            }


class NassimTalebLeader(LeaderBase):
    """纳西姆·塔勒布 Leader
    
    尾部风险管理风格，关注黑天鹅和反脆弱性
    """
    
    def _build_prompt(self, state: AgentState) -> str:
        """构建塔勒布风格的 prompt"""
        stock_data = state.get("stock_data", {})
        code = state.get("code", "")
        name = stock_data.get("name", "未知")
        price = stock_data.get("price", 0)
        
        analyst_signals = state.get("analyst_signals", [])
        
        return f"""作为纳西姆·塔勒布，请对{name}（{code}）进行尾部风险管理分析：

当前行情：
- 价格: ¥{price:.2f}
- 市盈率(PE): {stock_data.get('pe', 'N/A')}
- 行业: {stock_data.get('industry', '未知')}

分析师信号：
{chr(10).join([f"- {s.get('agent', '未知')}: {s.get('signal', 'neutral')}" for s in analyst_signals[:3]]) or '暂无'}

请从塔勒布的尾部风险管理角度分析：
1. 公司的"反脆弱"性评估
2. 潜在"黑天鹅"风险
3. 收益风险比不对称性
4. "脆弱"性因素识别
5. 杠铃策略建议
6. 最终投资决策

请用JSON格式返回：
{{
    "decision": "buy" | "hold" | "sell",
    "confidence": 0-100,
    "anti_fragility": "反脆弱性评估",
    "black_swan_risks": ["风险1", "风险2"],
    "asymmetry": "收益风险不对称性",
    "fragility_factors": ["脆弱因素1", "脆弱因素2"],
    "barbell_strategy": "杠铃策略建议",
    "key_factors": ["因素1", "因素2"],
    "risk_factors": ["风险1", "风险2"],
    "reasoning": "分析理由（100字以内）",
    "position_recommendation": "建议仓位（%）"
}}"""
    
    def _parse_response(self, content: str) -> dict:
        """解析塔勒布分析响应"""
        try:
            json_match = content.match(r'\{[\s\S]*\}') if hasattr(content, 'match') else None
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)
            
            return {
                "decision": data.get("decision", "hold"),
                "confidence": min(100, max(0, int(data.get("confidence", 50)))),
                "anti_fragility": data.get("anti_fragility", "N/A"),
                "black_swan_risks": data.get("black_swan_risks", []),
                "asymmetry": data.get("asymmetry", "N/A"),
                "fragility_factors": data.get("fragility_factors", []),
                "barbell_strategy": data.get("barbell_strategy", "N/A"),
                "key_factors": data.get("key_factors", []),
                "risk_factors": data.get("risk_factors", []),
                "reasoning": data.get("reasoning", "")[:200],
                "position_recommendation": data.get("position_recommendation", 10),
            }
        except json.JSONDecodeError:
            return {
                "decision": "hold",
                "confidence": 50,
                "anti_fragility": "N/A",
                "black_swan_risks": [],
                "asymmetry": "N/A",
                "fragility_factors": [],
                "barbell_strategy": "N/A",
                "key_factors": [],
                "risk_factors": ["响应解析失败"],
                "reasoning": content[:200] if content else "分析完成",
                "position_recommendation": 10,
            }


# ========== Leader 工厂函数 ==========

def create_leader(leader_id: str) -> LeaderBase | None:
    """创建 Leader 实例
    
    根据 leader_id 创建对应的 Leader 子类实例。
    
    Args:
        leader_id: Leader ID，如 "warren_buffett", "ben_graham" 等
        
    Returns:
        LeaderBase 子类实例，如果 ID 不存在则返回 None
    """
    leader_map = {
        "warren_buffett": WarrenBuffettLeader,
        "ben_graham": BenGrahamLeader,
        "peter_lynch": PeterLynchLeader,
        "charlie_munger": CharlieMungerLeader,
        "michael_burry": MichaelBurryLeader,
        "nassim_taleb": NassimTalebLeader,
    }
    
    leader_class = leader_map.get(leader_id)
    if not leader_class:
        return None
    
    # 获取配置
    config = get_leader_config(leader_id)
    if not config:
        return None
    
    return leader_class(config)


async def run_leader(
    leader_id: str,
    state: AgentState,
    llm_service: LLMService
) -> dict:
    """运行指定 Leader 的分析
    
    这是一个便捷函数，用于快速运行单个 Leader。
    
    Args:
        leader_id: Leader ID
        state: 当前工作流状态
        llm_service: LLM 服务实例
        
    Returns:
        Leader 分析结果
    """
    leader = create_leader(leader_id)
    if not leader:
        return {
            "error": f"未知的 Leader: {leader_id}",
            "available_leaders": [l["id"] for l in LEADERS],
        }
    
    return await leader.analyze(state, llm_service)
