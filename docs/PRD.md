# FinancePulse 产品需求文档 (PRD)

**版本**: v3.0  
**日期**: 2026-04-26  
**参考项目**: 
- [TradingAgents](https://github.com/martin861101/AI_TradingAgents_LangGraph)
- [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)

---

## 1. 三种多智能体分析模式

用户可以选择三种不同的分析模式，适应不同场景和需求。

---

## 2. 功能参数设计 (用户可配置)

### 2.1 参数分类

| 类别 | 参数 | 适用模式 | 说明 |
|------|------|---------|------|
| **基础参数** | code, name, mode | 全部 | 必需 |
| **收敛参数** | max_iterations, gap | A, C | 辩论控制 |
| **大师选择** | leader_id | B, C | 19选1 |
| **风险偏好** | risk_level | B, C | 激进/平衡/保守 |
| **输出偏好** | show_details, save_history | 全部 | 显示和存储 |

### 2.2 通用基础参数

```typescript
interface BaseAnalysisRequest {
    code: string;              // 股票代码，如 "600519"
    name?: string;             // 股票名称，如 "贵州茅台"
    mode: "tradingagents" | "aihedgefund" | "fusion";  // 分析模式
    language?: "zh" | "en";   // 输出语言，默认中文
    show_details?: boolean;    // 是否显示详细分析过程，默认true
    save_history?: boolean;    // 是否保存到历史记录，默认true
}
```

### 2.3 模式 A: TradingAgents 专用参数

```typescript
interface TradingAgentsRequest extends BaseAnalysisRequest {
    mode: "tradingagents";
    max_iterations?: number;      // 最大辩论轮次，默认3 (范围: 1-5)
    convergence_gap?: number;     // 收敛差距阈值(%)，默认15 (范围: 10-30)
    early_stop_gap?: number;     // 提前停止差距阈值(%)，默认10 (范围: 5-20)
}
```

### 2.4 模式 B: ai-hedge-fund 专用参数

```typescript
interface AIHedgeFundRequest extends BaseAnalysisRequest {
    mode: "aihedgefund";
    leader_id: string;          // 19位大师之一
    auto_select_analysts?: boolean;  // 自动选择分析师，默认true
    analyst_ids?: string[];      // 手动选择的分析师ID列表
    risk_level?: "conservative" | "moderate" | "aggressive"; // 默认: moderate
    enable_dynamic_weights?: boolean;  // 启用动态权重调整，默认true
    enable_leader_intervention?: boolean;  // 启用Leader干预，默认true
}
```

### 2.5 模式 C: 融合模式专用参数

```typescript
interface FusionRequest extends BaseAnalysisRequest {
    mode: "fusion";
    leader_id: string;          // 19位大师之一
    max_iterations?: number;      // 最大辩论轮次，默认3
    convergence_gap?: number;     // 收敛差距阈值(%)，默认15
    early_stop_gap?: number;     // 提前停止差距阈值(%)，默认10
    risk_level?: "conservative" | "moderate" | "aggressive"; // 默认: moderate
    leader_can_adjust?: boolean; // Leader是否可以调整结论，默认true
}
```

---

## 3. 风险偏好详细设置

### 3.1 风险偏好级别

```python
RISK_PREFERENCES = {
    "conservative": {
        "name": "保守型",
        "max_position": 20,
        "stop_loss_percent": 3,
        "volatility_alert": 5,
        "volatility_extreme": 10,
        "max_pe": 40,
        "require_stop_loss": True,
        "description": "严格风控，适合风险厌恶型投资者"
    },
    "moderate": {
        "name": "平衡型",
        "max_position": 30,
        "stop_loss_percent": 5,
        "volatility_alert": 8,
        "volatility_extreme": 15,
        "max_pe": 60,
        "require_stop_loss": True,
        "description": "平衡风险和收益，适合大多数投资者"
    },
    "aggressive": {
        "name": "激进型",
        "max_position": 50,
        "stop_loss_percent": 8,
        "volatility_alert": 12,
        "volatility_extreme": 20,
        "max_pe": 100,
        "require_stop_loss": False,
        "description": "追求高收益，适合风险承受能力强投资者"
    }
}
```

---

## 4. 收敛参数设计

### 4.1 参数说明

| 参数 | 默认值 | 范围 | 说明 |
|------|--------|------|------|
| max_iterations | 3 | 1-5 | 最大辩论轮次 |
| convergence_gap | 15% | 10-30% | 收敛差距阈值 |
| early_stop_gap | 10% | 5-20% | 提前停止差距阈值 |

### 4.2 预设方案

```python
CONVERGENCE_PRESETS = {
    "quick": {"max_iterations": 1, "convergence_gap": 20, "early_stop_gap": 15},
    "standard": {"max_iterations": 3, "convergence_gap": 15, "early_stop_gap": 10},
    "deep": {"max_iterations": 5, "convergence_gap": 10, "early_stop_gap": 5},
}
```

---

## 5. 19位大师配置

### 5.1 大师列表 (基于 ai-hedge-fund)

```python
LEADERS = [
    # 价值投资派
    {"id": "warren_buffett", "name": "沃伦·巴菲特", "style": "价值投资", "avatar": "🎯"},
    {"id": "ben_graham", "name": "本杰明·格雷厄姆", "style": "价值投资", "avatar": "📖"},
    {"id": "charlie_munger", "name": "查理·芒格", "style": "价值投资", "avatar": "⚖️"},
    {"id": "peter_lynch", "name": "彼得·林奇", "style": "成长投资", "avatar": "🔍"},
    
    # 宏观/策略派
    {"id": "george_soros", "name": "乔治·索罗斯", "style": "宏观对冲", "avatar": "🌍"},
    {"id": "ray_dalio", "name": "雷·达里奥", "style": "宏观策略", "avatar": "🏛️"},
    {"id": "stanley_druckenmiller", "name": "斯坦利·德鲁肯米勒", "style": "宏观交易", "avatar": "💹"},
    {"id": "paul_tudor_jones", "name": "保罗·都铎·琼斯", "style": "趋势跟踪", "avatar": "📈"},
    
    # 量化/技术派
    {"id": "jim_simons", "name": "吉姆·西蒙斯", "style": "量化投资", "avatar": "🔢"},
    {"id": "ed_thorp", "name": "爱德华·索普", "style": "量化对冲", "avatar": "🎰"},
    {"id": "john_bogle", "name": "约翰·博格", "style": "指数投资", "avatar": "📊"},
    
    # 行业/个股派
    {"id": "cathie_wood", "name": "凯西·伍德", "style": "颠覆性创新", "avatar": "🚀"},
    {"id": "michael_burry", "name": "迈克尔·伯里", "style": "价值发现", "avatar": "🎭"},
    {"id": "nassim_taleb", "name": "纳西姆·塔勒布", "style": "尾部风险", "avatar": "⚠️"},
    {"id": "howard_marks", "name": "霍华德·马克斯", "style": "逆向投资", "avatar": "🔄"},
    {"id": "seth_klarman", "name": "塞思·卡拉曼", "style": "深度价值", "avatar": "💎"},
    
    # 特殊专长派
    {"id": "carl_icahn", "name": "卡尔·伊坎", "style": "激进投资", "avatar": "⚔️"},
    {"id": "george_aultman", "name": "乔治·奥特曼", "style": "风险量化", "avatar": "🛡️"},
    {"id": "aswath_damodaran", "name": "阿斯瓦特·达莫达兰", "style": "估值专家", "avatar": "📐"},
]
```

### 5.2 Leader System Prompt 示例 (ai-hedge-fund 风格)

```python
LEADER_PROMPTS = {
    "warren_buffett": """You are Warren Buffett, the Oracle of Omaha. Your investment philosophy:
- Seek wonderful companies at a fair price, not fair companies at a wonderful price
- Focus on intrinsic value and competitive moats
- Invest with a 5-10 year time horizon
- Moat comes from: intangible assets, switching costs, network effects, cost advantages
- Always maintain a margin of safety
- Be fearful when others are greedy, greedy when others are fearful""",
    
    "ben_graham": """You are Benjamin Graham, the father of value investing. Your philosophy:
- Always maintain a margin of safety
- Mr. Market is your servant, not your master
- Invest in companies with low P/E and P/B ratios
- Diversification is crucial for the defensive investor
- Focus on intrinsic value calculation""",
    
    # ... 其他大师的 prompt 类似
}
```

---

## 6. 三种模式完整设计

### 6.1 模式 A: TradingAgents (完全对标)

#### 架构 (基于 TradingAgents v2)

```
┌─────────────────────────────────────────────────────────────┐
│                    8阶段工作流 (TradingAgents)              │
├─────────────────────────────────────────────────────────────┤
│  1. market_analyst     - 市场概览和趋势分析                │
│  2. social_analyst     - 社交媒体情绪                      │
│  3. news_analyst      - 新闻事件分析                       │
│  4. fundamentals      - 财务数据分析                       │
│  5. bull_bear_debate  - 多空辩论 (可循环)                 │
│  6. trader_proposal   - 交易员提案                        │
│  7. risk_debate      - 风险辩论 (激进/中性/保守)          │
│  8. portfolio_manager  - 投资组合经理最终决策               │
└─────────────────────────────────────────────────────────────┘
```

#### 分析师配置 (与 TradingAgents 一致)

```python
ANALYSTS = [
    {"id": "market", "name": "Market Analyst", "name_cn": "市场分析师", "avatar": "🌐"},
    {"id": "social", "name": "Social Analyst", "name_cn": "社交分析师", "avatar": "💬"},
    {"id": "news", "name": "News Analyst", "name_cn": "新闻分析师", "avatar": "📰"},
    {"id": "fundamentals", "name": "Fundamentals Analyst", "name_cn": "基本面分析师", "avatar": "📊"},
    {"id": "bull", "name": "Bull Researcher", "name_cn": "多头研究员", "avatar": "📈"},
    {"id": "bear", "name": "Bear Researcher", "name_cn": "空头研究员", "avatar": "📉"},
    {"id": "trader", "name": "Trader", "name_cn": "交易员", "avatar": "💼"},
    {"id": "risk", "name": "Risk Analyzer", "name_cn": "风险分析师", "avatar": "🛡️"},
    {"id": "portfolio", "name": "Portfolio Manager", "name_cn": "组合经理", "avatar": "👔"},
]
```

#### 工作流实现 (server/graph/tradingagents_workflow.py)

```python
from langgraph.graph import StateGraph, END
from .state import AgentState, should_continue

def create_tradingagents_workflow(llm_service: LLMService) -> StateGraph:
    """
    TradingAgents 8阶段工作流
    
    参考: TradingAgents/tradingagents/graph/trading_graph.py
    """
    workflow = StateGraph(AgentState)
    
    # 阶段1: 市场分析
    workflow.add_node("market_analyst", market_analyst_node)
    
    # 阶段2: 社交情绪
    workflow.add_node("social_analyst", social_analyst_node)
    
    # 阶段3: 新闻分析
    workflow.add_node("news_analyst", news_analyst_node)
    
    # 阶段4: 基本面分析
    workflow.add_node("fundamentals", fundamentals_node)
    
    # 阶段5: 多空辩论 (可循环)
    workflow.add_node("bull_bear_debate", bull_bear_debate_node)
    
    # 条件路由: 辩论后决定是否继续
    workflow.add_conditional_edges(
        "bull_bear_debate",
        should_continue,
        {"debate": "bull_bear_debate", "synthesize": "trader_proposal"}
    )
    
    # 阶段6: 交易员提案
    workflow.add_node("trader_proposal", trader_proposal_node)
    
    # 阶段7: 风险辩论
    workflow.add_node("risk_debate", risk_debate_node)
    
    # 阶段8: 投资组合经理
    workflow.add_node("portfolio_manager", portfolio_manager_node)
    
    # 设置入口和边
    workflow.set_entry_point("market_analyst")
    workflow.add_edge("market_analyst", "social_analyst")
    workflow.add_edge("social_analyst", "news_analyst")
    workflow.add_edge("news_analyst", "fundamentals")
    workflow.add_edge("fundamentals", "bull_bear_debate")
    workflow.add_edge("trader_proposal", "risk_debate")
    workflow.add_edge("risk_debate", "portfolio_manager")
    workflow.add_edge("portfolio_manager", END)
    
    return workflow.compile()
```

#### 分析师节点实现示例 (server/agents/market.py)

```python
async def market_analyst_node(state: AgentState, llm_service: LLMService) -> AgentState:
    """
    市场分析师节点
    
    参考: TradingAgents/tradingagents/agents/market.py
    """
    stock_data = state.get("stock_data", {})
    code = state.get("code", "")
    name = state.get("name", f"Stock {code}")
    
    prompt = f"""Analyze the market context for {name} ({code}):

Current Data:
- Price: ¥{stock_data.get('price', 0):.2f}
- Change: {stock_data.get('change_percent', 0):+.2f}%
- Volume: {stock_data.get('volume', 0)/10000:.2f}M
- Turnover: ¥{stock_data.get('amount', 0)/1e8:.2f}B

Provide:
1. Market sector/industry context
2. Overall market sentiment indicators
3. Related market indices performance
4. Key market drivers for this sector

Return JSON: {{"market_context": "...", "sector_trend": "bullish/bearish/neutral", "confidence": 0-100}}"""

    response = await llm_service.complete([
        {"role": "system", "content": "You are a Market Analyst expert. Provide clear, data-driven market context."},
        {"role": "user", "content": prompt}
    ])
    
    state["market_signal"] = parse_json_response(response["content"])
    return state
```

#### 风险辩论实现 (server/agents/risk_debate.py)

```python
async def risk_debate_node(state: AgentState, llm_service: LLMService) -> AgentState:
    """
    风险辩论节点 - 三种风险偏好辩论
    
    参考: TradingAgents/tradingagents/agents/risk.py
    """
    risk_level = state.get("risk_level", "moderate")
    stock_data = state.get("stock_data", {})
    recommendation = state.get("recommendation", {})
    
    prompt = f"""Analyze this investment from three risk perspectives:

Stock: {stock_data.get('name', state['code'])}
Price: ¥{stock_data.get('price', 0):.2f}
Recommended Action: {recommendation.get('action', 'hold')}

1. Conservative View (保守):
   - Focus on downside protection
   - Strict stop-loss requirements
   - Maximum position sizing

2. Moderate View (平衡):
   - Balance risk and return
   - Reasonable stop-loss
   - Standard position sizing

3. Aggressive View (激进):
   - Focus on upside potential
   - Wider tolerance for volatility
   - Larger position sizing

Return JSON:
{{
    "conservative": {{"action": "...", "position": 0-100, "stop_loss": "price or %", "risk_rating": "low/medium/high"}},
    "moderate": {{...}},
    "aggressive": {{...}},
    "final_recommendation": "..."
}}"""

    response = await llm_service.complete([
        {"role": "system", "content": "You are a Risk Management expert. Analyze investments from all three perspectives."},
        {"role": "user", "content": prompt}
    ])
    
    state["risk_analysis"] = parse_json_response(response["content"])
    return state
```

#### 性能指标

| 指标 | 数值 |
|------|------|
| Token消耗 | ~15-20次 LLM调用 |
| 耗时 | 15-25秒 |
| Leader | ❌ 无 |
| 风险管理 | ✅ 独立风险辩论 |

---

### 6.2 模式 B: ai-hedge-fund (完全对标)

### 架构 (基于 ai-hedge-fund 源码)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    4层架构 (ai-hedge-fund)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 4: 投资组合经理 (Portfolio Manager)                           │
│  - 整合所有信号                                                     │
│  - 最终交易决策                                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 3: 风险管理 (Risk Manager)                                   │
│  - 仓位控制 (波动率调整)                                             │
│  - 回撤保护                                                         │
│  - 动态调仓                                                         │
│  - 风险评级                                                         │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 2: 19位分析师 (可选择部分运行)                                │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐               │
│  │Warren   │ Ben     │ Cathie  │ Peter   │ Stanley │               │
│  │Buffett  │ Graham  │ Wood    │ Lynch   │ Druck.  │               │
│  ├─────────┼─────────┼─────────┼─────────┼─────────┤               │
│  │Charlie  │ Michael │ Nassim  │ Bill    │ Stanley │               │
│  │Munger   │ Burry   │ Taleb   │ Ackman  │ Druck.  │               │
│  ├─────────┼─────────┼─────────┼─────────┼─────────┤               │
│  │Fundam.  │ Techni. │Sentim.  │Valuat.  │ Growth  │               │
│  │Analyst  │ Analyst │ Analyst │ Analyst │ Analyst │               │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘               │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: 数据层 (AKShare + 模拟财务数据)                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 核心实现 (100%基于 ai-hedge-fund/src/ 源码)

#### 1. ANALYST_CONFIG 配置 (src/utils/analysts.py)

```python
# 基于 ai-hedge-fund/src/utils/analysts.py
ANALYST_CONFIG = {
    "warren_buffett": {
        "display_name": "Warren Buffett",
        "description": "The Oracle of Omaha",
        "investing_style": "Seeks companies with strong fundamentals and competitive advantages through value investing and long-term ownership.",
        "agent_func": warren_buffett_agent,  # 来自 src/agents/warren_buffett.py
        "type": "analyst",
        "order": 12,
    },
    "ben_graham": {
        "display_name": "Ben Graham",
        "description": "The Father of Value Investing",
        "investing_style": "Emphasizes a margin of safety and invests in undervalued companies with strong fundamentals.",
        "agent_func": ben_graham_agent,
        "type": "analyst",
        "order": 1,
    },
    # ... 19位分析师完整配置
    "fundamentals_analyst": {
        "display_name": "Fundamentals Analyst",
        "description": "Financial Statement Specialist",
        "agent_func": fundamentals_analyst_agent,
        "type": "analyst",
        "order": 14,
    },
    # ... 更多分析师
}

# 获取分析师节点映射 - 关键方法
def get_analyst_nodes():
    return {key: (f"{key}_agent", config["agent_func"]) 
            for key, config in ANALYST_CONFIG.items()}
```

#### 2. AgentState 定义 (src/graph/state.py)

```python
# 基于 ai-hedge-fund/src/graph/state.py
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # 消息历史(累积)
    data: Annotated[dict[str, any], merge_dicts]              # 数据+分析师信号
    metadata: Annotated[dict[str, any], merge_dicts]         # 元数据(模型选择等)

def show_agent_reasoning(output, agent_name):
    """打印agent推理过程用于调试"""
    print(f"\n{'=' * 10} {agent_name.center(28)} {'=' * 10}")
    # JSON格式化输出
```

#### 3. Warren Buffett Agent 完整实现 (src/agents/warren_buffett.py)

```python
# 基于 ai-hedge-fund/src/agents/warren_buffett.py

class WarrenBuffettSignal(BaseModel):
    signal: Literal["bullish", "bearish", "neutral"]
    confidence: int  # 0-100
    reasoning: str

def warren_buffett_agent(state: AgentState, agent_id: str = "warren_buffett_agent"):
    """
    使用巴菲特原则分析股票
    
    分析维度(7个):
    1. analyze_fundamentals - ROE、负债、利润率、流动性
    2. analyze_consistency - 盈利一致性和增长
    3. analyze_moat - 护城河分析 (ROE稳定性、定价权、规模优势)
    4. analyze_management_quality - 管理层质量 (股票回购、分红)
    5. analyze_pricing_power - 定价能力分析
    6. analyze_book_value_growth - 每股净资产增长
    7. calculate_intrinsic_value - DCF内在价值计算
    
    核心算法:
    - margin_of_safety = (intrinsic_value - market_cap) / market_cap
    - signal: bullish if strong business AND margin_of_safety > 0
    """
    
    # Step 1: 获取财务指标
    metrics = get_financial_metrics(ticker, end_date, period="ttm", limit=10)
    
    # Step 2: 获取财务明细
    financial_line_items = search_line_items(ticker, [...], end_date)
    
    # Step 3: 获取市值
    market_cap = get_market_cap(ticker, end_date)
    
    # Step 4: 执行7维度分析
    fundamental_analysis = analyze_fundamentals(metrics)
    moat_analysis = analyze_moat(metrics)
    intrinsic_value_analysis = calculate_intrinsic_value(financial_line_items)
    
    # Step 5: 计算安全边际
    margin_of_safety = (intrinsic_value - market_cap) / market_cap
    
    # Step 6: LLM生成最终决策 (使用ChatPromptTemplate)
    buffett_output = generate_buffett_output(analysis_data, state)
    
    # Step 7: 添加到分析师信号
    state["data"]["analyst_signals"][agent_id] = buffett_analysis
    
    return {"messages": [message], "data": state["data"]}
```

#### 4. 工作流创建 (src/main.py)

```python
# 基于 ai-hedge-fund/src/main.py

def create_workflow(selected_analysts=None):
    """
    创建ai-hedge-fund工作流
    
    架构:
    start_node → [选择的分析师们] → risk_management → portfolio_manager → END
    
    关键点:
    - 所有分析师并行运行
    - 分析师结果汇聚到risk_management
    - risk_management结果到portfolio_manager
    """
    workflow = StateGraph(AgentState)
    workflow.add_node("start_node", start)
    
    # 获取分析师节点
    analyst_nodes = get_analyst_nodes()
    
    # 默认运行所有分析师
    if selected_analysts is None:
        selected_analysts = list(analyst_nodes.keys())
    
    # 添加选定的分析师节点
    for analyst_key in selected_analysts:
        node_name, node_func = analyst_nodes[analyst_key]
        workflow.add_node(node_name, node_func)
        workflow.add_edge("start_node", node_name)
    
    # 添加风险管理
    workflow.add_node("risk_management_agent", risk_management_agent)
    workflow.add_node("portfolio_manager", portfolio_management_agent)
    
    # 连接所有分析师到风险管理
    for analyst_key in selected_analysts:
        node_name = analyst_nodes[analyst_key][0]
        workflow.add_edge(node_name, "risk_management_agent")
    
    workflow.add_edge("risk_management_agent", "portfolio_manager")
    workflow.add_edge("portfolio_manager", END)
    
    return workflow

def run_hedge_fund(tickers, start_date, end_date, portfolio, 
                   selected_analysts=None, model_name="gpt-4.1"):
    """运行对冲基金工作流"""
    workflow = create_workflow(selected_analysts)
    agent = workflow.compile()
    
    final_state = agent.invoke({
        "messages": [HumanMessage(content="Make trading decisions...")],
        "data": {
            "tickers": tickers,
            "portfolio": portfolio,
            "start_date": start_date,
            "end_date": end_date,
            "analyst_signals": {},  # 空的，由各agent填充
        },
        "metadata": {
            "show_reasoning": show_reasoning,
            "model_name": model_name,
        },
    })
    
    return {
        "decisions": parse_hedge_fund_response(final_state["messages"][-1].content),
        "analyst_signals": final_state["data"]["analyst_signals"],
    }
```

#### 5. Risk Manager 完整实现 (src/agents/risk_manager.py)

```python
# 基于 ai-hedge-fund/src/agents/risk_manager.py

def risk_management_agent(state: AgentState, agent_id: str = "risk_management_agent"):
    """
    基于波动率的风险管理
    
    核心算法:
    1. calculate_volatility_metrics - 计算波动率指标
    2. calculate_volatility_adjusted_limit - 基于波动率调整仓位
    3. calculate_correlation_multiplier - 相关性调整
    
    输出: 每个ticker的剩余仓位限制
    """
    
    for ticker in tickers:
        # Step 1: 获取历史价格数据
        prices = get_prices(ticker, start_date, end_date)
        prices_df = prices_to_df(prices)
        
        # Step 2: 计算波动率
        volatility_metrics = calculate_volatility_metrics(prices_df)
        # 返回: daily_volatility, annualized_volatility, volatility_percentile
        
        # Step 3: 基于波动率计算仓位限制
        # 低波动(<15%): 25%仓位
        # 中波动(15-30%): 15-20%仓位
        # 高波动(>30%): 10-15%仓位
        # 极高波动(>50%): 最大10%仓位
        vol_adjusted_limit_pct = calculate_volatility_adjusted_limit(
            volatility["annualized_volatility"]
        )
        
        # Step 4: 相关性调整
        if correlation_matrix is not None:
            corr_multiplier = calculate_correlation_multiplier(avg_correlation)
        
        # Step 5: 组合调整
        combined_limit_pct = vol_adjusted_limit_pct * corr_multiplier
        position_limit = total_portfolio_value * combined_limit_pct
        
        risk_analysis[ticker] = {
            "remaining_position_limit": position_limit - current_position_value,
            "volatility_metrics": {...},
            "correlation_metrics": {...},
            "reasoning": {...},
        }
```

#### 6. Portfolio Manager 实现 (src/agents/portfolio_manager.py)

```python
# 基于 ai-hedge-fund/src/agents/portfolio_manager.py

def portfolio_management_agent(state: AgentState, agent_id: str = "portfolio_manager"):
    """
    投资组合经理 - 最终决策
    
    综合所有分析师信号和风险管理结果
    输出最终交易决策
    """
    
    # 获取所有分析师信号
    analyst_signals = state["data"]["analyst_signals"]
    
    # 获取风险分析
    risk_analysis = state["data"].get("risk_analysis", {})
    
    # 综合决策...
    return {
        "messages": [HumanMessage(content=json.dumps(decisions))],
        "data": state["data"],
    }
```

### 19位分析师完整配置表

| ID | 显示名 | Order | 类型 | 投资风格 |
|----|--------|-------|------|---------|
| aswath_damodaran | Aswath Damodaran | 0 | Leader | 估值专家 |
| ben_graham | Ben Graham | 1 | Leader | 深度价值、安全边际 |
| bill_ackman | Bill Ackman | 2 | Leader | 激进投资、公司改造 |
| cathie_wood | Cathie Wood | 3 | Leader | 颠覆性创新 |
| charlie_munger | Charlie Munger | 4 | Leader | 理性思维、优质企业 |
| michael_burry | Michael Burry | 5 | Leader | 逆向投资、Big Short |
| mohnish_pabrai | Mohnish Pabrai | 6 | Leader | Dhandho投资 |
| nassim_taleb | Nassim Taleb | 7 | Leader | 尾部风险、反脆弱 |
| peter_lynch | Peter Lynch | 8 | Leader | 成长投资、10倍股 |
| phil_fisher | Phil Fisher | 9 | Leader | 闲聊法、长期成长 |
| rakesh_jhunjhunwala | Rakesh Jhunjhunwala | 10 | Leader | 新兴市场 |
| stanley_druckenmiller | Stanley Druckenmiller | 11 | Leader | 宏观交易 |
| warren_buffett | Warren Buffett | 12 | Leader | 价值投资、长期持有 |
| technical_analyst | Technical Analyst | 13 | 功能 | 图表形态分析 |
| fundamentals_analyst | Fundamentals Analyst | 14 | 功能 | 财务报表分析 |
| growth_analyst | Growth Analyst | 15 | 功能 | 成长趋势分析 |
| news_sentiment_analyst | News Sentiment Analyst | 16 | 功能 | 新闻情感分析 |
| sentiment_analyst | Sentiment Analyst | 17 | 功能 | 市场情绪分析 |
| valuation_analyst | Valuation Analyst | 18 | 功能 | 公司估值 |

### FinancePulse 实现差异

| 组件 | ai-hedge-fund 原版 | FinancePulse 实现 | 说明 |
|------|------------------|-------------------|------|
| 数据源 | Financial Datasets API | AKShare + 模拟 | A股支持 |
| 分析师选择 | 全部或指定 | 可选运行部分 | 灵活性 |
| 护城河分析 | 完整DCF | 简化版 | 适应A股数据 |
| 波动率计算 | 真实历史数据 | 简化估算 | 兼容A股 |
| 仓位管理 | 基于波动率 | 固定+调整 | 简化实现 |

### 性能指标

| 指标 | 数值 |
|------|------|
| Token消耗 | 12-18次 LLM调用 |
| 耗时 | 15-25秒 |
| 分析师 | ✅ 19位可选 |
| 风险管理 | ✅ 波动率调整 (完整版) |

### 输出数据结构

```python
# 基于 ai-hedge-fund/src/utils/display.py
{
    "decisions": {
        "600519": {
            "action": "buy" | "sell" | "hold",
            "confidence": 0-100,
            "reasoning": "基于巴菲特原则...",
            "position_size": 0-100,
            "stop_loss": price
        }
    },
    "analyst_signals": {
        "warren_buffett_agent": {"signal": "bullish", "confidence": 85, "reasoning": "..."},
        "fundamentals_analyst": {...},
        # ... 每个agent的信号
    }
}
```

---

### 6.3 模式 C: 融合模式

#### 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Leader (19选1)                          │
│         - 定义分析重点 - 审核辩论结果 - 最终决策拍板          │
├─────────────────────────────────────────────────────────────┤
│                    5 Analysts (并行)                        │
│  Bull / Bear / Technical / Fundamental / Sentiment         │
├─────────────────────────────────────────────────────────────┤
│                    Bull/Bear Debate                         │
│              (可循环直到收敛或达到最大轮次)                   │
├─────────────────────────────────────────────────────────────┤
│                    Risk Agent (简化版)                      │
│              LLM Agent - 风险评估/调整建议                 │
├─────────────────────────────────────────────────────────────┤
│                    Leader 最终决策                           │
│         - 置信度调整 (±15%) - 微调action                  │
└─────────────────────────────────────────────────────────────┘
```

#### Leader决策权限

```python
LEADER_DECISION_RULES = {
    "max_confidence_adjust": 15,    # 置信度最多±15%
    "can_adjust_action": True,     # 可以微调 action
    "can_reverse": False,          # 不能完全推翻
    "min_bull_to_buy": 60,       # 最低多头置信度要求
    "min_bear_to_sell": 60,      # 最低空头置信度要求
    "must_explain": True,         # 必须说明调整原因
    "must_show_risk": True,       # 必须显示风险检查结果
}
```

#### 执行流程

```python
async def fusion_workflow(code: str, leader_id: str, llm_service: LLMService) -> dict:
    """
    融合模式工作流
    """
    # Step 1: Leader定义分析重点
    leader = get_leader(leader_id)
    stock_data = await data_service.get_stock_data(code)
    focus = await leader.define_focus(stock_data)
    
    # Step 2: 5分析师并行
    analyst_tasks = [
        run_bull_researcher(stock_data, llm_service),
        run_bear_researcher(stock_data, llm_service),
        run_technical_analyst(stock_data, llm_service),
        run_fundamental_analyst(stock_data, llm_service),
        run_sentiment_analyst(stock_data, llm_service),
    ]
    analyst_results = await asyncio.gather(*analyst_tasks)
    
    # Step 3: Bull/Bear辩论 (可循环)
    debate_result = await bull_bear_debate(analyst_results, llm_service)
    
    # Step 4: Leader审核辩论结果
    leader_review = await leader.review_debate(debate_result, analyst_results)
    
    # Step 5: 综合分析
    synthesis = await synthesize(analyst_results, debate_result, llm_service)
    
    # Step 6: Risk Agent评估 (简化版)
    risk_result = await risk_agent.evaluate(synthesis, stock_data)
    
    # Step 7: Leader最终决策
    final_decision = await leader.final_decision(
        synthesis=synthesis,
        risk_result=risk_result,
        leader_review=leader_review
    )
    
    return final_decision
```

#### 性能指标

| 指标 | 数值 |
|------|------|
| Token消耗 | 12-15次 LLM调用 |
| 耗时 | 15-22秒 |
| Leader | ✅ 19选1，决策层 |
| 风险管理 | ✅ Risk Agent简化版 |

---

## 7. 输出结果设计

### 7.1 输出内容

```typescript
interface AnalysisOutput {
    // 基础信息
    code: string;
    name: string;
    mode: string;
    timestamp: number;
    duration_ms: number;
    
    // 分析师信号
    signals: Array<{
        agent: string;
        agent_id: string;
        signal: "bullish" | "bearish" | "neutral";
        confidence: number;
        reasoning: string;
    }>;
    
    // 辩论/讨论结果
    debate_result?: {
        round: number;
        bullish: { confidence: number; reasoning: string };
        bearish: { confidence: number; reasoning: string };
        consensus_reached: boolean;
    };
    
    // 综合分析
    summary: string;
    
    // 投资建议
    recommendation: {
        action: "buy" | "hold" | "sell" | "watch";
        confidence: number;
        timeframe: string;
        entry_price?: number;
        exit_price?: number;
        stop_loss?: number;
        position_size?: number;
        risks: string[];
    };
    
    // Leader信息 (模式B/C)
    leader?: {
        id: string;
        name: string;
        style: string;
    };
    
    // 风险评估
    risk_assessment?: {
        level: "low" | "medium" | "high";
        warnings: string[];
        adjustments?: {
            position_size?: number;
            stop_loss?: number;
        };
    };
    
    // 分层输出 (模式B专有)
    layers?: {
        layer1_data: object;
        layer2_strategy: object;
        layer3_risk: object;
        layer4_decision: object;
    };
    
    // 元信息
    tokens_used: number;
    error?: string;
}
```

---

## 8. API 设计

### 8.1 POST /analyze

```typescript
// Request
{
    code: string;
    name?: string;
    mode: "tradingagents" | "aihedgefund" | "fusion";
    leader_id?: string;  // 模式B/C必需
    max_iterations?: number;
    convergence_gap?: number;
    early_stop_gap?: number;
    risk_level?: "conservative" | "moderate" | "aggressive";
}

// Response: AnalysisOutput
```

### 8.2 GET /api/leaders

```typescript
// Response
{
    leaders: [
        {
            id: string;
            name: string;
            style: string;
            avatar: string;
            description: string;
        }
    ]
}
```

### 8.3 GET /api/config/convergence

```typescript
// Response
{
    presets: {
        quick: { max_iterations: 1, convergence_gap: 20, early_stop_gap: 15 },
        standard: { max_iterations: 3, convergence_gap: 15, early_stop_gap: 10 },
        deep: { max_iterations: 5, convergence_gap: 10, early_stop_gap: 5 }
    }
}
```

### 8.4 GET /api/config/risk-levels

```typescript
// Response
{
    risk_levels: RISK_PREFERENCES
}
```

---

## 9. 实现规范

### 9.1 必须遵循的原则

| 原则 | 说明 |
|------|------|
| **使用原仓库工具栈** | 参考的仓库用什么技术，就用什么技术 |
| **禁止写伪代码** | 所有实现必须是可运行的代码 |
| **保持一致性** | 新功能必须与现有架构兼容 |

### 9.2 参考项目

- **TradingAgents**: `~/FinancePulse_reference/TradingAgents/`
- **ai-hedge-fund**: `~/FinancePulse_reference/ai-hedge-fund/`

### 9.3 工具栈 (不可替换)

| 工具 | 版本要求 | 用途 | 来源 |
|------|----------|------|------|
| **LangGraph** | ≥0.2.0 | 工作流编排/状态管理/循环控制 | TradingAgents |
| **LangChain** | ≥0.3.0 | LLM 调用封装 | ai-hedge-fund |
| **FastAPI** | ≥0.115.0 | API 服务框架 | 项目自选 |
| **httpx** | ≥0.27.0 | 异步 HTTP 请求 | 项目自选 |
| **akshare** | ≥1.18.0 | 金融数据采集 | 项目自选 |
| **pydantic** | ≥2.8.0 | 数据模型验证 | 项目自选 |

---

## 10. 文件结构

```
server/
├── agents/
│   ├── __init__.py
│   ├── analyst.py           # 基础分析师
│   ├── market.py            # 市场分析师 (新增)
│   ├── social.py            # 社交分析师 (新增)
│   ├── news.py              # 新闻分析师 (已有数据)
│   ├── fundamentals.py       # 基本面分析师
│   ├── bull.py              # 多头研究员
│   ├── bear.py              # 空头研究员
│   ├── technical.py          # 技术分析师
│   ├── sentiment.py         # 情绪分析师
│   ├── valuation.py         # 估值分析师 (新增)
│   ├── trader.py            # 交易员 (新增)
│   ├── risk.py              # 风险分析师
│   ├── risk_debate.py      # 风险辩论 (新增)
│   ├── risk_manager.py      # 风险管理器 (ai-hedge-fund风格)
│   ├── portfolio.py          # 组合经理 (新增)
│   ├── debate.py            # 多空辩论
│   ├── synthesizer.py        # 综合分析
│   ├── decision.py          # 决策
│   └── leaders/
│       ├── __init__.py
│       ├── base.py           # Leader基类
│       ├── warren_buffett.py
│       ├── ben_graham.py
│       └── ...              # 其他19位大师
│
├── graph/
│   ├── __init__.py
│   ├── state.py             # AgentState定义
│   ├── workflow.py          # 模式A基础工作流
│   ├── tradingagents_workflow.py  # 模式A完整8阶段
│   ├── aihedgefund_workflow.py   # 模式B 4层架构
│   └── fusion_workflow.py        # 模式C融合模式
│
├── config/
│   ├── __init__.py
│   ├── leaders.py           # 19位大师配置
│   ├── convergence.py       # 收敛参数配置
│   ├── risk.py             # 风险偏好配置
│   └── analysts.py         # 分析师配置
│
├── services/
│   ├── llm.py              # LLM服务
│   └── data.py             # 数据服务
│
└── main.py                 # FastAPI入口
```

---

## 11. TODO 清单

### 11.1 P0 必须实现

#### P0.1 补全8阶段工作流 (TradingAgents模式)

| 任务 | 文件 | 说明 |
|------|------|------|
| 市场分析师 | agents/market.py | 市场概览和趋势 |
| 社交分析师 | agents/social.py | 社交媒体情绪 |
| 新闻分析师 | agents/news.py | 新闻事件分析 |
| 交易员提案 | agents/trader.py | 交易提案生成 |
| 风险辩论 | agents/risk_debate.py | 三种风险偏好辩论 |
| 组合经理 | agents/portfolio.py | 最终投资决策 |
| 8阶段工作流 | graph/tradingagents_workflow.py | 完整工作流 |

#### P0.2 Leader机制 (ai-hedge-fund模式)

| 任务 | 文件 | 说明 |
|------|------|------|
| Leader基类 | agents/leaders/base.py | Leader抽象基类 |
| 14位大师实现 | agents/leaders/*.py | 各自投资哲学 |
| Leader动态选择 | config/leaders.py | 根据风格选分析师 |
| 4层工作流 | graph/aihedgefund_workflow.py | Layer1-4实现 |

#### P0.3 前端分析参数组件

| 任务 | 文件 | 说明 |
|------|------|------|
| AnalysisParams | src/components/analysis/AnalysisParams.tsx | 参数选择面板 |
| SignalPanel | src/components/analysis/SignalPanel.tsx | 5分析师信号 |
| RecommendationCard | src/components/analysis/RecommendationCard.tsx | 投资建议 |

### 11.2 P1 重要功能

| 任务 | 说明 |
|------|------|
| Memory机制 | bull/bear/trader上下文记忆 |
| 双层LLM | deep_thinking + quick_thinking |
| 舆情分析 | 新闻情感评分 |
| 资金流向 | 北向/融资融券数据 |

### 11.3 P2 增强功能

| 任务 | 说明 |
|------|------|
| A-share规则 | T+1等规则验证 |
| 回测支持 | 绩效评估 |

---

## 12. 三模式对比总结

### 12.1 功能对比

| 维度 | 模式A | 模式B | 模式C |
|------|:-----:|:-----:|:-----:|
| 架构 | 8阶段 | 4层 | 5分析师+Leader |
| Leader | ❌ | ✅ 14位全程 | ✅ 19位决策 |
| 分析师 | 9个固定 | 动态选择 | 5个固定 |
| Bull/Bear辩论 | ✅ | ❌ | ✅ |
| 风险辩论 | ✅ 三层 | ✅ | ⚠️ 简化版 |
| 复杂度 | 高 | 中 | 中 |

### 12.2 场景推荐

| 场景 | 推荐 |
|------|:-----:|
| 短线/题材 | A |
| 快速信号 | A |
| 蓝筹/长线 | B/C |
| 复杂决策 | B |
| 机构级 | B |

---

*文档版本: v3.0 | 2026-04-26 | 基于TradingAgents和ai-hedge-fund参考实现*

---

## 12. 前端展示设计

### 12.1 分析页面布局

```
┌─────────────────────────────────────────────────────────────────────┐
│  AI 分析师                                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ StockHeader: 股票搜索 + 基本行情                              │  │
│  │ 股票: [贵州茅台600519]  ¥1458.49  +2.78%  PE:28.5  成交:80亿│  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌────────────────────────────┐  ┌────────────────────────────┐  │
│  │ KlineChart: K线图表         │  │ FundFlowPanel: 资金流向    │  │
│  │                            │  │                            │  │
│  │  [日/周/月] 切换          │  │ 北向资金: +23亿 ▲        │  │
│  │                            │  │ 融资余额: 156亿           │  │
│  │  ┌────────────────────┐   │  │ 主力净流入: +5.2亿        │  │
│  │  │    K线图表       │   │  │                            │  │
│  │  │   (Recharts)     │   │  │  [流向图表]               │  │
│  │  └────────────────────┘   │  │                            │  │
│  └────────────────────────────┘  └────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ AnalysisParams: 参数设置面板                                   │  │
│  │                                                              │  │
│  │ 模式: [●TradingAgents] [○ai-hedge-fund] [○Fusion]         │  │
│  │                                                              │  │
│  │ 大师: [🎯沃伦·巴菲特 ▼]  (ai-hedge/fusion模式显示)        │  │
│  │                                                              │  │
│  │ 收敛: [●快速1轮] [○标准3轮] [○深度5轮]                    │  │
│  │                                                              │  │
│  │ 风险: [○保守] [●平衡] [○激进]                              │  │
│  │                                                              │  │
│  │                                           [开始分析]           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SignalPanel: 多维度分析                                       │  │
│  │                                                              │  │
│  │  📈 Bull Researcher    78%  ████████████████░░░         │  │
│  │  📉 Bear Researcher    65%  █████████████░░░░░░         │  │
│  │  📊 Technical Analyst   72%  ███████████████░░░░         │  │
│  │  💼 Fundamental         75%  ████████████████░░         │  │
│  │  🌊 Sentiment           58%  ███████████░░░░░░         │  │
│  │                                                              │  │
│  │  辩论: Bull 78% vs Bear 65%  差距13%  → 收敛 ✅        │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ RecommendationCard: 投资建议                                   │  │
│  │                                                              │  │
│  │  行动: [持有]   置信度: [72%]   周期: [中线1月]         │  │
│  │  仓位: [30%]    止损: [¥1380]  目标: [¥1550]          │  │
│  │                                                              │  │
│  │  ⚠️ 风险: PE偏高(28.5) | 波动风险(+2.78%)              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 12.2 组件结构

```typescript
interface AnalysisPage {
  components: {
    StockHeader: { /* 股票搜索 + 基本行情 */ };
    KlineChart: { /* K线图表 (Recharts) */ };
    FundFlowPanel: { /* 北向资金、融资融券、主力净流入 */ };
    AnalysisParams: { /* 模式/大师/风险参数设置 */ };
    SignalPanel: { /* 5分析师信号可视化 */ };
    RecommendationCard: { /* 投资建议展示 */ };
    SummaryText: { /* 分析总结 */ };
  }
}
```

### 12.3 数据需求

| 组件 | 数据 | 来源 | 状态 |
|------|------|------|------|
| StockHeader | price, change, pe, volume | /api/quotes | ✅ |
| KlineChart | ohlc, volume | /api/kline | ✅ |
| FundFlowPanel | northbound, margin, main_flow | 需新增API | ⚠️ |
| SignalPanel | signals[] | /analyze | ✅ |
| RecommendationCard | recommendation | /analyze | ✅ |
| SummaryText | summary | /analyze | ✅ |

---

## 13. 首页优化设计

### 13.1 当前问题

| 问题 | 说明 |
|------|------|
| 80%数据硬编码 | 恐惧贪婪、北向资金等都是静态数据 |
| 无实时连接 | API已实现但未连接前端 |
| 图表用静态数据 | Recharts组件没有真实数据 |

### 13.2 优化后的首页布局

```
┌─────────────────────────────────────────────────────────────────────┐
│  DashboardHome: 首页                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 市场状态栏 (实时数据)                                         │    │
│  │ A股修复期 | 恐惧贪婪: 26 | 北向: +23亿                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│  │   📊     │ │   📈     │ │   🎯     │ │   🔮     │      │
│  │  A股行情  │ │  宏观数据  │ │  仓位管理  │ │  预测市场  │      │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘      │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 关键指标 (实时数据 + 图表)                                   │    │
│  │  恐惧贪婪指数 | 仓位建议 | 北向资金 | 市场情绪             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 我的关注 (实时行情 + 一键跳转分析)                             │    │
│  │  🎯贵州茅台 | 🎯五粮液 | 🎯宁德时代 | +添加                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 今日资讯 (爬虫/新闻API)                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 14. A股情绪页优化设计

### 14.1 优化后的布局

```
┌─────────────────────────────────────────────────────────────────────┐
│  AStockSentiment: A股市场情绪                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 恐惧贪婪指数 (实时)  [━━━━━━━━━━●━━━━━━━━━━━━] 26 极度恐惧│    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 量化信号面板 (实时数据)                                       │    │
│  │  涨停47 | 跌停8 | 成交7821亿 | 北向+23亿                    │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 北向资金趋势 (7日实时图表)                                   │    │
│  │  7日累计净买入: +127亿                                      │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 融资融券余额 (实时)                                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ 板块资金流向 (实时)                                          │    │
│  │  🟢 AI算力 +28亿 | 🟢 半导体设备 +15亿                    │    │
│  │  🔴 房地产 -8亿 | 🔴 银行 -3亿                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 15. 新增数据API需求

### 15.1 数据API汇总

| API | 用途 | 来源 | 状态 |
|-----|------|------|------|
| `/api/quotes` | 股票行情 | 新浪/东财 | ✅ 已实现 |
| `/api/kline` | K线数据 | 东财 | ✅ 已实现 |
| `/api/fundflow/{code}` | 资金流向 | 东财 | ⚠️ 需新增 |
| `/api/market/fear-greed` | 恐惧贪婪 | 需API | ⚠️ 需新增 |
| `/api/market/quant-signals` | 量化信号 | 东财/聚宽 | ⚠️ 需新增 |
| `/api/market/northbound` | 北向资金 | 东财 | ⚠️ 需新增 |
| `/api/news` | 资讯新闻 | 爬虫/新闻API | ⚠️ 需新增 |

### 15.2 新增API设计

```typescript
// GET /api/market/northbound
Response: {
    daily: number;          // 当日净买入(亿)
    weekly: Array<{ date: string; value: number }>;  // 近7日数据
    monthly: number;         // 本月累计(亿)
}

// GET /api/margin/{code}
Response: {
    margin_balance: number;   // 融资余额(亿)
    margin_change: number;    // 融资变化(亿)
    short_balance: number;    // 融券余额(亿)
    short_change: number;    // 融券变化(亿)
}

// GET /api/sector/flow
Response: {
    sectors: Array<{
        name: string;
        flow: number;
        change: number;
    }>;
}

// GET /api/news
Response: {
    items: Array<{
        category: string;
        title: string;
        source: string;
        time: string;
    }>;
}
```

---

## 16. 实现规范

### 16.1 必须遵循的原则

| 原则 | 说明 |
|------|------|
| **使用原仓库工具栈** | 参考的仓库用什么技术，就用什么技术 |
| **禁止写伪代码** | 所有实现必须是可运行的代码 |
| **保持一致性** | 新功能必须与现有架构兼容 |

### 16.2 参考项目

- **TradingAgents**: `~/FinancePulse_reference/TradingAgents/`
- **ai-hedge-fund**: `~/FinancePulse_reference/ai-hedge-fund/`

### 16.3 工具栈 (不可替换)

| 工具 | 版本要求 | 用途 | 来源 |
|------|----------|------|------|
| **LangGraph** | ≥0.2.0 | 工作流编排/状态管理/循环控制 | TradingAgents |
| **LangChain** | ≥0.3.0 | LLM 调用封装 | ai-hedge-fund |
| **FastAPI** | ≥0.115.0 | API 服务框架 | 项目自选 |
| **httpx** | ≥0.27.0 | 异步 HTTP 请求 | 项目自选 |
| **akshare** | ≥1.18.0 | 金融数据采集 | 项目自选 |
| **pydantic** | ≥2.8.0 | 数据模型验证 | 项目自选 |

### 16.4 禁止事项

```
❌ 禁止在代码中写伪代码或 TODO 注释
❌ 禁止使用未在依赖列表中的工具
❌ 禁止跳过错误处理
❌ 禁止硬编码测试数据在生产代码中
```

---

## 17. TODO 清单

### 17.1 P0 必须实现

#### P0.1 补全8阶段工作流 (TradingAgents模式)

| 任务 | 文件 | 说明 |
|------|------|------|
| 市场分析师 | agents/tradingagents/researchers/market.py | 市场概览和趋势 |
| 社交分析师 | agents/tradingagents/researchers/social.py | 社交媒体情绪 |
| 新闻分析师 | agents/tradingagents/researchers/news.py | 新闻事件分析 |
| 交易员提案 | agents/tradingagents/managers/trader.py | 交易提案生成 |
| 风险辩论 | agents/tradingagents/risk_debate.py | 三种风险偏好辩论 |
| 组合经理 | agents/tradingagents/managers/portfolio_manager.py | 最终投资决策 |
| 8阶段工作流 | graph/tradingagents_workflow.py | 完整工作流 |

#### P0.2 Leader机制 (ai-hedge-fund模式)

| 任务 | 文件 | 说明 |
|------|------|------|
| Leader基类 | agents/leaders/base.py | Leader抽象基类 |
| 14位大师实现 | agents/leaders/*.py | 各自投资哲学 |
| Leader动态选择 | config/leaders.py | 根据风格选分析师 |
| 4层工作流 | graph/aihedgefund_workflow.py | Layer1-4实现 |

#### P0.3 前端分析参数组件

| 任务 | 文件 | 说明 |
|------|------|------|
| AnalysisParams | src/components/analysis/AnalysisParams.tsx | 参数选择面板 |
| SignalPanel | src/components/analysis/SignalPanel.tsx | 5分析师信号 |
| RecommendationCard | src/components/analysis/RecommendationCard.tsx | 投资建议 |

### 17.2 P1 重要功能

| 任务 | 说明 |
|------|------|
| Memory机制 | bull/bear/trader上下文记忆 |
| 双层LLM | deep_thinking + quick_thinking |
| 舆情分析 | 新闻情感评分 |
| 资金流向 | 北向/融资融券数据 |

### 17.3 P2 增强功能

| 任务 | 说明 |
|------|------|
| A-share规则 | T+1等规则验证 |
| 回测支持 | 绩效评估 |

### 17.4 已完成 ✅

- [x] 三种模式设计 (TradingAgents / ai-hedge-fund / Fusion)
- [x] 19位投资大师配置
- [x] 用户可配置参数 (模式/大师/风险/收敛)
- [x] 输出结果设计
- [x] 前端展示设计 (首页/分析页/情绪页)
- [x] 收敛参数用户选择设计
- [x] PRD文档结构完善

---

## 18. 待确认项

### 18.1 已确认 ✅

- [x] 三种模式设计 (TradingAgents / ai-hedge-fund / Fusion)
- [x] 19位投资大师配置
- [x] 用户可配置参数 (模式/大师/风险/收敛)
- [x] 输出结果设计
- [x] 前端展示设计 (首页/分析页/情绪页)
- [x] 数据增强需求
- [x] 收敛参数用户选择设计

### 18.2 待讨论 ❌

- [ ] 默认模式选择 (TradingAgents / ai-hedge-fund / Fusion)
- [ ] 默认大师选择 (19位大师中选哪位)
- [ ] 数据增强优先级 (P0/P1/P2)

---

*文档版本: v3.1 | 2026-04-26 | 完整包含前端设计、首页优化、情绪页设计*

