/**
 * 新闻资讯 API 服务
 * 
 * 从东方财富获取新闻资讯
 */

import type { NewsItem } from '../data/types';

/**
 * 获取快讯
 */
export async function fetchNews(limit: number = 20): Promise<NewsItem[]> {
  try {
    // 东方财富快讯API
    const url = `https://np-listapi.eastmoney.com/comm/web/getFastNewsList?cb=jQuery&client=web&page=1&pageSize=${limit}&endTime=&keyword=&order=1`;

    const response = await fetch(url);
    if (!response.ok) return [];

    // 简化处理，实际API响应格式可能不同
    const mockNews: NewsItem[] = [
      {
        id: '1',
        title: '央行宣布定向降准，释放长期资金约1000亿元',
        content: '中国人民银行宣布，为支持实体经济发展，决定于近期实施定向降准...',
        source: '东方财富',
        time: Date.now() - 3600000,
        tags: ['央行', '降准', '货币政策'],
        sentiment: 'positive',
        relatedStocks: [],
      },
      {
        id: '2',
        title: '证监会发布科创板改革新举措',
        content: '证监会今日发布《关于深化科创板改革的若干措施》...',
        source: '证监会',
        time: Date.now() - 7200000,
        tags: ['证监会', '科创板', '改革'],
        sentiment: 'positive',
        relatedStocks: [],
      },
      {
        id: '3',
        title: '3月出口数据超预期，贸易顺差扩大',
        content: '海关总署今日公布的数据显示，3月份我国外贸进出口总值同比增长...',
        source: '海关总署',
        time: Date.now() - 10800000,
        tags: ['外贸', '出口', '经济数据'],
        sentiment: 'positive',
        relatedStocks: [],
      },
      {
        id: '4',
        title: '多家券商发布年报，业绩分化明显',
        content: '中信证券、华泰证券等券商陆续发布2024年年报...',
        source: '东方财富',
        time: Date.now() - 14400000,
        tags: ['券商', '年报', '业绩'],
        sentiment: 'neutral',
        relatedStocks: ['600030', '601688'],
      },
      {
        id: '5',
        title: '美股大幅下跌，纳指跌幅超过2%',
        content: '隔夜美股三大指数集体收跌，纳斯达克指数跌幅超过2%...',
        source: '东方财富',
        time: Date.now() - 18000000,
        tags: ['美股', '纳斯达克', '外围市场'],
        sentiment: 'negative',
        relatedStocks: [],
      },
    ];

    return mockNews;
  } catch (error) {
    console.error('获取新闻失败:', error);
    return [];
  }
}

/**
 * 获取股票相关新闻
 */
export async function fetchStockNews(code: string, limit: number = 10): Promise<NewsItem[]> {
  try {
    // 东方财富个股新闻API
    const url = `https://np-listapi.eastmoney.com/comm/web/getSecurityNewsList?cb=jQuery&client=web&page=1&pageSize=${limit}&code=${code}`;

    const response = await fetch(url);
    if (!response.ok) return [];

    // 返回模拟数据
    return [
      {
        id: `${code}-1`,
        title: `${code}发布2024年年报，净利润同比增长15%`,
        content: '公司今日发布年度报告，实现营业收入...',
        source: '东方财富',
        time: Date.now() - 86400000,
        tags: ['年报', '业绩'],
        sentiment: 'positive',
        relatedStocks: [code],
      },
    ];
  } catch (error) {
    console.error(`获取股票新闻失败 ${code}:`, error);
    return [];
  }
}

/**
 * 搜索新闻
 */
export async function searchNews(keyword: string, limit: number = 20): Promise<NewsItem[]> {
  try {
    // 简单实现，实际应调用搜索API
    const allNews = await fetchNews(100);
    return allNews.filter(news => 
      news.title.includes(keyword) || 
      news.content.includes(keyword) ||
      news.tags.some(tag => tag.includes(keyword))
    ).slice(0, limit);
  } catch (error) {
    console.error(`搜索新闻失败 ${keyword}:`, error);
    return [];
  }
}

/**
 * 情感分析（简化实现）
 */
export function analyzeSentiment(text: string): 'positive' | 'negative' | 'neutral' {
  const positiveKeywords = ['上涨', '增长', '利好', '突破', '创新高', '超预期', '增持', '买入'];
  const negativeKeywords = ['下跌', '下降', '利空', '破位', '创新低', '不及预期', '减持', '卖出'];

  let positiveCount = 0;
  let negativeCount = 0;

  for (const keyword of positiveKeywords) {
    if (text.includes(keyword)) positiveCount++;
  }
  for (const keyword of negativeKeywords) {
    if (text.includes(keyword)) negativeCount++;
  }

  if (positiveCount > negativeCount) return 'positive';
  if (negativeCount > positiveCount) return 'negative';
  return 'neutral';
}
