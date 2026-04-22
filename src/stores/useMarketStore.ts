/**
 * FinancePulse 市场数据状态管理
 * 
 * 使用 Zustand 管理市场数据状态
 * 与 AutoUpdateService 集成实现数据自动更新
 */

import { create } from 'zustand';
import { DataType } from '../services/data';
import { getAutoUpdateService, UpdateResult, TaskStatus } from '../services/autoUpdate';

// ========== 类型定义 ==========

export interface MarketQuotes {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

export interface FearGreedIndex {
  value: number;
  phase: string;
}

export interface NorthboundData {
  value: number;
  trend: 'up' | 'down';
  history: number[];
}

export interface LimitUpDown {
  limitUp: number;
  limitDown: number;
  炸板率?: number;
}

export interface MacroData {
  gdp?: number;
  cpi?: number;
  ppi?: number;
  pmi?: number;
  lpr?: number;
  m2?: number;
}

export interface NewsItem {
  id: string;
  title: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  time: string;
  source?: string;
}

// ========== Store 接口 ==========

interface MarketState {
  // 数据
  quotes: MarketQuotes[];
  fearGreed: FearGreedIndex;
  northbound: NorthboundData;
  limitUpDown: LimitUpDown;
  macroData: MacroData;
  news: NewsItem[];
  
  // 状态
  isLoading: boolean;
  lastUpdate: Date | null;
  updateErrors: Map<string, string>;
  
  // 任务状态
  taskStatuses: TaskStatus[];
  
  // 操作
  refreshAll: () => Promise<void>;
  refreshData: (dataType: DataType) => Promise<void>;
  setQuotes: (quotes: MarketQuotes[]) => void;
  setFearGreed: (data: FearGreedIndex) => void;
  setNorthbound: (data: NorthboundData) => void;
  setLimitUpDown: (data: LimitUpDown) => void;
  setMacroData: (data: MacroData) => void;
  setNews: (news: NewsItem[]) => void;
}

// ========== 默认值 ==========

const defaultFearGreed: FearGreedIndex = {
  value: 50,
  phase: '中性',
};

const defaultNorthbound: NorthboundData = {
  value: 0,
  trend: 'up',
  history: [],
};

const defaultLimitUpDown: LimitUpDown = {
  limitUp: 0,
  limitDown: 0,
};

const defaultMacroData: MacroData = {
  gdp: undefined,
  cpi: undefined,
  ppi: undefined,
  pmi: undefined,
  lpr: undefined,
  m2: undefined,
};

// ========== 创建 Store ==========

export const useMarketStore = create<MarketState>((set) => ({
  // 初始状态
  quotes: [],
  fearGreed: defaultFearGreed,
  northbound: defaultNorthbound,
  limitUpDown: defaultLimitUpDown,
  macroData: defaultMacroData,
  news: [],
  isLoading: false,
  lastUpdate: null,
  updateErrors: new Map<string, string>(),
  taskStatuses: [],
  
  // 操作方法
  setQuotes: (quotes: MarketQuotes[]) => set({ quotes, lastUpdate: new Date() }),
  setFearGreed: (data: FearGreedIndex) => set({ fearGreed: data }),
  setNorthbound: (data: NorthboundData) => set({ northbound: data }),
  setLimitUpDown: (data: LimitUpDown) => set({ limitUpDown: data }),
  setMacroData: (data: MacroData) => set({ macroData: data }),
  setNews: (news: NewsItem[]) => set({ news }),
  
  refreshAll: async () => {
    set({ isLoading: true });
    try {
      const service = getAutoUpdateService();
      
      // 触发所有任务更新
      await service.triggerUpdate('quotes');
      await service.triggerUpdate('fear_greed');
      await service.triggerUpdate('northbound');
      await service.triggerUpdate('limit_up_down');
      
      set({ lastUpdate: new Date(), isLoading: false });
    } catch (error) {
      console.error('刷新数据失败:', error);
      set({ isLoading: false });
    }
  },
  
  refreshData: async (dataType: DataType) => {
    const service = getAutoUpdateService();
    await service.triggerUpdate(dataType);
  },
}));

// ========== 自动更新订阅 ==========

// 初始化自动更新并订阅数据更新
let isInitialized = false;

export function initializeAutoUpdate(): void {
  if (isInitialized) return;
  isInitialized = true;
  
  const service = getAutoUpdateService();
  const store = useMarketStore.getState();
  
  // 启动服务
  service.start();
  
  // 订阅更新结果
  service.subscribe((result: UpdateResult) => {
    if (!result.success) {
      console.error(`更新失败: ${result.taskId}`, result.error);
      return;
    }
    
    // 根据任务ID更新 store
    switch (result.taskId) {
      case 'quotes':
        if (result.data) {
          const quotes: MarketQuotes[] = result.data.map((item: any) => ({
            symbol: item.f12,
            name: item.f14,
            price: item.f2 / 100,
            change: item.f3,
            changePercent: item.f3,
          }));
          store.setQuotes(quotes);
        }
        break;
      case 'fear_greed':
        if (result.data) {
          store.setFearGreed(result.data);
        }
        break;
      case 'northbound':
        if (result.data && result.data.length > 0) {
          const data = result.data[0] as any;
          store.setNorthbound({
            value: (data.total as number) ?? 0,
            trend: ((data.total as number) ?? 0) >= 0 ? 'up' : 'down',
            history: store.northbound.history,
          });
        }
        break;
      case 'limit_up_down':
        if (result.data) {
          store.setLimitUpDown(result.data);
        }
        break;
    }
  });
  
  // 定期更新任务状态
  setInterval(() => {
    const statuses = service.getAllTaskStatuses();
    useMarketStore.setState({ taskStatuses: statuses });
  }, 5000);
}
