/**
 * LLM 服务封装
 * 
 * 支持 MiniMax / OpenAI / Anthropic / DeepSeek / Mock 多provider
 * 配置从 settingsStore 读取
 */

import type { LLMMessage, LLMResponse, LLMProvider } from './types';
import { useSettingsStore } from '../../stores/settingsStore';

// 从设置中获取配置
function getConfig() {
  const { llmConfig } = useSettingsStore.getState();
  return llmConfig;
}

// 默认配置 (MiniMax)
const DEFAULT_CONFIG = {
  provider: 'minimax' as LLMProvider,
  apiKey: 'sk-cp-tV4TuUIpZt64tdZO3kjFDIydJtrgaSDPDAXNo8zYk8CTHD39wz7vg1JN7_Dqd8LpevwJo-ZozDcpRo1REhX3PaCak4A8M-Rl8MXAEMvGbMoNOSi73B27yoM',
  model: 'MiniMax-M2.7-0508',
  baseUrl: 'https://api.minimaxi.com/anthropic',
};

class LLMService {
  private config = DEFAULT_CONFIG;
  private initialized = false;

  configure(config?: { provider: LLMProvider; apiKey: string; model: string; baseUrl: string }) {
    if (config) {
      this.config = config;
    } else {
      // 从设置中读取
      const storeConfig = getConfig();
      this.config = storeConfig;
    }
    this.initialized = true;
    console.log('[LLMService] 配置已更新:', this.config.provider, this.config.model);
  }

  // 初始化时自动使用设置中的配置
  private ensureInitialized() {
    if (!this.initialized) {
      this.configure();
    }
  }

  isConfigured(): boolean {
    return this.config?.apiKey?.length > 0;
  }

  getProvider(): string {
    this.ensureInitialized();
    return this.config?.provider || 'mock';
  }

  getCurrentConfig() {
    this.ensureInitialized();
    return this.config;
  }

  async complete(
    messages: LLMMessage[],
    options?: { maxTokens?: number; temperature?: number }
  ): Promise<LLMResponse> {
    this.ensureInitialized();
    
    // 每次调用时重新读取配置（支持动态修改）
    const storeConfig = getConfig();
    this.config = storeConfig;

    const { maxTokens = 2048, temperature = 0.7 } = options || {};

    try {
      const provider = this.config.provider;
      
      if (provider === 'mock') {
        return {
          content: '这是模拟分析结果。配置 LLM 后可获得真实分析。',
          model: 'mock-v1.0',
          tokens: 100,
          finishReason: 'stop',
        };
      }
      
      if (provider === 'minimax' || provider === 'anthropic') {
        return await this.callAnthropic(messages, maxTokens, temperature);
      } else if (provider === 'openai') {
        return await this.callOpenAI(messages, maxTokens, temperature);
      } else if (provider === 'deepseek') {
        return await this.callDeepSeek(messages, maxTokens, temperature);
      }

      throw new Error(`不支持的 LLM Provider: ${provider}`);
    } catch (error) {
      console.error('[LLMService] 调用失败:', error);
      throw error;
    }
  }

  private async callOpenAI(
    messages: LLMMessage[],
    maxTokens: number,
    temperature: number
  ): Promise<LLMResponse> {
    const response = await fetch(`${this.config.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`,
      },
      body: JSON.stringify({
        model: this.config.model,
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        max_tokens: maxTokens,
        temperature,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenAI API错误: ${response.status} - ${error}`);
    }

    const data = await response.json();
    return {
      content: data.choices[0]?.message?.content || '',
      model: data.model,
      tokens: data.usage?.total_tokens || 0,
      finishReason: data.choices[0]?.finish_reason || 'stop',
    };
  }

  private async callAnthropic(
    messages: LLMMessage[],
    maxTokens: number,
    temperature: number
  ): Promise<LLMResponse> {
    const systemMessage = messages.find(m => m.role === 'system');
    const userMessages = messages.filter(m => m.role !== 'system');

    const response = await fetch(`${this.config.baseUrl}/v1/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.config.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: this.config.model,
        max_tokens: maxTokens,
        temperature,
        system: systemMessage?.content,
        messages: userMessages.map(m => ({ role: m.role, content: m.content })),
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[LLMService] API 错误详情:', errorText);
      throw new Error(`${this.config.provider} API错误: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      content: data.content?.[0]?.text || '',
      model: data.model || this.config.model,
      tokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0),
      finishReason: 'stop',
    };
  }

  private async callDeepSeek(
    messages: LLMMessage[],
    maxTokens: number,
    temperature: number
  ): Promise<LLMResponse> {
    const response = await fetch(`${this.config.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.apiKey}`,
      },
      body: JSON.stringify({
        model: this.config.model,
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        max_tokens: maxTokens,
        temperature,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`DeepSeek API错误: ${response.status} - ${error}`);
    }

    const data = await response.json();
    return {
      content: data.choices[0]?.message?.content || '',
      model: data.model,
      tokens: data.usage?.total_tokens || 0,
      finishReason: data.choices[0]?.finish_reason || 'stop',
    };
  }
}

// 单例导出
export const llmService = new LLMService();
export default llmService;
