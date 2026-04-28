"""LLM Provider Manager - handles different LLM backends (Claude, Groq, etc.)"""
import os
from typing import Optional, Dict, Any

class LLMProviderManager:
    """Manages multiple LLM provider configurations"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "claude")
        self._load_providers()
    
    def _load_providers(self):
        """Load available LLM providers from environment"""
        # Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            self.providers["claude"] = {
                "type": "claude",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
            }
        
        # Groq
        if os.getenv("GROQ_API_KEY"):
            self.providers["groq"] = {
                "type": "groq",
                "api_key": os.getenv("GROQ_API_KEY"),
                "model": os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
            }
    
    def get_provider(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get provider config by name"""
        name = provider_name or self.default_provider
        if name not in self.providers:
            return self.providers.get(list(self.providers.keys())[0], {})
        return self.providers[name]
    
    def list_providers(self) -> list:
        """List available providers"""
        return list(self.providers.keys())
"""Lightweight LLM provider manager used by legal agent.

This compatibility implementation avoids hard dependencies while keeping
public methods expected by existing code.
"""

from __future__ import annotations

import os
import json
import requests
from typing import AsyncGenerator


class GroqProvider:
    def __init__(self, model: str | None = None):
        self.api_key = (os.getenv("GROQ_API_KEY") or "").strip()
        self.model = model or os.getenv("GROQ_CHAT_MODEL", "llama-3.1-8b-instant")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def chat(self, messages: list, system: str = "", max_tokens: int = 4096, tools: list | None = None) -> dict:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY chưa được cấu hình")

        wire_messages = []
        if system:
            wire_messages.append({"role": "system", "content": system})
        wire_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": wire_messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        resp = requests.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        message = ((data.get("choices") or [{}])[0].get("message") or {})

        content = []
        if message.get("content"):
            content.append({"type": "text", "text": message["content"]})

        for tool_call in message.get("tool_calls") or []:
            func = tool_call.get("function") or {}
            try:
                parsed_input = json.loads(func.get("arguments") or "{}")
            except Exception:
                parsed_input = {}
            content.append({
                "type": "tool_use",
                "id": tool_call.get("id"),
                "name": func.get("name"),
                "input": parsed_input,
            })

        return {
            "content": content,
            "model": data.get("model", self.model),
            "usage": data.get("usage", {}),
            "stop_reason": "tool_use" if message.get("tool_calls") else "end_turn",
        }

    async def chat_stream(self, messages: list, system: str = "", max_tokens: int = 4096, tools: list | None = None) -> AsyncGenerator[dict, None]:
        # Compatibility fallback: emit one aggregated event.
        result = await self.chat(messages=messages, system=system, max_tokens=max_tokens, tools=tools)
        yield result


class LLMProviderManager:
    """Compatibility manager with the same API used by legal_agent."""

    def __init__(self, db_connection=None):
        self.db = db_connection

    def get_company_provider(self, company_id: str):
        # Current integration uses one default provider from env.
        return GroqProvider()
