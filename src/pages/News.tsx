import { useState } from 'react';
import { Card, Badge } from '../components';

type NewsCategory = 'all' | 'us-stock' | 'a-stock' | 'commodity' | 'crypto' | 'tech';

interface NewsItem {
  id: string;
  category: Exclude<NewsCategory, 'all'>;
  title: string;
  summary: string;
  source: string;
  time: string;
  impact?: 'positive' | 'negative' | 'neutral';
}

const categories: { key: NewsCategory; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'us-stock', label: '美股' },
  { key: 'a-stock', label: 'A股' },
  { key: 'commodity', label: '大宗' },
  { key: 'crypto', label: '加密' },
  { key: 'tech', label: '科技' },
];

const allNews: NewsItem[] = [
  {
    id: '1',
    category: 'us-stock',
    title: '特斯拉Q1交付量超预期，股价+5.2%',
    summary: '特斯拉今日公布Q1交付数据，环比+20%，超市场预期。分析师上调目标价至200美元。',
    source: 'Yahoo Finance',
    time: '2026-04-18 06:30',
    impact: 'positive',
  },
  {
    id: '2',
    category: 'commodity',
    title: '霍尔木兹局势紧张，原油单日-9.41%',
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
    title: 'BTC $75,951 (-1.86%)，恐慌情绪有所缓解',
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
    title: '黄金突破$4,879，创历史新高',
    summary: '避险需求推动黄金价格持续走高，突破$4,879美元/盎司。',
    source: 'Kitco',
    time: '2026-04-18 11:00',
    impact: 'positive',
  },
];

const categoryIcons: Record<Exclude<NewsCategory, 'all'>, string> = {
  'us-stock': '🟢',
  'a-stock': '🟡',
  'commodity': '🔴',
  'crypto': '🟣',
  'tech': '🔵',
};

export function News() {
  const [activeCategory, setActiveCategory] = useState<NewsCategory>('all');
  const [expandedNews, setExpandedNews] = useState<string | null>(null);

  const filteredNews = activeCategory === 'all'
    ? allNews
    : allNews.filter(news => news.category === activeCategory);

  const toggleExpand = (id: string) => {
    setExpandedNews(expandedNews === id ? null : id);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">📰 市场新闻</h2>
        <button className="text-finance-blue text-sm hover:underline">[筛选 ▼]</button>
      </div>

      {/* Category Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {categories.map((cat) => (
          <button
            key={cat.key}
            onClick={() => setActiveCategory(cat.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeCategory === cat.key
                ? 'bg-finance-blue text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* News List */}
      <div className="space-y-3">
        {filteredNews.map((news) => (
          <Card key={news.id} className="cursor-pointer" onClick={() => toggleExpand(news.id)}>
            <div className="flex items-start gap-3">
              <span className="text-xl">{categoryIcons[news.category]}</span>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Badge
                    text={categories.find(c => c.key === news.category)?.label || ''}
                    variant={
                      news.category === 'us-stock' ? 'green' :
                      news.category === 'a-stock' ? 'yellow' :
                      news.category === 'commodity' ? 'red' :
                      news.category === 'crypto' ? 'purple' : 'blue'
                    }
                  />
                  <span className="text-gray-500 text-xs">
                    {news.source} · {news.time}
                  </span>
                </div>
                <h3 className="text-white font-medium">{news.title}</h3>

                {/* Expandable Details */}
                {expandedNews === news.id && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <p className="text-gray-300 text-sm mb-3">{news.summary}</p>

                    {/* Event-driven Analysis (when expanded) */}
                    <div className="bg-gray-700/50 rounded-lg p-3 text-sm">
                      <div className="flex items-center gap-2 text-finance-blue mb-2">
                        <span>🔍</span>
                        <span className="font-medium">事件驱动分析</span>
                      </div>
                      <div className="space-y-2 text-gray-300">
                        <p>
                          <span className="text-gray-400">性质：</span>
                          {news.impact === 'positive' ? '实质性利好（影响利润）' :
                           news.impact === 'negative' ? '实质性利空（影响利润）' :
                           '中性消息（短期情绪影响有限）'}
                        </p>
                        <p>
                          <span className="text-gray-400">程度：</span>
                          {news.impact === 'positive' ? '量化影响待财报验证，短期情绪催化' :
                           news.impact === 'negative' ? '需关注后续进展，注意风险控制' :
                           '影响有限，关注后续发展'}
                        </p>
                        <p>
                          <span className="text-gray-400">市场反应：</span>
                          {news.impact === 'positive' ? '已部分定价，但仍有空间' :
                           news.impact === 'negative' ? '可能继续消化，等待企稳' :
                           '基本消化完毕'}
                        </p>
                        <p>
                          <span className="text-gray-400">决策：</span>
                          {news.impact === 'positive' ? '持有/小幅加仓，止损位-8%' :
                           news.impact === 'negative' ? '观望为主，不盲目抄底' :
                           '中性策略，关注主线机会'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="text-gray-500 text-xs mt-2 text-right">
              {expandedNews === news.id ? '点击收起 ▲' : '点击展开 ▼'}
            </div>
          </Card>
        ))}
      </div>

      {filteredNews.length === 0 && (
        <div className="text-center text-gray-400 py-8">
          暂无该分类新闻
        </div>
      )}
    </div>
  );
}
