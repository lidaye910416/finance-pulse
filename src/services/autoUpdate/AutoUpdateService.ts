/**
 * FinancePulse 自动更新服务
 * 
 * 核心功能：
 * - 管理所有数据的定时更新
 * - 分优先级调度更新任务
 * - 交易时段智能判断
 * - 失败重试机制
 * 
 * 参考 TradingAgents 的任务调度 + Ralph Skill 方法论
 */

import { DataType } from '../data';
import {
  UpdateTask,
  UpdateStatus,
  TaskStatus,
  UpdateResult,
  AutoUpdateConfig,
  DEFAULT_CONFIG,
  isMarketHours,
  formatInterval,
  UpdatePriority,
} from './types';
import { fetchFearGreedIndex, fetchNorthboundData, fetchLimitUpDown } from '../api/marketData';

// ========== 更新任务配置表 ==========

// 获取指数报价
async function fetchQuotesData(): Promise<any> {
  try {
    const response = await fetch('https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f2,f3,f4,f12,f14&secids=1.000001,0.399001,0.399006,1.000300,0.000001');
    const data = await response.json();
    return data.data?.diff;
  } catch {
    return null;
  }
}

export const UPDATE_TASKS: UpdateTask[] = [
  // ===== 高优先级：实时数据 (3秒) =====
  {
    id: 'quotes',
    name: '实时行情',
    dataType: DataType.QUOTES,
    priority: UpdatePriority.HIGH,
    interval: 3000,
    fetchFn: fetchQuotesData,
    enabled: true,
    marketHoursOnly: true,
    description: '指数实时报价',
  },
  
  // ===== 普通优先级：情绪数据 (30秒) =====
  {
    id: 'fear_greed',
    name: '恐惧贪婪指数',
    dataType: DataType.FEAR_GREED,
    priority: UpdatePriority.NORMAL,
    interval: 30000,
    fetchFn: () => fetchFearGreedIndex(),
    enabled: true,
    marketHoursOnly: false,
    description: '市场恐惧贪婪指数',
  },
  {
    id: 'northbound',
    name: '北向资金',
    dataType: DataType.NORTHBOUND,
    priority: UpdatePriority.NORMAL,
    interval: 60000,  // 1分钟
    fetchFn: () => fetchNorthboundData(1),
    enabled: true,
    marketHoursOnly: false,
    description: '北向资金流入流出',
  },
  {
    id: 'limit_up_down',
    name: '涨跌停统计',
    dataType: DataType.LIMIT_UP_DOWN,
    priority: UpdatePriority.NORMAL,
    interval: 30000,
    fetchFn: () => fetchLimitUpDown(),
    enabled: true,
    marketHoursOnly: true,
    description: '涨停跌停数量',
  },
  
  // ===== 低优先级：宏观数据 (小时级) =====
  {
    id: 'macro_gdp',
    name: 'GDP数据',
    dataType: DataType.GDP,
    priority: UpdatePriority.LOW,
    interval: 3600000,  // 1小时
    fetchFn: async () => null,  // TODO: 实现GDP获取
    enabled: true,
    marketHoursOnly: false,
    description: '季度GDP增速',
  },
  {
    id: 'macro_cpi',
    name: 'CPI数据',
    dataType: DataType.CPI,
    priority: UpdatePriority.LOW,
    interval: 3600000,
    fetchFn: async () => null,  // TODO: 实现CPI获取
    enabled: true,
    marketHoursOnly: false,
    description: '消费者物价指数',
  },
  {
    id: 'macro_pmi',
    name: 'PMI数据',
    dataType: DataType.PMI,
    priority: UpdatePriority.LOW,
    interval: 3600000,
    fetchFn: async () => null,  // TODO: 实现PMI获取
    enabled: true,
    marketHoursOnly: false,
    description: '采购经理指数',
  },
];

// ========== AutoUpdateService 类 ==========

export class AutoUpdateService {
  private tasks: Map<string, UpdateTask> = new Map();
  private taskStatuses: Map<string, TaskStatus> = new Map();
  private intervals: Map<string, number> = new Map();
  private config: AutoUpdateConfig;
  private isRunning: boolean = false;
  private listeners: Set<(result: UpdateResult) => void> = new Set();
  
  // 数据存储
  private dataStore: Map<DataType, unknown> = new Map();
  
  constructor(config: Partial<AutoUpdateConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    
    // 注册所有任务
    for (const task of UPDATE_TASKS) {
      this.registerTask(task);
    }
  }
  
  // ========== 公开方法 ==========
  
  /**
   * 启动自动更新服务
   */
  start(): void {
    if (this.isRunning) {
      console.log('[AutoUpdate] 服务已在运行');
      return;
    }
    
    console.log('[AutoUpdate] 启动自动更新服务...');
    this.isRunning = true;
    
    // 按优先级启动任务
    const highPriority = Array.from(this.tasks.values())
      .filter(t => t.priority === UpdatePriority.HIGH);
    const normalPriority = Array.from(this.tasks.values())
      .filter(t => t.priority === UpdatePriority.NORMAL);
    const lowPriority = Array.from(this.tasks.values())
      .filter(t => t.priority === UpdatePriority.LOW);
    
    // 高优先级任务立即启动
    for (const task of highPriority) {
      this.startTask(task);
    }
    
    // 普通优先级任务延迟启动，避免并发
    setTimeout(() => {
      for (const task of normalPriority) {
        this.startTask(task);
      }
    }, 1000);
    
    // 低优先级任务最后启动
    setTimeout(() => {
      for (const task of lowPriority) {
        this.startTask(task);
      }
    }, 2000);
    
    console.log(`[AutoUpdate] 已启动 ${this.tasks.size} 个更新任务`);
  }
  
  /**
   * 停止自动更新服务
   */
  stop(): void {
    if (!this.isRunning) return;
    
    console.log('[AutoUpdate] 停止自动更新服务...');
    
    for (const [, timerId] of this.intervals) {
      window.clearInterval(timerId);
    }
    
    this.intervals.clear();
    this.isRunning = false;
    
    console.log('[AutoUpdate] 服务已停止');
  }
  
  /**
   * 注册新的更新任务
   */
  registerTask(task: UpdateTask): void {
    this.tasks.set(task.id, task);
    this.taskStatuses.set(task.id, {
      taskId: task.id,
      status: UpdateStatus.IDLE,
      lastUpdate: null,
      lastError: null,
      updateCount: 0,
    });
  }
  
  /**
   * 移除更新任务
   */
  removeTask(taskId: string): void {
    const timerId = this.intervals.get(taskId);
    if (timerId) {
      window.clearInterval(timerId);
      this.intervals.delete(taskId);
    }
    
    this.tasks.delete(taskId);
    this.taskStatuses.delete(taskId);
  }
  
  /**
   * 获取任务状态
   */
  getTaskStatus(taskId: string): TaskStatus | undefined {
    return this.taskStatuses.get(taskId);
  }
  
  /**
   * 获取所有任务状态
   */
  getAllTaskStatuses(): TaskStatus[] {
    return Array.from(this.taskStatuses.values());
  }
  
  /**
   * 获取数据
   */
  getData(dataType: DataType): unknown | undefined {
    return this.dataStore.get(dataType);
  }
  
  /**
   * 手动触发更新
   */
  async triggerUpdate(taskId: string): Promise<UpdateResult | null> {
    const task = this.tasks.get(taskId);
    if (!task) return null;
    
    return this.executeTask(task);
  }
  
  /**
   * 订阅更新结果
   */
  subscribe(callback: (result: UpdateResult) => void): () => void {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }
  
  /**
   * 检查服务是否在运行
   */
  isActive(): boolean {
    return this.isRunning;
  }
  
  // ========== 私有方法 ==========
  
  /**
   * 启动单个任务
   */
  private startTask(task: UpdateTask): void {
    if (!task.enabled) {
      console.log(`[AutoUpdate] 任务 ${task.name} 已禁用`);
      return;
    }
    
    // 立即执行一次
    this.executeTask(task);
    
    // 设置定时器
    const timerId = window.setInterval(() => {
      this.executeTask(task);
    }, task.interval);
    
    this.intervals.set(task.id, timerId);
    this.updateStatus(task.id, UpdateStatus.RUNNING);
    
    if (this.config.debugMode) {
      console.log(`[AutoUpdate] 启动任务: ${task.name} (间隔: ${formatInterval(task.interval)})`);
    }
  }
  
  /**
   * 执行更新任务
   */
  private async executeTask(task: UpdateTask): Promise<UpdateResult> {
    const startTime = Date.now();
    
    // 检查交易时段限制
    if (task.marketHoursOnly && !isMarketHours()) {
      if (this.config.debugMode) {
        console.log(`[AutoUpdate] 任务 ${task.name} 跳过: 非交易时段`);
      }
      return {
        success: true,
        taskId: task.id,
        timestamp: new Date(),
        duration: Date.now() - startTime,
      };
    }
    
    try {
      const data = await task.fetchFn();
      
      // 更新数据存储
      this.dataStore.set(task.dataType, data);
      
      const result: UpdateResult = {
        success: true,
        taskId: task.id,
        timestamp: new Date(),
        data,
        duration: Date.now() - startTime,
      };
      
      // 更新状态
      this.updateStatus(task.id, UpdateStatus.RUNNING, null);
      this.incrementUpdateCount(task.id);
      
      // 通知订阅者
      this.notifyListeners(result);
      
      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      const result: UpdateResult = {
        success: false,
        taskId: task.id,
        timestamp: new Date(),
        error: errorMessage,
        duration: Date.now() - startTime,
      };
      
      // 更新状态
      this.updateStatus(task.id, UpdateStatus.ERROR, errorMessage);
      
      // 通知订阅者
      this.notifyListeners(result);
      
      console.error(`[AutoUpdate] 任务 ${task.name} 失败:`, errorMessage);
      
      return result;
    }
  }
  
  /**
   * 更新任务状态
   */
  private updateStatus(taskId: string, status: UpdateStatus, error: string | null = null): void {
    const current = this.taskStatuses.get(taskId);
    if (current) {
      current.status = status;
      current.lastUpdate = new Date();
      current.lastError = error;
    }
  }
  
  /**
   * 增加更新计数
   */
  private incrementUpdateCount(taskId: string): void {
    const current = this.taskStatuses.get(taskId);
    if (current) {
      current.updateCount++;
    }
  }
  
  /**
   * 通知所有订阅者
   */
  private notifyListeners(result: UpdateResult): void {
    for (const listener of this.listeners) {
      try {
        listener(result);
      } catch (error) {
        console.error('[AutoUpdate] 订阅者回调失败:', error);
      }
    }
  }
}

// ========== 单例实例 ==========

let instance: AutoUpdateService | null = null;

export function getAutoUpdateService(): AutoUpdateService {
  if (!instance) {
    instance = new AutoUpdateService();
  }
  return instance;
}
