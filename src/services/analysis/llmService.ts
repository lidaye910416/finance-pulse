/**
 * LLM 服务封装
 * 
 * 支持 MiniMax / OpenAI / Anthropic / DeepSeek / Mock 多provider
 */

import type { LLMConfig, LLMMessage, LLMResponse, LLMProvider } from './types';

// MiniMax API 配置 (兼容 Anthropic 格式)
const MINIMAX_API_KEY = 'sk-cp-tV4TuUIpZt64tdZO3kjFDIydJtrgaSDPDAXNo8zYk8CTHD39wz7vg1JN7_Dqd8LpevwJo-ZozDcpRo1REhX3PaCak4A8M-Rl8MXAEMvGbMoNOSi73B27yoM';
const MINIMAX_BASE_URL = 'https://api.minimaxi.com/anthropic';

const DEFAULT_CONFIGS: Record<LLMProvider, Partial<LLMConfig>> = {
  minimax: {
    model: 'MiniMax-M2.7-0508',
    baseUrl: MINIMAX_BASE_URL,
    apiKey: MINIMAX_API_KEY,
  },
  openai: {
    model: 'gpt-4o-mini',
    baseUrl: 'https://api.openai.com/v1',
  },
  anthropic: {
    model: 'claude-3-haiku-20240307',
    baseUrl: 'https://api.anthropic.com/v1',
  },
  deepseek: {
    model: 'deepseek-chat',
    baseUrl: 'https://api.deepseek.com/v1',
  },
  mock: {
    model: 'mock-v1.0',
    baseUrl: '',
  },
};

class LLMService {
  private config: LLMConfig | null = null;

  configure(config: LLMConfig) {
    this.config = {
      ...DEFAULT_CONFIGS[config.provider],
      ...config,
    };
  }

  // 初始化时自动使用 MiniMax
  initializeWithMiniMax() {
    this.config = {
      provider: 'minimax',
      model: 'MiniMax-M2.7-0508',
      baseUrl: MINIMAX_BASE_URL,
      apiKey: MINIMAX_API_KEY,
    };
    console.log('[LLMService] 已初始化 MiniMax API');
  }

  isConfigured(): boolean {
    return this.config !== null && this.config.apiKey.length > 0;
  }

  getProvider(): string {
    return this.config?.provider || 'mock';
  }

  async complete(
    messages: LLMMessage[],
    options?: { maxTokens?: number; temperature?: number }
  ): Promise<LLMResponse> {
    // 如果未配置，自动使用 MiniMax
    if (!this.config || this.config.provider === 'mock') {
      this.initializeWithMiniMax();
    }

    const { maxTokens = 2048, temperature = 0.7 } = options || {};

    // 确保 config 已初始化
    if (!this.config) {
      this.initializeWithMiniMax();
    }

    try {
      const provider = this.config!.provider;
      if (provider === 'minimax' || provider === 'anthropic') {
        // MiniMax 和 Anthropic 使用相同的 API 格式
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
    const response = await fetch(`${this.config!.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config!.apiKey}`,
      },
      body: JSON.stringify({
        model: this.config!.model,
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
    // Anthropic/MiniMax 使用相同的 API 格式
    const systemMessage = messages.find(m => m.role === 'system');
    const userMessages = messages.filter(m => m.role !== 'system');

    const response = await fetch(`${this.config!.baseUrl}/v1/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.config!.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: this.config!.model,
        max_tokens: maxTokens,
        temperature,
        system: systemMessage?.content,
        messages: userMessages.map(m => ({ role: m.role, content: m.content })),
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('[LLMService] API 错误详情:', errorText);
      throw new Error(`${this.config!.provider} API错误: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    return {
      content: data.content?.[0]?.text || '',
      model: data.model || this.config!.model,
      tokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0),
      finishReason: 'stop',
    };
  }

  private async callDeepSeek(
    messages: LLMMessage[],
    maxTokens: number,
    temperature: number
  ): Promise<LLMResponse> {
    const response = await fetch(`${this.config!.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config!.apiKey}`,
      },
      body: JSON.stringify({
        model: this.config!.model,
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
