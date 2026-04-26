import { useState, useEffect } from 'react';
import { Card, Badge } from '../components';
import { fetchNews, NewsCategory, NewsItem } from '../services/api/newsData';

const categories: { key: NewsCategory; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'us-stock', label: '美股' },
  { key: 'a-stock', label: 'A股' },
  { key: 'commodity', label: '大宗' },
  { key: 'crypto', label: '加密' },
  { key: 'tech', label: '科技' },
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
  const [allNews, setAllNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  // 加载新闻数据
  useEffect(() => {
    async function loadNews() {
      setLoading(true);
      const news = await fetchNews('all', 20);
      setAllNews(news);
      setLoading(false);
    }
    loadNews();
  }, []);

  // 切换分类时重新加载
  useEffect(() => {
    async function loadFilteredNews() {
      setLoading(true);
      const news = await fetchNews(activeCategory, 20);
      setAllNews(news);
      setLoading(false);
    }
    loadFilteredNews();
  }, [activeCategory]);

  const filteredNews = allNews;

  const toggleExpand = (id: string) => {
    setExpandedNews(expandedNews === id ? null : id);
  };

  const handleCategoryChange = (category: NewsCategory) => {
    setActiveCategory(category);
    setExpandedNews(null);
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
            onClick={() => handleCategoryChange(cat.key)}
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

      {/* Loading State */}
      {loading && (
        <div className="text-center text-gray-400 py-8">
          <div className="animate-pulse">加载中...</div>
        </div>
      )}

      {/* News List */}
      {!loading && (
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
      )}

      {!loading && filteredNews.length === 0 && (
        <div className="text-center text-gray-400 py-8">
          暂无该分类新闻
        </div>
      )}
    </div>
  );
}
