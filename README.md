# FinancePulse

<p align="center">
  <img src="public/tauri.svg" alt="FinancePulse" width="120" />
</p>

<p align="center">
  AI驱动的中国金融市场每日仪表板，整合20项金融技能
</p>

<p align="center">
  <a href="https://github.com/lidaye910416/finance-pulse/actions">
    <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" alt="version" />
  </a>
  <a href="https://github.com/lidaye910416/finance-pulse/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="license" />
  </a>
  <img src="https://img.shields.io/badge/platform-Tauri%20v2-blue.svg" alt="platform" />
</p>

---

## 功能特性

### 📊 市场情绪分析
- 恐惧贪婪指数实时监测
- 涨停/跌停数量统计
- 北向资金流向追踪
- 量化信号面板

### 📈 宏观数据看板
- GDP增速、CPI、PPI、PMI指数
- LPR贷款市场报价利率
- 货币供应量（M0/M1/M2）
- 人民币汇率走势

### 🎯 仓位管理
- 五条仓位铁律
- 市场阶段判断
- 智能仓位建议
- 风险控制提示

### 📰 资讯中心
- 实时新闻摘要
- 板块资金流向
- 盘前情绪分析

### 🔮 预测市场
- 市场趋势预测
- 板块轮动分析
- 风险预警提示

### 🛠️ 工具箱
- 财务计算器
- 风险评估工具

## 技术栈

- **桌面框架**: Tauri v2
- **前端框架**: React 18 + TypeScript
- **样式方案**: Tailwind CSS
- **图表库**: Recharts
- **字体**: Inter + JetBrains Mono + Space Grotesk

## 开始使用

### 环境要求

- Node.js 18+
- Rust 1.70+
- Xcode Command Line Tools (macOS)

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run tauri dev
```

### 构建应用

```bash
npm run tauri build
```

## 项目结构

```
finance-pulse/
├── src/                    # React 前端源码
│   ├── components/         # 可复用组件
│   ├── pages/              # 页面组件
│   ├── hooks/              # 自定义 Hooks
│   ├── data/               # 模拟数据
│   └── types/              # TypeScript 类型定义
├── src-tauri/              # Rust 后端源码
├── public/                 # 静态资源
└── scripts/                # 辅助脚本
```

## 核心功能演示

### 指标详细解释

点击任意指标卡片，可查看详细的计算方法和投资建议：

- **恐惧贪婪指数**: AlternativeMe 加权计算，包含波动率、做空/做多比率、垃圾债券需求等
- **仓位建议**: 基于恐惧贪婪指数、北向资金、涨停数量等多因素综合评估
- **宏观指标**: GDP、CPI、PMI、LPR 等的计算权重和解读指南

### 页面关联导航

首页与各功能页面紧密关联：
- 首页 → A股行情/宏观数据/仓位管理/预测市场
- 快速跳转到相关页面

## 设计风格

采用 "Precision Instrument" 精密仪器风格：
- 玻璃态效果 (Glassmorphism)
- 微妙的渐变和光晕
- 深色主题
- 流畅的动画效果

## License

MIT License © 2024 FinancePulse
