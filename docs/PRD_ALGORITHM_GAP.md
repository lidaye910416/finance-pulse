# FinancePulse 算法差距弥合 PRD

**版本**: v1.0  
**日期**: 2026-04-26  
**目标**: 弥合与参考仓库 ai-hedge-fund 的算法差距

---

## 1. 背景

当前项目 `ralph/multi-agent-stock-analysis` 的算法实现与参考仓库存在显著差距：

| 项目 | 参考 (ai-hedge-fund) | 当前 | 差距 |
|------|---------------------|------|------|
| Leaders | 19位投资大师 | 1位 | -18位 |
| 数据API | 完整集成 | 无 | 缺失 |
| Risk Manager | 已集成 | 未集成 | 未生效 |

---

## 2. P0 优先级任务

### 2.1 数据服务层 (DataService)

**目标**: 封装 AKShare 获取真实股票数据

```python
# server/services/data_service.py

async def get_stock_data(code: str) -> StockData:
    """获取股票基础数据"""
    # 使用 akshare 获取:
    # - 实时行情 (price, change, volume, etc.)
    # - 财务指标 (PE, PB, market_cap)
    # - 历史K线 (for volatility calculation)
    
async def get_financial_metrics(code: str, period: str = "ttm", limit: int = 10) -> list:
    """获取财务指标时间序列"""
    
async def search_line_items(code: str, items: list, limit: int = 10) -> list:
    """获取财务明细项目"""

async def get_market_cap(code: str, date: str = None) -> float:
    """获取市值"""
```

### 2.2 Leaders 补全 (18位)

**目标**: 实现剩余18位投资大师

| ID | 名称 | 风格 | 核心分析 |
|----|------|------|----------|
| ben_graham | 本杰明·格雷厄姆 | 价值投资 | 安全边际、低估筛选 |
| charlie_munger | 查理·芒格 | 价值投资 | 心理模型、多元思维 |
| peter_lynch | 彼得·林奇 | 成长投资 | 十倍股识别 |
| cathie_wood | 凯西·伍德 | 颠覆性创新 | 未来趋势 |
| michael_burry | 迈克尔·伯里 | 价值发现 | 逆向投资 |
| nassim_taleb | 纳西姆·塔勒布 | 尾部风险 | 黑天鹅防御 |
| bill_ackman | 比尔·阿克曼 | 激进投资 | 催化剂驱动 |
| stanley_druckenmiller | 斯坦利·德鲁肯米勒 | 宏观交易 | 趋势跟踪 |
| aswath_damodaran | 阿斯瓦特·达莫达兰 | 估值专家 | DCF建模 |
| mohnish_pabrai | 莫尼什·帕伯莱 | 深度价值 | 雪球复利 |
| phil_fisher | 菲利普·费雪 | 成长投资 | 15要点 |
| rakesh_jhunjhunwala | 拉克曼·詹姆辛格拉 | 印度股神 | 新兴市场 |
| george_soros | 乔治·索罗斯 | 宏观对冲 | 反身性理论 |
| ray_dalio | 雷·达里奥 | 宏观策略 | 全天候 |
| paul_tudor_jones | 保罗·都铎·琼斯 | 趋势跟踪 | 技术分析 |
| jim_simons | 吉姆·西蒙斯 | 量化投资 | 量化模型 |
| ed_thorp | 爱德华·索普 | 量化对冲 | 概率论 |
| john_bogle | 约翰·博格 | 指数投资 | 低成本指数 |

### 2.3 专用 Analyst Agents

**目标**: 实现专业分析师Agent

| Agent | 文件 | 功能 |
|-------|------|------|
| Technical Analyst | `agents/analysts/technicals.py` | 均线/MACD/KDJ/布林带 |
| Sentiment Analyst | `agents/analysts/sentiment.py` | 市场情绪、舆情分析 |
| Valuation Analyst | `agents/analysts/valuation.py` | DCF/PE/PB估值 |
| Growth Analyst | `agents/analysts/growth_agent.py` | 成长股筛选 |

### 2.4 Risk Manager 集成

**目标**: 将 risk_manager.py 集成到工作流

```python
# 集成到 aihedgefund_workflow.py Layer 3

async def layer3_risk_management(state, llm_service, data_service):
    # 1. 获取波动率数据
    prices = await data_service.get_price_history(code, lookback_days=60)
    volatility = calculate_volatility_metrics(prices)
    
    # 2. 计算波动率调整仓位
    vol_adjusted_limit = calculate_volatility_adjusted_limit(volatility)
    
    # 3. 获取相关性数据
    correlations = await data_service.get_correlations(code)
    corr_multiplier = calculate_correlation_multiplier(correlations)
    
    # 4. 组合调整
    final_position_limit = vol_adjusted_limit * corr_multiplier
    
    return {
        "volatility_metrics": volatility,
        "position_limit": final_position_limit,
        ...
    }
```

### 2.5 Leader 配置映射

**目标**: 实现 leader → analyst 自动映射

```python
# config/leaders.py

STYLE_ANALYST_MAP = {
    "价值投资": ["fundamental", "valuation", "financial"],
    "成长投资": ["growth", "fundamental", "technical"],
    "宏观对冲": ["sentiment", "technical", "financial"],
    "量化投资": ["technical", "sentiment", "valuation"],
    "逆向投资": ["fundamental", "sentiment", "valuation"],
    # ...
}
```

---

## 3. 验收标准

### 3.1 DataService

- [ ] `get_stock_data("600519")` 返回完整行情
- [ ] `get_financial_metrics("600519", limit=10)` 返回10期数据
- [ ] `search_line_items("600519", ["revenue", "net_income"])` 返回财务明细
- [ ] Typecheck passes

### 3.2 Leaders

- [ ] 所有19位 Leaders 可通过 `create_leader(id)` 创建
- [ ] 每位 Leader 有独特的 system_prompt 和分析逻辑
- [ ] Warren Buffett 有7维度量化分析
- [ ] Typecheck passes

### 3.3 Analyst Agents

- [ ] Technical Analyst 输出技术指标
- [ ] Sentiment Analyst 输出情绪评分
- [ ] Typecheck passes

### 3.4 Risk Manager

- [ ] Risk Manager 在 Layer 3 被调用
- [ ] 输出波动率调整后的仓位限制
- [ ] Typecheck passes

### 3.5 集成测试

- [ ] `aihedgefund_workflow` 使用 selected_leader 运行成功
- [ ] 返回包含 leader_analysis 的完整结果
- [ ] Token 消耗在合理范围

---

## 4. 实施顺序

1. **DataService** - 基础数据获取
2. **Leaders 补全** - 18位大师实现
3. **Analyst Agents** - 专用分析师
4. **Risk Manager 集成** - 集成到工作流
5. **Leader 配置** - 风格映射

---

*文档版本: v1.0 | 2026-04-26*
