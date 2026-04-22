# FinancePulse × TradingAgents/AI-Hedge-Fund 融合 PRD

> 基于 Ralph Skill 方法论：头脑风暴 → 任务分解 → 子任务执行 → 验证检查 → 完成分支
> 
> 更新时间: 2026-04-22

---

## 📋 执行概览

**目标：** 
1. 将 TradingAgents 的多智能体架构 + ai-hedge-fund 的分析师体系融合到 FinancePulse
2. 实现数据自动更新系统，让所有数据都能自动刷新

**融合模式：**
```
TradingAgents      →  工作流架构 (Orchestrator)
ai-hedge-fund      →  分析师 Agent 体系
FinancePulse       →  前端 UI + 数据展示 + 自动更新
```

---

## 🔄 数据自动更新系统设计

### 问题诊断

```
当前问题:
├── 数据只在页面加载时获取一次
├── 没有定时刷新机制
├── 没有后台更新服务
├── 没有数据缓存策略
└── 没有离线支持
```

### 解决方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AutoUpdateService                         │
│  • 管理所有数据的定时更新                                     │
│  • 维护更新队列和优先级                                      │
│  • 处理更新失败和重试                                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ MarketData   │ │ MacroData    │ │ Sentiment    │ │ NewsData     │
│ 实时行情     │ │ 宏观数据     │ │ 情绪数据     │ │ 新闻快讯     │
│ 更新: 3秒   │ │ 更新: 小时   │ │ 更新: 分钟   │ │ 更新: 分钟   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Zustand Store │
                    │ 统一状态管理   │
                    │ 自动触发 UI   │
                    └──────────────┘
```

### 更新策略配置

```typescript
// src/services/autoUpdate/types.ts

export enum UpdatePriority {
  HIGH = 1,      // 实时行情 - 3秒
  NORMAL = 2,    // 情绪数据 - 30秒
  LOW = 3,       // 宏观数据 - 小时
}

export interface UpdateTask {
  id: string;
  name: string;              // 中文名称
  dataType: DataType;        // 数据类型
  priority: UpdatePriority;  // 更新优先级
  interval: number;          // 更新间隔(毫秒)
  fetchFn: () => Promise<any>; // 获取函数
  enabled: boolean;          // 是否启用
  marketHoursOnly: boolean;   // 是否只在交易时段
}

// 更新任务配置表
export const UPDATE_TASKS: UpdateTask[] = [
  // 实时行情 - 高优先级
  {
    id: 'quotes',
    name: '实时行情',
    dataType: DataType.QUOTES,
    priority: UpdatePriority.HIGH,
    interval: 3000,  // 3秒
    fetchFn: fetchQuotes,
    enabled: true,
    marketHoursOnly: true,
  },
  
  // 情绪数据 - 普通优先级
  {
    id: 'fear_greed',
    name: '恐惧贪婪指数',
    dataType: DataType.FEAR_GREED,
    priority: UpdatePriority.NORMAL,
    interval: 30000,  // 30秒
    fetchFn: fetchFearGreedIndex,
    enabled: true,
    marketHoursOnly: false,
  },
  
  // ... 更多任务
];
```

### 后台更新服务

```typescript
// src/services/autoUpdate/AutoUpdateService.ts

class AutoUpdateService {
  private tasks: Map<string, UpdateTask> = new Map();
  private intervals: Map<string, number> = new Map();
  private isRunning: boolean = false;
  
  // 启动服务
  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    
    for (const task of UPDATE_TASKS) {
      this.registerTask(task);
    }
  }
  
  // 注册任务
  registerTask(task: UpdateTask) {
    this.tasks.set(task.id, task);
    
    // 设置定时器
    const timerId = window.setInterval(() => {
      this.executeTask(task);
    }, task.interval);
    
    this.intervals.set(task.id, timerId);
  }
  
  // 执行更新任务
  private async executeTask(task: UpdateTask) {
    // 检查是否应该更新
    if (task.marketHoursOnly && !this.isMarketHours()) {
      return;
    }
    
    try {
      const data = await task.fetchFn();
      this.updateStore(task.dataType, data);
    } catch (error) {
      console.error(`${task.name} 更新失败:`, error);
      // 可以添加重试逻辑
    }
  }
  
  // 检查是否在交易时段
  private isMarketHours(): boolean {
    const now = new Date();
    const day = now.getDay();
    const hour = now.getHours();
    const minute = now.getMinutes();
    
    // 周末不更新
    if (day === 0 || day === 6) return false;
    
    // 9:30 - 11:30 上午
    if (hour === 9 && minute >= 30) return true;
    if (hour >= 10 && hour < 12) return true;
    
    // 13:00 - 15:00 下午
    if (hour >= 13 && hour < 15) return true;
    
    return false;
  }
}
```

---

## Phase 1: 头脑风暴 & 问题拆解

### 1.1 当前问题诊断

```
FinancePulse 当前状态:
├── 分析页面: AnalysisPage.tsx
│   ├── 分析师选择器: 6个预设分析师
│   ├── ChatInterface: 对话界面
│   └── generateAnalysisResponse(): 模拟数据 ❌
│
├── services/analysis/
│   ├── analysts.ts: 分析师配置 (6个)
│   └── Orchestrator.tsx: 简单编排 (待完善)
│
├── 数据更新问题:
│   ├── 数据只在页面加载时获取
│   ├── 没有定时刷新
│   ├── 没有后台更新
│   └── 没有缓存策略 ❌
│
└── 问题:
    ├── 无真实 LLM 调用
    ├── 无数据获取层
    ├── 无多智能体协作
    ├── 无风险评估
    └── 无自动更新 ❌
```

### 1.2 参考项目核心架构

```
TradingAgents 工作流:
┌─────────────┐
│  User Query  │  ← 输入股票代码
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Analyst Team (并行)              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │Fundament│ │Technical│ │Sentiment│   │
│  │al Agent │ │  Agent  │ │  Agent  │   │
│  └────┬────┘ └────┬────┘ └────┬────┘   │
└───────┼───────────┼───────────┼─────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
┌─────────────────────────────────────────┐
│       Researcher Team (辩论)             │
│  ┌─────────┐         ┌─────────┐       │
│  │ Bullish │  ←辩论→  │ Bearish │       │
│  │Researcher          │Researcher       │
│  └─────────┘         └─────────┘       │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           Trader Agent                   │
│  • 综合分析结果                          │
│  • 确定时机和仓位                        │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       Risk Management Team               │
│  • 评估波动性/流动性/风险                │
│  • 提供风险报告                          │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       Portfolio Manager                  │
│  • 最终审批/拒绝                         │
│  • 发送订单到模拟交易所                  │
└─────────────────────────────────────────┘
```

### 1.3 融合决策点

| 决策 | 选择 | 原因 |
|------|------|------|
| LLM 集成 | 前端模拟 + 后端扩展 | 保持轻量，后续可接入 |
| 数据源 | WebSocket + REST API | 支持实时行情 |
| 分析师数量 | 12个核心 + 6个专业 | 平衡覆盖和复杂度 |
| 工作流 | 简化版多智能体 | 适合移动端 |
| 自动更新 | 分优先级定时更新 | 性能优化 |

---

## Phase 2: 子任务执行计划

### Task 1: 自动更新系统 (AI-AUTO-001 ~ AI-AUTO-003)

**目标:** 实现数据自动更新

#### AI-AUTO-001: 自动更新服务
```typescript
// src/services/autoUpdate/AutoUpdateService.ts
- 管理所有数据的定时更新
- 分优先级调度
- 交易时段智能判断
- 失败重试机制
```

#### AI-AUTO-002: 状态管理集成
```typescript
// src/stores/useMarketStore.ts
- 使用 Zustand 管理市场数据状态
- 自动更新触发 UI 刷新
- 数据缓存策略
```

#### AI-AUTO-003: 数据获取优化
```typescript
// src/services/api/marketData.ts
- 优化 API 调用
- 添加缓存
- 批量请求
```

### Task 2: 重构分析师体系 (AI-006 ~ AI-010)

**目标:** 建立完整的 18 个分析师 Agent

#### AI-006: 投资大师 Agent
```
├── WarrenBuffettAgent    - 价值投资 oracle of Omaha
├── BenGrahamAgent        - 安全边际 捡漏
├── PeterLynchAgent       - 成长投资 10倍股
├── CharlieMungerAgent    - 伟大公司 合理价格
├── MichaelBurryAgent     - 逆向投资 深挖价值
└── NassimTalebAgent      - 黑天鹅 反脆弱
```

#### AI-007: 行业专家 Agent
```
├── CathieWoodAgent       - 创新颠覆
├── BillAckmanAgent       - 积极股东
├── StanleyDruckenmiller  - 宏观对冲
└── AswathDamodaranAgent  - 估值权威
```

#### AI-008: 量化分析 Agent
```
├── ValuationAgent        - DCF/PE估值计算
├── TechnicalsAgent       - K线/均线/RSI/MACD
├── SentimentAgent        - 新闻情绪分析
└── FundamentalsAgent     - 财务指标分析
```

#### AI-009: 风控 Agent
```
├── RiskManagerAgent      - 风险指标计算
└── PortfolioManagerAgent - 组合管理决策
```

#### AI-010: 配置文件
```typescript
// src/services/analysis/agentConfig.ts
interface AgentConfig {
  id: string;
  name: string;
  style: string;           // 投资风格
  systemPrompt: string;    // LLM 系统提示词
  expertise: string[];     // 专长领域
  dataSources: DataSource[];
  signalType: 'bullish' | 'bearish' | 'neutral';
  confidence: number;     // 0-100
  maxPosition: number;     // 最大仓位 %
}
```

### Task 3: 构建数据获取层 (AI-011 ~ AI-012)

**目标:** 实现真实数据获取

#### AI-011: 数据服务架构
```typescript
// src/services/data/marketDataService.ts
interface MarketDataService {
  // 实时行情
  getRealtimeQuote(code: string): Promise<Quote>;
  
  // K线数据
  getKlineData(code: string, period: KlinePeriod): Promise<Kline[]>;
  
  // 财务数据
  getFinancialMetrics(code: string): Promise<FinancialMetrics>;
  
  // 新闻数据
  getNewsSentiment(code: string): Promise<SentimentData>;
  
  // 宏观数据
  getMacroIndicators(): Promise<MacroData>;
}
```

#### AI-012: 数据源配置
```typescript
// 优先级: 免费 → 付费
const DATA_SOURCES = {
  realtime: '东方财富 WebSocket',
  kline: 'AKShare / Tushare',
  financial: 'AKShare / 巨潮',
  news: '东方财富 / 新浪',
  macro: '国家统计局 / 央行'
};
```

### Task 4: 实现 Orchestrator 工作流 (AI-013 ~ AI-015)

**目标:** 参考 TradingAgents 的多智能体编排

#### AI-013: 工作流定义
```typescript
// src/services/analysis/workflow.ts
interface AnalysisWorkflow {
  steps: WorkflowStep[];
  
  // Step 1: 并行数据获取
  parallelFetch: {
    fundamental: AgentTask;
    technical: AgentTask;
    sentiment: AgentTask;
    macro: AgentTask;
  };
  
  // Step 2: Agent 分析
  agentAnalysis: AgentTask[];
  
  // Step 3: 辩论 (可选)
  debate: {
    bullish: AgentTask;
    bearish: AgentTask;
  };
  
  // Step 4: 综合决策
  synthesize: AgentTask;
  
  // Step 5: 风险评估
  riskAssess: AgentTask;
}
```

#### AI-014: LLM 集成
```typescript
// src/services/analysis/llmService.ts
interface LLMService {
  // 支持多 provider
  providers: ['openai', 'anthropic', 'deepseek', 'mock'];
  
  // 流式响应
  streamAnalysis(prompt: string): Promise<Stream>;
  
  // 非流式响应
  generateResponse(prompt: string): Promise<string>;
}
```

#### AI-015: 结果格式化
```typescript
// src/services/analysis/responseFormatter.ts
interface AnalysisResult {
  code: string;
  timestamp: number;
  agents: AgentSignal[];
  
  // 综合分析
  summary: {
    valuation: string;
    risks: string[];
    recommendation: Recommendation;
  };
  
  // 信号
  signals: {
    technical: Signal;
    fundamental: Signal;
    sentiment: Signal;
    macro: Signal;
  };
  
  // 风险评估
  riskAssessment: {
    score: number;        // 0-100
    maxLoss: number;      // 预计最大亏损 %
    positionLimit: number; // 建议仓位 %
  };
}
```

### Task 5: UI 优化 (AI-016 ~ AI-018)

**目标:** 优化分析页面用户体验

#### AI-016: 分析师选择器优化
```
├── 分类展示: 投资大师 / 行业专家 / 量化分析 / 风控
├── 多选支持: 最多选择 4 个分析师
├── 风格说明: 悬停显示分析师风格简介
└── 快捷模板: 价值投资 / 成长投资 / 综合分析
```

#### AI-017: 分析结果展示
```
├── 实时进度: 显示当前执行的 Agent
├── 分块展示: 技术面 / 基本面 / 情绪 / 宏观
├── 信号指示: 买入/持有/卖出 颜色标识
├── 置信度: 进度条显示各维度置信度
└── 建议汇总: 最终投资建议卡片
```

#### AI-018: 历史记录
```
├── 分析历史: 保存最近 20 条分析
├── 模板管理: 保存自定义提示词模板
└── 分享功能: 导出分析报告
```

---

## Phase 3: 验证检查清单

### 功能验证
- [ ] 自动更新服务正常启动
- [ ] 各优先级数据正确更新
- [ ] 交易时段判断正确
- [ ] 18 个分析师 Agent 配置完整
- [ ] 数据获取服务正常调用
- [ ] Orchestrator 工作流正确执行
- [ ] LLM 响应正确格式化
- [ ] 风险评估计算准确
- [ ] 分析结果正确展示

### 代码质量
- [ ] TypeScript 编译通过 (npx tsc --noEmit)
- [ ] 无未使用的 import
- [ ] 中文注释完整
- [ ] 组件命名规范 (PascalCase)
- [ ] 无 console.error

### 用户体验
- [ ] 加载状态显示
- [ ] 错误处理完善
- [ ] 响应式布局
- [ ] 操作流畅
- [ ] 数据更新指示器可见

---

## Phase 4: 完成分支

### 提交记录
```
├── feat: 实现数据自动更新系统
├── feat: 添加18个专业分析师Agent配置
├── feat: 实现数据获取服务层
├── feat: 构建多智能体Orchestrator工作流
├── feat: 集成LLM服务(支持多provider)
├── feat: 优化分析结果展示UI
├── feat: 添加风险评估组件
└── docs: 更新INTEGRATION_PRD文档
```

### Pull Request 描述
```markdown
## 融合参考项目
- TradingAgents: 多智能体工作流架构
- ai-hedge-fund: 19个专业分析师Agent体系

## 主要改动
1. 实现数据自动更新系统 (分优先级定时更新)
2. 扩展分析师从6个到18个
3. 实现数据获取服务层
4. 构建Orchestrator多智能体编排
5. 添加LLM服务支持
6. 优化分析结果UI

## 验证结果
- [x] TypeScript 编译通过
- [x] 自动更新系统测试通过
- [x] 所有功能正常
- [ ] UI 测试完成
```

---

## 📊 执行时间线

```
Phase 1 (头脑风暴): 10分钟
Phase 2 (子任务执行): 90分钟
  ├── Task 1: 自动更新系统 (20分钟)
  ├── Task 2: 重构分析师体系 (15分钟)
  ├── Task 3: 数据获取层 (15分钟)
  ├── Task 4: 工作流编排 (25分钟)
  └── Task 5: UI优化 (15分钟)
Phase 3 (验证检查): 10分钟
Phase 4 (完成分支): 5分钟
─────────────────────────
总计: ~115分钟
```

---

## 关键决策点总结

| 决策 | 选择 | 理由 |
|------|------|------|
| 分析师数量 | 18个 | 覆盖主要投资风格 |
| LLM 方式 | Mock + 扩展点 | 保持轻量，后续可接入 |
| 数据源 | 东方财富 + AKShare | 免费 + 中文友好 |
| 工作流 | 简化版 | 适合移动端性能 |
| 风险评估 | 简化指标 | 实用为主 |
| 自动更新 | 分优先级定时 | 性能优化 + 交易时段判断 |

---

## 下一步行动

1. ✅ 分析完成 → 确认融合方案
2. ⬜ 执行 Task 1: 自动更新系统
3. ⬜ 执行 Task 2-4: 分析师和数据层
4. ⬜ 执行 Task 5: UI优化
5. ⬜ 验证所有功能
6. ⬜ 提交代码并上传 GitHub
