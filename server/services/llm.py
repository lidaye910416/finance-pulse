"""
LLM 服务

支持多种 LLM Provider:
- MiniMax (Anthropic compatible)
- OpenAI
- Anthropic
- DeepSeek
"""

import os
import json
from typing import Literal

import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """LLM 服务类"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "minimax")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "MiniMax-M2.7-0508")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.minimaxi.com/anthropic")
        
        print(f"[LLMService] 初始化完成: provider={self.provider}, model={self.model}")
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_key)
    
    def get_provider(self) -> str:
        """获取当前 provider"""
        return self.provider
    
    async def complete(
        self,
        messages: list[dict],
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> dict:
        """
        调用 LLM
        
        Args:
            messages: 消息列表 [{"role": "system"|"user"|"assistant", "content": "..."}]
            max_tokens: 最大 token 数
            temperature: 温度参数
            
        Returns:
            {"content": "...", "model": "...", "tokens": 100}
        """
        if not self.api_key:
            raise ValueError("LLM API Key 未配置，请设置 LLM_API_KEY 环境变量")
        
        if self.provider == "minimax" or self.provider == "anthropic":
            return await self._call_anthropic(messages, max_tokens, temperature)
        elif self.provider == "openai":
            return await self._call_openai(messages, max_tokens, temperature)
        elif self.provider == "deepseek":
            return await self._call_deepseek(messages, max_tokens, temperature)
        else:
            raise ValueError(f"不支持的 Provider: {self.provider}")
    
    async def _call_anthropic(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
    ) -> dict:
        """调用 Anthropic 兼容 API (MiniMax)"""
        # 分离 system 消息
        system_message = None
        for msg in messages:
            if msg.get("role") == "system":
                system_message = msg.get("content")
                break
        
        user_messages = [m for m in messages if m.get("role") != "system"]
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": m["role"], "content": m["content"]} for m in user_messages],
        }
        
        if system_message:
            payload["system"] = system_message
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=payload,
            )
            
            if response.status_code != 200:
                raise Exception(f"API 错误: {response.status_code} - {response.text}")
            
            data = response.json()
            
            return {
                "content": data["content"][0]["text"] if data.get("content") else "",
                "model": data.get("model", self.model),
                "tokens": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0),
            }
    
    async def _call_openai(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
    ) -> dict:
        """调用 OpenAI API"""
        payload = {
            "model": self.model,
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            
            if response.status_code != 200:
                raise Exception(f"API 错误: {response.status_code} - {response.text}")
            
            data = response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": data.get("model", self.model),
                "tokens": data.get("usage", {}).get("total_tokens", 0),
            }
    
    async def _call_deepseek(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
    ) -> dict:
        """调用 DeepSeek API"""
        return await self._call_openai(messages, max_tokens, temperature)
