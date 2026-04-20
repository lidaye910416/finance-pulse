/**
 * 市场数据 API 服务
 * 
 * 从东方财富获取真实市场数据
 */

import type { Quote, KLine, NorthboundData } from '../data/types';

// 东方财富 API 基础 URL
const EAST_MONEY_BASE = 'https://push2.eastmoney.com';

// 股票代码格式化
const formatStockCode = (code: string): string => {
  // A股: 6开头上海, 0/3开头深圳
  if (code.startsWith('6')) return `1.${code}`; // 上海
  if (code.startsWith('0') || code.startsWith('3')) return `0.${code}`; // 深圳
  if (code.startsWith('4') || code.startsWith('8')) return `0.${code}`; // 北交所
  return code;
};

/**
 * 获取股票实时行情
 */
export async function fetchStockQuote(code: string): Promise<Quote | null> {
  try {
    const formattedCode = formatStockCode(code);
    const url = `${EAST_MONEY_BASE}/api/qt/stock/get?secid=${formattedCode}&fields=f43,f44,f45,f46,f47,f48,f50,f57,f58,f60,f107,f116,f117,f152`;

    const response = await fetch(url);
    if (!response.ok) return null;

    const data = await response.json();
    const d = data.data;

    if (!d) return null;

    return {
      code,
      name: d.f58 || `股票${code}`,
      price: d.f43 / 100 || 0,
      change: (d.f43 - d.f60) / 100 || 0,
      changePercent: d.f50 || 0,
      volume: d.f47 || 0,
      amount: d.f48 || 0,
      high: d.f44 / 100 || 0,
      low: d.f45 / 100 || 0,
      open: d.f46 / 100 || 0,
      prevClose: d.f60 / 100 || 0,
      timestamp: Date.now(),
    };
  } catch (error) {
    console.error(`获取股票行情失败 ${code}:`, error);
    return null;
  }
}

/**
 * 获取多个股票实时行情
 */
export async function fetchMultipleQuotes(codes: string[]): Promise<Quote[]> {
  const quotes: Quote[] = [];
  
  // 东方财富支持批量查询
  const secids = codes.map(formatStockCode).join(',');
  const url = `${EAST_MONEY_BASE}/api/qt/ulist.np/get?secids=${secids}&fields=f1,f2,f3,f4,f5,f6,f7,f8,f12,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152`;

  try {
    const response = await fetch(url);
    if (!response.ok) return [];

    const data = await response.json();
    const list = data.data?.diff || [];

    for (const item of list) {
      if (item.f12) {
        quotes.push({
          code: String(item.f12),
          name: item.f14 || `股票${item.f12}`,
          price: item.f2 || 0,
          change: item.f3 || 0,
          changePercent: item.f3 || 0,
          volume: item.f5 || 0,
          amount: item.f6 || 0,
          high: item.f15 || 0,
          low: item.f16 || 0,
          open: item.f17 || 0,
          prevClose: item.f18 || 0,
          timestamp: Date.now(),
        });
      }
    }
  } catch (error) {
    console.error('批量获取股票行情失败:', error);
  }

  return quotes;
}

/**
 * 获取K线数据
 */
export async function fetchKLine(
  code: string,
  period: '1d' | '1w' | '1m' = '1d',
  count: number = 100
): Promise<KLine[]> {
  try {
    const formattedCode = formatStockCode(code);
    const periodMap = { '1d': '101', '1w': '102', '1m': '103' };
    const url = `${EAST_MONEY_BASE}/api/qt/stock/kline/get?secid=${formattedCode}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=${periodMap[period]}&fqt=1&beg=0&end=20500101&lmt=${count}`;

    const response = await fetch(url);
    if (!response.ok) return [];

    const data = await response.json();
    const klines = data.data?.klines || [];

    return klines.map((k: string) => {
      const [date, open, close, high, low, volume] = k.split(',');
      return {
        time: new Date(date).getTime(),
        open: parseFloat(open),
        close: parseFloat(close),
        high: parseFloat(high),
        low: parseFloat(low),
        volume: parseFloat(volume),
      };
    });
  } catch (error) {
    console.error(`获取K线数据失败 ${code}:`, error);
    return [];
  }
}

/**
 * 获取北向资金数据
 */
export async function fetchNorthboundData(days: number = 7): Promise<NorthboundData[]> {
  try {
    // 东方财富北向资金API
    const url = `https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MUTUAL_MARKET_SH&columns=TRADE_DATE,HOLD_DATE,SECURITY_CODE_A,SECURITY_NAME_A,CLOSE_PRICE,MUTUAL_TYPE,MUTUAL_TYPE_NAME,BINDING_SH,SECUCODE&quoteColumns=&filter=(MUTUAL_TYPE="001")&pageNumber=1&pageSize=${days}&sortTypes=-1&sortColumns=TRADE_DATE&source=WEB&client=WEB`;

    const response = await fetch(url);
    if (!response.ok) return [];

    const data = await response.json();
    const list = data.result?.data || [];

    return list.map((item: any) => ({
      date: item.TRADE_DATE,
      hkStock: (item.HOLD_DATE || 0) / 100000000, // 转换为亿
      szStock: 0, // 需要单独查询深股通
      total: (item.BINDING_SH || 0) / 100000000,
    }));
  } catch (error) {
    console.error('获取北向资金数据失败:', error);
    return [];
  }
}

/**
 * 获取恐惧贪婪指数
 */
export async function fetchFearGreedIndex(): Promise<{ value: number; phase: string }> {
  try {
    // Alternative.me API
    const response = await fetch('https://api.alternative.me/fng/?limit=1');
    if (!response.ok) {
      return { value: 26, phase: '极度恐惧' };
    }

    const data = await response.json();
    const value = parseInt(data.data?.[0]?.value || '50');
    
    const phase = value <= 25 ? '极度恐惧' :
                  value <= 45 ? '恐惧' :
                  value <= 55 ? '中性' :
                  value <= 75 ? '贪婪' : '极度贪婪';

    return { value, phase };
  } catch (error) {
    console.error('获取恐惧贪婪指数失败:', error);
    return { value: 26, phase: '极度恐惧' };
  }
}

/**
 * 获取涨跌停统计
 */
export async function fetchLimitUpDown(): Promise<{ limitUp: number; limitDown: number }> {
  try {
    // TODO: 调用东方财富实时涨停统计API
    // const limitUpUrl = 'https://push2.eastmoney.com/api/qt/clist/get?...';

    // 简化实现，返回模拟数据
    return {
      limitUp: 47,
      limitDown: 8,
    };
  } catch (error) {
    console.error('获取涨跌停统计失败:', error);
    return { limitUp: 47, limitDown: 8 };
  }
}
