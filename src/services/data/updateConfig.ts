/**
 * FinancePulse 数据更新配置
 * 
 * 定义各类数据的更新频率和更新策略
 * 参考 Superpowers 方法论：模块化、可配置、易扩展
 */

// 数据类型枚举
export enum DataType {
  // 市场数据
  QUOTES = 'quotes',           // 实时行情
  KLINE_1M = 'kline_1m',       // 1分钟K线
  KLINE_5M = 'kline_5m',       // 5分钟K线
  KLINE_1D = 'kline_1d',       // 日K线
  MONEY_FLOW = 'money_flow',    // 资金流向
  NORTHBOUND = 'northbound',    // 北向资金

  // 宏观数据
  GDP = 'gdp',                  // GDP增速
  CPI = 'cpi',                  // 消费者物价指数
  PPI = 'ppi',                  // 生产者物价指数
  PMI = 'pmi',                  // 采购经理指数
  LPR = 'lpr',                  // 贷款市场报价利率
  M2 = 'm2',                    // 货币供应量M2

  // 情绪数据
  FEAR_GREED = 'fear_greed',    // 恐惧贪婪指数
  LIMIT_UP_DOWN = 'limit_up_down', // 涨跌停统计
  MARGIN_BALANCE = 'margin_balance', // 两融余额

  // 资讯数据
  NEWS = 'news',                // 新闻快讯
  ANNOUNCEMENT = 'announcement', // 公告
  RESEARCH_REPORT = 'research_report', // 研报
}

// 更新频率配置
export interface UpdateConfig {
  type: DataType;
  name: string;                 // 中文名称
  updateFrequency: UpdateFrequency;
  marketHoursOnly: boolean;     // 是否只在交易时段更新
  description: string;          // 描述
}

export enum UpdateFrequency {
  REALTIME = 'realtime',        // 实时（WebSocket推送）
  MINUTE = 'minute',            // 分钟级
  HOURLY = 'hourly',            // 小时级
  DAILY = 'daily',              // 日更
  WEEKLY = 'weekly',            // 周更
  MONTHLY = 'monthly',          // 月更
}

// 数据更新配置表
export const DATA_UPDATE_CONFIG: UpdateConfig[] = [
  // ========== 市场数据 ==========
  {
    type: DataType.QUOTES,
    name: '实时行情',
    updateFrequency: UpdateFrequency.REALTIME,
    marketHoursOnly: true,
    description: '股票、指数的实时价格和涨跌',
  },
  {
    type: DataType.KLINE_1M,
    name: '1分钟K线',
    updateFrequency: UpdateFrequency.MINUTE,
    marketHoursOnly: true,
    description: '分时数据和1分钟K线',
  },
  {
    type: DataType.KLINE_5M,
    name: '5分钟K线',
    updateFrequency: UpdateFrequency.MINUTE,
    marketHoursOnly: true,
    description: '5分钟K线数据',
  },
  {
    type: DataType.KLINE_1D,
    name: '日K线',
    updateFrequency: UpdateFrequency.DAILY,
    marketHoursOnly: false,
    description: '日K线数据，收盘后更新',
  },
  {
    type: DataType.MONEY_FLOW,
    name: '资金流向',
    updateFrequency: UpdateFrequency.HOURLY,
    marketHoursOnly: true,
    description: '行业、概念板块资金流向',
  },
  {
    type: DataType.NORTHBOUND,
    name: '北向资金',
    updateFrequency: UpdateFrequency.DAILY,
    marketHoursOnly: false,
    description: '沪股通、深股通净买入，收盘后15:30更新',
  },

  // ========== 宏观数据 ==========
  {
    type: DataType.GDP,
    name: 'GDP增速',
    updateFrequency: UpdateFrequency.MONTHLY,
    marketHoursOnly: false,
    description: '季度GDP同比增速，国家统计局发布',
  },
  {
    type: DataType.CPI,
    name: 'CPI消费者物价指数',
    updateFrequency: UpdateFrequency.MONTHLY,
    marketHoursOnly: false,
    description: '月度CPI环比、同比，统计局9:30发布',
  },
  {
    type: DataType.PPI,
    name: 'PPI生产者物价指数',
    updateFrequency: UpdateFrequency.MONTHLY,
    marketHoursOnly: false,
    description: '月度PPI，统计局9:30发布',
  },
  {
    type: DataType.PMI,
    name: 'PMI采购经理指数',
    updateFrequency: UpdateFrequency.MONTHLY,
    marketHoursOnly: false,
    description: '制造业/非制造业PMI，统计局月末发布',
  },
  {
    type: DataType.LPR,
    name: 'LPR贷款市场报价利率',
    updateFrequency: UpdateFrequency.MONTHLY,
    marketHoursOnly: false,
    description: '1年期、5年期LPR，每月20日9:15发布',
  },
  {
    type: DataType.M2,
    name: '货币供应量',
    updateFrequency: UpdateFrequency.MONTHLY,
    marketHoursOnly: false,
    description: 'M0、M1、M2货币供应量，央行中旬发布',
  },

  // ========== 情绪数据 ==========
  {
    type: DataType.FEAR_GREED,
    name: '恐惧贪婪指数',
    updateFrequency: UpdateFrequency.DAILY,
    marketHoursOnly: false,
    description: 'AlternativeMe计算，每个交易日23:00更新',
  },
  {
    type: DataType.LIMIT_UP_DOWN,
    name: '涨跌停统计',
    updateFrequency: UpdateFrequency.REALTIME,
    marketHoursOnly: true,
    description: '涨停数、跌停数、炸板率',
  },
  {
    type: DataType.MARGIN_BALANCE,
    name: '融资融券余额',
    updateFrequency: UpdateFrequency.DAILY,
    marketHoursOnly: false,
    description: '两融余额，交易所16:00发布',
  },

  // ========== 资讯数据 ==========
  {
    type: DataType.NEWS,
    name: '新闻快讯',
    updateFrequency: UpdateFrequency.REALTIME,
    marketHoursOnly: false,
    description: '重要财经新闻实时推送',
  },
  {
    type: DataType.ANNOUNCEMENT,
    name: '上市公司公告',
    updateFrequency: UpdateFrequency.REALTIME,
    marketHoursOnly: true,
    description: '交易所收盘后集中披露',
  },
  {
    type: DataType.RESEARCH_REPORT,
    name: '券商研报',
    updateFrequency: UpdateFrequency.DAILY,
    marketHoursOnly: false,
    description: '机构研报摘要，每日更新',
  },
];

// 辅助函数：根据类型获取配置
export function getUpdateConfig(type: DataType): UpdateConfig | undefined {
  return DATA_UPDATE_CONFIG.find(config => config.type === type);
}

// 辅助函数：获取下次更新时间
export function getNextUpdateTime(type: DataType): Date | null {
  const config = getUpdateConfig(type);
  if (!config) return null;

  const now = new Date();
  const marketOpen = new Date(now);
  marketOpen.setHours(9, 30, 0, 0);
  
  const marketClose = new Date(now);
  marketClose.setHours(15, 0, 0, 0);

  switch (config.updateFrequency) {
    case UpdateFrequency.REALTIME:
      // 交易时段实时
      if (config.marketHoursOnly) {
        if (now < marketOpen || now > marketClose) {
          // 非交易时段，返回下一个开盘时间
          const nextOpen = new Date(now);
          if (now > marketClose) {
            nextOpen.setDate(nextOpen.getDate() + 1);
          }
          nextOpen.setHours(9, 30, 0, 0);
          return nextOpen;
        }
      }
      return now;

    case UpdateFrequency.MINUTE:
      return new Date(now.getTime() + 60000);

    case UpdateFrequency.HOURLY:
      const nextHour = new Date(now);
      nextHour.setMinutes(0, 0, 0);
      nextHour.setHours(nextHour.getHours() + 1);
      return nextHour;

    case UpdateFrequency.DAILY:
      // 收盘后更新
      const nextDay = new Date(marketClose);
      if (now >= marketClose) {
        nextDay.setDate(nextDay.getDate() + 1);
      }
      return nextDay;

    case UpdateFrequency.MONTHLY:
      // 月度数据，下月中旬
      const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 15, 9, 30);
      if (now >= nextMonth) {
        nextMonth.setMonth(nextMonth.getMonth() + 1);
      }
      return nextMonth;

    default:
      return null;
  }
}
