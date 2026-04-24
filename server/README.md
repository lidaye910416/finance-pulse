# FinancePulse AI 服务

基于 **LangGraph** 的多智能体股票分析后端服务。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph 工作流                      │
│                                                          │
│  ┌─────────────┐     ┌─────────────┐                    │
│  │ collect_data│────→│ run_analysts│                    │
│  └─────────────┘     └──────┬──────┘                    │
│                             │                            │
│                    ┌────────▼────────┐                   │
│                    │     debate     │ ◄──┐              │
│                    └────────┬────────┘    │            │
│                             │              │            │
│                    ┌────────▼────────┐    │ 循环       │
│                    │ should_continue │────┘            │
│                    └────────┬────────┘                 │
│                             │                           │
│                    ┌────────▼────────┐                  │
│                    │   synthesize   │                  │
│                    └────────┬────────┘                  │
│                             │                           │
│                    ┌────────▼────────┐                  │
│                    │    decision    │                  │
│                    └────────┬────────┘                  │
│                             │                           │
└──────────────────────────────┼───────────────────────────┘
                               │
                               ▼
                    [ 返回分析结果给前端 ]
```

## 安装

```bash
cd server
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

## 配置

编辑 `.env` 文件：

```env
LLM_PROVIDER=minimax        # 或 openai, anthropic, deepseek
LLM_API_KEY=your_api_key
LLM_MODEL=MiniMax-M2.7-0508
LLM_BASE_URL=https://api.minimaxi.com/anthropic
```

## 运行

```bash
# 开发模式
uvicorn main:app --reload --port 5000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 4
```

## API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/analyze` | 分析股票 |
| GET | `/quote/{code}` | 获取行情 |
| GET | `/llm/test` | 测试 LLM |

## API 文档

启动服务后访问：http://localhost:5000/docs

## 调用示例

```bash
# 测试健康检查
curl http://localhost:5000/health

# 分析股票
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "600519", "name": "贵州茅台", "max_iterations": 3}'

# 获取行情
curl http://localhost:5000/quote/600519
```

## 工作流说明

### 1. collect_data
收集股票实时数据（价格、成交量、PE等）

### 2. run_analysts (并行)
并行运行 5 个分析师：
- 沃伦·巴菲特（价值投资）
- 本杰明·格雷厄姆（安全边际）
- 彼得·林奇（成长投资）
- 技术分析专家
- 情绪分析专家

### 3. debate (循环)
多空双方辩论，**循环直到**：
- 置信度差距 < 15%（收敛）
- 达到最大迭代次数

### 4. synthesize
综合所有分析结果，生成综合报告

### 5. decision
基于综合分析，给出最终投资建议

## 前端集成

前端通过 HTTP 调用：

```typescript
const response = await fetch('http://localhost:5000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ code: '600519', name: '贵州茅台' }),
});

const result = await response.json();
// result.recommendation.action => 'buy' | 'hold' | 'sell' | 'watch'
```
