/**
 * 宏观数据 API 服务
 * 
 * 从国家统计局、央行等获取宏观数据
 */

import type { MacroIndicator } from '../data/types';

/**
 * 获取GDP数据
 */
export async function fetchGDPData(): Promise<MacroIndicator | null> {
  try {
    // 模拟数据 - 实际应调用国家统计局API
    // https://data.stats.gov.cn/easyquery.htm?cn=A01
    return {
      type: 'gdp',
      date: new Date().toISOString().slice(0, 7),
      value: 5.0,
      yoy: 5.0,
      unit: '%',
      source: '国家统计局',
      releaseTime: '每季度结束后15日左右',
    };
  } catch (error) {
    console.error('获取GDP数据失败:', error);
    return null;
  }
}

/**
 * 获取CPI数据
 */
export async function fetchCPIData(): Promise<MacroIndicator | null> {
  try {
    // 模拟数据 - 实际应调用国家统计局API
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
  } catch (error) {
    console.error('获取CPI数据失败:', error);
    return null;
  }
}

/**
 * 获取PMI数据
 */
export async function fetchPMIData(): Promise<MacroIndicator | null> {
  try {
    // 模拟数据 - 实际应调用国家统计局API
    return {
      type: 'pmi',
      date: new Date().toISOString().slice(0, 7),
      value: 49.2,
      yoy: -0.8,
      unit: '',
      source: '国家统计局',
      releaseTime: '每月最后一天',
    };
  } catch (error) {
    console.error('获取PMI数据失败:', error);
    return null;
  }
}

/**
 * 获取LPR数据
 */
export async function fetchLPRData(): Promise<{ oneYear: number; fiveYear: number }> {
  try {
    // 模拟数据 - 实际应调用央行API
    // https://www.pbc.gov.cn/zhengcehuobisi/125207/125213/125440/125497/index.html
    return {
      oneYear: 3.45,
      fiveYear: 4.20,
    };
  } catch (error) {
    console.error('获取LPR数据失败:', error);
    return { oneYear: 3.45, fiveYear: 4.20 };
  }
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
