# FinancePulse 开发规范

## 数据规范（铁律 - 最高优先级）

**禁止使用任何模拟数据、硬编码数据填充 UI。**

### 规则：
1. **实时数据优先**：所有市场数据必须来自真实 API
2. **API 失败显示 `*`**：数据获取失败时，UI 显示 `*` 或空值，不填充假数据
3. **记录数据源**：代码注释中标明数据来源 API

### 错误示例：
```typescript
// ❌ 错误 - 使用硬编码数据 fallback
return { value: 26, phase: '极度恐惧' };

// ❌ 错误 - 前端初始化使用假数据
const [fearGreed, setFearGreed] = useState(26);  // 硬编码
```

### 正确示例：
```typescript
// ✅ API 失败返回 null，前端显示 *
export async function fetchFearGreedIndex(): Promise<{ value: number; phase: string } | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/fear-greed`);
    if (response.ok) return await response.json();
  } catch (error) { console.error(...); }
  return null;  // 不返回假数据
}

// ✅ 前端状态初始化为 * / 空值
const [sentimentData, setSentimentData] = useState({
  fearGreed: 0,
  phase: '-',
  signals: [
    { label: '涨停数量', value: '*', status: '-', variant: 'gray' },
  ],
});

// ✅ API 成功时才更新，失败保持 *
if (fearGreed) {
  setSentimentData(prev => ({ ...prev, fearGreed: fearGreed.value }));
}
```

## 数据源配置

| 数据类型 | 优先级1 | 优先级2 |
|---------|---------|---------|
| 股票行情 | 腾讯财经 `qt.gtimg.cn` | 后端 `/quote/{code}` |
| 指数行情 | 腾讯财经 `qt.gtimg.cn` | 后端 `/quote/{code}` |
| K线数据 | 东方财富 `push2.eastmoney.com` | - |
| 北向资金 | 后端 `/api/market/northbound` | - |
| 宏观数据 | 后端 `/api/market/macro` | - |

## 后端服务

- 端口：`5003`
- 基础URL：`http://localhost:5003`
- 启动命令：`cd server && python3 -m uvicorn main:app --port 5003`

## 前端配置

- 端口：`5173`
- 基础URL：`http://localhost:5173`

## 调试命令

```bash
# 测试后端行情接口
curl http://localhost:5003/quote/000001

# 测试后端指数接口
curl http://localhost:5003/quote/600519
```
