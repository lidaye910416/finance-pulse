/**
 * 新闻资讯 API 服务
 *
 * 调用后端 API 获取新闻资讯
 */

import { API_BASE_URL } from './apiService';

// 新闻分类
export type NewsCategory = 'all' | 'us-stock' | 'a-stock' | 'commodity' | 'crypto' | 'tech';

// 新闻条目接口
export interface NewsItem {
  id: string;
  category: Exclude<NewsCategory, 'all'>;
  title: string;
  summary: string;
  source: string;
  time: string;
  impact?: 'positive' | 'negative' | 'neutral';
}

// 新闻响应
interface NewsResponse {
  items: NewsItem[];
  updateTime: string;
}

// Fallback 新闻数据
const FALLBACK_NEWS: NewsItem[] = [
  {
    id: '1',
    category: 'us-stock',
    title: '特斯拉Q1交付量超预期，股价大幅上涨',
    summary: '特斯拉今日公布Q1交付数据，环比增长显著，超市场预期。分析师上调目标价。',
    source: 'Yahoo Finance',
    time: '2026-04-18 06:30',
    impact: 'positive',
  },
  {
    id: '2',
    category: 'commodity',
    title: '霍尔木兹局势紧张，原油价格大幅下跌',
    summary: '地缘政治风险升温，霍尔木兹海峡紧张局势导致原油价格大幅下跌。',
    source: 'Bloomberg',
    time: '2026-04-18 07:15',
    impact: 'negative',
  },
  {
    id: '3',
    category: 'a-stock',
    title: 'AI芯片板块集体爆发，多股涨停',
    summary: '国家发布AI芯片补贴政策，规模百亿级。寒武纪、海光信息等多股涨停。',
    source: '东方财富',
    time: '2026-04-18 08:00',
    impact: 'positive',
  },
  {
    id: '4',
    category: 'crypto',
    title: 'BTC价格小幅回调，恐慌情绪有所缓解',
    summary: '比特币价格小幅回调，但恐慌贪婪指数显示情绪有所改善。机构买入增加。',
    source: 'CoinDesk',
    time: '2026-04-18 07:45',
    impact: 'neutral',
  },
  {
    id: '5',
    category: 'tech',
    title: '字节跳动发布Gauss 2.0，推理速度提升40%',
    summary: '字节跳动发布新一代大模型Gauss 2.0，在多项基准测试中超越GPT-4。',
    source: 'TechCrunch',
    time: '2026-04-18 09:00',
    impact: 'positive',
  },
  {
    id: '6',
    category: 'us-stock',
    title: '美联储官员重申：降息需更多通胀数据支持',
    summary: '多位美联储官员表示，需要看到更多通胀回落证据才会考虑降息。',
    source: 'Reuters',
    time: '2026-04-18 08:30',
    impact: 'neutral',
  },
  {
    id: '7',
    category: 'a-stock',
    title: '宁德时代辟谣：暂未与特斯拉合作建厂',
    summary: '针对市场传闻，宁德时代澄清目前暂无与特斯拉合作建厂的计划。',
    source: '证券时报',
    time: '2026-04-18 10:15',
    impact: 'neutral',
  },
  {
    id: '8',
    category: 'commodity',
    title: '黄金突破历史新高，避险需求旺盛',
    summary: '避险需求推动黄金价格持续走高，突破历史高位。',
    source: 'Kitco',
    time: '2026-04-18 11:00',
    impact: 'positive',
  },
];

/**
 * 获取市场新闻
 * @param category 新闻分类 (all/us-stock/a-stock/commodity/crypto/tech)
 * @param limit 返回数量限制
 */
export async function fetchNews(category: NewsCategory = 'all', limit: number = 20): Promise<NewsItem[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/news?category=${category}&limit=${limit}`);
    if (response.ok) {
      const data: NewsResponse = await response.json();
      return data.items || [];
    }
  } catch (error) {
    console.error('获取新闻失败:', error);
  }
  return FALLBACK_NEWS;
}

/**
 * 获取快讯 (兼容旧接口)
 */
export async function fetchFastNews(limit: number = 20): Promise<Array<{
  id: string;
  title: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  time: string;
}>> {
  try {
    const news = await fetchNews('all', limit);
    return news.map(item => ({
      id: item.id,
      title: item.title,
      sentiment: (item.impact || 'neutral') as 'positive' | 'negative' | 'neutral',
      time: item.time,
    }));
  } catch (error) {
    console.error('获取快讯失败:', error);
    return [];
  }
}

/**
 * 获取股票相关新闻
 */
export async function fetchStockNews(code: string, limit: number = 10): Promise<Array<{
  id: string;
  title: string;
  content: string;
  source: string;
  time: number;
  tags: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
  relatedStocks: string[];
}>> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/news?category=a-stock&limit=${limit}`);
    if (response.ok) {
      const data: NewsResponse = await response.json();
      return data.items.map(item => ({
        id: item.id,
        title: item.title,
        content: item.summary,
        source: item.source,
        time: new Date(item.time).getTime(),
        tags: [item.category],
        sentiment: (item.impact || 'neutral') as 'positive' | 'negative' | 'neutral',
        relatedStocks: [code],
      }));
    }
  } catch (error) {
    console.error(`获取股票新闻失败 ${code}:`, error);
  }
  return [];
}

/**
 * 搜索新闻
 */
export async function searchNews(keyword: string, limit: number = 20): Promise<NewsItem[]> {
  try {
    const news = await fetchNews('all', 100);
    return news.filter(item =>
      item.title.includes(keyword) ||
      item.summary.includes(keyword)
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
