# AI 多智能体分析系统 PRD

## 1. 当前问题分析

### Ralph Skill 检查结果

**问题 1: 模拟数据而非真实 LLM 调用**
```typescript
// 当前代码 - generateAnalysisResponse()
const mockData = {
  '600519': { name: '贵州茅台', price: 1688.0, change: -1.2, pe: 28.5, marketCap: '2.1万亿' },
  // ...
};
const data = mockData[code] || {
  name: `股票 ${code}`,
  price: Math.random() * 100 + 10,  // ❌ 随机生成数据
  // ...
};
```

**问题 2: 无多智能体编排**
- 只有单一响应函数
- 没有 Agents 协作
- 没有工作流编排

**问题 3: 无数据整合**
- 没有获取实时市场数据
- 没有整合宏观数据
- 没有整合新闻数据

### 参考项目分析

#### AI Hedge Fund 架构
```
src/agents/
├── warren_buffett.py      # 调用 get_financial_metrics()
├── peter_lynch.py        # 调用 search_line_items()
├── Portfolio Manager     # 汇总各 Agent 信号
└── Risk Manager          # 风险评估
```

#### ValueCell 架构
```
- DeepResearch Agent      # 深度研究
- Strategy Agent          # 策略生成
- News Retrieval Agent    # 新闻检索
```

## 2. 目标架构

### 2.1 多智能体编排

```
┌─────────────────────────────────────────────────────────┐
│                    用户输入                              │
│            (股票代码: 600519)                           │
└─────────────────────┬─────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Orchestrator (编排器)                        │
│  • 解析用户意图                                           │
│  • 分发任务给各 Agent                                    │
│  • 汇总结果                                              │
└─────────────────────┬─────────────────────────────────┘
                      │
        ┌───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Fundamental │ │ Technical │ │ Sentiment │ │ Macro   │
   │  Agent    │ │  Agent   │ │  Agent    │ │ Agent   │
   └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
         │             │             │             │
         └─────────────┴──────┬──────┴─────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   LLM (GPT-4)    │
                    │   整合分析       │
                    └────────┬─────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Final Analysis  │
                    │  (投资建议)       │
                    └──────────────────┘
```

### 2.2 核心组件

| 组件 | 功能 | 数据来源 |
|------|------|----------|
| `FundamentalAgent` | 财务分析 | 获取财务指标、估值 |
| `TechnicalAgent` | 技术分析 | K线、均线、RSI |
| `SentimentAgent` | 情绪分析 | 新闻、研报、社交媒体 |
| `MacroAgent` | 宏观分析 | GDP、CPI、LPR |
| `Orchestrator` | 编排协调 | 汇总并调用 LLM |

### 2.3 LLM 集成

```typescript
// 调用 OpenAI/Claude API
interface LLMConfig {
  provider: 'openai' | 'anthropic' | 'deepseek';
  model: string;
  apiKey: string;
}
```

## 3. 实现计划

### Sprint 1: 基础架构
- [ ] 定义 Agent 接口
- [ ] 创建 Orchestrator
- [ ] 实现 LLM 服务封装

### Sprint 2: 数据获取
- [ ] FundamentalAgent - 财务数据获取
- [ ] TechnicalAgent - K线数据获取
- [ ] SentimentAgent - 新闻数据获取

### Sprint 3: 智能分析
- [ ] MacroAgent - 宏观数据整合
- [ ] LLM 提示词工程
- [ ] 分析结果格式化

### Sprint 4: 用户体验
- [ ] 加载状态优化
- [ ] 错误处理
- [ ] 缓存机制

## 4. API 设计

### 4.1 分析请求

```typescript
interface AnalysisRequest {
  code: string;           // 股票/基金代码
  analysts: string[];     // 分析师列表
  includeHistory: boolean; // 包含历史分析
}

interface AnalysisResponse {
  code: string;
  timestamp: number;
  signals: AgentSignal[];      // 各 Agent 信号
  summary: string;            // LLM 总结
  recommendation: {
    action: 'buy' | 'hold' | 'sell';
    confidence: number;
    entryPrice?: number;
    stopLoss?: number;
    timeframe: string;
  };
}
```

### 4.2 Agent 信号

```typescript
interface AgentSignal {
  agent: string;
  signal: 'bullish' | 'bearish' | 'neutral';
  confidence: number;        // 0-100
  reasoning: string;
  data: Record<string, any>; // 原始数据
}
```

## 5. 实现细节

### 5.1 Orchestrator 工作流

```
1. 接收用户请求 (股票代码)
   ↓
2. 并行获取:
   - 财务数据 (FundamentalAgent)
   - K线数据 (TechnicalAgent)  
   - 新闻数据 (SentimentAgent)
   - 宏观数据 (MacroAgent)
   ↓
3. 汇总所有 Agent 信号
   ↓
4. 构建 LLM prompt:
   - 包含各 Agent 分析结果
   - 包含 systemPrompt (分析师风格)
   - 包含格式要求
   ↓
5. 调用 LLM API
   ↓
6. 解析并格式化结果
```

### 5.2 LLM Prompt 示例

```typescript
const buildAnalysisPrompt = (
  analyst: Analyst,
  stockData: StockData,
  agentSignals: AgentSignal[]
) => `
你是${analyst.name}，风格类似${analyst.style}。

你的专长包括: ${analyst.expertise.join(', ')}

当前分析股票: ${stockData.name} (${stockData.code})
基础数据:
- 价格: ¥${stockData.price}
- 涨跌幅: ${stockData.change}%
- 市盈率: ${stockData.pe}
- 市值: ${stockData.marketCap}

各维度分析结果:
${agentSignals.map(s => `- ${s.agent}: ${s.signal} (置信度 ${s.confidence}%)`).join('\n')}

请基于以上数据，从${analyst.style}角度给出分析，包括:
1. 当前估值评估
2. 主要风险因素
3. 投资建议

请用中文回复，格式如下:
[估值评估]
[风险因素]
[投资建议]
`;
```
