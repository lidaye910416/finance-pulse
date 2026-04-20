/**
 * FinancePulse 数据服务
 * 
 * 统一的数据获取和存储服务
 * 参考 Superpowers 方法论：模块化、可测试
 */

export * from './types';
export * from './updateConfig';

// ========== 数据存储键 ==========
export const STORAGE_KEYS = {
  WATCHLIST: 'financepulse_watchlist',
  POSITIONS: 'financepulse_positions',
  SETTINGS: 'financepulse_settings',
  LAST_UPDATE: 'financepulse_last_update',
  CACHE_PREFIX: 'financepulse_cache_',
} as const;

// ========== 数据缓存配置 ==========
export const CACHE_CONFIG = {
  // 实时数据缓存时间（毫秒）
  REALTIME_TTL: 0,           // 不缓存
  MINUTE_TTL: 60000,         // 1分钟
  HOURLY_TTL: 3600000,       // 1小时
  DAILY_TTL: 86400000,       // 24小时
  MONTHLY_TTL: 2592000000,   // 30天
} as const;

// ========== 数据源配置 ==========
export const DATA_SOURCES = {
  EAST_MONEY: {
    name: '东方财富',
    api: 'https://push2.eastmoney.com',
    websocket: 'wss://push2.eastmoney.com',
  },
  TongHuaShun: {
    name: '同花顺',
    api: 'https://d.10jqka.com.cn',
  },
  Sina: {
    name: '新浪财经',
    api: 'https://hq.sinajs.cn',
  },
  NationalBureau: {
    name: '国家统计局',
    api: 'https://data.stats.gov.cn',
  },
  PBOC: {
    name: '中国人民银行',
    api: 'https://www.pbc.gov.cn',
  },
  AlternativeMe: {
    name: 'AlternativeMe',
    api: 'https://api.alternative.me',
  },
} as const;
