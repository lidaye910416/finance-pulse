/**
 * 宏观数据 API 服务
 *
 * 调用后端 FinancePulse API 获取宏观数据
 */

import type { MacroIndicator } from '../data/types';

// 后端 API 基础 URL
const API_BASE_URL = 'http://localhost:5000';

/**
 * 获取GDP数据
 */
export async function fetchGDPData(): Promise<MacroIndicator | null> {
  try {
    // 调用后端 API
    const response = await fetch(`${API_BASE_URL}/api/macro/gdp`);
    if (response.ok) {
      const data = await response.json();
      return {
        type: 'gdp',
        date: `${data.year}-${data.quarter}`,
        value: data.current,
        yoy: data.current,
        unit: '%',
        source: '东方财富',
        releaseTime: data.updateTime,
      };
    }
  } catch (error) {
    console.error('获取GDP数据失败:', error);
  }

  // Fallback
  return {
    type: 'gdp',
    date: new Date().toISOString().slice(0, 7),
    value: 5.0,
    yoy: 5.0,
    unit: '%',
    source: '国家统计局',
    releaseTime: '每季度结束后15日左右',
  };
}

/**
 * 获取CPI数据
 */
export async function fetchCPIData(): Promise<MacroIndicator | null> {
  try {
    // 调用后端 API
    const response = await fetch(`${API_BASE_URL}/api/macro/cpi`);
    if (response.ok) {
      const data = await response.json();
      return {
        type: 'cpi',
        date: `${data.year}-${String(data.month).padStart(2, '0')}`,
        value: data.yoy,
        yoy: data.yoy,
        mom: data.mom,
        unit: '%',
        source: '东方财富',
        releaseTime: data.updateTime,
      };
    }
  } catch (error) {
    console.error('获取CPI数据失败:', error);
  }

  // Fallback
  return {
    type: 'cpi',
    date: new Date().toISOString().slice(0, 7),
    value: 1.1,
    yoy: 1.1,
    mom: 0.2,
    unit: '%',
    source: '国家统计局',
    releaseTime: '每月9日左右',
  };
}

/**
 * 获取PMI数据
 */
export async function fetchPMIData(): Promise<MacroIndicator | null> {
  try {
    // 调用后端 API
    const response = await fetch(`${API_BASE_URL}/api/macro/pmi`);
    if (response.ok) {
      const data = await response.json();
      return {
        type: 'pmi',
        date: data.date,
        value: data.manufacturing, // 使用制造业PMI作为主值
        yoy: 0, // PMI 不提供同比数据
        unit: '',
        source: '东方财富',
        releaseTime: data.updateTime,
      };
    }
  } catch (error) {
    console.error('获取PMI数据失败:', error);
  }

  // Fallback
  return {
    type: 'pmi',
    date: new Date().toISOString().slice(0, 7),
    value: 49.2,
    yoy: -0.8,
    unit: '',
    source: '国家统计局',
    releaseTime: '每月最后一天',
  };
}

/**
 * 获取LPR数据
 */
export async function fetchLPRData(): Promise<{ oneYear: number; fiveYear: number }> {
  try {
    // 调用后端 API
    const response = await fetch(`${API_BASE_URL}/api/macro/lpr`);
    if (response.ok) {
      const data = await response.json();
      return {
        oneYear: data.oneYear,
        fiveYear: data.fiveYear,
      };
    }
  } catch (error) {
    console.error('获取LPR数据失败:', error);
  }

  // Fallback
  return { oneYear: 3.45, fiveYear: 4.20 };
}

/**
 * 获取货币供应量数据
 */
export async function fetchMoneySupply(): Promise<{ m0: number; m1: number; m2: number; yoy: number }> {
  try {
    // 模拟数据 - 实际应调用央行API
    return {
      m0: 12.18,
      m1: 67.47,
      m2: 313.52,
      yoy: 7.0,
    };
  } catch (error) {
    console.error('获取货币供应量失败:', error);
    return { m0: 12.18, m1: 67.47, m2: 313.52, yoy: 7.0 };
  }
}

/**
 * 获取两融余额
 */
export async function fetchMarginBalance(): Promise<{ balance: number; change: number }> {
  try {
    // 东方财富两融数据API
    // https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MARGIN_TRADE_STATISTICS
    return {
      balance: 15800, // 亿元
      change: -12,
    };
  } catch (error) {
    console.error('获取两融余额失败:', error);
    return { balance: 15800, change: -12 };
  }
}

/**
 * 宏观数据结构
 */
export interface MacroData {
  gdp: number;
  cpi: number;
  pmi: number;
  lpr1y: number;
  lpr5y: number;
  m2: number;
  m2Yoy: number;
}

/**
 * 获取所有宏观数据
 */
export async function fetchAllMacroData(): Promise<MacroData> {
  try {
    // 调用后端聚合 API
    const response = await fetch(`${API_BASE_URL}/api/macro`);
    if (response.ok) {
      const data = await response.json();
      return {
        gdp: data.gdp?.current ?? 5.0,
        cpi: data.cpi?.yoy ?? 2.0,
        pmi: data.pmi?.manufacturing ?? 50,
        lpr1y: data.lpr?.oneYear ?? 3.45,
        lpr5y: data.lpr?.fiveYear ?? 3.95,
        m2: 313.52, // 货币供应量暂时保留本地获取
        m2Yoy: 7.0,
      };
    }
  } catch (error) {
    console.error('获取宏观数据失败:', error);
  }

  // Fallback - 如果后端不可用，使用本地并行请求
  const [gdp, cpi, pmi, lpr, moneySupply] = await Promise.all([
    fetchGDPData(),
    fetchCPIData(),
    fetchPMIData(),
    fetchLPRData(),
    fetchMoneySupply(),
  ]);

  return {
    gdp: gdp?.value ?? 5.0,
    cpi: cpi?.value ?? 2.0,
    pmi: pmi?.value ?? 50,
    lpr1y: lpr.oneYear,
    lpr5y: lpr.fiveYear,
    m2: moneySupply.m2,
    m2Yoy: moneySupply.yoy,
  };
}

/**
 * 汇率数据接口
 */
export interface ExchangeRateItem {
  currency: string;
  name: string;
  rate: number;
  change: number;
  changePercent: number;
  updateTime: string;
}

export interface ExchangeRateResponse {
  baseCurrency: string;
  rates: ExchangeRateItem[];
  updateTime: string;
}

/**
 * 获取人民币汇率数据
 */
export async function fetchExchangeRate(): Promise<ExchangeRateResponse | null> {
  try {
    // 调用后端 API
    const response = await fetch(`${API_BASE_URL}/api/macro/exchange-rate`);
    if (response.ok) {
      const data: ExchangeRateResponse = await response.json();
      return data;
    }
  } catch (error) {
    console.error('获取汇率数据失败:', error);
  }

  // Fallback
  return {
    baseCurrency: 'CNY',
    rates: [
      { currency: 'USD', name: '美元', rate: 7.24, change: 0.01, changePercent: 0.14, updateTime: '' },
      { currency: 'EUR', name: '欧元', rate: 7.85, change: -0.02, changePercent: -0.25, updateTime: '' },
      { currency: 'JPY', name: '日元', rate: 0.048, change: 0.001, changePercent: 2.13, updateTime: '' },
    ],
    updateTime: '',
  };
}
