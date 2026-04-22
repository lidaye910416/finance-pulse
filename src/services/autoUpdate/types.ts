/**
 * FinancePulse 自动更新系统类型定义
 * 
 * 定义更新任务、优先级、调度配置等核心类型
 * 参考 Ralph Skill 方法论：类型安全、可扩展
 */

import { DataType } from '../data';

// ========== 更新优先级 ==========
export enum UpdatePriority {
  HIGH = 1,      // 高优先级 - 实时行情，3秒
  NORMAL = 2,    // 普通优先级 - 情绪数据，30秒
  LOW = 3,       // 低优先级 - 宏观数据，小时级
}

// ========== 更新任务接口 ==========
export interface UpdateTask {
  id: string;                    // 任务ID
  name: string;                  // 中文名称
  dataType: DataType;           // 对应的数据类型
  priority: UpdatePriority;     // 更新优先级
  interval: number;              // 更新间隔(毫秒)
  fetchFn: () => Promise<any>;   // 数据获取函数
  enabled: boolean;              // 是否启用
  marketHoursOnly: boolean;      // 是否只在交易时段更新
  description?: string;         // 描述
}

// ========== 更新状态 ==========
export enum UpdateStatus {
  IDLE = 'idle',           // 空闲
  RUNNING = 'running',     // 运行中
  PAUSED = 'paused',       // 暂停
  ERROR = 'error',         // 错误
}

export interface TaskStatus {
  taskId: string;
  status: UpdateStatus;
  lastUpdate: Date | null;
  lastError: string | null;
  updateCount: number;      // 更新次数
}

// ========== 更新结果 ==========
export interface UpdateResult {
  success: boolean;
  taskId: string;
  timestamp: Date;
  data?: any;
  error?: string;
  duration: number;        // 耗时(ms)
}

// ========== AutoUpdateService 配置 ==========
export interface AutoUpdateConfig {
  // 是否启用自动更新
  enabled: boolean;
  
  // 是否只在交易时段更新高优先级数据
  marketHoursOnly: boolean;
  
  // 最大并发更新数
  maxConcurrentUpdates: number;
  
  // 更新失败重试次数
  maxRetries: number;
  
  // 重试间隔(ms)
  retryInterval: number;
  
  // 是否启用调试模式
  debugMode: boolean;
}

// 默认配置
export const DEFAULT_CONFIG: AutoUpdateConfig = {
  enabled: true,
  marketHoursOnly: true,
  maxConcurrentUpdates: 3,
  maxRetries: 3,
  retryInterval: 5000,
  debugMode: false,
};

// ========== 工具函数 ==========

/**
 * 判断是否在交易时段
 */
export function isMarketHours(): boolean {
  const now = new Date();
  const day = now.getDay();
  const hour = now.getHours();
  const minute = now.getMinutes();
  
  // 周末不交易
  if (day === 0 || day === 6) return false;
  
  // 9:30 - 11:30 上午盘
  if (hour === 9 && minute >= 30) return true;
  if (hour >= 10 && hour < 12) return true;
  
  // 13:00 - 15:00 下午盘
  if (hour >= 13 && hour < 15) return true;
  
  return false;
}

/**
 * 获取下次交易时段开始时间
 */
export function getNextMarketOpen(): Date {
  const now = new Date();
  const next = new Date(now);
  
  // 如果已经收盘，设置下一天
  if (now.getHours() >= 15) {
    next.setDate(next.getDate() + 1);
  }
  
  // 找到下一个工作日
  while (next.getDay() === 0 || next.getDay() === 6) {
    next.setDate(next.getDate() + 1);
  }
  
  // 设置为 9:30
  next.setHours(9, 30, 0, 0);
  
  return next;
}

/**
 * 格式化更新时间间隔
 */
export function formatInterval(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${Math.round(ms / 1000)}秒`;
  if (ms < 3600000) return `${Math.round(ms / 60000)}分钟`;
  return `${Math.round(ms / 3600000)}小时`;
}
