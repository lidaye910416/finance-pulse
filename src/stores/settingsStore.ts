/**
 * FinancePulse 设置状态管理
 * 
 * 管理 LLM 配置、主题设置等
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { LLMProvider } from '../services/analysis/types';

// ========== LLM 配置接口 ==========

export interface LLMConfig {
  provider: LLMProvider;
  apiKey: string;
  model: string;
  baseUrl: string;
}

// ========== Store 接口 ==========

interface SettingsState {
  // LLM 配置
  llmConfig: LLMConfig;
  
  // 设置操作
  setLLMConfig: (config: Partial<LLMConfig>) => void;
  resetLLMConfig: () => void;
  
  // 便捷方法
  setProvider: (provider: LLMProvider) => void;
  setApiKey: (apiKey: string) => void;
}

// ========== 默认配置 (不包含 API Key，用户需要自行输入) ==========

const DEFAULT_LLM_CONFIG: LLMConfig = {
  provider: 'minimax',
  apiKey: '',  // 用户必须自行输入 API Key
  model: 'MiniMax-M2.7-0508',
  baseUrl: 'https://api.minimaxi.com/anthropic',
};

// ========== Provider 配置 ==========

export const LLM_PROVIDERS: Record<LLMProvider, { name: string; defaultModel: string; baseUrl: string; docsUrl: string }> = {
  minimax: {
    name: 'MiniMax',
    defaultModel: 'MiniMax-M2.7-0508',
    baseUrl: 'https://api.minimaxi.com/anthropic',
    docsUrl: 'https://www.minimaxi.com/',
  },
  openai: {
    name: 'OpenAI',
    defaultModel: 'gpt-4o-mini',
    baseUrl: 'https://api.openai.com/v1',
    docsUrl: 'https://platform.openai.com/',
  },
  anthropic: {
    name: 'Anthropic (Claude)',
    defaultModel: 'claude-3-haiku-20240307',
    baseUrl: 'https://api.anthropic.com/v1',
    docsUrl: 'https://www.anthropic.com/',
  },
  deepseek: {
    name: 'DeepSeek',
    defaultModel: 'deepseek-chat',
    baseUrl: 'https://api.deepseek.com/v1',
    docsUrl: 'https://platform.deepseek.com/',
  },
  mock: {
    name: 'Mock (模拟)',
    defaultModel: 'mock-v1.0',
    baseUrl: '',
    docsUrl: '',
  },
};

// ========== 创建 Store ==========

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      llmConfig: DEFAULT_LLM_CONFIG,
      
      setLLMConfig: (config) => 
        set((state) => ({
          llmConfig: { ...state.llmConfig, ...config },
        })),
      
      resetLLMConfig: () => 
        set({ llmConfig: DEFAULT_LLM_CONFIG }),
      
      setProvider: (provider) => {
        const providerConfig = LLM_PROVIDERS[provider];
        set((state) => ({
          llmConfig: {
            ...state.llmConfig,
            provider,
            model: providerConfig.defaultModel,
            baseUrl: providerConfig.baseUrl,
          },
        }));
      },
      
      setApiKey: (apiKey) => 
        set((state) => ({
          llmConfig: { ...state.llmConfig, apiKey },
        })),
    }),
    {
      name: 'financepulse-settings',
    }
  )
);

// ========== 导出便捷函数 ==========

export function getLLMConfig(): LLMConfig {
  return useSettingsStore.getState().llmConfig;
}
