/**
 * LLM 设置面板组件
 * 
 * 允许用户选择模型提供商和输入 API Key
 */

import { useState } from 'react';
import { useSettingsStore, LLM_PROVIDERS } from '../../stores/settingsStore';
import { LLMProvider } from '../../services/analysis/types';
import { llmService } from '../../services/analysis/llmService';

interface LLMSettingsProps {
  onClose?: () => void;
}

export function LLMSettings({ onClose }: LLMSettingsProps) {
  const { llmConfig, setProvider, setApiKey, setLLMConfig, resetLLMConfig } = useSettingsStore();
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);

  // 测试连接
  const testConnection = async () => {
    setIsTesting(true);
    setTestResult(null);

    try {
      // 配置 LLM 服务
      llmService.configure({
        provider: llmConfig.provider,
        apiKey: llmConfig.apiKey,
        model: llmConfig.model,
        baseUrl: llmConfig.baseUrl,
      });

      // 发送测试请求
      const response = await llmService.complete([
        { role: 'user', content: '请回复"连接成功"四个字' }
      ], { maxTokens: 50, temperature: 0.1 });

      setTestResult({
        success: true,
        message: `连接成功！模型: ${response.model}, 消耗: ${response.tokens} tokens`,
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: `连接失败: ${error instanceof Error ? error.message : '未知错误'}`,
      });
    } finally {
      setIsTesting(false);
    }
  };

  // 切换 Provider
  const handleProviderChange = (provider: LLMProvider) => {
    setProvider(provider);
    setTestResult(null);
  };

  return (
    <div className="space-y-4">
      {/* 标题 */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">🔧 LLM 设置</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        )}
      </div>

      {/* 提供商选择 */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">模型提供商</label>
        <div className="grid grid-cols-2 gap-2">
          {(Object.keys(LLM_PROVIDERS) as LLMProvider[]).map((provider) => (
            <button
              key={provider}
              onClick={() => handleProviderChange(provider)}
              className={`
                p-3 rounded-xl border transition-all text-left
                ${llmConfig.provider === provider
                  ? 'bg-accent-blue/20 border-accent-blue text-accent-blue'
                  : 'bg-surface-200/50 border-white/10 text-gray-300 hover:border-white/20'
                }
              `}
            >
              <div className="font-medium">{LLM_PROVIDERS[provider].name}</div>
              <div className="text-xs text-gray-500 mt-1">
                {LLM_PROVIDERS[provider].defaultModel}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* API Key 输入 */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">API Key</label>
        <div className="relative">
          <input
            type={showApiKey ? 'text' : 'password'}
            value={llmConfig.apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="输入你的 API Key"
            className="w-full bg-surface-200/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-blue/50 pr-12"
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
          >
            {showApiKey ? '👁️' : '👁️‍🗨️'}
          </button>
        </div>
        {llmConfig.provider !== 'mock' && (
          <a
            href={LLM_PROVIDERS[llmConfig.provider].docsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block mt-2 text-xs text-accent-blue hover:underline"
          >
            获取 {LLM_PROVIDERS[llmConfig.provider].name} API Key →
          </a>
        )}
      </div>

      {/* 模型选择 */}
      <div>
        <label className="block text-sm text-gray-400 mb-2">模型</label>
        <input
          type="text"
          value={llmConfig.model}
          onChange={(e) => setLLMConfig({ model: e.target.value })}
          placeholder="输入模型名称"
          className="w-full bg-surface-200/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-blue/50"
        />
        <div className="mt-2 text-xs text-gray-500">
          推荐模型:
          {llmConfig.provider !== 'mock' && (
            <button
              onClick={() => setLLMConfig({ model: LLM_PROVIDERS[llmConfig.provider].defaultModel })}
              className="ml-2 text-accent-blue hover:underline"
            >
              {LLM_PROVIDERS[llmConfig.provider].defaultModel}
            </button>
          )}
        </div>
      </div>

      {/* API 地址 */}
      {llmConfig.provider !== 'mock' && (
        <div>
          <label className="block text-sm text-gray-400 mb-2">API 地址</label>
          <input
            type="text"
            value={llmConfig.baseUrl}
            onChange={(e) => setLLMConfig({ baseUrl: e.target.value })}
            placeholder="API 基础地址"
            className="w-full bg-surface-200/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-blue/50"
          />
        </div>
      )}

      {/* 测试结果 */}
      {testResult && (
        <div className={`
          p-3 rounded-xl text-sm
          ${testResult.success
            ? 'bg-accent-green/10 border border-accent-green/30 text-accent-green'
            : 'bg-accent-red/10 border border-accent-red/30 text-accent-red'
          }
        `}>
          {testResult.message}
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex gap-2">
        <button
          onClick={testConnection}
          disabled={isTesting || llmConfig.provider === 'mock' || !llmConfig.apiKey}
          className={`
            flex-1 py-3 rounded-xl font-medium transition-all
            ${isTesting
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-accent-blue text-white hover:bg-accent-blue/80'
            }
          `}
        >
          {isTesting ? '测试中...' : '测试连接'}
        </button>
        <button
          onClick={resetLLMConfig}
          className="px-4 py-3 bg-surface-200/50 border border-white/10 rounded-xl text-gray-300 hover:border-white/20 transition-all"
        >
          重置
        </button>
      </div>

      {/* 提示 */}
      <div className="text-xs text-gray-500 space-y-1">
        <p>💡 API Key 仅保存在本地浏览器中</p>
        <p>💡 支持 OpenAI、MiniMax、Anthropic、DeepSeek</p>
        <p>💡 MiniMax 已预配置，可直接使用</p>
      </div>
    </div>
  );
}
