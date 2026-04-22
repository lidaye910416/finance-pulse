/**
 * LLM 服务封装
 * 
 * 支持 OpenAI / Anthropic / DeepSeek / Mock 多provider
 */

import type { LLMConfig, LLMMessage, LLMResponse, LLMProvider } from './types';

const DEFAULT_CONFIGS: Record<LLMProvider, Partial<LLMConfig>> = {
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

  isConfigured(): boolean {
    return this.config !== null && this.config.apiKey.length > 0;
  }

  async complete(
    messages: LLMMessage[],
    options?: { maxTokens?: number; temperature?: number }
  ): Promise<LLMResponse> {
    // Mock 模式直接返回模拟数据
    if (!this.config || this.config.provider === 'mock') {
      return {
        content: '这是模拟分析结果。实际应用中会调用真实 LLM API。',
        model: 'mock-v1.0',
        tokens: 100,
        finishReason: 'stop',
      };
    }

    const { maxTokens = 2048, temperature = 0.7 } = options || {};

    try {
      if (this.config.provider === 'openai') {
        return await this.callOpenAI(messages, maxTokens, temperature);
      } else if (this.config.provider === 'anthropic') {
        return await this.callAnthropic(messages, maxTokens, temperature);
      } else if (this.config.provider === 'deepseek') {
        return await this.callDeepSeek(messages, maxTokens, temperature);
      }

      throw new Error(`不支持的 LLM Provider: ${this.config.provider}`);
    } catch (error) {
      console.error('LLM调用失败:', error);
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
    // Anthropic 使用不同的 API 格式
    const systemMessage = messages.find(m => m.role === 'system');
    const userMessages = messages.filter(m => m.role !== 'system');

    const response = await fetch(`${this.config!.baseUrl}/messages`, {
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
      const error = await response.text();
      throw new Error(`Anthropic API错误: ${response.status} - ${error}`);
    }

    const data = await response.json();
    return {
      content: data.content[0]?.text || '',
      model: data.model,
      tokens: data.usage?.input_tokens + data.usage?.output_tokens || 0,
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
